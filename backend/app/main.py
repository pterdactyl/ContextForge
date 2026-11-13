import pymupdf

from uuid import UUID

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.services.ingestion_service import ingest_document

from pydantic import BaseModel
from app.services.retrieval_service import search_similar_chunks

from app.services.llm_service import generate_answer

from fastapi.middleware.cors import CORSMiddleware

from app.database.models import Document

app = FastAPI(title="ContextForge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/documents/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session= Depends(get_db)

):
    if not file.filename or not file.filename.lower().endswith((".txt", ".pdf")):
        raise HTTPException(
            status_code = 400,
            detail="Only .txt and .pdf files are supported"
        )

    try:
        content = file.file.read()

        document = ingest_document(
            filename=file.filename,
            content=content,
            db=db
        )

    except (UnicodeDecodeError, ValueError, pymupdf.FileDataError) as e:
        raise HTTPException(
            status_code = 400,
            detail="Could not extract text from uploaded file"
        ) from e

    return {
            "document_id": str(document.id),
            "filename": document.filename,
            "chunk_created": len(document.chunks),
            "status": "processed"
    }


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@app.post("/documents/search")
def search_documents(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    try:
        results = search_similar_chunks(
            query=request.query,
            db=db,
            top_k=request.top_k
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) from e

    return {
        "query": request.query,
        "results": results
    }

@app.post("/chat/ask")
def ask_question(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    try:
        chunks = search_similar_chunks(
            query=request.query,
            db=db,
            top_k=request.top_k
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        ) from e

    if not chunks:
        return {
            "answer": "No documents available to answer this question.",
            "sources": []
        }

    answer = generate_answer(request.query, chunks)

    return {
        "answer": answer,
        "sources": [
            {
                "filename": chunk["filename"],
                "chunk_index": chunk["chunk_index"],
                "similarity": chunk["similarity"]
            }
            for chunk in chunks
        ]
    }

@app.get("/documents")
def list_documents(db: Session = Depends(get_db)):
    documents = db.scalars(
        select(Document).order_by(Document.id.desc())
    ).all()

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
        }
        for doc in documents
    ]

@app.delete("/documents/{document_id}")
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db)
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    db.delete(document)
    db.commit()

    return {"message": "Document deleted successfully"}

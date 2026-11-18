import pymupdf

from uuid import UUID

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.services.ingestion_service import ingest_document

from pydantic import BaseModel
from app.services.retrieval_service import (
        search_similar_chunks,
        hybrid_search,
)

from app.services.llm_service import generate_answer, rewrite_query

from app.services.reranking_service import rerank_chunks

from app.services.conversation_service import (
    create_conversation,
    get_conversation,
    get_conversation_history,
    save_message,
)

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

class ChatRequest(SearchRequest):
    conversation_id: UUID | None = None


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
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    if request.conversation_id is not None:
        conversation = get_conversation(
            db, request.conversation_id
        )

        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )
    else:
        conversation = create_conversation(db)

    history = get_conversation_history(
        db,
        conversation.id,
        limit=10
    )

    search_query = rewrite_query(
    question=request.query,
    history=history
    )

    candidates = hybrid_search(
        query=search_query,
        db=db,
        top_k=max(request.top_k * 4, 20)
    )

    chunks = rerank_chunks(
        query=search_query,
        chunks=candidates,
        top_k=request.top_k
    )

    answer = generate_answer(
        question=request.query,
        chunks=chunks,
        history=history
    )

    print(f"Original query: {request.query}")
    print(f"Search query: {search_query}")

    sources = [
        {
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "similarity": chunk.get("similarity"),
            "rrf_score": chunk.get("rrf_score"),
            "rerank_score": chunk.get("rerank_score")
        }
        for chunk in chunks
    ]

    save_message(
        db, conversation.id, "user", request.query
    )

    save_message(
        db, conversation.id, "assistant", answer
    )

    return {
        "answer": answer,
        "sources": sources,
        "conversation_id": conversation.id
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


from sqlalchemy.orm import Session

from app.database.models import Document, DocumentChunk
from app.services.document_service import extract_text
from app.services.chunking_service import chunk_text
from app.services.embedding_service import generate_embeddings

def ingest_document(
    filename: str,
    content: bytes,
    db: Session
) -> Document:

    # 1. Extract text
    text = extract_text(filename, content)

    # 2. Split text into chunks
    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("Document contains no extractable text")

    # 3. Generate embeddings
    embeddings = generate_embeddings(chunks)

    # 4. Create document record
    document = Document(
        filename=filename,
        content_type=(
            "application/pdf"
            if filename.lower().endswith(".pdf")
            else "text/plain"
        )
    )

    # 5. Associate chunks with the document
    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings, strict=True)
    ):
        document.chunks.append(
            DocumentChunk(
                chunk_index=index,
                content=chunk,
                embedding=embedding
            )
        )

    # 6. Save everything in one transaction
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise

    return document

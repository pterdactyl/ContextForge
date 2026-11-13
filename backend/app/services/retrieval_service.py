
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Document, DocumentChunk
from app.services.embedding_service import generate_embeddings


def search_similar_chunks(
    query: str,
    db: Session,
    top_k: int = 5
) -> list[dict]:

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if top_k < 1:
        raise ValueError("top_k must be positive")

    # Convert the question into an embedding
    query_embedding = generate_embeddings([query])[0]

    # Cosine distance: smaller means more similar
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    stmt = (
        select(
            DocumentChunk,
            Document.filename,
            distance.label("distance")
        )
        .join(Document, DocumentChunk.document_id == Document.id)
        .order_by(distance)
        .limit(top_k)
    )

    results = db.execute(stmt).all()

    return [
        {
            "chunk_id": str(chunk.id),
            "document_id": str(chunk.document_id),
            "filename": filename,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "similarity": float(1 - dist)
        }
        for chunk, filename, dist in results
    ]


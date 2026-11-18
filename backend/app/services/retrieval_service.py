from sqlalchemy import select, func
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

def search_keyword_chunks(
    query: str,
    db: Session,
    top_k: int = 5
) -> list[dict]:

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if top_k < 1:
        raise ValueError("top_k must be positive")

    # Convert document content into searchable tokens
    document_vector = func.to_tsvector(
        "english",
        DocumentChunk.content
    )

    # Convert the user's query into search tokens
    search_query = func.plainto_tsquery(
        "english",
        query
    )

    # Calculate relevance based on keyword matching
    rank = func.ts_rank(
        document_vector,
        search_query
    )

    stmt = (
        select(
            DocumentChunk,
            Document.filename,
            rank.label("rank")
        )
        .join(
            Document,
            DocumentChunk.document_id == Document.id
        )
        .where(
            document_vector.op("@@")(search_query)
        )
        .order_by(rank.desc(), DocumentChunk.id)
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
            "keyword_score": float(score)
        }
        for chunk, filename, score in results
    ]

def hybrid_search(
    query: str,
    db: Session,
    top_k: int = 5
) -> list[dict]:

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if top_k < 1:
        raise ValueError("top_k must be positive")

    candidate_k = max(top_k * 4, 20)
    rrf_k = 60

    vector_results = search_similar_chunks(
        query, db, top_k=candidate_k
    )

    keyword_results = search_keyword_chunks(
        query, db, top_k=candidate_k
    )

    combined = {}

    for results in (vector_results, keyword_results):
        for rank, chunk in enumerate(results, start=1):
            chunk_id = chunk["chunk_id"]

            if chunk_id not in combined:
                combined[chunk_id] = {
                    **chunk,
                    "rrf_score": 0.0
                }

            combined[chunk_id]["rrf_score"] += (
                1 / (rrf_k + rank)
            )

    ranked = sorted(
        combined.values(),
        key=lambda chunk: (-chunk["rrf_score"], chunk["chunk_id"])
    )

    return ranked[:top_k]

from sentence_transformers import CrossEncoder

# Load model once, not on every request
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L6-v2"
)


def rerank_chunks(
    query: str,
    chunks: list[dict],
    top_k: int = 5
) -> list[dict]:

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if top_k < 1:
        raise ValueError("top_k must be positive")

    if not chunks:
        return []

    # Pair the question with every retrieved chunk
    pairs = [
        (query, chunk["content"])
        for chunk in chunks
    ]

    # Cross-encoder predicts relevance scores
    scores = reranker.predict(pairs)

    # Attach scores to the chunks
    ranked_chunks = [
        {
            **chunk,
            "rerank_score": float(score)
        }
        for chunk, score in zip(chunks, scores)
    ]

    # Sort by relevance, highest first
    ranked_chunks.sort(
        key=lambda chunk: chunk["rerank_score"],
        reverse=True
    )

    return ranked_chunks[:top_k]

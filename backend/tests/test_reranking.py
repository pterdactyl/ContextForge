from app.services.reranking_service import rerank_chunks


def test_reranking():

    chunks = [
        {
            "chunk_id": "1",
            "content": "Python is a programming language."
        },
        {
            "chunk_id": "2",
            "content": "PostgreSQL is a relational database."
        },
        {
            "chunk_id": "3",
            "content": "React is a JavaScript frontend library."
        }
    ]

    results = rerank_chunks(
        query="What database is used?",
        chunks=chunks,
        top_k=2
    )

    assert len(results) == 2

    for result in results:
        print(
            result["chunk_id"],
            result["rerank_score"],
            result["content"]
        )

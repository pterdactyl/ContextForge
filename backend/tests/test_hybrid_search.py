from app.database.connection import SessionLocal
from app.services.retrieval_service import hybrid_search


def test_hybrid_search():
    with SessionLocal() as db:
        results = hybrid_search(
            query="Python",
            db=db,
            top_k=5
        )

        assert len(results) <= 5

        for result in results:
            print("Filename:", result["filename"])
            print("RRF Score:", result["rrf_score"])
            print("Content:", result["content"][:200])
            print("-" * 50)

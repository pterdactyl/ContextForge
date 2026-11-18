from app.database.connection import SessionLocal
from app.services.retrieval_service import search_keyword_chunks

def test_keyword_search():
    with SessionLocal() as db:
        results = search_keyword_chunks(
            query="Python",
            db=db,
            top_k=5
        )

        for result in results:
            print("Filename:", result["filename"])
            print("Keyword Score:", result["keyword_score"])
            print("Content:", result["content"][:200])
            print("-" * 50)


if __name__ == "__main__":
    test_keyword_search()


import json
from pathlib import Path

from app.database.connection import SessionLocal
from app.services.retrieval_service import (
    search_similar_chunks,
    hybrid_search,
)
from app.services.reranking_service import rerank_chunks

from evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)

DATASET_PATH = Path(__file__).with_name("eval_dataset.json")

TOP_K = 5
CANDIDATE_K = 20


def evaluate_results(results, relevant_ids):
    retrieved_ids = [
        chunk["chunk_id"]
        for chunk in results
    ]

    return {
        "precision": precision_at_k(
            retrieved_ids, relevant_ids, TOP_K
        ),
        "recall": recall_at_k(
            retrieved_ids, relevant_ids, TOP_K
        ),
        "mrr": reciprocal_rank(
            retrieved_ids[:TOP_K], relevant_ids
        ),
    }


def run_evaluation():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        dataset = json.load(file)

    if not dataset:
        raise ValueError("Evaluation dataset is empty")

    methods = {
        "vector": [],
        "hybrid": [],
        "reranked": [],
    }

    with SessionLocal() as db:
        for item in dataset:
            query = item["query"]
            relevant_ids = set(item["relevant_chunk_ids"])

            if not relevant_ids:
                raise ValueError(
                    f"No relevant chunks for: {query}"
                )

            print(f"Evaluating: {query}")

            # 1. Vector-only search
            vector_results = search_similar_chunks(
                query=query,
                db=db,
                top_k=TOP_K
            )

            # 2. Hybrid search
            hybrid_results = hybrid_search(
                query=query,
                db=db,
                top_k=TOP_K
            )

            # 3. Hybrid search + reranking
            candidates = hybrid_search(
                query=query,
                db=db,
                top_k=CANDIDATE_K
            )

            reranked_results = rerank_chunks(
                query=query,
                chunks=candidates,
                top_k=TOP_K
            )

            results_by_method = {
                "vector": vector_results,
                "hybrid": hybrid_results,
                "reranked": reranked_results,
            }

            for method, results in results_by_method.items():
                scores = evaluate_results(
                    results,
                    relevant_ids
                )
                methods[method].append(scores)

    print("\n=== RETRIEVAL EVALUATION RESULTS ===")

    for method, scores in methods.items():
        count = len(scores)

        print(f"\n{method.upper()}")
        print(
            f"Precision@5: "
            f"{sum(s['precision'] for s in scores) / count:.3f}"
        )
        print(
            f"Recall@5: "
            f"{sum(s['recall'] for s in scores) / count:.3f}"
        )
        print(
            f"MRR@5: "
            f"{sum(s['mrr'] for s in scores) / count:.3f}"
        )


if __name__ == "__main__":
    run_evaluation()


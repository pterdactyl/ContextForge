from evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_retrieval_metrics():
    retrieved = ["A", "B", "C", "D", "E"]
    relevant = {"B", "D"}

    assert precision_at_k(retrieved, relevant, 5) == 0.4
    assert recall_at_k(retrieved, relevant, 5) == 1.0
    assert reciprocal_rank(retrieved, relevant) == 0.5

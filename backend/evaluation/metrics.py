def precision_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int
) -> float:
    if k < 1:
        raise ValueError("k must be positive")

    hits = sum(
        chunk_id in relevant_ids
        for chunk_id in retrieved_ids[:k]
    )

    return hits / k


def recall_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int
) -> float:
    if k < 1:
        raise ValueError("k must be positive")

    if not relevant_ids:
        return 0.0

    hits = sum(
        chunk_id in relevant_ids
        for chunk_id in retrieved_ids[:k]
    )

    return hits / len(relevant_ids)


def reciprocal_rank(
    retrieved_ids: list[str],
    relevant_ids: set[str]
) -> float:
    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant_ids:
            return 1 / rank

    return 0.0

from dataclasses import dataclass
from typing import List


@dataclass
class QueryResult:
    query: str
    expected_id: int
    ranked_ids: List[int]


def recall_at_k(results: List[QueryResult], k: int) -> float:
    if not results:
        return 0.0
    hits = sum(1 for r in results if r.expected_id in r.ranked_ids[:k])
    return hits / len(results)


def mrr_at_k(results: List[QueryResult], k: int) -> float:
    if not results:
        return 0.0
    rr_sum = 0.0
    for r in results:
        top_k = r.ranked_ids[:k]
        if r.expected_id in top_k:
            rr_sum += 1.0 / (top_k.index(r.expected_id) + 1)
    return rr_sum / len(results)

import sys
sys.path.insert(0, '..')

from metrics import QueryResult, recall_at_k, mrr_at_k


def test_recall_at_1_hit():
    assert recall_at_k([QueryResult("q", 1, [1, 2, 3])], 1) == 1.0


def test_recall_at_1_miss():
    assert recall_at_k([QueryResult("q", 1, [2, 3, 4])], 1) == 0.0


def test_recall_at_5_found_at_position_3():
    assert recall_at_k([QueryResult("q", 3, [1, 2, 3, 4, 5])], 5) == 1.0


def test_recall_at_5_not_in_top_5():
    assert recall_at_k([QueryResult("q", 6, [1, 2, 3, 4, 5])], 5) == 0.0


def test_recall_multiple_results():
    results = [QueryResult("q1", 1, [1, 2, 3]), QueryResult("q2", 2, [3, 1, 2])]
    assert recall_at_k(results, 1) == 0.5


def test_mrr_at_5_first_position():
    assert mrr_at_k([QueryResult("q", 1, [1, 2, 3, 4, 5])], 5) == 1.0


def test_mrr_at_5_second_position():
    assert mrr_at_k([QueryResult("q", 2, [1, 2, 3, 4, 5])], 5) == 0.5


def test_mrr_at_5_not_found():
    assert mrr_at_k([QueryResult("q", 6, [1, 2, 3, 4, 5])], 5) == 0.0


def test_mrr_multiple_results():
    results = [QueryResult("q1", 1, [1, 2, 3, 4, 5]), QueryResult("q2", 2, [1, 2, 3, 4, 5])]
    assert mrr_at_k(results, 5) == 0.75  # (1.0 + 0.5) / 2


def test_empty_results():
    assert recall_at_k([], 1) == 0.0
    assert mrr_at_k([], 5) == 0.0

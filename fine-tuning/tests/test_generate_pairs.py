import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unittest.mock import MagicMock
from autosearch.config import AutoSearchConfig
from generate_pairs import generate_queries, item_hash, item_text, split_pairs

REPO_ROOT = Path(__file__).parent.parent.parent
CFG = AutoSearchConfig.from_yaml(REPO_ROOT / "config.yaml")

ITEM = {"item_id": 1, "wpp_id": 1, "name": "GP FTE",
        "description": "Full-time equivalent general practitioners."}


def test_item_hash_changes_on_name_change():
    assert item_hash({**ITEM, "name": "GP FTE"}, CFG) != item_hash({**ITEM, "name": "GP Headcount"}, CFG)


def test_item_hash_is_stable():
    assert item_hash(ITEM, CFG) == item_hash(ITEM, CFG)


def test_item_text_combines_name_and_description():
    assert item_text(ITEM, CFG) == "GP FTE Full-time equivalent general practitioners."


def test_item_text_no_description():
    assert item_text({**ITEM, "description": ""}, CFG) == "GP FTE"


def test_split_pairs_80_20():
    queries = [f"query {i}" for i in range(10)]
    train, holdout = split_pairs(queries, ITEM, CFG)
    assert len(train) == 8
    assert len(holdout) == 2


def test_split_pairs_all_carry_item_text_and_id():
    queries = [f"q{i}" for i in range(10)]
    train, holdout = split_pairs(queries, ITEM, CFG)
    for pair in train + holdout:
        assert pair["item_text"] == item_text(ITEM, CFG)
        assert pair["item_id"] == 1


def test_generate_queries_calls_haiku_and_parses_json():
    client = MagicMock()
    client.messages.create.return_value.content = [
        MagicMock(text='["query 1", "query 2", "query 3"]')
    ]
    result = generate_queries(client, ITEM, CFG)
    assert result == ["query 1", "query 2", "query 3"]
    call_kwargs = client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-haiku-4-5-20251001"

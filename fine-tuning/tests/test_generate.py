import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from autosearch.config import AutoSearchConfig
from generate_pairs import item_hash, item_text, split_pairs

FIXTURE_CFG = Path(__file__).parent / "fixtures" / "test-config.yaml"


def test_item_hash_uses_config():
    cfg = AutoSearchConfig.from_yaml(FIXTURE_CFG)
    item = {"service_id": 1, "category_id": 1, "title": "Password Reset", "summary": "Reset creds"}
    h = item_hash(item, cfg)
    assert len(h) == 64


def test_item_text_uses_config():
    cfg = AutoSearchConfig.from_yaml(FIXTURE_CFG)
    item = {"service_id": 1, "category_id": 1, "title": "Password Reset", "summary": "Reset creds"}
    assert item_text(item, cfg) == "Password Reset Reset creds"


def test_split_pairs_uses_config_id_field():
    cfg = AutoSearchConfig.from_yaml(FIXTURE_CFG)
    item = {"service_id": 7, "category_id": 1, "title": "Account Deactivation", "summary": "Disable account"}
    queries = [f"query {i}" for i in range(10)]
    train, holdout = split_pairs(queries, item, cfg)
    assert all(p["item_id"] == 7 for p in train + holdout)
    assert len(train) + len(holdout) == 10

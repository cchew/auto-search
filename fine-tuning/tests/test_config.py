import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from autosearch.config import AutoSearchConfig, item_hash, item_text

FIXTURE_YAML = Path(__file__).parent / "fixtures" / "test-config.yaml"


def test_loads_corpus_fields():
    cfg = AutoSearchConfig.from_yaml(FIXTURE_YAML)
    assert cfg.corpus.id_field == "service_id"
    assert cfg.corpus.group_field == "category_id"
    assert cfg.corpus.name_field == "title"
    assert cfg.corpus.description_field == "summary"


def test_loads_pipeline_domain_description():
    cfg = AutoSearchConfig.from_yaml(FIXTURE_YAML)
    assert "helpdesk" in cfg.pipeline.domain_description


def test_loads_name():
    cfg = AutoSearchConfig.from_yaml(FIXTURE_YAML)
    assert cfg.name == "it-service-catalogue"


def test_item_hash_uses_config_fields():
    cfg = AutoSearchConfig.from_yaml(FIXTURE_YAML)
    item = {"service_id": 1, "category_id": 2, "title": "Password Reset", "summary": "Reset credentials"}
    h = item_hash(item, cfg)
    assert isinstance(h, str) and len(h) == 64


def test_item_text_uses_config_fields():
    cfg = AutoSearchConfig.from_yaml(FIXTURE_YAML)
    item = {"service_id": 1, "category_id": 2, "title": "Password Reset", "summary": "Reset credentials"}
    assert item_text(item, cfg) == "Password Reset Reset credentials"


def test_item_text_handles_missing_description():
    cfg = AutoSearchConfig.from_yaml(FIXTURE_YAML)
    item = {"service_id": 1, "category_id": 2, "title": "Password Reset"}
    assert item_text(item, cfg) == "Password Reset"

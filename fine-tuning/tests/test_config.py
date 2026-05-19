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


def test_validate_rejects_missing_name(tmp_path):
    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text("""
corpus:
  id_field: item_id
  group_field: wpp_id
  name_field: name
  description_field: description
""")
    with pytest.raises(ValueError, match="name"):
        AutoSearchConfig.from_yaml(yaml_path)


def test_validate_rejects_empty_id_field(tmp_path):
    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text("""
name: test
corpus:
  id_field: ""
  group_field: wpp_id
  name_field: name
  description_field: description
""")
    with pytest.raises(ValueError, match="id_field"):
        AutoSearchConfig.from_yaml(yaml_path)


def test_validate_rejects_invalid_pairs_per_item(tmp_path):
    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text("""
name: test
corpus:
  id_field: item_id
  group_field: wpp_id
  name_field: name
  description_field: description
pipeline:
  pairs_per_item: 0
""")
    with pytest.raises(ValueError, match="pairs_per_item"):
        AutoSearchConfig.from_yaml(yaml_path)


def test_validate_rejects_invalid_train_test_split(tmp_path):
    yaml_path = tmp_path / "bad.yaml"
    yaml_path.write_text("""
name: test
corpus:
  id_field: item_id
  group_field: wpp_id
  name_field: name
  description_field: description
pipeline:
  train_test_split: 1.5
""")
    with pytest.raises(ValueError, match="train_test_split"):
        AutoSearchConfig.from_yaml(yaml_path)

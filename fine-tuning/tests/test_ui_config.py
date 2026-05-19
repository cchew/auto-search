import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autosearch.config import AutoSearchConfig
from autosearch.ui_config import derive_ui_config


class FakeClient:
    """Stand-in for anthropic.Anthropic — returns scripted responses by call order."""
    def __init__(self, responses: list[str]):
        self._responses = list(responses)
        self.messages = self

    def create(self, **_kwargs):
        text = self._responses.pop(0)
        class Block:
            def __init__(self, t): self.text = t
        class Resp:
            def __init__(self, t): self.content = [Block(t)]
        return Resp(text)


FIXTURE_CFG = Path(__file__).parent / "fixtures" / "test-config.yaml"


def test_derive_ui_config_builds_expected_shape(tmp_path):
    cfg = AutoSearchConfig.from_yaml(FIXTURE_CFG)
    corpus = [
        {"service_id": 1, "category_id": 1, "title": "Password Reset", "summary": "Reset creds"},
        {"service_id": 2, "category_id": 1, "title": "Account Unlock", "summary": "Unlock account"},
        {"service_id": 3, "category_id": 2, "title": "Laptop Replacement", "summary": "Get a new laptop"},
    ]
    labels_json = json.dumps({
        "appTitle": "IT Service Catalogue",
        "appLede": "Semantic search across IT services.",
        "groupNames": {"1": "Identity & Access", "2": "Hardware"},
    })
    suggestions_json = json.dumps([
        "I forgot my password",
        "I need a new laptop",
        "Unlock my account",
        "Wi-fi setup help",
    ])
    client = FakeClient([labels_json, suggestions_json])

    ui = derive_ui_config(corpus, cfg, client)

    assert ui["appTitle"] == "IT Service Catalogue"
    assert ui["appLede"] == "Semantic search across IT services."
    assert ui["groupNames"] == {"1": "Identity & Access", "2": "Hardware"}
    assert ui["suggestions"] == [
        "I forgot my password",
        "I need a new laptop",
        "Unlock my account",
        "Wi-fi setup help",
    ]
    assert ui["idField"] == cfg.corpus.id_field
    assert ui["groupField"] == cfg.corpus.group_field
    assert ui["nameField"] == cfg.corpus.name_field
    assert ui["descriptionField"] == cfg.corpus.description_field


def test_derive_ui_config_handles_unknown_group_ids(tmp_path):
    cfg = AutoSearchConfig.from_yaml(FIXTURE_CFG)
    corpus = [
        {"service_id": 1, "category_id": 1, "title": "X", "summary": ""},
        {"service_id": 2, "category_id": 99, "title": "Y", "summary": ""},
    ]
    labels_json = json.dumps({
        "appTitle": "T", "appLede": "L",
        "groupNames": {"1": "Identity & Access"},
    })
    suggestions_json = json.dumps(["a", "b", "c", "d"])
    client = FakeClient([labels_json, suggestions_json])

    ui = derive_ui_config(corpus, cfg, client)

    assert ui["groupNames"]["1"] == "Identity & Access"
    assert ui["groupNames"]["99"] == "Group 99"

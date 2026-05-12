import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np

from generate_pairs import item_hash
from precompute_embeddings import load_embeddings, load_manifest

CORPUS = [
    {"item_id": 1, "wpp_id": 1, "name": "GP FTE", "description": "Full-time equivalent GPs."},
    {"item_id": 2, "wpp_id": 1, "name": "GP Headcount", "description": "Total number of GPs."},
]


def test_load_manifest_returns_empty_when_missing():
    assert load_manifest(Path("/nonexistent/manifest.json")) == {}


def test_load_embeddings_returns_empty_when_missing():
    assert load_embeddings(Path("/nonexistent/data-items.json")) == []


def test_all_items_treated_as_new_on_first_run():
    manifest = {}
    new_items = [i for i in CORPUS if item_hash(i) != manifest.get(str(i["item_id"]))]
    assert len(new_items) == 2


def test_unchanged_items_skipped_when_manifest_current():
    manifest = {str(i["item_id"]): item_hash(i) for i in CORPUS}
    new_items = [i for i in CORPUS if item_hash(i) != manifest.get(str(i["item_id"]))]
    assert len(new_items) == 0


def test_changed_item_detected():
    manifest = {str(i["item_id"]): item_hash(i) for i in CORPUS}
    changed = {**CORPUS[0], "name": "GP FTE (revised)"}
    corpus_updated = [changed, CORPUS[1]]
    new_items = [i for i in corpus_updated if item_hash(i) != manifest.get(str(i["item_id"]))]
    assert len(new_items) == 1
    assert new_items[0]["item_id"] == 1

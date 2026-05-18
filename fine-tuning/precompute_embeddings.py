import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from autosearch.config import AutoSearchConfig, item_hash, item_text

REPO_ROOT = Path(__file__).parent.parent


def load_manifest(path: Path) -> dict[str, str]:
    return json.loads(path.read_text()) if path.exists() else {}


def load_embeddings(path: Path) -> list[dict]:
    return json.loads(path.read_text()) if path.exists() else []


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--config", default=str(REPO_ROOT / "config.yaml"), type=Path)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    cfg = AutoSearchConfig.from_yaml(args.config)
    output_dir = cfg.output_dir(local=args.local)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest-embeddings.json"
    embeddings_path = output_dir / "data-items.json"

    id_field = cfg.corpus.id_field
    corpus: list[dict] = json.loads(args.corpus.read_text())
    manifest = load_manifest(manifest_path)
    existing_by_id = {str(e[id_field]): e for e in load_embeddings(embeddings_path)}

    new_items = [i for i in corpus if item_hash(i, cfg) != manifest.get(str(i[id_field]))]
    print(f"{len(new_items)} items need re-embedding")

    if new_items:
        model = SentenceTransformer(str(output_dir / "model"))
        vectors = model.encode([item_text(i, cfg) for i in new_items], normalize_embeddings=True)
        for item, vec in zip(new_items, vectors):
            record = {k: item[k] for k in (id_field, cfg.corpus.group_field, cfg.corpus.name_field) if k in item}
            record["embedding"] = vec.tolist()
            existing_by_id[str(item[id_field])] = record
            manifest[str(item[id_field])] = item_hash(item, cfg)

    embeddings_path.write_text(json.dumps(list(existing_by_id.values()), indent=2))
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"data-items.json: {len(existing_by_id)} items")


if __name__ == "__main__":
    main()

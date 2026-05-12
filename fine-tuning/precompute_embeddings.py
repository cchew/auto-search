import argparse
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from generate_pairs import item_hash, item_text


def load_manifest(path: Path) -> dict[str, str]:
    return json.loads(path.read_text()) if path.exists() else {}


def load_embeddings(path: Path) -> list[dict]:
    return json.loads(path.read_text()) if path.exists() else []


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    output_dir = Path("output" if args.local else "/tmp/pipeline")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest-embeddings.json"
    embeddings_path = output_dir / "data-items.json"

    corpus: list[dict] = json.loads(args.corpus.read_text())
    manifest = load_manifest(manifest_path)
    existing_by_id = {str(e["item_id"]): e for e in load_embeddings(embeddings_path)}

    new_items = [i for i in corpus if item_hash(i) != manifest.get(str(i["item_id"]))]
    print(f"{len(new_items)} items need re-embedding")

    if new_items:
        model = SentenceTransformer(str(output_dir / "model"))
        vectors = model.encode([item_text(i) for i in new_items], normalize_embeddings=True)
        for item, vec in zip(new_items, vectors):
            existing_by_id[str(item["item_id"])] = {
                "item_id": item["item_id"],
                "wpp_id": item["wpp_id"],
                "name": item["name"],
                "embedding": vec.tolist(),
            }
            manifest[str(item["item_id"])] = item_hash(item)

    embeddings_path.write_text(json.dumps(list(existing_by_id.values()), indent=2))
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"data-items.json: {len(existing_by_id)} items")


if __name__ == "__main__":
    main()

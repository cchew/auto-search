import argparse
import json
import os
import random
import time
from pathlib import Path

import anthropic

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from autosearch.config import AutoSearchConfig, item_hash, item_text

REPO_ROOT = Path(__file__).parent.parent


def generate_queries(client: anthropic.Anthropic, item: dict, cfg: AutoSearchConfig) -> list[str]:
    prompt = (
        f"Item:\nName: {item[cfg.corpus.name_field]}\n"
        f"Description: {item.get(cfg.corpus.description_field, '')}\n\n"
        f"Generate {cfg.pipeline.pairs_per_item} diverse natural-language queries "
        f"{cfg.pipeline.domain_description} might type to find this item. "
        f"Include synonyms, colloquial phrasings, and different specificity levels. "
        f"Return as a JSON array of strings only."
    )
    for attempt in range(5):
        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            break
        except anthropic.RateLimitError:
            wait = 60 * (attempt + 1)
            print(f"  Rate limited; waiting {wait}s (attempt {attempt + 1}/5)...")
            time.sleep(wait)
    else:
        raise RuntimeError(f"Rate limit not resolved after 5 attempts for item {item[cfg.corpus.id_field]}")
    text = response.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


def split_pairs(queries: list[str], item: dict, cfg: AutoSearchConfig) -> tuple[list[dict], list[dict]]:
    text = item_text(item, cfg)
    item_id = item[cfg.corpus.id_field]
    pairs = [{"query": q, "item_text": text, "item_id": item_id} for q in queries]
    holdout_n = max(1, round(len(pairs) * (1 - cfg.pipeline.train_test_split)))
    random.shuffle(pairs)
    return pairs[holdout_n:], pairs[:holdout_n]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--config", default=str(REPO_ROOT / "examples" / "health-workforce" / "config.yaml"), type=Path)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    cfg = AutoSearchConfig.from_yaml(args.config)
    output_dir = cfg.output_dir(local=args.local)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest-pairs.json"

    corpus: list[dict] = json.loads(args.corpus.read_text())
    manifest: dict[str, str] = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    id_field = cfg.corpus.id_field
    new_items = [i for i in corpus if item_hash(i, cfg) != manifest.get(str(i[id_field]))]
    print(f"{len(new_items)} new/changed items out of {len(corpus)}")
    if not new_items:
        print("Nothing to generate.")
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")
    client = anthropic.Anthropic(api_key=api_key)

    def append_jsonl(path: Path, records: list[dict]) -> None:
        with open(path, "a") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    total_train, total_holdout = 0, 0
    for item in new_items:
        print(f"  Generating: {item[cfg.corpus.name_field]}")
        queries = generate_queries(client, item, cfg)
        train, holdout = split_pairs(queries, item, cfg)
        append_jsonl(output_dir / "pairs-train.jsonl", train)
        append_jsonl(output_dir / "pairs-holdout.jsonl", holdout)
        manifest[str(item[id_field])] = item_hash(item, cfg)
        manifest_path.write_text(json.dumps(manifest, indent=2))
        total_train += len(train)
        total_holdout += len(holdout)

    print(f"Generated {total_train} train / {total_holdout} holdout pairs")


if __name__ == "__main__":
    main()

import argparse
import hashlib
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

QUERIES_PER_ITEM = 10
HOLDOUT_FRACTION = 0.2


def item_hash(item: dict) -> str:
    payload = f"{item['wpp_id']}:{item['item_id']}:{item['name']}:{item.get('description', '')}"
    return hashlib.sha256(payload.encode()).hexdigest()


def item_text(item: dict) -> str:
    return f"{item['name']} {item.get('description', '')}".strip()


def generate_queries(client: anthropic.Anthropic, item: dict) -> list[str]:
    prompt = (
        f"Data item:\nName: {item['name']}\nDescription: {item.get('description', '')}\n\n"
        f"Generate {QUERIES_PER_ITEM} diverse natural-language queries a health workforce planner "
        f"might type to find this item. Include acronym expansions, synonyms, colloquial phrasings, "
        f"and different specificity levels. Return as a JSON array of strings only."
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
        raise RuntimeError(f"Rate limit not resolved after 5 attempts for item {item['item_id']}")
    text = response.content[0].text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0].strip()
    return json.loads(text)


def split_pairs(queries: list[str], item: dict) -> tuple[list[dict], list[dict]]:
    text = item_text(item)
    pairs = [{"query": q, "item_text": text, "item_id": item["item_id"]} for q in queries]
    holdout_n = max(1, round(len(pairs) * HOLDOUT_FRACTION))
    random.shuffle(pairs)
    return pairs[holdout_n:], pairs[:holdout_n]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()

    output_dir = Path("output" if args.local else "/tmp/pipeline")
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest-pairs.json"

    corpus: list[dict] = json.loads(args.corpus.read_text())
    manifest: dict[str, str] = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    new_items = [i for i in corpus if item_hash(i) != manifest.get(str(i["item_id"]))]
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
        print(f"  Generating: {item['name']}")
        queries = generate_queries(client, item)
        train, holdout = split_pairs(queries, item)
        append_jsonl(output_dir / "pairs-train.jsonl", train)
        append_jsonl(output_dir / "pairs-holdout.jsonl", holdout)
        manifest[str(item["item_id"])] = item_hash(item)
        manifest_path.write_text(json.dumps(manifest, indent=2))
        total_train += len(train)
        total_holdout += len(holdout)

    print(f"Generated {total_train} train / {total_holdout} holdout pairs")


if __name__ == "__main__":
    main()

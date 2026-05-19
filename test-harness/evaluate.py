import argparse
import csv
import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from autosearch.config import AutoSearchConfig, item_text

from metrics import QueryResult, mrr_at_k, recall_at_k
from models import SentenceTransformerEmbedder

REPO_ROOT = Path(__file__).parent.parent


def load_json(path: Path) -> list:
    return json.loads(path.read_text())


def run_evaluation(
    embedder: SentenceTransformerEmbedder,
    corpus: List[Dict],
    queries: List[Dict],
    cfg: AutoSearchConfig,
) -> List[QueryResult]:
    corpus_embeddings = embedder.embed([item_text(i, cfg) for i in corpus])
    item_ids = [i[cfg.corpus.id_field] for i in corpus]
    expected_field = f"expected_{cfg.corpus.id_field}"
    results = []
    for q in queries:
        qvec = embedder.embed([q["query"]])[0]
        ranked = [item_ids[i] for i in np.argsort(-(corpus_embeddings @ qvec))]
        results.append(QueryResult(q["query"], q[expected_field], ranked))
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--config", default=str(REPO_ROOT / "examples" / "health-workforce" / "config.yaml"), type=Path)
    parser.add_argument("--fine-tuned-model", type=Path)
    args = parser.parse_args()

    cfg = AutoSearchConfig.from_yaml(args.config)
    corpus = load_json(args.corpus)
    queries = load_json(args.queries)

    models: List[Tuple[str, SentenceTransformerEmbedder]] = [
        ("all-MiniLM-L6-v2", SentenceTransformerEmbedder("all-MiniLM-L6-v2")),
        ("bge-small-en-v1.5", SentenceTransformerEmbedder("BAAI/bge-small-en-v1.5")),
    ]
    if args.fine_tuned_model:
        models.append(("fine-tuned", SentenceTransformerEmbedder(str(args.fine_tuned_model))))

    rows = []
    print(f"\n{'Model':<30} {'Recall@1':>10} {'MRR@5':>10}")
    print("-" * 52)
    for name, embedder in models:
        results = run_evaluation(embedder, corpus, queries, cfg)
        r1 = recall_at_k(results, 1)
        mrr = mrr_at_k(results, 5)
        print(f"{name:<30} {r1:>10.3f} {mrr:>10.3f}")
        rows.append({"model": name, "recall_at_1": r1, "mrr_at_5": mrr})

    results_dir = cfg.output_dir(local=True) / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    html_rows = "".join(
        f"<tr><td>{r['model']}</td><td>{r['recall_at_1']:.3f}</td><td>{r['mrr_at_5']:.3f}</td></tr>"
        for r in rows
    )
    (results_dir / f"report-{today}.html").write_text(
        f"<html><body><h1>Evaluation {today}</h1>"
        f"<table border='1'><tr><th>Model</th><th>Recall@1</th><th>MRR@5</th></tr>"
        f"{html_rows}</table></body></html>"
    )
    with open(results_dir / f"scores-{today}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["model", "recall_at_1", "mrr_at_5"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved: {results_dir}/report-{today}.html  {results_dir}/scores-{today}.csv")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Mock Auto Search API server.

Serves the real corpus data and returns plausible search results from it.
Allows Playwright tests to run without a live Drupal instance.

Usage:
  python3 tests/mock_server.py [--port 8080] [--corpus it-service-catalogue]
"""

import json
import math
import sys
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(__file__).resolve().parents[2]  # projects/auto-search/


def load_corpus(corpus: str) -> tuple[list, dict]:
    examples = BASE / "repo" / "examples" / corpus
    output = BASE / "repo" / "output" / corpus

    corpus_items = json.loads((examples / "corpus.json").read_text())
    ui_config = json.loads((examples / "corpus-ui.json").read_text())

    id_field = ui_config.get("idField", "item_id")
    group_field = ui_config.get("groupField", "group_id")
    name_field = ui_config.get("nameField", "name")

    data_items = json.loads((output / "data-items.json").read_text())

    return corpus_items, ui_config, data_items, id_field, group_field, name_field


def dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def cosine_search(query_lower: str, data_items: list, id_field: str, group_field: str, name_field: str, min_score: float = 0.0, top_k: int = 5) -> list:
    """
    Keyword-based mock search (no ONNX here — just string matching).
    Returns results in the same shape as the real API.
    """
    terms = query_lower.lower().split()

    scored = []
    for item in data_items:
        name = str(item.get(name_field, "")).lower()
        # Simple TF-inspired score: fraction of query terms that appear in name
        hits = sum(1 for t in terms if t in name)
        score = hits / max(len(terms), 1)
        if score > 0:
            scored.append({
                "group_id": item[group_field],
                "item_id": item[id_field],
                "name": item[name_field],
                "score": round(score * 0.9, 4),  # cap below 1.0 to look realistic
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


class Handler(BaseHTTPRequestHandler):
    corpus_items: list = []
    ui_config: dict = {}
    data_items: list = []
    id_field: str = "item_id"
    group_field: str = "group_id"
    name_field: str = "name"

    def log_message(self, fmt, *args):
        print(f"  {self.command} {self.path} → {args[1]}")

    def send_json(self, status: int, data) -> None:
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/v1/search/health":
            self.send_json(200, {"status": "UP"})
        elif path == "/api/v1/corpus":
            self.send_json(200, self.corpus_items)
        elif path == "/api/v1/corpus/ui-config":
            self.send_json(200, self.ui_config)
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/v1/search":
            self.send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            req = json.loads(body)
        except json.JSONDecodeError:
            self.send_json(400, {"error": "invalid json"})
            return

        query = req.get("query", "").strip()
        top_k = max(1, min(20, int(req.get("topK", 5))))

        if not query:
            self.send_json(400, {"error": "query is required"})
            return

        results = cosine_search(
            query, self.data_items,
            self.id_field, self.group_field, self.name_field,
            top_k=top_k,
        )
        self.send_json(200, results)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--corpus", default="it-service-catalogue")
    args = parser.parse_args()

    corpus_items, ui_config, data_items, id_field, group_field, name_field = load_corpus(args.corpus)
    Handler.corpus_items = corpus_items
    Handler.ui_config = ui_config
    Handler.data_items = data_items
    Handler.id_field = id_field
    Handler.group_field = group_field
    Handler.name_field = name_field

    server = HTTPServer(("0.0.0.0", args.port), Handler)
    print(f"Mock Auto Search API  http://localhost:{args.port}")
    print(f"  corpus: {args.corpus} ({len(data_items)} items)")
    print(f"  GET  /api/v1/search/health")
    print(f"  POST /api/v1/search")
    print(f"  GET  /api/v1/corpus")
    print(f"  GET  /api/v1/corpus/ui-config")
    print("")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()

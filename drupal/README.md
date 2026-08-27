# Auto Search — Drupal Module

Semantic search inside Drupal. No Ollama. No external API. The ONNX model runs in the PHP process.

Mirrors the Auto Search Spring Boot REST contract so the existing Vue SPA works unchanged.

> **Demo only.** Default credentials (`admin`/`admin`, DB password `drupal`) are intentional for local development. Never use these in a real deployment.

---

## Quick Start

**Step 1 — get model artefacts**

```bash
cd drupal
bash setup-model.sh it-service-catalogue
```

`output/` (the trained model + embeddings) is gitignored. If you've run the training
pipeline yourself it copies from there; on a fresh clone it downloads a pretrained
copy of the bundled corpus from this repo's [GitHub Release](https://github.com/cchew/auto-search/releases/tag/drupal-demo-assets-v1) instead. Either way, this step is automatic.

**Step 2 — build and start**

```bash
docker compose up --build
```

**Step 3 — install Drupal** (first run only)

Open http://localhost:8080 and complete the installer with:
- Database: MySQL / Host: `db` / DB: `drupal` / User: `drupal` / Pass: `drupal`

**Step 4 — enable the module**

```bash
docker compose exec drupal drush en autosearch -y
docker compose exec drupal composer require ankane/onnxruntime
```

**Step 5 — test**

```bash
curl -s http://localhost:8080/api/v1/search/health
curl -s -X POST http://localhost:8080/api/v1/search \
     -H 'Content-Type: application/json' \
     -d '{"query":"password reset","topK":5}'
```

---

## Testing

### Parity test (PHP tokenizer vs Python reference)

Validates that `BertTokenizer.php` produces bit-identical token IDs to the HuggingFace fast tokenizer.
Runs in Docker — no local PHP required.

```bash
python3 tests/parity/generate_reference.py   # generate reference.json (once)
docker build -t autosearch-parity -f tests/parity/Dockerfile.parity tests/parity/
docker run --rm \
  -v $(pwd):/drupal:ro \
  -v $(pwd)/../../repo/output:/repo/output:ro \
  -e AUTOSEARCH_VOCAB_PATH=/repo/output/it-service-catalogue/artefacts/vocab.txt \
  -e AUTOSEARCH_REFERENCE_PATH=/drupal/tests/parity/reference.json \
  autosearch-parity php /drupal/tests/parity/compare_tokens.php
# Expected: 14 passed, 0 failed
```

### Functional E2E tests (API contract + browser)

```bash
# Terminal 1 — mock API server
python3 tests/mock_server.py

# Terminal 2 — Vue SPA (from repo/frontend/)
cd ../../repo/frontend && npm run dev

# Terminal 3 — run tests (from drupal/)
cd tests && npm install   # once
bash tests/e2e.sh
# Expected: 15 passed, 0 failed
```

Against real Drupal once it's running:
```bash
BACKEND=http://localhost:8080 FRONTEND=http://localhost:5173 bash tests/e2e.sh
```

All 15 tests must pass before the demo.

---

## REST API

Matches the Spring Boot Auto Search contract exactly.

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/search/health` | Liveness check |
| POST | `/api/v1/search` | `{"query": "...", "topK": 5}` → ranked results |
| GET | `/api/v1/corpus` | Full corpus JSON (for Vue SPA bootstrap) |
| GET | `/api/v1/corpus/ui-config` | UI labels and group names |

---

## Architecture

```
User query
  → BertTokenizer.php   (WordPiece, in PHP, from vocab.txt)
  → EmbeddingService.php (ONNX inference via ankane/onnxruntime-php)
  → SimilarityService.php (dot product over pre-computed embeddings.json)
  → JSON response
```

No network hop. No sidecar. The model (~22 MB INT8) is a fixed, in-repo file, but
under stock `mod_php` (share-nothing per request) it is re-read from disk and the
ONNX session rebuilt on every request that hits a fresh worker; `lazy: true` only
defers that cost to the first search request, it does not keep the model resident
across requests. No PHP-path latency numbers exist yet — that is the next thing to
measure before calling this production-ready.

### GovCMS / managed hosting note

`ankane/onnxruntime-php` requires `libonnxruntime.so` on the server. On self-hosted
Drupal or GovCMS PaaS (agency-owned Docker image) it installs in one line. GovCMS
SaaS doesn't permit custom code outside its shared, security-reviewed module
distribution at all, so neither this module nor a FastAPI sidecar workaround has a
realistic path there, that's a SaaS constraint on any bespoke code, not specific to
ONNX.

---

## Files

```
drupal/
├── Dockerfile.php          — PHP 8.3 + ONNX Runtime + intl
├── docker-compose.yml      — Drupal 10 + MariaDB
├── setup-model.sh          — copy artefacts from repo/output/, or fetch from GitHub Release if absent
├── modules/autosearch/
│   ├── autosearch.info.yml
│   ├── autosearch.routing.yml
│   ├── autosearch.services.yml
│   ├── autosearch.module
│   ├── composer.json
│   ├── model/              — artefacts (gitignored); populate via setup-model.sh
│   └── src/
│       ├── BertTokenizer.php
│       ├── EmbeddingService.php
│       ├── SimilarityService.php
│       └── Controller/
│           ├── SearchController.php
│           └── CorpusController.php
└── tests/parity/
    ├── generate_reference.py
    ├── compare_tokens.php
    └── reference.json      — generated; not committed
```

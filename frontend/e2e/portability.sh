#!/usr/bin/env bash
# E2E: prove a single frontend build serves IT and health-workforce by restarting
# the backend with different artefact paths.
#
# Preconditions:
#   - Both pipelines already run; artefacts at ../../repo/output/{it-service-catalogue,health-workforce}/
#   - playwright-cli on PATH
#   - mvn, node, npm on PATH
#
# Usage: npm run test:e2e   (from frontend/)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REPO="$(cd "$ROOT/../repo" && pwd)"
FRONTEND="$ROOT/frontend"
CLEANUP="$FRONTEND/e2e/cleanup.sh"

trap "bash $CLEANUP" EXIT

start_backend() {
  local config="$1"
  local artefacts="$2"
  local corpus="$3"
  local ui_config="$4"

  lsof -ti:8080 2>/dev/null | xargs kill 2>/dev/null || true
  sleep 2

  (cd "$ROOT" && mvn -q -f backend/autosearch-spring/pom.xml spring-boot:run \
    -Dspring-boot.run.arguments="\
      --autosearch.config-path=$config \
      --autosearch.model-path=$artefacts/artefacts/autosearch-embed.onnx \
      --autosearch.tokenizer-path=$artefacts/artefacts/ \
      --autosearch.embeddings-path=$artefacts/data-items.json \
      --autosearch.corpus-path=$corpus \
      --autosearch.ui-config-path=$ui_config" >/dev/null 2>&1 &)

  echo "  waiting for backend..."
  for _ in $(seq 1 90); do
    curl -sf http://localhost:8080/api/v1/search/health >/dev/null && return 0
    sleep 1
  done
  echo "  backend failed to start"
  return 1
}

start_frontend() {
  if lsof -ti:5173 >/dev/null 2>&1; then
    echo "  vite already running"
    return 0
  fi
  (cd "$FRONTEND" && npm run dev >/dev/null 2>&1 &)
  echo "  waiting for vite..."
  for _ in $(seq 1 60); do
    curl -sf http://localhost:5173 >/dev/null && return 0
    sleep 1
  done
  echo "  vite failed to start"
  return 1
}

assert_snapshot_contains() {
  local needle="$1"
  local snap
  snap=$(playwright-cli -s=tier2-e2e --raw snapshot)
  if ! grep -qF "$needle" <<<"$snap"; then
    echo "  ASSERTION FAILED: snapshot missing '$needle'"
    echo "  --- snapshot tail ---"
    echo "$snap" | tail -40
    echo "  ---------------------"
    return 1
  fi
  echo "  OK: '$needle'"
}

echo "[1/5] Booting backend with IT corpus..."
start_backend \
  "$ROOT/examples/it-service-catalogue/config.yaml" \
  "$REPO/output/it-service-catalogue" \
  "$ROOT/examples/it-service-catalogue/corpus.json" \
  "$ROOT/examples/it-service-catalogue/corpus-ui.json"

echo "[2/5] Booting frontend..."
start_frontend

echo "[3/5] Asserting IT UI..."
playwright-cli -s=tier2-e2e open http://localhost:5173 >/dev/null
sleep 3
playwright-cli -s=tier2-e2e goto http://localhost:5173 >/dev/null
sleep 2
assert_snapshot_contains "IT Helpdesk Request Catalogue"
assert_snapshot_contains "password reset"
assert_snapshot_contains "Account & Authentication"

echo "[4/5] Restarting backend with health-workforce..."
start_backend \
  "$REPO/config.yaml" \
  "$REPO/output/health-workforce" \
  "$REPO/test-harness/data/corpus.json" \
  "$ROOT/examples/health-workforce/corpus-ui.json"

echo "[5/5] Reloading + asserting health UI..."
playwright-cli -s=tier2-e2e goto http://localhost:5173 >/dev/null
sleep 3
assert_snapshot_contains "Auto Search"
assert_snapshot_contains "Primary care doctor staffing levels"
assert_snapshot_contains "GP Workforce"

echo ""
echo "PORTABILITY E2E: PASS"

#!/usr/bin/env bash
# Auto Search Drupal module — functional verification via playwright-cli.
#
# Tests two layers:
#   1. REST API contract  (health, search, corpus, ui-config)
#   2. Browser E2E        (Vue SPA search flow)
#
# Requires:
#   - Drupal running on port 8080  (docker compose up)
#   - playwright-cli installed     (tests/node_modules/.bin/playwright-cli)
#
# Usage (from drupal/):
#   bash tests/e2e.sh

set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
PW="$DIR/node_modules/.bin/playwright-cli"
BACKEND="${BACKEND:-http://localhost:8080}"
FRONTEND="${FRONTEND:-http://localhost:8080/autosearch}"

pass=0
fail=0

# Check that $expected appears in $result (JSON-normalised).
check() {
  local label="$1"
  local result="$2"
  local expected="$3"
  if python3 - "$result" "$expected" <<'PY'
import sys, json
result, expected = sys.argv[1], sys.argv[2]
try:
    result = json.dumps(json.loads(result), separators=(',', ':'))
except Exception:
    pass
sys.exit(0 if expected in result else 1)
PY
  then
    echo "  PASS  $label"
    pass=$((pass+1))
  else
    echo "  FAIL  $label"
    echo "        expected: $expected"
    echo "        got:      $(echo "$result" | head -c 120)"
    fail=$((fail+1))
  fi
}

echo ""
echo "── API contract tests  ($BACKEND) ──────────────────────────"

# Health
r=$(curl -sf "$BACKEND/api/v1/search/health")
check "GET /health returns UP" "$r" '"status":"UP"'

# Corpus
r=$(curl -sf "$BACKEND/api/v1/corpus")
check "GET /corpus returns array" "$r" "["
count=$(echo "$r" | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d))")
check "GET /corpus has items (got $count)" "$count" ""
echo "    corpus item count: $count"

# UI config
r=$(curl -sf "$BACKEND/api/v1/corpus/ui-config")
check "GET /corpus/ui-config has appTitle"    "$r" "appTitle"
check "GET /corpus/ui-config has idField"     "$r" "idField"
check "GET /corpus/ui-config has groupNames"  "$r" "groupNames"

# Search — valid query (GP term)
r=$(curl -sf -X POST "$BACKEND/api/v1/search" \
     -H 'Content-Type: application/json' \
     -d '{"query":"GP staffing","topK":3}')
check "POST /search returns array" "$r" "["
check "POST /search result has score" "$r" "score"

# Search — exact field names
fields=$(echo "$r" | python3 -c "import json,sys; d=json.load(sys.stdin); print(list(d[0].keys()) if d else [])" 2>/dev/null || echo "[]")
check "POST /search result has group_id"  "$fields" "group_id"
check "POST /search result has item_id"   "$fields" "item_id"
check "POST /search result has name"      "$fields" "name"

# Search — demo chip queries (regression: all must return at least one result)
for query in \
  "primary care doctor staffing levels" \
  "How many aged care staff are we employing" \
  "public hospital medical officer staffing levels" \
  "regional breakdown of unnecessary hospital admissions"; do
  r=$(curl -sf -X POST "$BACKEND/api/v1/search" \
       -H 'Content-Type: application/json' \
       -d "{\"query\":\"$query\",\"topK\":3}")
  check "POST /search returns result for: $query" "$r" '"name"'
done

# Search — empty query → 400
status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BACKEND/api/v1/search" \
          -H 'Content-Type: application/json' -d '{"query":""}')
check "POST /search empty query → 400" "$status" "400"

echo ""
echo "── Browser E2E tests  ($FRONTEND) ──────────────────────────"

"$PW" open "$FRONTEND" 2>/dev/null

# ── 1. Page load ─────────────────────────────────────────────
snap=$("$PW" --raw snapshot 2>/dev/null)
check "Page title visible on load"        "$snap" 'Find the data item'
check "Search box visible on load"        "$snap" 'combobox'
check "Suggestion chips visible on load"  "$snap" 'Primary care doctor'
check "Corpus list renders on load"       "$snap" 'GP Workforce'

# ── 2. Semantic search — results show real content (not field mapping errors) ─
"$PW" fill "input[role=combobox]" "GP staffing" 2>/dev/null
sleep 2
snap=$("$PW" --raw snapshot 2>/dev/null)
check "Results dropdown visible"               "$snap" '"Search results"'
check "Results show item name"                 "$snap" "GP FTE"
check "Results show real group name"           "$snap" "GP Workforce"
check "Results do NOT show GROUP UNDEFINED"    "$(echo "$snap" | grep -c 'UNDEFINED' || true)" "0"

# ── 3. Demo chip queries — all must return results (regression) ───────────────
"$PW" press "Escape" 2>/dev/null; sleep 1

for chip in \
  "Primary care doctor staffing levels" \
  "How many aged care staff are we employing?" \
  "public hospital medical officer staffing levels" \
  "regional breakdown of unnecessary hospital admissions"; do
  "$PW" fill "input[role=combobox]" "$chip" 2>/dev/null
  sleep 2
  snap=$("$PW" --raw snapshot 2>/dev/null)
  check "Chip query returns results: ${chip:0:40}…" "$snap" '"Search results"'
  check "Chip results not GROUP UNDEFINED: ${chip:0:30}…" "$(echo "$snap" | grep -c 'UNDEFINED' || true)" "0"
  "$PW" press "Escape" 2>/dev/null; sleep 1
done

# ── 4. Escape clears results and restores chips ───────────────────────────────
snap=$("$PW" --raw snapshot 2>/dev/null)
check "Chips restored after Escape" "$snap" 'Primary care doctor'

# ── 5. Keyword mode — badge switches, results appear ─────────────────────────
"$PW" open "${FRONTEND}?mode=keyword" 2>/dev/null; sleep 1
snap=$("$PW" --raw snapshot 2>/dev/null)
check "Keyword mode badge visible"  "$snap" 'Keyword search'

"$PW" fill "input[role=combobox]" "GP FTE" 2>/dev/null
sleep 1
snap=$("$PW" --raw snapshot 2>/dev/null)
check "Keyword search returns results"          "$snap" '"Search results"'
check "Keyword results show real group names"   "$snap" "GP Workforce"
check "Keyword results not GROUP UNDEFINED"     "$(echo "$snap" | grep -c 'UNDEFINED' || true)" "0"

# ── 6. Result selection — item highlighted in corpus list ────────────────────
"$PW" open "$FRONTEND" 2>/dev/null; sleep 1
"$PW" fill "input[role=combobox]" "GP staffing" 2>/dev/null
sleep 2
"$PW" click "[role=option]:first-child" 2>/dev/null
sleep 1
snap=$("$PW" --raw snapshot 2>/dev/null)
check "Corpus list still visible after selection"  "$snap" 'GP Workforce'
check "Selected item present in page"              "$snap" 'GP FTE'

"$PW" close 2>/dev/null

echo ""
echo "── Summary ─────────────────────────────────────────────────"
echo "  $pass passed  |  $fail failed"
echo ""

exit $((fail > 0 ? 1 : 0))

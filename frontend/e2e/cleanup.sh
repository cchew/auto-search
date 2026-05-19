#!/usr/bin/env bash
# Stop any backend/frontend started by portability.sh and close playwright sessions.
set -u
playwright-cli -s=tier2-e2e close >/dev/null 2>&1 || true
lsof -ti:8080 2>/dev/null | xargs kill 2>/dev/null || true
lsof -ti:5173 2>/dev/null | xargs kill 2>/dev/null || true
sleep 1
exit 0

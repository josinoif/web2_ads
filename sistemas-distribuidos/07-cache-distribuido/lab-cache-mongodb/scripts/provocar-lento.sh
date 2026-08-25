#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://127.0.0.1:8095}"
MS="${1:-0}"

curl -s -X POST "${API}/admin/store_hold_ms" \
  -H "Content-Type: application/json" \
  -d "{\"ms\": ${MS}}" | python3 -m json.tool

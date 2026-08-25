#!/usr/bin/env bash
set -euo pipefail
MS="${1:-5000}"
curl -sS -X POST http://127.0.0.1:8093/admin/store_hold_ms \
  -H 'Content-Type: application/json' \
  -d "{\"ms\": ${MS}}" | python3 -m json.tool

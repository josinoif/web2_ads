#!/usr/bin/env bash
# Injeta atraso no store (ms). Ex.: ./scripts/provocar-lento.sh 5000
set -euo pipefail
MS="${1:-5000}"
curl -sS -X POST http://127.0.0.1:8092/admin/store_hold_ms \
  -H 'Content-Type: application/json' \
  -d "{\"ms\": ${MS}}" | python3 -m json.tool

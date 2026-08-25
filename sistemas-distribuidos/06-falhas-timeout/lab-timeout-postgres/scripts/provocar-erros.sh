#!/usr/bin/env bash
# FAIL_RATE 0–100. Ex.: ./scripts/provocar-erros.sh 80
set -euo pipefail
RATE="${1:-50}"
curl -sS -X POST http://127.0.0.1:8092/admin/fail_rate \
  -H 'Content-Type: application/json' \
  -d "{\"rate\": ${RATE}}" | python3 -m json.tool

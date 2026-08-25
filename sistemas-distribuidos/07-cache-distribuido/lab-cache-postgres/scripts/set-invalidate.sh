#!/usr/bin/env bash
# Liga/desliga invalidação: ./scripts/set-invalidate.sh 0|1
set -euo pipefail
API="${API:-http://127.0.0.1:8094}"
ON="${1:?uso: ./scripts/set-invalidate.sh 0|1}"

ENABLED=true
[[ "${ON}" == "0" || "${ON}" == "false" ]] && ENABLED=false

curl -s -X POST "${API}/admin/invalidate_on_write" \
  -H "Content-Type: application/json" \
  -d "{\"enabled\": ${ENABLED}}" | python3 -m json.tool

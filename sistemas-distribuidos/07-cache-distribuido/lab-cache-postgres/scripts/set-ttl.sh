#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://127.0.0.1:8094}"
SEC="${1:?uso: ./scripts/set-ttl.sh 5}"

curl -s -X POST "${API}/admin/cache_ttl_sec" \
  -H "Content-Type: application/json" \
  -d "{\"sec\": ${SEC}}" | python3 -m json.tool

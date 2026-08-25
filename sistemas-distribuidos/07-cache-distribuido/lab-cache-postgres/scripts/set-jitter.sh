#!/usr/bin/env bash
# uso: ./scripts/set-jitter.sh 2   # TTL ± 2s
set -euo pipefail
API="${API:-http://127.0.0.1:8094}"
SEC="${1:?uso: ./scripts/set-jitter.sh <sec>}"

curl -s -X POST "${API}/admin/ttl_jitter_sec" \
  -H "Content-Type: application/json" \
  -d "{\"sec\": ${SEC}}" | python3 -m json.tool

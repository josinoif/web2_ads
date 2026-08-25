#!/usr/bin/env bash
set -euo pipefail
SEC="${1:?uso: ./scripts/set-ttl.sh 10}"
APIS="${APIS:-http://127.0.0.1:8095 http://127.0.0.1:8096}"

for API in ${APIS}; do
  curl -s -X POST "${API}/admin/cache_ttl_sec" \
    -H "Content-Type: application/json" \
    -d "{\"sec\": ${SEC}}" >/dev/null
  echo "${API}: ttl=${SEC}"
done

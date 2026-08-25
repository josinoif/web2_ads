#!/usr/bin/env bash
set -euo pipefail
ON="${1:?uso: ./scripts/set-invalidate.sh 0|1}"
APIS="${APIS:-http://127.0.0.1:8095 http://127.0.0.1:8096}"
ENABLED=true
[[ "${ON}" == "0" || "${ON}" == "false" ]] && ENABLED=false

for API in ${APIS}; do
  curl -s -X POST "${API}/admin/invalidate_on_write" \
    -H "Content-Type: application/json" \
    -d "{\"enabled\": ${ENABLED}}" >/dev/null
  echo "${API}: invalidate=${ENABLED}"
done

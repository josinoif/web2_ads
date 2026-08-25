#!/usr/bin/env bash
set -euo pipefail
APIS="${APIS:-http://127.0.0.1:8095 http://127.0.0.1:8096}"

for API in ${APIS}; do
  curl -s -X POST "${API}/admin/flush_cache" \
    -H "Content-Type: application/json" -d '{}' >/dev/null
  curl -s -X POST "${API}/admin/stats_reset" \
    -H "Content-Type: application/json" -d '{}' >/dev/null
  echo "${API}: flushed"
done

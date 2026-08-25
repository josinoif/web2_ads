#!/usr/bin/env bash
# Aplica backend nas duas APIs (ou só API= se definido)
set -euo pipefail
BACKEND="${1:?uso: ./scripts/set-backend.sh redis|local|off}"
APIS="${APIS:-http://127.0.0.1:8095 http://127.0.0.1:8096}"

for API in ${APIS}; do
  echo "=== ${API} ==="
  curl -s -X POST "${API}/admin/cache_backend" \
    -H "Content-Type: application/json" \
    -d "{\"backend\": \"${BACKEND}\"}" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['instance_id'], d['cache_backend'])"
done

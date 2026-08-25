#!/usr/bin/env bash
# Backend: redis | local | off
set -euo pipefail
API="${API:-http://127.0.0.1:8094}"
BACKEND="${1:?uso: ./scripts/set-backend.sh redis|local|off}"

curl -s -X POST "${API}/admin/cache_backend" \
  -H "Content-Type: application/json" \
  -d "{\"backend\": \"${BACKEND}\"}" | python3 -m json.tool

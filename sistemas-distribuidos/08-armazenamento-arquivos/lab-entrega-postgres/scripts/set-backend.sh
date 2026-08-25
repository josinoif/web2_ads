#!/usr/bin/env bash
# Uso: ./scripts/set-backend.sh minio|local
set -euo pipefail
BACKEND="${1:?uso: set-backend.sh minio|local}"
for port in 8090 8091; do
  curl -s -X PUT "http://127.0.0.1:${port}/admin/config" \
    -H 'Content-Type: application/json' \
    -d "{\"storage_backend\": \"${BACKEND}\"}" | python3 -m json.tool
done

#!/usr/bin/env bash
# Uso: ./scripts/set-fail-after-blob.sh 0|1
set -euo pipefail
VAL="${1:?uso: set-fail-after-blob.sh 0|1}"
for port in 8090 8091; do
  curl -s -X PUT "http://127.0.0.1:${port}/admin/config" \
    -H 'Content-Type: application/json' \
    -d "{\"fail_after_blob\": ${VAL}}" | python3 -m json.tool
done

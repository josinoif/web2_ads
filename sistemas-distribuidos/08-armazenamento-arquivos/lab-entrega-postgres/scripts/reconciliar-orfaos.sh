#!/usr/bin/env bash
set -euo pipefail
echo "=== órfãos antes ==="
curl -s http://127.0.0.1:8090/admin/orfaos | python3 -m json.tool
echo "=== reconciliar (DELETE no MinIO) ==="
curl -s -X POST http://127.0.0.1:8090/admin/reconciliar-orfaos | python3 -m json.tool
echo "=== órfãos depois ==="
curl -s http://127.0.0.1:8090/admin/orfaos | python3 -m json.tool

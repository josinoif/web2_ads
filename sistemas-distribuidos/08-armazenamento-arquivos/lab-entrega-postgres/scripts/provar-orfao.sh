#!/usr/bin/env bash
# Simula blob órfão (PutObject ok, metadado não grava) e lista órfãos.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

./scripts/set-backend.sh minio
./scripts/set-fail-after-blob.sh 1

TMP="$(mktemp)"
echo "blob-orfao-$(date +%s)" >"${TMP}"
echo "=== upload com FAIL_AFTER_BLOB=1 (espera 503 + blob_orfao) ==="
curl -s -X POST "http://127.0.0.1:8090/entregas" \
  -H "X-Aluno-Id: aluno-orfao" \
  -H "X-Disciplina: SD" \
  -H "X-Nome-Arquivo: orfao.txt" \
  -H "Content-Type: text/plain" \
  --data-binary "@${TMP}" | python3 -m json.tool

./scripts/set-fail-after-blob.sh 0
rm -f "${TMP}"

echo "=== órfãos ==="
curl -s http://127.0.0.1:8090/admin/orfaos | python3 -m json.tool

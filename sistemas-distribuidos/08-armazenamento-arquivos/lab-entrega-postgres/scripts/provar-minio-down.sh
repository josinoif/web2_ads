#!/usr/bin/env bash
# Para o MinIO, tenta upload (espera 503), sobe de novo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

./scripts/set-backend.sh minio
./scripts/set-fail-after-blob.sh 0

echo "=== parando minio ==="
compose stop minio

TMP="$(mktemp)"
echo "sem-minio" >"${TMP}"
echo "=== upload (espera 503 storage_indisponivel) ==="
curl -s -X POST "http://127.0.0.1:8090/entregas" \
  -H "X-Aluno-Id: aluno-minio-down" \
  -H "X-Disciplina: SD" \
  -H "X-Nome-Arquivo: fail.txt" \
  -H "Content-Type: text/plain" \
  --data-binary "@${TMP}" | python3 -m json.tool
rm -f "${TMP}"

echo "=== subindo minio ==="
compose start minio
sleep 3
# recria bucket se necessário
compose run --rm minio-init >/dev/null 2>&1 || true
echo "=== health ==="
curl -s http://127.0.0.1:8090/health | python3 -m json.tool

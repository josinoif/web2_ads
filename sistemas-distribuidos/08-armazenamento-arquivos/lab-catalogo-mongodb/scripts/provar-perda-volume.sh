#!/usr/bin/env bash
# Apaga volume MinIO — metadados ficam; download falha (perda / RPO).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

TMP="$(mktemp)"
printf 'perda-volume\n' >"${TMP}"
RESP=$(curl -s -X POST http://127.0.0.1:8092/entregas \
  -H "X-Aluno-Id: aluno-perda" -H "X-Disciplina: SD" -H "X-Nome-Arquivo: x.txt" \
  -H "Content-Type: text/plain" --data-binary "@${TMP}")
rm -f "${TMP}"
echo "${RESP}" | python3 -m json.tool
ID=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['id'])")

echo "=== remove container+volume do MinIO (Mongo permanece) ==="
compose stop minio
compose rm -f minio
docker volume rm -f sd08-catalogo-mongodb_minio_data 2>/dev/null || true

compose up -d minio
sleep 4
compose run --rm minio-init

echo "=== metadado ainda existe ==="
curl -s http://127.0.0.1:8092/entregas | python3 -m json.tool | head -n 50

echo "=== download (espera 404 blob ausente) ==="
curl -s "http://127.0.0.1:8092/entregas/${ID}/arquivo" | python3 -m json.tool
echo
echo "Discuta RPO: metadado sem backup do storage não recupera o PDF."

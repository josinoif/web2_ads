#!/usr/bin/env bash
# Contrasta local vs MinIO: upload na api1, download na api2.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

echo "=== 1) STORAGE=local: upload api1, download api2 (espera 404) ==="
./scripts/set-backend.sh local
RESP=$(./scripts/enviar.sh aluno-local /dev/null 8090 2>/dev/null || true)
# enviar com arquivo real
TMP="$(mktemp)"
echo "conteudo-local-only" >"${TMP}"
RESP=$(curl -s -X POST "http://127.0.0.1:8090/entregas" \
  -H "X-Aluno-Id: aluno-local" \
  -H "X-Disciplina: SD" \
  -H "X-Nome-Arquivo: local.txt" \
  -H "Content-Type: text/plain" \
  --data-binary "@${TMP}")
echo "${RESP}" | python3 -m json.tool
ID=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['id'])")
echo "--- download api2 (deve falhar) ---"
curl -s "http://127.0.0.1:8091/entregas/${ID}/arquivo" | python3 -m json.tool || true

echo
echo "=== 2) STORAGE=minio: upload api1, download api2 (espera 200) ==="
./scripts/set-backend.sh minio
echo "conteudo-minio-shared" >"${TMP}"
RESP=$(curl -s -X POST "http://127.0.0.1:8090/entregas" \
  -H "X-Aluno-Id: aluno-minio" \
  -H "X-Disciplina: SD" \
  -H "X-Nome-Arquivo: minio.txt" \
  -H "Content-Type: text/plain" \
  --data-binary "@${TMP}")
echo "${RESP}" | python3 -m json.tool
ID=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['id'])")
echo "--- download api2 ---"
curl -sS -D - "http://127.0.0.1:8091/entregas/${ID}/arquivo" -o /tmp/minio-ok.bin | head -n 15
echo
ls -la /tmp/minio-ok.bin
rm -f "${TMP}"
echo "=== fim ==="

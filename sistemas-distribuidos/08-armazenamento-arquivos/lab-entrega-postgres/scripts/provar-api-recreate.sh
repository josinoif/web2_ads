#!/usr/bin/env bash
# Recreate das APIs — objeto MinIO e metadado Postgres permanecem.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

./scripts/set-backend.sh minio
TMP="$(mktemp)"
echo "sobrevive-ao-recreate" >"${TMP}"
RESP=$(curl -s -X POST "http://127.0.0.1:8090/entregas" \
  -H "X-Aluno-Id: aluno-persist" \
  -H "X-Disciplina: SD" \
  -H "X-Nome-Arquivo: persist.txt" \
  -H "Content-Type: text/plain" \
  --data-binary "@${TMP}")
rm -f "${TMP}"
echo "${RESP}" | python3 -m json.tool
ID=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['id'])")

echo "=== recreate api1 api2 ==="
compose up -d --force-recreate --no-deps api1 api2
for i in $(seq 1 30); do
  if curl -sf http://127.0.0.1:8090/health >/dev/null && curl -sf http://127.0.0.1:8091/health >/dev/null; then
    break
  fi
  sleep 2
done

echo "=== download após recreate (api2) ==="
curl -sS -D - "http://127.0.0.1:8091/entregas/${ID}/arquivo" -o /tmp/persist-ok.bin | head -n 12
echo
cat /tmp/persist-ok.bin
echo

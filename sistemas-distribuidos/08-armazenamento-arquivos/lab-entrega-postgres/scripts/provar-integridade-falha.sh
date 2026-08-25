#!/usr/bin/env bash
# Sobrescreve o objeto no MinIO → soft verify (200 + falha) e depois rejeição 409.
# Ferramenta: cliente `mc` (serviço Compose minio-init), não precisa instalar no host.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

./scripts/set-backend.sh minio
./scripts/set-fail-after-blob.sh 0
./scripts/set-reject-integrity.sh 0

TMP="$(mktemp)"
printf 'conteudo-integro-original\n' >"${TMP}"
RESP=$(curl -s -X POST "http://127.0.0.1:8090/entregas" \
  -H "X-Aluno-Id: aluno-integ" \
  -H "X-Disciplina: SD" \
  -H "X-Nome-Arquivo: integ.txt" \
  -H "Content-Type: text/plain" \
  --data-binary "@${TMP}")
rm -f "${TMP}"
echo "${RESP}" | python3 -m json.tool
ID=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['id'])")
KEY=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['object_key'])")
SHA=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['sha256'])")

echo "=== download íntegro (espera X-Integridade: ok) ==="
./scripts/baixar.sh "${ID}" 8090

echo "=== corrompe objeto no MinIO (mc pipe, via serviço minio-init) ==="
printf 'BYTES-CORROMPIDOS-%s\n' "$$" | compose run --rm --no-deps -T \
  --entrypoint /bin/sh \
  minio-init \
  -c "mc alias set local http://minio:9000 minioadmin minioadmin >/dev/null && mc pipe 'local/trabalhos/${KEY}'"

echo "=== A) soft verify (REJECT=0): 200 + X-Integridade: falha + body ==="
./scripts/baixar.sh "${ID}" 8090

echo "=== B) modo produção (REJECT=1): espera HTTP 409 JSON ==="
./scripts/set-reject-integrity.sh 1
curl -sS -D - "http://127.0.0.1:8090/entregas/${ID}/arquivo" -o /tmp/entrega-${ID}-reject.bin | head -n 20
echo
python3 -m json.tool < /tmp/entrega-${ID}-reject.bin 2>/dev/null || \
  echo "(corpo não-JSON ou vazio — confira status 409 acima)"

./scripts/set-reject-integrity.sh 0
echo "sha256 no metadado (Postgres): ${SHA}"
echo "Padrão do lab volta a soft verify (REJECT=0)."

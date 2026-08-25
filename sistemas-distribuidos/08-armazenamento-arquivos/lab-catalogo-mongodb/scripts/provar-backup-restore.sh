#!/usr/bin/env bash
# Prova positiva leve de proteção: backup do bucket → wipe volume → restore → download ok.
# Contraste com provar-perda-volume.sh (sem backup = RPO ruim).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

BACKUP_DIR="${TMPDIR:-/tmp}/sd08-catalogo-minio-backup"
rm -rf "${BACKUP_DIR}"
mkdir -p "${BACKUP_DIR}"

TMP="$(mktemp)"
printf 'conteudo-para-backup-restore\n' >"${TMP}"
RESP=$(curl -s -X POST http://127.0.0.1:8092/entregas \
  -H "X-Aluno-Id: aluno-backup" -H "X-Disciplina: SD" -H "X-Nome-Arquivo: backup.txt" \
  -H "Content-Type: text/plain" --data-binary "@${TMP}")
rm -f "${TMP}"
echo "${RESP}" | python3 -m json.tool
ID=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['id'])")
KEY=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['object_key'])")

echo "=== 1) backup do bucket trabalhos → ${BACKUP_DIR} ==="
compose run --rm --no-deps \
  -v "${BACKUP_DIR}:/backup:Z" \
  --entrypoint /bin/sh \
  minio-init \
  -c "mc alias set local http://minio:9000 minioadmin minioadmin && mc mirror --overwrite local/trabalhos /backup/trabalhos && mc ls /backup/trabalhos"

echo "=== 2) wipe volume MinIO (simula perda de disco) ==="
compose stop minio
compose rm -f minio
docker volume rm -f sd08-catalogo-mongodb_minio_data 2>/dev/null || true
compose up -d minio
sleep 4
compose run --rm minio-init

echo "=== 3) download sem restore (espera 404) ==="
curl -s "http://127.0.0.1:8092/entregas/${ID}/arquivo" | python3 -m json.tool || true

echo "=== 4) restore do backup ==="
compose run --rm --no-deps \
  -v "${BACKUP_DIR}:/backup:Z" \
  --entrypoint /bin/sh \
  minio-init \
  -c "mc alias set local http://minio:9000 minioadmin minioadmin && mc mirror --overwrite /backup/trabalhos local/trabalhos && mc ls local/trabalhos"

echo "=== 5) download após restore (espera 200 + X-Integridade: ok) ==="
curl -sS -D - "http://127.0.0.1:8092/entregas/${ID}/arquivo" -o /tmp/sd08-restored.bin | \
  grep -iE '^(HTTP/|X-Sha256|X-Integridade)' || true
echo
cat /tmp/sd08-restored.bin
echo
echo "key=${KEY}"
echo "Discuta: backup do storage é a prova positiva leve de proteção (não é cluster/erasure)."

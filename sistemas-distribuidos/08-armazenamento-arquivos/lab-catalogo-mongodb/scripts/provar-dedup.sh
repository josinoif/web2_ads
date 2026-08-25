#!/usr/bin/env bash
# Dois alunos, mesmo conteúdo → 1 objeto MinIO, 2 entregas.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

TMP="$(mktemp)"
printf 'pdf-modelo-turma-identico\n' >"${TMP}"

echo "=== aluno-A ==="
./scripts/enviar.sh aluno-A "${TMP}"
echo "=== aluno-B (mesmo bytes) ==="
./scripts/enviar.sh aluno-B "${TMP}"
rm -f "${TMP}"

echo "=== objetos (espera n_objetos_minio=1 e n_referencias=2) ==="
./scripts/status-objetos.sh

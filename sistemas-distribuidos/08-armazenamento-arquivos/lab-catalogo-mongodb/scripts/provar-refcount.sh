#!/usr/bin/env bash
# Apaga uma entrega: refcount 2→1 (blob fica); depois a outra (remove objeto).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

TMP="$(mktemp)"
printf 'refcount-demo-%s\n' "$$" >"${TMP}"

R1=$(curl -s -X POST http://127.0.0.1:8092/entregas \
  -H "X-Aluno-Id: ref-1" -H "X-Disciplina: SD" -H "X-Nome-Arquivo: a.txt" \
  -H "Content-Type: text/plain" --data-binary "@${TMP}")
R2=$(curl -s -X POST http://127.0.0.1:8092/entregas \
  -H "X-Aluno-Id: ref-2" -H "X-Disciplina: SD" -H "X-Nome-Arquivo: b.txt" \
  -H "Content-Type: text/plain" --data-binary "@${TMP}")
rm -f "${TMP}"

ID1=$(echo "${R1}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['id'])")
ID2=$(echo "${R2}" | python3 -c "import sys,json; print(json.load(sys.stdin)['entrega']['id'])")
echo "ids: ${ID1} ${ID2}"

echo "=== apaga 1 (espera removeu_objeto_minio=false) ==="
./scripts/apagar.sh "${ID1}"
./scripts/status-objetos.sh

echo "=== apaga 2 (espera removeu_objeto_minio=true) ==="
./scripts/apagar.sh "${ID2}"
./scripts/status-objetos.sh

#!/usr/bin/env bash
# PUT nota — uso: ./scripts/atualizar.sh aluno-01 9.5
set -euo pipefail
API="${API:-http://127.0.0.1:8094}"
ALUNO="${1:-aluno-01}"
NOTA="${2:?informe a nota: ./scripts/atualizar.sh aluno-01 9.5}"

curl -s -X PUT "${API}/boletim/${ALUNO}" \
  -H "Content-Type: application/json" \
  -d "{\"nota\": ${NOTA}}" | python3 -m json.tool

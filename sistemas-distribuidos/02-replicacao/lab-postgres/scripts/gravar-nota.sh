#!/usr/bin/env bash
# Grava ou atualiza uma nota (sempre no primary).
# Uso: ./scripts/gravar-nota.sh aluno-01 "SD" 8.5
set -euo pipefail
ALUNO="${1:?aluno_id}"
DISC="${2:?disciplina}"
VALOR="${3:?valor}"
BASE="${BASE_URL:-http://localhost:8082}"
curl -s -X POST "${BASE}/notas" \
  -H "Content-Type: application/json" \
  -d "{\"aluno_id\":\"${ALUNO}\",\"disciplina\":\"${DISC}\",\"valor\":${VALOR}}" \
  | python3 -m json.tool

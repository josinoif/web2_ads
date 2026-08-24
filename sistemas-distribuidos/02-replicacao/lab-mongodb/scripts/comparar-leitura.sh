#!/usr/bin/env bash
# Grava no primary e compara leitura primary vs secondary + status do replica set.
# Uso: ./scripts/comparar-leitura.sh [aluno_id] [disciplina] [valor]
set -euo pipefail

ALUNO="${1:-aluno-cmp}"
DISC="${2:-SD}"
VALOR="${3:-9.5}"
BASE="${BASE_URL:-http://localhost:8083}"

echo "== gravando no primary =="
curl -s -X POST "${BASE}/notas" \
  -H "Content-Type: application/json" \
  -d "{\"aluno_id\":\"${ALUNO}\",\"disciplina\":\"${DISC}\",\"valor\":${VALOR}}" \
  | python3 -m json.tool

echo ""
echo "== leitura imediata primary =="
curl -s "${BASE}/notas/${ALUNO}?dest=primary" | python3 -m json.tool

echo ""
echo "== leitura imediata secondary =="
curl -s "${BASE}/notas/${ALUNO}?dest=secondary" | python3 -m json.tool

echo ""
echo "== status do replica set =="
curl -s "${BASE}/replicacao/status" | python3 -m json.tool

#!/usr/bin/env bash
# Mede latência de POST /notas e mostra sync_state.
set -euo pipefail
ALUNO="${1:-aluno-sync}"
DISC="${2:-SD}"
VALOR="${3:-8.0}"
BASE="${BASE_URL:-http://localhost:8084}"

echo "== POST /notas =="
curl -s -X POST "${BASE}/notas" \
  -H "Content-Type: application/json" \
  -d "{\"aluno_id\":\"${ALUNO}\",\"disciplina\":\"${DISC}\",\"valor\":${VALOR}}" \
  | python3 -m json.tool

echo ""
echo "== GET /replicacao/status =="
curl -s "${BASE}/replicacao/status" | python3 -m json.tool

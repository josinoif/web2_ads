#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8085}"
DISC="${1:-SD-101}"
ALUNO="${2:-aluno-$(date +%s)}"
# max-time folgado — sob partição a API responde 503 rápido; sob carga sync pode demorar
MAX_TIME="${MAX_TIME:-70}"
curl -sS --max-time "${MAX_TIME}" -X POST "${API}/matricular" \
  -H 'Content-Type: application/json' \
  -d "{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"${ALUNO}\"}" \
  | python3 -m json.tool

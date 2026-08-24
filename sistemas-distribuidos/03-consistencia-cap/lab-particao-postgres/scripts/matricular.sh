#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8085}"
DISC="${1:-SD-101}"
ALUNO="${2:-aluno-$(date +%s)}"
curl -sS -X POST "${API}/matricular" \
  -H 'Content-Type: application/json' \
  -d "{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"${ALUNO}\"}" \
  | python3 -m json.tool

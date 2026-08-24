#!/usr/bin/env bash
# Lê notas de um aluno no primary ou na réplica.
# Uso: ./scripts/ler-notas.sh aluno-01 replica
set -euo pipefail
ALUNO="${1:?aluno_id}"
DEST="${2:-primary}"
BASE="${BASE_URL:-http://localhost:8082}"
curl -s "${BASE}/notas/${ALUNO}?dest=${DEST}" | python3 -m json.tool

#!/usr/bin/env bash
set -euo pipefail
ALUNO="${1:?aluno_id}"
DEST="${2:-primary}"
BASE="${BASE_URL:-http://localhost:8083}"
curl -s "${BASE}/notas/${ALUNO}?dest=${DEST}" | python3 -m json.tool

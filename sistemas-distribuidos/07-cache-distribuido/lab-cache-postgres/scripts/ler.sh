#!/usr/bin/env bash
# GET /boletim/{aluno}
set -euo pipefail
API="${API:-http://127.0.0.1:8094}"
ALUNO="${1:-aluno-01}"

curl -s "${API}/boletim/${ALUNO}" | python3 -m json.tool

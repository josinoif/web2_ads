#!/usr/bin/env bash
set -euo pipefail
ALUNO="${1:-aluno-01}"
ARQ="${2:-prova.pdf}"
curl -sS -X POST http://127.0.0.1:8100/provas \
  -H 'Content-Type: application/json' \
  -d "{\"aluno\":\"${ALUNO}\",\"arquivo\":\"${ARQ}\"}" | python3 -m json.tool

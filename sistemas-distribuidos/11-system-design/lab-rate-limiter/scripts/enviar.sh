#!/usr/bin/env bash
# Uso: ./scripts/enviar.sh [closed|open] [key]
set -euo pipefail
MODO="${1:-closed}"
KEY="${2:-aluno-1}"
if [[ "$MODO" == "open" ]]; then
  BASE="http://127.0.0.1:8161"
else
  BASE="http://127.0.0.1:8160"
fi
curl -s -X POST "$BASE/api" \
  -H "Content-Type: application/json" \
  -d "{\"key\":\"${KEY}\",\"echo\":\"ok\"}" | python3 -m json.tool

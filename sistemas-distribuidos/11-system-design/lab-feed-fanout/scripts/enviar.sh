#!/usr/bin/env bash
# Uso: ./scripts/enviar.sh [write|read] [author] [texto]
set -euo pipefail
MODO="${1:-write}"
AUTHOR="${2:-u1}"
TEXT="${3:-olá do ${AUTHOR} $(date +%H:%M:%S)}"
if [[ "$MODO" == "read" ]]; then
  BASE="http://127.0.0.1:8151"
else
  BASE="http://127.0.0.1:8150"
fi
echo "POST $BASE/posts author=${AUTHOR}"
curl -s -X POST "$BASE/posts" \
  -H "Content-Type: application/json" \
  -d "{\"author\":\"${AUTHOR}\",\"text\":\"${TEXT}\"}" | python3 -m json.tool

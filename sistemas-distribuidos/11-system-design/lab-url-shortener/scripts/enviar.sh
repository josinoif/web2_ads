#!/usr/bin/env bash
# Uso: ./scripts/enviar.sh [contador|hash] [url]
set -euo pipefail
MODO="${1:-contador}"
URL="${2:-https://ifpe.edu.br/portal/prova-$(date +%s)}"
if [[ "$MODO" == "hash" ]]; then
  BASE="http://127.0.0.1:8141"
else
  BASE="http://127.0.0.1:8140"
fi
echo "POST $BASE/encurtar"
curl -s -X POST "$BASE/encurtar" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"${URL}\"}" | python3 -m json.tool

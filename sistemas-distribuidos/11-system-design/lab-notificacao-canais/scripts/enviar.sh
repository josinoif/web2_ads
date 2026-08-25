#!/usr/bin/env bash
# Uso: ./scripts/enviar.sh [unico|canais] [id]
set -euo pipefail
MODO="${1:-canais}"
ID="${2:-evt-$(date +%s)}"
if [[ "$MODO" == "unico" ]]; then
  BASE="http://127.0.0.1:8170"
else
  BASE="http://127.0.0.1:8171"
fi
echo "POST $BASE/eventos id=${ID}"
curl -s -X POST "$BASE/eventos" \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"${ID}\",\"user\":\"aluno-1\",\"canais\":[\"push\",\"email\",\"sms\"]}" \
  | python3 -m json.tool

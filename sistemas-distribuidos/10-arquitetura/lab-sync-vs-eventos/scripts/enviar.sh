#!/usr/bin/env bash
# Uso: ./scripts/enviar.sh [sync|eventos] [aluno]
set -euo pipefail
MODO="${1:-sync}"
ALUNO="${2:-aluno-demo}"
if [[ "$MODO" == "eventos" || "$MODO" == "evt" ]]; then
  URL="http://127.0.0.1:8131/provas"
else
  URL="http://127.0.0.1:8130/provas"
fi
echo "POST $URL"
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"aluno\":\"${ALUNO}\",\"arquivo\":\"${ALUNO}.pdf\"}" | python3 -m json.tool
curl -s -o /dev/null -w "time_total=%{time_total} http=%{http_code}\n" \
  -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"aluno\":\"${ALUNO}-t\",\"arquivo\":\"${ALUNO}-t.pdf\"}"

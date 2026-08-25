#!/usr/bin/env bash
# Uso: ./scripts/enviar.sh [mono|servicos] [aluno]
set -euo pipefail
MODO="${1:-mono}"
ALUNO="${2:-aluno-demo}"
if [[ "$MODO" == "servicos" || "$MODO" == "srv" ]]; then
  URL="http://127.0.0.1:8121/provas"
else
  URL="http://127.0.0.1:8120/provas"
fi
echo "POST $URL"
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"aluno\":\"${ALUNO}\",\"arquivo\":\"${ALUNO}.pdf\"}" | python3 -m json.tool
echo "(time_total via curl -w)"
curl -s -o /dev/null -w "time_total=%{time_total} http=%{http_code}\n" \
  -X POST "$URL" \
  -H "Content-Type: application/json" \
  -d "{\"aluno\":\"${ALUNO}-t\",\"arquivo\":\"${ALUNO}-t.pdf\"}"

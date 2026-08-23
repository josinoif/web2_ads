#!/usr/bin/env bash
# Consulta o status de uma prova até ficar concluido/erro ou estourar o tempo.
# Uso: ./scripts/acompanhar.sh prova-abc12345

set -euo pipefail
ID="${1:?informe o submission_id}"
BASE="${BASE_URL:-http://localhost:8080}"

for i in $(seq 1 40); do
  RESP=$(curl -s "${BASE}/provas/${ID}")
  STATUS=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))")
  echo "[$i] status=${STATUS}"
  if [[ "$STATUS" == "concluido" || "$STATUS" == "erro" ]]; then
    echo "$RESP" | python3 -m json.tool
    exit 0
  fi
  sleep 1
done

echo "timeout esperando ${ID}"
echo "$RESP" | python3 -m json.tool
exit 1

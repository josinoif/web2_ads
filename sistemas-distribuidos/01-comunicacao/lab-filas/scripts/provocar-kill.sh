#!/usr/bin/env bash
# Experimento 4 (alternativa): envia uma prova, espera "processando" e mata o worker.
# Uso: ./scripts/provocar-kill.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BASE="${BASE_URL:-http://localhost:8080}"

docker compose exec redis redis-cli DEL prova:fila >/dev/null 2>&1 || true
docker compose up -d worker >/dev/null

ID=$(curl -s -X POST "${BASE}/provas" \
  -H "Content-Type: application/json" \
  -d '{"aluno":"teste-kill","arquivo":"kill.pdf"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['submission_id'])")
echo "submission_id=${ID}"

for _ in $(seq 1 30); do
  STATUS=$(curl -s "${BASE}/provas/${ID}" \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))")
  echo "aguardando processando… status=${STATUS}"
  if [[ "$STATUS" == "processando" ]]; then
    break
  fi
  sleep 0.5
done

echo "matando worker…"
docker kill "$(docker compose ps -q worker)" >/dev/null
sleep 1

echo "--- status após kill ---"
curl -s "${BASE}/provas/${ID}" | python3 -m json.tool
echo "--- fila ---"
curl -s "${BASE}/fila" | python3 -m json.tool

echo ""
echo "Suba o worker de novo: docker compose up -d worker"

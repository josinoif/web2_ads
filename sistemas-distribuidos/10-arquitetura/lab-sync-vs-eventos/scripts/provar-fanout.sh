#!/usr/bin/env bash
# Fan-out: notificador recebe eventos sem mudar o gateway.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

compose start notificador worker >/dev/null 2>&1 || true
sleep 1

# limpa lista de notificações
compose exec -T redis redis-cli DEL prova:notificacoes >/dev/null

ALUNO="fanout-$(date +%s)"
RESP=$(curl -s -X POST http://127.0.0.1:8131/provas \
  -H "Content-Type: application/json" \
  -d "{\"aluno\":\"${ALUNO}\",\"arquivo\":\"${ALUNO}.pdf\"}")
echo "$RESP" | python3 -m json.tool
SID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin)['submission_id'])")

echo "aguardando worker + notificador…"
for i in $(seq 1 20); do
  ST=$(curl -s "http://127.0.0.1:8131/provas/${SID}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || true)
  if [[ "$ST" == "concluido" ]]; then break; fi
  sleep 1
done

echo "=== status prova ==="
curl -s "http://127.0.0.1:8131/provas/${SID}" | python3 -m json.tool
echo "=== notificações (fan-out) ==="
curl -s http://127.0.0.1:8131/notificacoes | python3 -m json.tool
echo
echo "Interprete: gateway não conhece o notificador; o fato foi publicado e consumido à parte."

#!/usr/bin/env bash
# Desliga propagação no gateway → cada hop (gateway vs cadeia) com IDs diferentes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

echo "=== PROPAGATE_TRACE=0 no gateway ==="
PROPAGATE_TRACE=0 compose up -d --no-deps gateway
sleep 2
echo "=== enviando prova ==="
RESP=$(curl -sS -X POST http://127.0.0.1:8100/provas \
  -H 'Content-Type: application/json' \
  -d '{"aluno":"sem-prop","arquivo":"x.pdf"}')
echo "${RESP}" | python3 -m json.tool
TRACE=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('trace_id',''))")
echo ""
echo "trace_id do gateway (resposta): ${TRACE}"
echo "No Grafana Explore (Loki), busque:"
echo "  {job=\"portal\"} |= \"${TRACE}\""
echo "→ deve aparecer só no gateway. Depois busque aluno=sem-prop nos outros serviços (outros trace_id)."
echo ""
echo "=== restaurando PROPAGATE_TRACE=1 ==="
PROPAGATE_TRACE=1 compose up -d --no-deps gateway

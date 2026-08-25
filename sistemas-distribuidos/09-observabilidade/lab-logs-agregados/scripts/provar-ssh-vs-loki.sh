#!/usr/bin/env bash
# Contrasta caça via docker compose logs vs um único filtro Loki.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

echo "=== enviando prova ==="
RESP=$(curl -sS -X POST http://127.0.0.1:8100/provas \
  -H 'Content-Type: application/json' \
  -d '{"aluno":"ssh-vs-loki","arquivo":"prova.pdf"}')
echo "${RESP}" | python3 -m json.tool
TRACE=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin)['trace_id'])")

echo ""
echo "=== Abordagem A — SSH / docker logs (3 comandos) ==="
echo "--- gateway ---"
compose logs gateway --tail=20 2>/dev/null | grep -F "${TRACE}" || echo "(sem match óbvio no tail)"
echo "--- analise ---"
compose logs analise --tail=20 2>/dev/null | grep -F "${TRACE}" || echo "(sem match óbvio no tail)"
echo "--- store ---"
compose logs store --tail=20 2>/dev/null | grep -F "${TRACE}" || echo "(sem match óbvio no tail)"

echo ""
echo "=== Abordagem B — agregador (1 filtro) ==="
echo "Grafana Explore → Loki → Last 15 minutes → Run:"
echo "  {job=\"portal\"} |= \"${TRACE}\""
echo ""
echo "Esperado: 1 query remonta os 3 hops; a abordagem A escala mal com N réplicas."

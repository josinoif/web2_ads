#!/usr/bin/env bash
# Contraste: store com log texto livre vs JSON estruturado.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

echo "=== UNSTRUCTURED_LOG=1 no store ==="
UNSTRUCTURED_LOG=1 compose up -d --no-deps store
sleep 2
echo "=== enviando prova ==="
RESP=$(curl -sS -X POST http://127.0.0.1:8100/provas \
  -H 'Content-Type: application/json' \
  -d '{"aluno":"log-texto","arquivo":"x.pdf"}')
echo "${RESP}" | python3 -m json.tool
TRACE=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('trace_id',''))")
echo ""
echo "Última linha do store (texto livre):"
compose exec -T store sh -c 'tail -n 1 /var/log/app/store.log' || true
echo ""
echo "No Loki (aguarde ~15s): {job=\"portal\",service=\"store\"} |= \"log-texto\""
echo "→ linha sem JSON; gateway/analise continuam estruturados (trace_id=${TRACE})."
echo ""
echo "=== restaurando UNSTRUCTURED_LOG=0 ==="
UNSTRUCTURED_LOG=0 compose up -d --no-deps store

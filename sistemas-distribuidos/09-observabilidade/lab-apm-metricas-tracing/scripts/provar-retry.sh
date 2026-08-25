#!/usr/bin/env bash
# Ponte com 06: retry no gateway → vários spans no mesmo trace.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

echo "=== GATEWAY_RETRIES=1 + error_rate=1 (duas tentativas falham) ==="
compose exec -T gateway python - <<'PY'
import json, urllib.request
body = json.dumps({"retries": 1}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/admin/retries", data=body, method="POST")
req.add_header("Content-Type", "application/json")
print(urllib.request.urlopen(req).read().decode())
PY
./scripts/set-inject.sh 0 1

RESP=$(curl -sS -X POST http://127.0.0.1:8110/provas \
  -H 'Content-Type: application/json' \
  -d '{"aluno":"retry-06","arquivo":"x.pdf"}' || true)
echo "${RESP}" | python3 -m json.tool || echo "${RESP}"
TRACE=$(echo "${RESP}" | python3 -c "import sys,json; print(json.load(sys.stdin).get('trace_id',''))" 2>/dev/null || true)

echo ""
echo "No Tempo, abra trace_id=${TRACE}"
echo "Waterfall esperado:"
echo "  POST /provas"
echo "   ├─ chamar_analise_tentativa_1  (ERROR)"
echo "   └─ chamar_analise_tentativa_2  (ERROR)"
echo "Ponte [06]: retry multiplica spans/carga — idempotência importa."
echo ""
echo "=== restaurando retries=0 inject=0 ==="
compose exec -T gateway python - <<'PY'
import json, urllib.request
body = json.dumps({"retries": 0}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/admin/retries", data=body, method="POST")
req.add_header("Content-Type", "application/json")
print(urllib.request.urlopen(req).read().decode())
PY
./scripts/set-inject.sh 0 0

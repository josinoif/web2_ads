#!/usr/bin/env bash
# Worker parado: POST write aceita; inbox não atualiza até o worker voltar.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

echo "=== fanout_mode=worker ==="
curl -s -X POST http://127.0.0.1:8150/admin/config \
  -H "Content-Type: application/json" \
  -d '{"fanout_mode":"worker"}' | python3 -m json.tool

echo "=== stop worker ==="
compose stop worker

MARKER="worker-down-$(date +%s)"
echo "=== POST u1 (worker down) ==="
curl -s -X POST http://127.0.0.1:8150/posts \
  -H "Content-Type: application/json" \
  -d "{\"author\":\"u1\",\"text\":\"${MARKER}\"}" | python3 -m json.tool

echo "=== feed u2 (segue u1) — não deve conter o texto ainda ==="
curl -s http://127.0.0.1:8150/feed/u2 | python3 -c "
import json,sys
d=json.load(sys.stdin)
texts=[i.get('text','') for i in d.get('items',[])]
m='${MARKER}'
print('tempo_ms', d.get('tempo_ms'), 'n', d.get('n'), 'achou_marker', m in texts)
"

echo "=== start worker + espera ==="
compose start worker
sleep 3

echo "=== feed u2 de novo ==="
curl -s http://127.0.0.1:8150/feed/u2 | python3 -c "
import json,sys
d=json.load(sys.stdin)
texts=[i.get('text','') for i in d.get('items',[])]
m='${MARKER}'
print('tempo_ms', d.get('tempo_ms'), 'n', d.get('n'), 'achou_marker', m in texts)
"

echo
echo "Observe: POST 202 com worker down; inbox fria; depois do start, o post aparece."
echo "Interprete: desacoplar no tempo ([10] lab B, [01] fila) — consistência eventual ([03])."
echo "=== voltar inline ==="
curl -s -X POST http://127.0.0.1:8150/admin/config \
  -H "Content-Type: application/json" \
  -d '{"fanout_mode":"inline"}' >/dev/null

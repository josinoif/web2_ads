#!/usr/bin/env bash
# Redis down: closed → 503; open → 200 (fail-open).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

KEY="redis-down-$(date +%s)"
curl -s -X POST http://127.0.0.1:8160/admin/reset >/dev/null || true
curl -s -X POST http://127.0.0.1:8161/admin/reset >/dev/null || true

echo "=== stop redis ==="
compose stop redis
sleep 1

echo "=== closed (espera 503) ==="
curl -s -X POST http://127.0.0.1:8160/api \
  -H "Content-Type: application/json" \
  -d "{\"key\":\"${KEY}\"}" | python3 -m json.tool

echo "=== open (espera 200 fail_open) ==="
curl -s -X POST http://127.0.0.1:8161/api \
  -H "Content-Type: application/json" \
  -d "{\"key\":\"${KEY}\"}" | python3 -m json.tool

echo "=== start redis ==="
compose start redis
sleep 2

echo
echo "Observe: mesmo Redis down → políticas opostas (503 vs 200)."
echo "Nota: latência de 1–2 s no DNS do container parado = artefato Compose, não o algoritmo."
echo "Interprete: pagamento/matricícula → fail-closed; feed público pode fail-open. Lab C = janela fixa."

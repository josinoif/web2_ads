#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8088}"
DISC="${DISC:-SD-101}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

reset() {
  (cd "${ROOT}" && docker compose down -v >/dev/null 2>&1 || true)
  (cd "${ROOT}" && docker compose up -d --build)
  for _ in $(seq 1 30); do
    curl -sf "${API}/health" >/dev/null 2>&1 && break
    sleep 2
  done
  sleep 2
}

echo "=== rmw (esperado: overbooking) ==="
reset
MODO=rmw API="${API}" "${ROOT}/scripts/disputa-fila.sh" --paralelo

echo
echo "=== atomic (esperado: 1 reserva) ==="
reset
MODO=atomic API="${API}" "${ROOT}/scripts/disputa-fila.sh" --paralelo

echo
echo "=== redis-lock (esperado: 1 reserva + fencing_token) ==="
reset
MODO=redis-lock API="${API}" "${ROOT}/scripts/disputa-fila.sh" --paralelo

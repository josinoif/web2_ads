#!/usr/bin/env bash
# Remove lock Redis da disciplina (não há rota HTTP admin).
set -euo pipefail
DISC="${1:-SD-101}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "DEL lock:reserva:${DISC}"
(cd "${ROOT}" && docker compose exec -T redis redis-cli DEL "lock:reserva:${DISC}") \
  || echo "(redis não acessível — rode a partir de lab-coordenacao-mongo/)"

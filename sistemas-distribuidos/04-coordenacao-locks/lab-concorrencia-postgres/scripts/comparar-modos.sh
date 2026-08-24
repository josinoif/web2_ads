#!/usr/bin/env bash
# Compara modos broken vs transaction vs advisory na SD-101.
# Demo completa: ~5 min (3 resets Compose). Prefira em revisão / aula do professor.
set -euo pipefail
API="${API:-http://localhost:8087}"
DISC="${DISC:-SD-101}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "Este script demora ~5 min (docker compose down -v + up para cada modo)."
echo "Para o caminho mínimo, rode só disputa-vaga.sh nos modos broken e transaction."
echo

reset() {
  echo ">>> reset: docker compose down -v && up"
  (cd "${ROOT}" && docker compose down -v >/dev/null 2>&1 || true)
  (cd "${ROOT}" && docker compose up -d --build)
  echo ">>> aguardando postgres..."
  for _ in $(seq 1 40); do
    if curl -sf "${API}/health" >/dev/null 2>&1; then
      break
    fi
    sleep 2
  done
  sleep 2
}

rodar_modo() {
  local modo="$1"
  echo
  echo "========== modo: ${modo} =========="
  reset
  MODO="${modo}" DISC="${DISC}" API="${API}" "${ROOT}/scripts/disputa-vaga.sh" --paralelo
}

rodar_modo broken
rodar_modo transaction
rodar_modo advisory

echo
echo "=== resumo esperado ==="
echo "broken      → 2 matrículas possíveis (overbooking)"
echo "transaction → 1 matrícula + 1 conflito (409)"
echo "advisory    → igual transaction (exclusão explícita)"

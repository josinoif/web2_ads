#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

echo "=== compose up --build ==="
compose up -d --build

echo "=== aguardando unico :8170 e canais :8171 ==="
ok_u=0
ok_c=0
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8170/health >/dev/null 2>&1; then ok_u=1; fi
  if curl -sf http://127.0.0.1:8171/health >/dev/null 2>&1; then ok_c=1; fi
  if [[ "$ok_u" -eq 1 && "$ok_c" -eq 1 ]]; then
    echo "unico + canais ok"
    curl -s http://127.0.0.1:8170/health | python3 -m json.tool
    curl -s http://127.0.0.1:8171/health | python3 -m json.tool
    exit 0
  fi
  sleep 2
done
echo "ERRO: timeout health (unico=$ok_u canais=$ok_c)" >&2
compose ps >&2 || true
exit 1

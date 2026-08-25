#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

echo "=== compose up --build ==="
compose up -d --build

echo "=== aguardando closed :8160 e open :8161 ==="
ok_c=0
ok_o=0
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8160/health >/dev/null 2>&1; then ok_c=1; fi
  if curl -sf http://127.0.0.1:8161/health >/dev/null 2>&1; then ok_o=1; fi
  if [[ "$ok_c" -eq 1 && "$ok_o" -eq 1 ]]; then
    echo "closed + open ok"
    curl -s http://127.0.0.1:8160/health | python3 -m json.tool
    curl -s http://127.0.0.1:8161/health | python3 -m json.tool
    exit 0
  fi
  sleep 2
done
echo "ERRO: timeout health (closed=$ok_c open=$ok_o)" >&2
compose ps >&2 || true
exit 1

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

echo "=== compose up --build ==="
compose up -d --build

echo "=== aguardando sync :8130 e eventos :8131 ==="
ok_s=0
ok_e=0
for i in $(seq 1 90); do
  if curl -sf http://127.0.0.1:8130/health >/dev/null 2>&1; then ok_s=1; fi
  if curl -sf http://127.0.0.1:8131/health >/dev/null 2>&1; then ok_e=1; fi
  if [[ "$ok_s" -eq 1 && "$ok_e" -eq 1 ]]; then
    echo "sync + eventos ok"
    curl -s http://127.0.0.1:8130/admin/config | python3 -m json.tool
    curl -s http://127.0.0.1:8131/admin/config | python3 -m json.tool
    exit 0
  fi
  sleep 2
done
echo "ERRO: timeout (sync=$ok_s eventos=$ok_e)" >&2
compose ps >&2 || true
exit 1

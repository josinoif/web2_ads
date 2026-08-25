#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

echo "=== compose up --build ==="
compose up -d --build

echo "=== aguardando write :8150 e read :8151 ==="
ok_w=0
ok_r=0
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8150/health >/dev/null 2>&1; then ok_w=1; fi
  if curl -sf http://127.0.0.1:8151/health >/dev/null 2>&1; then ok_r=1; fi
  if [[ "$ok_w" -eq 1 && "$ok_r" -eq 1 ]]; then
    echo "write + read ok"
    curl -s http://127.0.0.1:8150/health | python3 -m json.tool
    curl -s http://127.0.0.1:8151/health | python3 -m json.tool
    exit 0
  fi
  sleep 2
done
echo "ERRO: timeout health (write=$ok_w read=$ok_r)" >&2
compose ps >&2 || true
exit 1

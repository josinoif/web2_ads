#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

echo "=== compose up --build ==="
compose up -d --build

echo "=== aguardando monólito :8120 e gateway :8121 ==="
ok_mono=0
ok_gw=0
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8120/health >/dev/null 2>&1; then ok_mono=1; fi
  if curl -sf http://127.0.0.1:8121/health >/dev/null 2>&1; then ok_gw=1; fi
  if [[ "$ok_mono" -eq 1 && "$ok_gw" -eq 1 ]]; then
    echo "monólito + gateway ok"
    curl -s http://127.0.0.1:8120/admin/config | python3 -m json.tool
    curl -s http://127.0.0.1:8121/admin/config | python3 -m json.tool
    exit 0
  fi
  sleep 2
done
echo "ERRO: timeout health (mono=$ok_mono gw=$ok_gw)" >&2
compose ps >&2 || true
exit 1

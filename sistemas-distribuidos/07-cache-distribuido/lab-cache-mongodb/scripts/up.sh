#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

echo "=== compose up --build ==="
compose up -d --build

echo "=== aguardando /health (api1 + api2) ==="
ok1=0
ok2=0
for i in $(seq 1 45); do
  curl -sf http://127.0.0.1:8095/health >/dev/null 2>&1 && ok1=1
  curl -sf http://127.0.0.1:8096/health >/dev/null 2>&1 && ok2=1
  if [[ "${ok1}" == "1" && "${ok2}" == "1" ]]; then
    echo "APIs ok"
    echo "--- api1 ---"
    curl -s http://127.0.0.1:8095/admin/config | python3 -m json.tool
    echo "--- api2 ---"
    curl -s http://127.0.0.1:8096/admin/config | python3 -m json.tool
    exit 0
  fi
  sleep 2
done
echo "ERRO: timeout health :8095/:8096" >&2
compose ps >&2 || true
exit 1

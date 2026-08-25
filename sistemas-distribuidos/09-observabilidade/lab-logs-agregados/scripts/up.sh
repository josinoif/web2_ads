#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

echo "=== compose up --build ==="
compose up -d --build

echo "=== aguardando gateway :8100/health ==="
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8100/health >/dev/null 2>&1; then
    echo "gateway ok"
    curl -s http://127.0.0.1:8100/admin/config | python3 -m json.tool
    echo "Grafana: http://127.0.0.1:3100 (admin/admin) · Explore → Loki"
    exit 0
  fi
  sleep 2
done
echo "ERRO: timeout health gateway" >&2
compose ps >&2 || true
exit 1

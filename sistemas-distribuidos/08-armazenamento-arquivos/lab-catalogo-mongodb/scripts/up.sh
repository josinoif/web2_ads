#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

echo "=== compose up --build ==="
compose up -d --build

echo "=== aguardando /health :8092 ==="
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8092/health >/dev/null 2>&1; then
    echo "API ok"
    curl -s http://127.0.0.1:8092/admin/config | python3 -m json.tool
    exit 0
  fi
  sleep 2
done
echo "ERRO: timeout health :8092" >&2
compose ps >&2 || true
exit 1

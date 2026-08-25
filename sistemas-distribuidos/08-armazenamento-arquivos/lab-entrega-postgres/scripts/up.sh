#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

echo "=== compose up --build ==="
compose up -d --build

echo "=== aguardando /health api1 (:8090) e api2 (:8091) ==="
ok1=0
ok2=0
for i in $(seq 1 60); do
  if curl -sf http://127.0.0.1:8090/health >/dev/null 2>&1; then ok1=1; fi
  if curl -sf http://127.0.0.1:8091/health >/dev/null 2>&1; then ok2=1; fi
  if [[ "${ok1}" -eq 1 && "${ok2}" -eq 1 ]]; then
    echo "APIs ok"
    curl -s http://127.0.0.1:8090/admin/config | python3 -m json.tool
    exit 0
  fi
  sleep 2
done
echo "ERRO: timeout health (api1=${ok1} api2=${ok2})" >&2
compose ps >&2 || true
exit 1

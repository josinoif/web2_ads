#!/usr/bin/env bash
# Aplica delay só em api2 (worker lento) via compose exec.
set -euo pipefail
MS="${1:-80}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=_compose.sh
source "${ROOT}/scripts/_compose.sh"
echo "=== EXTRA_DELAY em api2 = ${MS}ms (outras instâncias inalteradas) ==="
if ! (cd "${ROOT}" && compose exec -T api2 \
  python -c "
import json, urllib.request
req = urllib.request.Request(
    'http://127.0.0.1:8000/admin/delay',
    data=json.dumps({'ms': ${MS}}).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
print(urllib.request.urlopen(req, timeout=10).read().decode())
"); then
  echo "ERRO: falha no exec em api2. Rode: ${SD_COMPOSE} ps && ${SD_COMPOSE} up -d" >&2
  echo "Ver troubleshooting.md § Worker lento" >&2
  exit 1
fi
echo
echo "Rode: API=http://localhost:8089 ./scripts/medir-rps.sh  (compare p50 vs p99)"
echo "Zerar: $0 0"

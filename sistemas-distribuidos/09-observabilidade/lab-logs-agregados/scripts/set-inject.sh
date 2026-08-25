#!/usr/bin/env bash
# Uso: ./scripts/set-inject.sh [delay_ms] [error_rate]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
DELAY="${1:-0}"
RATE="${2:-0}"
compose exec -T analise python - <<PY
import json, urllib.request
body = json.dumps({"delay_ms": int("${DELAY}"), "error_rate": float("${RATE}")}).encode()
req = urllib.request.Request("http://127.0.0.1:8000/admin/inject", data=body, method="POST")
req.add_header("Content-Type", "application/json")
print(urllib.request.urlopen(req).read().decode())
PY

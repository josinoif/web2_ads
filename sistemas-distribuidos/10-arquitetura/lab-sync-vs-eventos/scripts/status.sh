#!/usr/bin/env bash
set -euo pipefail
echo "=== sync :8130 ==="
curl -s http://127.0.0.1:8130/health | python3 -m json.tool || echo "(down)"
echo "=== eventos :8131 ==="
curl -s http://127.0.0.1:8131/health | python3 -m json.tool || echo "(down)"
curl -s http://127.0.0.1:8131/fila | python3 -m json.tool 2>/dev/null || true

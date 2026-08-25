#!/usr/bin/env bash
set -euo pipefail
echo "=== contador :8140/health ==="
curl -s http://127.0.0.1:8140/health | python3 -m json.tool || echo "(indisponível)"
echo "=== hash :8141/health ==="
curl -s http://127.0.0.1:8141/health | python3 -m json.tool || echo "(indisponível)"

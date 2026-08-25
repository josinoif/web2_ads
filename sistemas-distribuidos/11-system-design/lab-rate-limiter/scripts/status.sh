#!/usr/bin/env bash
set -euo pipefail
echo "=== closed :8160 ==="
curl -s http://127.0.0.1:8160/health | python3 -m json.tool || echo "(indisponível)"
echo "=== open :8161 ==="
curl -s http://127.0.0.1:8161/health | python3 -m json.tool || echo "(indisponível)"

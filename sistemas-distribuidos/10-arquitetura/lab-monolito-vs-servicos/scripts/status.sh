#!/usr/bin/env bash
set -euo pipefail
echo "=== monólito :8120/health ==="
curl -s http://127.0.0.1:8120/health | python3 -m json.tool || echo "(indisponível)"
echo "=== gateway :8121/health ==="
curl -s http://127.0.0.1:8121/health | python3 -m json.tool || echo "(indisponível)"
echo "=== analise (via compose) config — se estiver up ==="
curl -s http://127.0.0.1:8121/admin/config | python3 -m json.tool || true

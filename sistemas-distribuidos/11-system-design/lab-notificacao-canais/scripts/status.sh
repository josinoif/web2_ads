#!/usr/bin/env bash
set -euo pipefail
echo "=== unico :8170 ==="
curl -s http://127.0.0.1:8170/health | python3 -m json.tool || echo "(indisponível)"
echo "=== canais :8171 ==="
curl -s http://127.0.0.1:8171/health | python3 -m json.tool || echo "(indisponível)"
echo "=== status ==="
curl -s http://127.0.0.1:8170/status | python3 -m json.tool || true
curl -s http://127.0.0.1:8171/status | python3 -m json.tool || true

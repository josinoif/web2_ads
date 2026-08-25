#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://127.0.0.1:8094}"

curl -s -X POST "${API}/admin/flush_cache" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
curl -s -X POST "${API}/admin/stats_reset" \
  -H "Content-Type: application/json" \
  -d '{}' >/dev/null
echo "cache flushed + stats reset"

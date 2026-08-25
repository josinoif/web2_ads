#!/usr/bin/env bash
# Uso: ./scripts/feed.sh [write|read] [user]
set -euo pipefail
MODO="${1:-write}"
USER="${2:-u1}"
if [[ "$MODO" == "read" ]]; then
  BASE="http://127.0.0.1:8151"
else
  BASE="http://127.0.0.1:8150"
fi
echo "GET $BASE/feed/${USER}"
curl -s "$BASE/feed/${USER}" | python3 -m json.tool

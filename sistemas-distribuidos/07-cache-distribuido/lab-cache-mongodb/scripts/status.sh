#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://127.0.0.1:8095}"

if ! curl -sf "${API}/health" >/dev/null; then
  echo "API fora em ${API}" >&2
  exit 7
fi

curl -s "${API}/admin/config" | python3 -m json.tool

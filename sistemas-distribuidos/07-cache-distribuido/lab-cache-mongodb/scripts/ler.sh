#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://127.0.0.1:8095}"

curl -s "${API}/avisos" | python3 -m json.tool

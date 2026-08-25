#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8089}"
curl -sS "${API}/escala/status" | python3 -m json.tool

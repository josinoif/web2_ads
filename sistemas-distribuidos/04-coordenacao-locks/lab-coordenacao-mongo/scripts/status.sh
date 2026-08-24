#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8088}"
curl -sS "${API}/coordenacao/status" | python3 -m json.tool

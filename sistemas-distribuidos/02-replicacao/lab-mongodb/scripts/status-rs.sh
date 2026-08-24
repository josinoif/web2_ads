#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE_URL:-http://localhost:8083}"
curl -s "${BASE}/replicacao/status" | python3 -m json.tool

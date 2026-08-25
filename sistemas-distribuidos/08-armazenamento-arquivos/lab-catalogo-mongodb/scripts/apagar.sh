#!/usr/bin/env bash
# Uso: ./scripts/apagar.sh <id>
set -euo pipefail
ID="${1:?uso: apagar.sh <id>}"
curl -s -X DELETE "http://127.0.0.1:8092/entregas/${ID}" | python3 -m json.tool

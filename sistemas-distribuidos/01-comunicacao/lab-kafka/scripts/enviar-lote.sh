#!/usr/bin/env bash
set -euo pipefail
N="${1:-10}"
BASE="${BASE_URL:-http://localhost:8081}"
echo "Publicando ${N} eventos em ${BASE} ..."
curl -s -X POST "${BASE}/provas/lote?n=${N}" | python3 -m json.tool

#!/usr/bin/env bash
# uso: ./scripts/publicar.sh "Titulo" "Corpo" [campus]
set -euo pipefail
API="${API:-http://127.0.0.1:8095}"
TITULO="${1:?titulo}"
CORPO="${2:-}"
CAMPUS="${3:-REC}"

BODY="$(TITULO="${TITULO}" CORPO="${CORPO}" CAMPUS="${CAMPUS}" python3 - <<'PY'
import json, os
print(json.dumps({
    "titulo": os.environ["TITULO"],
    "corpo": os.environ["CORPO"],
    "campus_id": os.environ["CAMPUS"],
}, ensure_ascii=False))
PY
)"

curl -s -X POST "${API}/avisos" \
  -H "Content-Type: application/json" \
  -d "${BODY}" | python3 -m json.tool

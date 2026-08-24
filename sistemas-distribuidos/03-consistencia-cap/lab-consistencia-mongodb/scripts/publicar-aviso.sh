#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8086}"
TITULO="${1:-Aviso $(date +%H:%M:%S)}"
CORPO="${2:-Conteúdo de teste do lab}"
WC="${WC:-majority}"
curl -sS -X POST "${API}/avisos?writeConcern=${WC}" \
  -H 'Content-Type: application/json' \
  -d "{\"titulo\":\"${TITULO}\",\"corpo\":\"${CORPO}\"}" \
  | python3 -m json.tool

#!/usr/bin/env bash
set -euo pipefail
# 1/true → unique on (limpa coleção); 0/false → off
RAW="${1:-1}"
case "${RAW}" in
  1|true|True|yes|on) JSON_BOOL=true ;;
  0|false|False|no|off) JSON_BOOL=false ;;
  *) JSON_BOOL=true ;;
esac
curl -sS -X POST http://127.0.0.1:8093/admin/require_unique \
  -H 'Content-Type: application/json' \
  -d "{\"enabled\": ${JSON_BOOL}}" | python3 -m json.tool

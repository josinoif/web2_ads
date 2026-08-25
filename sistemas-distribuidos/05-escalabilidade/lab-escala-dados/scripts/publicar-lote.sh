#!/usr/bin/env bash
# Publica N avisos — hot (tudo campus A) ou espalhado (A/B).
set -euo pipefail
API="${API:-http://localhost:8090}"
N="${N:-40}"
MODO="${1:-hot}"  # hot | spread

echo "=== publicar-lote modo=${MODO} N=${N} ==="

for i in $(seq 1 "${N}"); do
  if [[ "${MODO}" == "spread" ]]; then
    if (( i % 2 == 0 )); then C=A; else C=B; fi
  else
    C=A
  fi
  curl -sS -o /dev/null -w "%{http_code}\n" --max-time 15 \
    -X POST "${API}/avisos" \
    -H 'Content-Type: application/json' \
    -d "{\"campus_id\":\"${C}\",\"titulo\":\"aviso-${i}\",\"corpo\":\"lote ${MODO}\"}" &
  # limita rajada
  if (( i % 20 == 0 )); then wait; fi
done
wait

echo
curl -sS "${API}/escala/status" | python3 -m json.tool

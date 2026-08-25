#!/usr/bin/env bash
# Publica aviso. AVISO_ID / Idempotency-Key opcional.
# Exit: 0=2xx, 49=409, 53=503, 28=timeout curl, 7=API fora
set -euo pipefail
API="${API:-http://127.0.0.1:8093}"
TITULO="${1:-Aviso $(date +%H:%M:%S)}"
MAX_TIME="${MAX_TIME:-60}"
HDRS=(-H 'Content-Type: application/json')
BODY="{\"titulo\":\"${TITULO}\",\"corpo\":\"lab 06\",\"campus_id\":\"A\""
if [[ -n "${AVISO_ID:-}" ]]; then
  HDRS+=(-H "Idempotency-Key: ${AVISO_ID}")
  BODY+=",\"aviso_id\":\"${AVISO_ID}\""
fi
BODY+="}"

TMP="$(mktemp)"
trap 'rm -f "${TMP}"' EXIT
set +e
HTTP="$(curl -sS -o "${TMP}" -w '%{http_code}' --max-time "${MAX_TIME}" -X POST "${API}/avisos" \
  "${HDRS[@]}" -d "${BODY}" 2>"${TMP}.err")"
ec=$?
set -e
if [[ "${ec}" -ne 0 ]]; then
  detail="$(cat "${TMP}.err" 2>/dev/null || cat "${TMP}" 2>/dev/null || true)"
  if [[ "${ec}" -eq 28 ]]; then
    detalhe="timeout do cliente (esperado no Exp. retry) — a API pode ter escrito mesmo assim"
  elif [[ "${ec}" -eq 7 ]]; then
    detalhe="API inacessível — rode ./scripts/up.sh e ./scripts/status.sh"
  else
    detalhe="falha de rede/curl (exit ${ec}) — confira se a API está no ar"
  fi
  python3 -c "
import json, sys
print(json.dumps({
    'erro': 'cliente',
    'curl_exit': int(sys.argv[1]),
    'detalhe': sys.argv[2],
    'msg': sys.argv[3],
}, ensure_ascii=False))
" "${ec}" "${detalhe}" "${detail}"
  exit "${ec}"
fi
out="$(cat "${TMP}")"
if [[ -z "${out}" ]]; then
  echo '{"erro":"cliente","detalhe":"resposta vazia"}'
  exit 1
fi
echo "${out}" | python3 -m json.tool
case "${HTTP}" in
  2*) exit 0 ;;
  409) exit 49 ;;
  503) exit 53 ;;
  *) exit 1 ;;
esac

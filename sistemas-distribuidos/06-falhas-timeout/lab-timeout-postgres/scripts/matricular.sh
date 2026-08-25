#!/usr/bin/env bash
# Uma matrícula. Uso:
#   ./scripts/matricular.sh SD-101 aluno-1
#   MAX_TIME=2 ./scripts/matricular.sh SD-101 aluno-1
#   IDEM_KEY=abc ./scripts/matricular.sh SD-101 aluno-1
#   DEADLINE_MS=1000 ./scripts/matricular.sh SD-101 aluno-1  # propaga X-Deadline-Ms
#   NO_MAX_TIME=1 ./scripts/matricular.sh SD-101 aluno-1   # sem --max-time (Exp. 1)
#
# Exit codes (para scripts de retry):
#   0  — HTTP 2xx
#   49 — HTTP 409 (não retryar: já matriculado / sem vagas)
#   42 — HTTP 422 (Idempotency-Key reutilizada com outro corpo)
#   53 — HTTP 503 (retryable / circuit)
#   54 — HTTP 504 (deadline propagation — retryable)
#   28 — timeout do curl (falso negativo possível)
#   7  — API fora / conexão recusada
#   outros — falha de rede/curl
set -euo pipefail
API="${API:-http://127.0.0.1:8092}"
DISC="${1:-SD-101}"
ALUNO="${2:-aluno-$(date +%s%N)}"
HDRS=(-H 'Content-Type: application/json')
if [[ -n "${IDEM_KEY:-}" ]]; then
  HDRS+=(-H "Idempotency-Key: ${IDEM_KEY}")
fi
if [[ -n "${DEADLINE_MS:-}" ]]; then
  HDRS+=(-H "X-Deadline-Ms: ${DEADLINE_MS}")
fi

BODY="{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"${ALUNO}\"}"
TMP="$(mktemp)"
trap 'rm -f "${TMP}"' EXIT

set +e
if [[ -n "${NO_MAX_TIME:-}" ]]; then
  HTTP="$(curl -sS -o "${TMP}" -w '%{http_code}' -X POST "${API}/matricular" \
    "${HDRS[@]}" -d "${BODY}" 2>"${TMP}.err")"
  ec=$?
else
  MAX_TIME="${MAX_TIME:-60}"
  HTTP="$(curl -sS -o "${TMP}" -w '%{http_code}' --max-time "${MAX_TIME}" \
    -X POST "${API}/matricular" "${HDRS[@]}" -d "${BODY}" 2>"${TMP}.err")"
  ec=$?
fi
set -e

if [[ "${ec}" -ne 0 ]]; then
  err_msg="$(cat "${TMP}.err" 2>/dev/null || true)"
  body_msg="$(cat "${TMP}" 2>/dev/null || true)"
  detail="${err_msg:-${body_msg}}"
  if [[ "${ec}" -eq 28 ]]; then
    detalhe="timeout do cliente (esperado no Exp. 2/3/4) — a API pode ter commitado mesmo assim"
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
  422) exit 42 ;;
  503) exit 53 ;;
  504) exit 54 ;;
  *) exit 1 ;;
esac

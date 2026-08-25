#!/usr/bin/env bash
# Retry COM a mesma Idempotency-Key — no máximo um efeito de negócio; replay no cache.
# Após timeout, serializa (espera hold) — a 2ª tentativa costuma já vir com idempotent_replay.
# Ao final: passo 4b — confirmação explícita sem hold.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DISC="${1:-SD-101}"
ALUNO="${2:-aluno-idem-$(date +%s)}"
KEY="${IDEM_KEY:-key-${ALUNO}}"
RETRIES="${RETRIES:-3}"
MAX_TIME="${MAX_TIME:-1}"
HOLD_MS="${HOLD_MS:-}"
JITTER="${JITTER:-1}"

backoff_antes() {
  local i="$1" base
  case "${i}" in
    2) base=0.2 ;;
    3) base=0.5 ;;
    *) base=1.0 ;;
  esac
  local wait="${base}"
  if [[ "${JITTER}" == "1" ]]; then
    wait="$(python3 -c "import random; print(round(${base} * (0.5 + random.random()), 3))")"
  fi
  echo "(backoff ${wait}s antes da tentativa ${i})"
  sleep "${wait}"
}

reset_hold() {
  "${ROOT}/scripts/provocar-lento.sh" 0 >/dev/null || true
}

aguardar_apos_timeout() {
  local ms="${HOLD_MS:-0}"
  if [[ -z "${ms}" || "${ms}" == "0" ]]; then
    return 0
  fi
  local rest
  rest="$(python3 -c "print(max(1, int(${ms})/1000 - int('${MAX_TIME}') + 1))")"
  echo "(serializando: aguardando ${rest}s o request em voo terminar…)"
  sleep "${rest}"
}

if [[ -n "${HOLD_MS}" ]]; then
  "${ROOT}/scripts/provocar-lento.sh" "${HOLD_MS}" >/dev/null
  trap reset_hold EXIT
fi

echo "aluno=${ALUNO} key=${KEY} max-time=${MAX_TIME}s retries=${RETRIES} (com backoff)"
for i in $(seq 1 "${RETRIES}"); do
  if [[ "${i}" -gt 1 ]]; then
    backoff_antes "${i}"
  fi
  echo "--- tentativa ${i} ---"
  set +e
  MAX_TIME="${MAX_TIME}" IDEM_KEY="${KEY}" "${ROOT}/scripts/matricular.sh" "${DISC}" "${ALUNO}"
  ec=$?
  set -e
  case "${ec}" in
    0)
      echo "(sucesso / replay — encerra retries)"
      break
      ;;
    49)
      echo "(HTTP 409 — não retryar)"
      break
      ;;
    42)
      echo "(HTTP 422 — key reutilizada com outro corpo; não retryar)"
      break
      ;;
    53)
      echo "(HTTP 503 retryable)"
      ;;
    54)
      echo "(HTTP 504 deadline — retryable)"
      ;;
    28)
      echo "(timeout curl_exit=28)"
      if [[ "${i}" -lt "${RETRIES}" ]]; then
        aguardar_apos_timeout
        # Replay checa a key antes do hold; zerar hold deixa o 4º caminho ainda mais claro.
        reset_hold
        HOLD_MS=""
      fi
      ;;
    *)
      echo "(falha curl_exit=${ec} — se for 7, rode ./scripts/status.sh / up.sh)"
      ;;
  esac
done

reset_hold
trap - EXIT

echo "=== contagem DESTE aluno ==="
curl -sG "http://127.0.0.1:8092/matriculas" \
  --data-urlencode "disciplina_id=${DISC}" \
  --data-urlencode "aluno_id=${ALUNO}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(json.dumps(d, indent=2, ensure_ascii=False))
print(f\">> aluno matriculas={d.get('matriculas')} auditoria={d.get('auditoria_tentativas')}\")
"

echo
echo "=== 4b) mesma Idempotency-Key SEM hold — deve vir idempotent_replay=true ==="
set +e
MAX_TIME=5 IDEM_KEY="${KEY}" "${ROOT}/scripts/matricular.sh" "${DISC}" "${ALUNO}"
ec=$?
set -e
if [[ "${ec}" -eq 0 ]]; then
  echo "(ok: confira idempotent_replay=true acima; auditoria deste aluno não deve subir no replay)"
else
  echo "(inesperado exit=${ec} — key/aluno/API)"
fi

AUD_ANTES="$(curl -sG "http://127.0.0.1:8092/matriculas" \
  --data-urlencode "disciplina_id=${DISC}" \
  --data-urlencode "aluno_id=${ALUNO}" | python3 -c "import json,sys; print(json.load(sys.stdin).get('auditoria_tentativas'))")"

echo "=== contagem DESTE aluno (pós-replay; auditoria deve permanecer ${AUD_ANTES}) ==="
curl -sG "http://127.0.0.1:8092/matriculas" \
  --data-urlencode "disciplina_id=${DISC}" \
  --data-urlencode "aluno_id=${ALUNO}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(json.dumps(d, indent=2, ensure_ascii=False))
a=d.get('auditoria_tentativas')
print(f\">> aluno matriculas={d.get('matriculas')} auditoria={a}\")
if d.get('matriculas')==1 and a==int('${AUD_ANTES}'):
    print('>> OK Exp. 4: replay sem novo side effect')
"

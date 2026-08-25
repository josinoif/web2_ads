#!/usr/bin/env bash
# Retry sem Idempotency-Key — unique impede 2ª matrícula; auditoria sobe (efeito colateral).
# Após timeout, espera o hold em voo (serializa) — assim a 2ª tentativa costuma mostrar 409.
# Uso: HOLD_MS=3000 MAX_TIME=1 RETRIES=3 ./scripts/matricular-com-retry.sh SD-101 aluno-x
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DISC="${1:-SD-101}"
ALUNO="${2:-aluno-retry-$(date +%s)}"
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

# Evita empilhar N holds em paralelo (corrida confusa no log).
aguardar_apos_timeout() {
  local ms="${HOLD_MS:-0}"
  if [[ -z "${ms}" || "${ms}" == "0" ]]; then
    return 0
  fi
  local rest
  # Cliente já esperou MAX_TIME; falta ~hold - max_time (+ folga).
  rest="$(python3 -c "print(max(1, int(${ms})/1000 - int('${MAX_TIME}') + 1))")"
  echo "(serializando: aguardando ${rest}s o request em voo terminar…)"
  sleep "${rest}"
}

if [[ -n "${HOLD_MS}" ]]; then
  "${ROOT}/scripts/provocar-lento.sh" "${HOLD_MS}" >/dev/null
  trap reset_hold EXIT
fi

echo "aluno=${ALUNO} max-time=${MAX_TIME}s retries=${RETRIES} (SEM Idempotency-Key, com backoff)"
for i in $(seq 1 "${RETRIES}"); do
  if [[ "${i}" -gt 1 ]]; then
    backoff_antes "${i}"
  fi
  echo "--- tentativa ${i} ---"
  set +e
  MAX_TIME="${MAX_TIME}" IDEM_KEY= "${ROOT}/scripts/matricular.sh" "${DISC}" "${ALUNO}"
  ec=$?
  set -e
  case "${ec}" in
    0)
      echo "(sucesso HTTP 2xx — encerra retries)"
      break
      ;;
    49)
      echo "(HTTP 409 — conflito de negócio; NÃO retryar. Auditoria desta tentativa ainda pode ter sido gravada.)"
      break
      ;;
    42)
      echo "(HTTP 422 — Idempotency-Key com corpo diferente; NÃO retryar)"
      break
      ;;
    53)
      echo "(HTTP 503 retryable — próxima tentativa se houver)"
      ;;
    54)
      echo "(HTTP 504 deadline — retryable; API abortou rápido)"
      ;;
    28)
      echo "(timeout curl_exit=28 — a API pode ter commitado mesmo assim)"
      if [[ "${i}" -lt "${RETRIES}" ]]; then
        aguardar_apos_timeout
        # Sem hold nas tentativas seguintes: cliente vê 409 (não outro timeout).
        reset_hold
        HOLD_MS=""
      fi
      ;;
    *)
      echo "(falha curl_exit=${ec} — se for 7, a API pode estar fora; rode ./scripts/status.sh)"
      ;;
  esac
done

reset_hold
trap - EXIT

echo "=== contagem DESTE aluno (espere matriculas=1 e auditoria_tentativas>1) ==="
curl -sG "http://127.0.0.1:8092/matriculas" \
  --data-urlencode "disciplina_id=${DISC}" \
  --data-urlencode "aluno_id=${ALUNO}" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print(json.dumps(d, indent=2, ensure_ascii=False))
m,a = d.get('matriculas'), d.get('auditoria_tentativas')
print()
print(f'>> aluno={d.get(\"filtro\",{}).get(\"aluno_id\")} matriculas={m} auditoria={a}')
if m == 1 and (a or 0) > 1:
    print('>> OK didático Exp. 3: unique salvou o negócio; e-mails/auditoria duplicaram')
elif m == 1:
    print('>> 1 matrícula OK; se auditoria=1, a 2ª tentativa pode não ter corrido — confira o log (409)')
else:
    print('>> confira filtro aluno_id — totais da disciplina enganam após Exp. 1–2')
"
echo "Dica: ignore o total da disciplina; o ponto é ESTE aluno."

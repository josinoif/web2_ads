#!/usr/bin/env bash
# Retry do mesmo aviso_id — com unique=0 duplica; com unique=1 deduplica.
# Retry só em timeout (28) e 503 (53). Para em 2xx ou 409.
# Backoff 0.2 → 0.5 → 1.0 (+ jitter).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AVISO_ID="${AVISO_ID:-aviso-$(date +%s)}"
RETRIES="${RETRIES:-3}"
MAX_TIME="${MAX_TIME:-1}"
HOLD_MS="${HOLD_MS:-2500}"
UNIQUE="${UNIQUE:-0}"
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

"${ROOT}/scripts/ativar-unique.sh" "${UNIQUE}" >/dev/null
"${ROOT}/scripts/provocar-lento.sh" "${HOLD_MS}" >/dev/null
trap '"${ROOT}/scripts/provocar-lento.sh" 0 >/dev/null || true' EXIT

echo "aviso_id=${AVISO_ID} unique=${UNIQUE} hold=${HOLD_MS} max-time=${MAX_TIME}"
for i in $(seq 1 "${RETRIES}"); do
  if [[ "${i}" -gt 1 ]]; then
    backoff_antes "${i}"
  fi
  echo "--- tentativa ${i} ---"
  set +e
  MAX_TIME="${MAX_TIME}" AVISO_ID="${AVISO_ID}" \
    "${ROOT}/scripts/publicar.sh" "Prova adiada (${AVISO_ID})"
  ec=$?
  set -e
  case "${ec}" in
    0) echo "(sucesso / replay — encerra)"; break ;;
    49) echo "(HTTP 409 — não retryar)"; break ;;
    53) echo "(HTTP 503 retryable)" ;;
    28|*) echo "(timeout/rede — curl_exit=${ec})" ;;
  esac
done

sleep 3
echo "=== total ==="
curl -s http://127.0.0.1:8093/avisos | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('total=', d['total'])
ids=[a.get('aviso_id') for a in d['avisos'] if a.get('aviso_id')=='${AVISO_ID}']
print('docs com este aviso_id=', len(ids))
"

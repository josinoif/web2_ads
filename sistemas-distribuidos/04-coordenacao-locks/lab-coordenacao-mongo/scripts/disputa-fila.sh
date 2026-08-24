#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8088}"
MODO="${MODO:-rmw}"
DISC="${DISC:-SD-101}"
PARALELO=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --paralelo) PARALELO=true; shift ;;
    --mode) MODO="$2"; shift 2 ;;
    --modo) MODO="$2"; shift 2 ;;
    *) DISC="$1"; shift ;;
  esac
done

echo "=== reserva ${DISC} | mode=${MODO} | API=${API} ==="
echo "Reset: docker compose down -v && docker compose up -d --build"
echo

reservar() {
  local aluno="$1"
  local tmp
  tmp="$(mktemp)"
  local code
  code="$(
    curl -sS -o "${tmp}" -w "%{http_code}" --max-time 30 \
      -X POST "${API}/reservar?mode=${MODO}" \
      -H 'Content-Type: application/json' \
      -d "{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"${aluno}\"}"
  )"
  echo "--- ${aluno} HTTP ${code} ---"
  python3 -m json.tool < "${tmp}" 2>/dev/null || cat "${tmp}"
  echo
  rm -f "${tmp}"
}

if [[ "${PARALELO}" == true ]]; then
  reservar aluno-a &
  PID_A=$!
  reservar aluno-b &
  PID_B=$!
  wait "${PID_A}" || true
  wait "${PID_B}" || true
else
  for aluno in aluno-a aluno-b; do
    echo "--- POST ${aluno} ---"
    reservar "${aluno}"
  done
fi

curl -sS "${API}/filas/${DISC}" | python3 -m json.tool
echo
curl -sS "${API}/coordenacao/status" | python3 -m json.tool

#!/usr/bin/env bash
# Disputa a última vaga com modo configurável (default: broken).
set -euo pipefail
API="${API:-http://localhost:8087}"
MODO="${MODO:-broken}"
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

echo "=== disciplina ${DISC} | mode=${MODO} | API=${API} ==="
echo "Schema inicial: SD-101 tem 1 vaga. Reset: docker compose down -v && docker compose up -d --build"
echo

matricular() {
  local aluno="$1"
  local tmp
  tmp="$(mktemp)"
  local code
  code="$(
    curl -sS -o "${tmp}" -w "%{http_code}" --max-time 30 \
      -X POST "${API}/matricular?mode=${MODO}" \
      -H 'Content-Type: application/json' \
      -d "{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"${aluno}\"}"
  )"
  echo "--- ${aluno} HTTP ${code} ---"
  python3 -m json.tool < "${tmp}" 2>/dev/null || cat "${tmp}"
  echo
  rm -f "${tmp}"
}

if [[ "${PARALELO}" == true ]]; then
  echo "--- POST paralelo aluno-a e aluno-b (nginx → api1|2|3) ---"
  matricular aluno-a &
  PID_A=$!
  matricular aluno-b &
  PID_B=$!
  wait "${PID_A}" || true
  wait "${PID_B}" || true
else
  for aluno in aluno-a aluno-b; do
    echo "--- POST ${aluno} ---"
    matricular "${aluno}"
  done
fi

echo "=== estado ==="
curl -sS "${API}/disciplinas/${DISC}" | python3 -m json.tool
echo
echo "=== coordenacao/status ==="
curl -sS "${API}/coordenacao/status" | python3 -m json.tool

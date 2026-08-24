#!/usr/bin/env bash
# Disputa a última vaga: duas matrículas (sequenciais ou --paralelo).
set -euo pipefail
API="${API:-http://localhost:8085}"
DISC="${1:-SD-101}"
PARALELO=false
if [[ "${1:-}" == "--paralelo" ]]; then
  PARALELO=true
  DISC="${2:-SD-101}"
fi

echo "=== disciplina ${DISC} — schema inicial: SD-101 tem 1 vaga ==="
echo "Se já matriculou, recrie: docker compose down -v && docker compose up -d --build"
echo "Nota: este lab usa UM primary; overbooking multi-site é tema de decisoes §1 / módulo 04."
echo

if [[ "${PARALELO}" == true ]]; then
  echo "--- POST paralelo aluno-a e aluno-b ---"
  curl -sS --max-time 120 -X POST "${API}/matricular" \
    -H 'Content-Type: application/json' \
    -d "{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"aluno-a\"}" &
  PID_A=$!
  curl -sS --max-time 120 -X POST "${API}/matricular" \
    -H 'Content-Type: application/json' \
    -d "{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"aluno-b\"}" &
  PID_B=$!
  wait "${PID_A}" || true
  wait "${PID_B}" || true
  echo "(veja códigos HTTP nos logs acima ou repita sem --paralelo para JSON formatado)"
else
  for aluno in aluno-a aluno-b; do
    echo "--- POST ${aluno} ---"
    curl -sS --max-time 120 -X POST "${API}/matricular" \
      -H 'Content-Type: application/json' \
      -d "{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"${aluno}\"}" \
      | python3 -m json.tool || echo "(falhou ou timeout)"
    echo
  done
fi

echo "=== estado primary ==="
curl -sS "${API}/disciplinas/${DISC}?dest=primary" | python3 -m json.tool
echo "=== estado réplica ==="
curl -sS "${API}/disciplinas/${DISC}?dest=replica" | python3 -m json.tool

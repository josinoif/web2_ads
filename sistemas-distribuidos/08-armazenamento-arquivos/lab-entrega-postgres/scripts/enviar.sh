#!/usr/bin/env bash
# Uso: ./scripts/enviar.sh [aluno_id] [arquivo] [api_port]
set -euo pipefail
ALUNO="${1:-aluno-01}"
ARQ="${2:-}"
PORT="${3:-8090}"
TMP=""
cleanup() {
  if [[ -n "${TMP}" && -f "${TMP}" ]]; then
    rm -f "${TMP}"
  fi
}
trap cleanup EXIT

if [[ -z "${ARQ}" ]]; then
  TMP="$(mktemp)"
  echo "trabalho de ${ALUNO} $(date -Iseconds)" >"${TMP}"
  ARQ="${TMP}"
  NOME="trabalho.txt"
else
  NOME="$(basename "${ARQ}")"
fi

curl -s -X POST "http://127.0.0.1:${PORT}/entregas" \
  -H "X-Aluno-Id: ${ALUNO}" \
  -H "X-Disciplina: SD" \
  -H "X-Nome-Arquivo: ${NOME}" \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@${ARQ}" | python3 -m json.tool

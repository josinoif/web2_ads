#!/usr/bin/env bash
# Contrasta: análise down (serviços) vs monólito down.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

code() {
  # curl já imprime 000 se a conexão falhar; não concatenar outro 000
  curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 "$@" 2>/dev/null || printf '000'
}

echo "=== 1) Baseline: tudo up ==="
compose start monolito analise gateway store >/dev/null 2>&1 || compose up -d >/dev/null
sleep 2
echo "mono health=$(code http://127.0.0.1:8120/health)  gw health=$(code http://127.0.0.1:8121/health)"
echo "mono POST=$(code -X POST http://127.0.0.1:8120/provas -H 'Content-Type: application/json' -d '{"aluno":"a","arquivo":"a.pdf"}')"
echo "srv  POST=$(code -X POST http://127.0.0.1:8121/provas -H 'Content-Type: application/json' -d '{"aluno":"a","arquivo":"a.pdf"}')"

echo
echo "=== 2) stop analise (serviços) ==="
compose stop analise
sleep 1
echo "gw health=$(code http://127.0.0.1:8121/health)  ← deve continuar 200"
echo "srv  POST=$(code -X POST http://127.0.0.1:8121/provas -H 'Content-Type: application/json' -d '{"aluno":"a","arquivo":"a.pdf"}')  ← deve falhar (5xx/000)"
echo "mono health=$(code http://127.0.0.1:8120/health)  ← monólito independente ainda 200"

echo
echo "=== 3) restaura analise; stop monolito ==="
compose start analise
sleep 2
compose stop monolito
sleep 1
echo "mono health=$(code http://127.0.0.1:8120/health)  ← 000 (processo inteiro fora)"
echo "gw health=$(code http://127.0.0.1:8121/health)  ← serviços intactos"

echo
echo "=== 4) restaura tudo ==="
compose start monolito
sleep 1
echo "mono health=$(code http://127.0.0.1:8120/health)  gw health=$(code http://127.0.0.1:8121/health)"
echo
echo "Interprete: no monólito, 'matar a análise' = matar o processo. Nos serviços, a borda ainda respira."

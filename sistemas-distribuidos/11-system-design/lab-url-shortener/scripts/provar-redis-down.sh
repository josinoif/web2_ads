#!/usr/bin/env bash
# Redis down: contador POST falha; lookup de código já gravado ainda pode ir ao store.
# Se a API for antiga (sem timeout Redis), rode ./scripts/up.sh antes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

if ! curl -sf http://127.0.0.1:8140/health >/dev/null 2>&1; then
  echo "API fora — subindo com --build..."
  ./scripts/up.sh
fi

BASE_C="http://127.0.0.1:8140"
BASE_H="http://127.0.0.1:8141"

echo "=== gravar URL no contador (Redis up) ==="
CODE="$(curl -s -X POST "$BASE_C/encurtar" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://ifpe.edu.br/redis-down-$(date +%s)\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['codigo'])")"
echo "codigo=${CODE}"

echo "=== stop redis ==="
compose stop redis
sleep 1

echo "=== POST contador (espera 503) ==="
curl -s -X POST "$BASE_C/encurtar" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://ifpe.edu.br/deve-falhar"}' | python3 -m json.tool || true

echo "=== GET lookup contador codigo já existente (store local) ==="
curl -s "$BASE_C/lookup/${CODE}" | python3 -m json.tool || true

echo "=== POST hash (não precisa de INCR) ==="
curl -s -X POST "$BASE_H/encurtar" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://ifpe.edu.br/hash-sem-redis-$(date +%s)\"}" | python3 -m json.tool || true

echo "=== start redis ==="
compose start redis
sleep 2

echo
echo "Observe: contador POST depende do Redis; GET de código antigo pode sobreviver no store do processo."
echo "Interprete: na entrevista, nomeie o modo de falha (POST vs GET) — não só 'Redis SPOF'."

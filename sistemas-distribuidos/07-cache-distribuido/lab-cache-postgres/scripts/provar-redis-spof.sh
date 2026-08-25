#!/usr/bin/env bash
# SPOF do Redis (caminho completo, opcional)
# Para o Redis, vê falha na leitura cacheada, sobe de novo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
unset COMPOSE_FILE COMPOSE_PROJECT_NAME 2>/dev/null || true

API="${API:-http://127.0.0.1:8094}"
ALUNO="${1:-aluno-01}"

if ! curl -sf "${API}/health" >/dev/null; then
  echo "API fora — rode ./scripts/up.sh primeiro" >&2
  exit 7
fi

curl -s -X POST "${API}/admin/cache_backend" \
  -H "Content-Type: application/json" -d '{"backend":"redis"}' >/dev/null
curl -s -X POST "${API}/admin/flush_cache" \
  -H "Content-Type: application/json" -d '{}' >/dev/null

echo "=== 1) miss + hit com Redis no ar ==="
curl -s "${API}/boletim/${ALUNO}" | python3 -c "import json,sys; d=json.load(sys.stdin); print('1a', d.get('cache'), d.get('servido_de'))"
curl -s "${API}/boletim/${ALUNO}" | python3 -c "import json,sys; d=json.load(sys.stdin); print('1b', d.get('cache'), d.get('servido_de'))"

echo "=== 2) parando Redis (SPOF) ==="
compose stop redis
sleep 1

echo "=== 3) GET com Redis parado (espere 503 + code redis_indisponivel) ==="
code=$(curl -s -o /tmp/sd07-spof.json -w "%{http_code}" "${API}/boletim/${ALUNO}" || true)
echo "HTTP ${code}"
python3 -m json.tool /tmp/sd07-spof.json 2>/dev/null || cat /tmp/sd07-spof.json
echo
python3 -c "
import json
d=json.load(open('/tmp/sd07-spof.json'))
assert d.get('code')=='redis_indisponivel', d
print('>> code=redis_indisponivel OK — SPOF da camada de cache')
"
echo ">> Em produção: timeout + fallback à fonte, circuit breaker ([06]), ou cache local de emergência."

echo "=== 4) subindo Redis de novo ==="
compose start redis
for i in $(seq 1 20); do
  if compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
    break
  fi
  sleep 1
done
sleep 1

echo "=== 5) GET após recuperação ==="
curl -s "${API}/boletim/${ALUNO}" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('cache'), d.get('servido_de'), d.get('erro', d.get('nota')))"
echo ">> Com stop/start o Redis costuma manter os dados (hit possível)."
echo ">> O ponto do experimento é o 503 enquanto ele estava parado (SPOF)."

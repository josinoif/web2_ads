#!/usr/bin/env bash
# Exp. 3 opcional: delay na análise — health da borda responde enquanto POST espera.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

DELAY_MS="${1:-3000}"
compose start gateway analise monolito store >/dev/null 2>&1 || ./scripts/up.sh >/dev/null

echo "=== delay ${DELAY_MS}ms na análise (mono + pipeline) ==="
./scripts/set-delay.sh "${DELAY_MS}" >/dev/null

echo "--- pipeline: POST lento em background; health na borda ---"
curl -s -o /tmp/sd10-delay-post.json -w "POST time_total=%{time_total}s http=%{http_code}\n" \
  -X POST http://127.0.0.1:8121/provas \
  -H "Content-Type: application/json" \
  -d '{"aluno":"delay-demo","arquivo":"d.pdf"}' &
PID=$!
sleep 0.3
HEALTH=$(curl -s -o /tmp/sd10-delay-health.json -w "%{http_code}" --connect-timeout 2 \
  http://127.0.0.1:8121/health)
echo "health durante POST lento: HTTP ${HEALTH} ($(python3 -c "import json; print(json.load(open('/tmp/sd10-delay-health.json')).get('ok'))" 2>/dev/null || echo '?'))"
wait "${PID}" || true
python3 -m json.tool < /tmp/sd10-delay-post.json 2>/dev/null | head -12 || cat /tmp/sd10-delay-post.json

echo
echo "--- monólito: mesmo delay bloqueia o processo (health pode esperar) ---"
curl -s -o /tmp/sd10-delay-mono.json -w "POST mono time_total=%{time_total}s http=%{http_code}\n" \
  -X POST http://127.0.0.1:8120/provas \
  -H "Content-Type: application/json" \
  -d '{"aluno":"delay-mono","arquivo":"m.pdf"}' &
PID2=$!
sleep 0.3
HEALTH2=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 5 \
  http://127.0.0.1:8120/health 2>/dev/null || printf '000')
echo "health monólito durante POST lento: HTTP ${HEALTH2} (pode demorar — um processo)"
wait "${PID2}" || true

./scripts/set-delay.sh 0 >/dev/null
echo
echo "Interprete: no pipeline a borda pode ficar viva; no monólito tudo compartilha o mesmo processo."

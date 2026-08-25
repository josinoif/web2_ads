#!/usr/bin/env bash
# Compara cache local vs Redis entre api1 e api2
set -euo pipefail
API1="${API1:-http://127.0.0.1:8095}"
API2="${API2:-http://127.0.0.1:8096}"

echo "=== 1) Redis compartilhado ==="
./scripts/set-backend.sh redis
./scripts/flush.sh
./scripts/provocar-lento.sh 400 >/dev/null
# hold só na api1 — aplicar também na api2
curl -s -X POST "${API2}/admin/store_hold_ms" \
  -H "Content-Type: application/json" -d '{"ms":400}' >/dev/null

echo "miss na api1:"
curl -s "${API1}/avisos" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['cache'], d.get('servido_por'), 'servido_de=', d.get('servido_de'), 'total=', d['total'])"
echo "hit esperado na api2 (mesmo Redis):"
curl -s "${API2}/avisos" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['cache'], d.get('servido_por'), 'servido_de=', d.get('servido_de'), 'duracao_ms=', d['duracao_ms'])"

echo
echo "=== 2) Cache LOCAL (dict) — cada API isolada ==="
./scripts/set-backend.sh local
./scripts/flush.sh
curl -s -X POST "${API1}/admin/store_hold_ms" \
  -H "Content-Type: application/json" -d '{"ms":400}' >/dev/null
curl -s -X POST "${API2}/admin/store_hold_ms" \
  -H "Content-Type: application/json" -d '{"ms":400}' >/dev/null

echo "miss na api1:"
curl -s "${API1}/avisos" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['cache'], d.get('servido_por'), 'servido_de=', d.get('servido_de'))"
echo "miss também na api2 (local não compartilha):"
curl -s "${API2}/avisos" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['cache'], d.get('servido_por'), 'servido_de=', d.get('servido_de'), 'duracao_ms=', d['duracao_ms'])"

# restaura
./scripts/set-backend.sh redis
curl -s -X POST "${API1}/admin/store_hold_ms" \
  -H "Content-Type: application/json" -d '{"ms":0}' >/dev/null
curl -s -X POST "${API2}/admin/store_hold_ms" \
  -H "Content-Type: application/json" -d '{"ms":0}' >/dev/null
echo
echo ">> Redis: 2ª API faz hit. Local: as duas fazem miss."

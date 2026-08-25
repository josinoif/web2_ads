#!/usr/bin/env bash
# Idempotência: mesma URL / mesma Idempotency-Key não cria N códigos.
set -euo pipefail
BASE="${BASE:-http://127.0.0.1:8140}"

curl -s -X POST "$BASE/admin/config" \
  -H "Content-Type: application/json" \
  -d '{"reset_store":true,"flush_cache":true,"store_hold_ms":0}' >/dev/null

URL="https://ifpe.edu.br/idem-$(date +%s)"

echo "=== 1ª POST (cria) ==="
A="$(curl -s -X POST "$BASE/encurtar" -H "Content-Type: application/json" \
  -H "Idempotency-Key: key-demo-1" \
  -d "{\"url\":\"${URL}\"}")"
echo "$A" | python3 -m json.tool
CODE="$(echo "$A" | python3 -c "import json,sys; print(json.load(sys.stdin)['codigo'])")"

echo "=== 2ª POST mesma URL + mesma key (idempotente) ==="
curl -s -X POST "$BASE/encurtar" -H "Content-Type: application/json" \
  -H "Idempotency-Key: key-demo-1" \
  -d "{\"url\":\"${URL}\"}" | python3 -m json.tool

echo "=== 3ª POST mesma URL sem key (dedup por URL) ==="
curl -s -X POST "$BASE/encurtar" -H "Content-Type: application/json" \
  -d "{\"url\":\"${URL}\"}" | python3 -m json.tool

echo "=== 4ª POST mesma key, URL diferente (espera 409) ==="
curl -s -X POST "$BASE/encurtar" -H "Content-Type: application/json" \
  -H "Idempotency-Key: key-demo-1" \
  -d '{"url":"https://ifpe.edu.br/outra"}' | python3 -m json.tool

echo
echo "codigo_original=${CODE}"
echo "Observe: 2ª/3ª → idempotente true; 4ª → 409."
echo "Interprete: retry do cliente não deve criar N short links ([06])."

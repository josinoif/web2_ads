#!/usr/bin/env bash
# Força colisões no modo hash (espaço pequeno).
set -euo pipefail
BASE="http://127.0.0.1:8141"
N="${N:-250}"
CHARS="${CHARS:-3}"

echo "=== hash_chars=${CHARS} reset_store N=${N} ==="
curl -s -X POST "$BASE/admin/config" \
  -H "Content-Type: application/json" \
  -d "{\"hash_chars\":${CHARS},\"reset_store\":true,\"flush_cache\":true,\"store_hold_ms\":0}" \
  | python3 -m json.tool

echo "=== inserindo ${N} URLs distintas ==="
col=0
for i in $(seq 1 "${N}"); do
  out="$(curl -s -X POST "$BASE/encurtar" \
    -H "Content-Type: application/json" \
    -d "{\"url\":\"https://ifpe.edu.br/col-${i}-$(date +%s)\"}")"
  if echo "$out" | python3 -c "import json,sys; sys.exit(0 if json.load(sys.stdin).get('colisao') else 1)"; then
    col=$((col + 1))
  fi
done

echo
echo "=== health ==="
curl -s "$BASE/health" | python3 -m json.tool
echo
echo "colisoes_neste_lote=${col} (campo colisao=true no POST)"
echo "Observe: com ${CHARS} hex (~16^${CHARS} códigos) e ${N} URLs, colisão deixa de ser teórica."
echo "Interprete: hash truncado não é gerador de ID. Ponte: ficha unique IDs + [04]."

#!/usr/bin/env bash
# Mostra 301 vs 302 no mesmo código. Uso: ./scripts/provar-redirect.sh [contador|hash]
set -euo pipefail
MODO="${1:-contador}"
if [[ "$MODO" == "hash" ]]; then
  BASE="http://127.0.0.1:8141"
else
  BASE="http://127.0.0.1:8140"
fi

CODE="$(curl -s -X POST "$BASE/encurtar" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://ifpe.edu.br/redir-$(date +%s)\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['codigo'])")"

echo "=== 302 (temporário, no-store) codigo=${CODE} ==="
curl -s -X POST "$BASE/admin/config" \
  -H "Content-Type: application/json" \
  -d '{"redirect_code":302}' >/dev/null
curl -sI "${BASE}/r/${CODE}" | sed -n '1,12p'

echo
echo "=== 301 (permanente, cacheável no cliente) ==="
curl -s -X POST "$BASE/admin/config" \
  -H "Content-Type: application/json" \
  -d '{"redirect_code":301}' >/dev/null
curl -sI "${BASE}/r/${CODE}" | sed -n '1,12p'

echo
echo "Observe: o status e o Cache-Control mudam; o lab não controla o cache do browser."
echo "Interprete: 301 reduz QPS na origem (cliente nem pergunta de novo) — e complica trocar o destino."

#!/usr/bin/env bash
# Estoura a cota (limit=5 / 10s) — espera 429 após 5 OK.
set -euo pipefail
MODO="${1:-closed}"
KEY="${2:-burst-$(date +%s)}"
N="${N:-8}"
if [[ "$MODO" == "open" ]]; then
  BASE="http://127.0.0.1:8161"
else
  BASE="http://127.0.0.1:8160"
fi

curl -s -X POST "$BASE/admin/reset" >/dev/null
echo "=== $N POSTs key=${KEY} em ${BASE} (limit 5/10s) ==="
for i in $(seq 1 "${N}"); do
  code="$(curl -s -o /tmp/rl-body.json -w '%{http_code}' -X POST "$BASE/api" \
    -H "Content-Type: application/json" \
    -d "{\"key\":\"${KEY}\",\"echo\":${i}}")"
  echo "$i http=$code $(python3 -c "import json; d=json.load(open('/tmp/rl-body.json')); print(d.get('erro') or ('remaining='+str(d.get('remaining'))))")"
done
echo
curl -s "$BASE/health" | python3 -m json.tool
echo
echo "Observe: primeiros 5 → 200; seguintes → 429."
echo "Interprete: rate limit protege a API; não substitui escala ([05])."

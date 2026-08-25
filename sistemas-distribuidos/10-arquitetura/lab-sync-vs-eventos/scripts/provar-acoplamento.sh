#!/usr/bin/env bash
# Contrasta: análise/worker parado — sync falha na borda; eventos aceitam.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

code() {
  curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 --max-time 25 "$@" 2>/dev/null || printf '000'
}

echo "=== 1) Baseline ==="
compose start analise-sync worker >/dev/null 2>&1 || true
sleep 2
echo -n "sync POST time: "
curl -s -o /tmp/sd10-sync.json -w "%{time_total}s http=%{http_code}\n" \
  -X POST http://127.0.0.1:8130/provas -H "Content-Type: application/json" \
  -d '{"aluno":"base","arquivo":"b.pdf"}'
echo -n "evt  POST time: "
curl -s -o /tmp/sd10-evt.json -w "%{time_total}s http=%{http_code}\n" \
  -X POST http://127.0.0.1:8131/provas -H "Content-Type: application/json" \
  -d '{"aluno":"base","arquivo":"b.pdf"}'
python3 -m json.tool < /tmp/sd10-evt.json | head -15

echo
echo "=== 2) stop analise-sync + worker ==="
compose stop analise-sync worker
sleep 1
echo "sync POST=$(code -X POST http://127.0.0.1:8130/provas -H 'Content-Type: application/json' -d '{"aluno":"x","arquivo":"x.pdf"}')  ← deve falhar"
echo -n "evt  POST: "
RESP=$(curl -s -X POST http://127.0.0.1:8131/provas -H "Content-Type: application/json" -d '{"aluno":"fila","arquivo":"f.pdf"}')
echo "$RESP" | python3 -m json.tool
SID=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('submission_id',''))")
echo "status na_fila?:"
curl -s "http://127.0.0.1:8131/provas/${SID}" | python3 -m json.tool

echo
echo "=== 3) start worker — processa o que ficou na fila ==="
compose start worker
sleep 4
curl -s "http://127.0.0.1:8131/provas/${SID}" | python3 -m json.tool

echo
echo "=== 4) restaura analise-sync ==="
compose start analise-sync
echo "Interprete: sync acopla a borda ao miolo *agora*; eventos desacoplam no tempo."

#!/usr/bin/env bash
# Benchmark rápido: N leituras do mesmo aluno
# uso: ./scripts/benchmark.sh [N] [aluno]
set -euo pipefail
API="${API:-http://127.0.0.1:8094}"
N="${1:-20}"
ALUNO="${2:-aluno-01}"

if ! curl -sf "${API}/health" >/dev/null; then
  echo "API fora" >&2
  exit 7
fi

curl -s -X POST "${API}/admin/stats_reset" \
  -H "Content-Type: application/json" -d '{}' >/dev/null

echo "=== ${N} leituras de ${ALUNO} ==="
for i in $(seq 1 "${N}"); do
  curl -s "${API}/boletim/${ALUNO}" >/dev/null
done

curl -s "${API}/admin/config" | python3 -c "
import json,sys
d=json.load(sys.stdin)
s=d['stats']
lat=d.get('latencia') or {}
print(json.dumps({
  'cache_backend': d['cache_backend'],
  'store_hold_ms': d['store_hold_ms'],
  'hits': s['hits'],
  'misses': s['misses'],
  'store_reads': s['store_reads'],
  'hit_rate': d.get('hit_rate'),
  'p50_ms': lat.get('p50_ms'),
  'p95_ms': lat.get('p95_ms'),
  'max_ms': lat.get('max_ms'),
}, indent=2, ensure_ascii=False))
"

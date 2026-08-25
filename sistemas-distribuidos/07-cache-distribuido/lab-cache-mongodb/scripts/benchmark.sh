#!/usr/bin/env bash
# Benchmark rápido na API (padrão api1 :8095)
# uso: ./scripts/benchmark.sh [N]
set -euo pipefail
API="${API:-http://127.0.0.1:8095}"
N="${1:-15}"

if ! curl -sf "${API}/health" >/dev/null; then
  echo "API fora em ${API}" >&2
  exit 7
fi

curl -s -X POST "${API}/admin/stats_reset" \
  -H "Content-Type: application/json" -d '{}' >/dev/null

echo "=== ${N} leituras GET /avisos em ${API} ==="
for i in $(seq 1 "${N}"); do
  curl -s "${API}/avisos" >/dev/null
done

curl -s "${API}/admin/config" | python3 -c "
import json,sys
d=json.load(sys.stdin)
s=d['stats']
lat=d.get('latencia') or {}
print(json.dumps({
  'instance_id': d.get('instance_id'),
  'cache_backend': d['cache_backend'],
  'store_hold_ms': d['store_hold_ms'],
  'hits': s['hits'],
  'misses': s['misses'],
  'store_reads': s['store_reads'],
  'hit_rate': d.get('hit_rate'),
  'p50_ms': lat.get('p50_ms'),
  'p95_ms': lat.get('p95_ms'),
}, indent=2, ensure_ascii=False))
"

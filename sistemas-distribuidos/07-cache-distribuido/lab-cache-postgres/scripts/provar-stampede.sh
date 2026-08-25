#!/usr/bin/env bash
# Stampede: TTL curto, flush, N GETs paralelos
# uso: N=20 ./scripts/provar-stampede.sh
#      LOCK=1 N=20 ./scripts/provar-stampede.sh
set -euo pipefail
API="${API:-http://127.0.0.1:8094}"
ALUNO="${1:-aluno-01}"
N="${N:-20}"
LOCK="${LOCK:-0}"

curl -s -X POST "${API}/admin/store_hold_ms" \
  -H "Content-Type: application/json" -d '{"ms": 500}' >/dev/null
curl -s -X POST "${API}/admin/cache_ttl_sec" \
  -H "Content-Type: application/json" -d '{"sec": 2}' >/dev/null
curl -s -X POST "${API}/admin/stampede_lock" \
  -H "Content-Type: application/json" \
  -d "{\"enabled\": $([ "${LOCK}" = "1" ] && echo true || echo false)}" >/dev/null
curl -s -X POST "${API}/admin/flush_cache" \
  -H "Content-Type: application/json" -d '{}' >/dev/null
curl -s -X POST "${API}/admin/stats_reset" \
  -H "Content-Type: application/json" -d '{}' >/dev/null

echo "=== aquecimento (1 miss) ==="
curl -s "${API}/boletim/${ALUNO}" | python3 -c "import json,sys; print(json.load(sys.stdin).get('cache'))"

STORE_APOS_WARM=$(curl -s "${API}/admin/config" | python3 -c "import json,sys; print(json.load(sys.stdin)['stats']['store_reads'])")

echo "=== esperando TTL expirar (3s) ==="
sleep 3

echo "=== ${N} GETs paralelos (LOCK=${LOCK}) ==="
seq 1 "${N}" | xargs -P "${N}" -I{} curl -s "${API}/boletim/${ALUNO}" >/dev/null

export API STORE_APOS_WARM N LOCK
python3 - <<'PY'
import json, os, urllib.request
api = os.environ["API"]
warm = int(os.environ["STORE_APOS_WARM"])
n = int(os.environ["N"])
with urllib.request.urlopen(api + "/admin/config") as r:
    d = json.load(r)
s = d["stats"]
burst = s["store_reads"] - warm
print(json.dumps({
    "stampede_lock": d["stampede_lock"],
    "store_reads_total": s["store_reads"],
    "store_reads_aquecimento": warm,
    "store_reads_na_rajada": burst,
    "misses": s["misses"],
    "hits": s["hits"],
    "stampede_fills": s["stampede_fills"],
    "stampede_waits": s["stampede_waits"],
    "p95_ms": (d.get("latencia") or {}).get("p95_ms"),
}, indent=2, ensure_ascii=False))
print()
if d["stampede_lock"]:
    print(f">> Com lock: store_reads_na_rajada deve ficar << N={n} (fills+waits)")
else:
    print(f">> Sem lock: store_reads_na_rajada tende a aproximar N={n} (stampede)")
PY

# restaura defaults suaves
curl -s -X POST "${API}/admin/store_hold_ms" \
  -H "Content-Type: application/json" -d '{"ms": 0}' >/dev/null
curl -s -X POST "${API}/admin/cache_ttl_sec" \
  -H "Content-Type: application/json" -d '{"sec": 60}' >/dev/null
curl -s -X POST "${API}/admin/stampede_lock" \
  -H "Content-Type: application/json" -d '{"enabled": false}' >/dev/null

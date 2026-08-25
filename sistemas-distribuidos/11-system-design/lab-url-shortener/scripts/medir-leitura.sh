#!/usr/bin/env bash
# Mede GET /lookup com cache ligado vs desligado (store lento).
# Uso: ./scripts/medir-leitura.sh [contador|hash]
set -euo pipefail
MODO="${1:-contador}"
N="${N:-40}"
HOLD="${HOLD:-40}"
if [[ "$MODO" == "hash" ]]; then
  BASE="http://127.0.0.1:8141"
else
  BASE="http://127.0.0.1:8140"
fi

echo "=== preparar store_hold_ms=${HOLD} em ${BASE} ==="
curl -s -X POST "$BASE/admin/config" \
  -H "Content-Type: application/json" \
  -d "{\"store_hold_ms\":${HOLD},\"flush_cache\":true}" >/dev/null

CODE="$(curl -s -X POST "$BASE/encurtar" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"https://ifpe.edu.br/lab-a-$(date +%s%N)\"}" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['codigo'])")"
echo "codigo=${CODE}"

medir() {
  local label="$1"
  local tmp
  tmp="$(mktemp)"
  local i
  for i in $(seq 1 "${N}"); do
    curl -s "${BASE}/lookup/${CODE}" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tempo_ms',-1), d.get('fonte','?'))"
  done > "${tmp}"
  python3 - "${tmp}" "${label}" <<'PY'
import sys
path, label = sys.argv[1], sys.argv[2]
ms, fontes = [], {}
with open(path) as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 1:
            try:
                ms.append(float(parts[0]))
            except ValueError:
                continue
            if len(parts) > 1:
                fontes[parts[1]] = fontes.get(parts[1], 0) + 1
ms.sort()
if not ms:
    print(f"{label}: sem amostras")
else:
    def pct(p):
        i = min(len(ms) - 1, max(0, int(round((p / 100) * (len(ms) - 1)))))
        return ms[i]
    print(
        f"{label}: n={len(ms)} p50={pct(50):.1f} ms p99={pct(99):.1f} ms "
        f"max={ms[-1]:.1f} fontes={fontes}"
    )
PY
  rm -f "${tmp}"
}

echo
echo "=== cache LIGADO ==="
curl -s -X POST "$BASE/admin/config" \
  -H "Content-Type: application/json" \
  -d '{"cache_enabled":true,"flush_cache":true}' >/dev/null
medir "cache_on"

echo
echo "=== cache DESLIGADO ==="
curl -s -X POST "$BASE/admin/config" \
  -H "Content-Type: application/json" \
  -d '{"cache_enabled":false}' >/dev/null
medir "cache_off"

echo
echo "Observe: p50 cache_on deve ser << p50 cache_off (store_hold_ms=${HOLD})."
echo "Interprete: o gargalo da leitura estava no store, não no hash/contador. Ponte [07]."

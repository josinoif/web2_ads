#!/usr/bin/env bash
# Mede lote hot vs spread (distribuição + tempo) e fan-out de leitura.
# Evidência principal: contagem por shard. Tempo elapsed é apoio (WRITE_MS).
set -euo pipefail
API="${API:-http://localhost:8090}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=_compose.sh
source "${ROOT}/scripts/_compose.sh"
N="${N:-40}"

echo "=== reset volumes (estado limpo) ==="
(cd "${ROOT}" && compose down -v >/dev/null 2>&1 || true)
(cd "${ROOT}" && compose up -d --build)
for _ in $(seq 1 30); do
  curl -sf "${API}/health" >/dev/null 2>&1 && break
  sleep 2
done
sleep 2

echo
echo "=== writes HOT (tudo campus A) — evidência: B≈0 ==="
T0="$(date +%s%N)"
N="${N}" "${ROOT}/scripts/publicar-lote.sh" hot >/tmp/sd05-hot.txt
T1="$(date +%s%N)"
echo "elapsed_hot_ms=$(( (T1 - T0) / 1000000 ))"
grep -A20 '"shards"' /tmp/sd05-hot.txt || tail -20 /tmp/sd05-hot.txt

echo
echo "=== reset + writes SPREAD (A/B) — evidência: ~N/2 em cada ==="
(cd "${ROOT}" && compose down -v >/dev/null 2>&1 || true)
(cd "${ROOT}" && compose up -d --build)
for _ in $(seq 1 30); do
  curl -sf "${API}/health" >/dev/null 2>&1 && break
  sleep 2
done
sleep 2
T0="$(date +%s%N)"
N="${N}" "${ROOT}/scripts/publicar-lote.sh" spread >/tmp/sd05-spread.txt
T1="$(date +%s%N)"
echo "elapsed_spread_ms=$(( (T1 - T0) / 1000000 ))"
grep -A20 '"shards"' /tmp/sd05-spread.txt || tail -20 /tmp/sd05-spread.txt

echo
echo "=== leitura single shard vs fan-out (olhe duracao_ms) ==="
echo "--- campus A ---"
curl -sS "${API}/avisos?campus_id=A&limit=5" | python3 -m json.tool | head -35
echo "--- fan-out (todos) ---"
curl -sS "${API}/avisos?limit=5" | python3 -m json.tool | head -45

echo
echo "Interprete:"
echo "1) Contagens: hot → B≈0; spread → A≈B (EVIDÊNCIA PRINCIPAL da partição)."
echo "2) Tempo: com WRITE_MS, spread costuma ser mais rápido (dois stores em paralelo)."
echo "3) Fan-out: duracao_ms da leitura global ≥ single (READ_SHARD_MS); em rede real o gap cresce."

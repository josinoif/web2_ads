#!/usr/bin/env bash
# Sampling REAL no SDK OTel (ParentBasedTraceIdRatio).
# Só recreata o gateway (span raiz decide; filhos respeitam o parent).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

RATIO="${1:-0.2}"
N="${2:-40}"
TAG="smp$(date +%s)"

echo "=== OTEL_SAMPLE_RATIO=${RATIO} (só gateway — mais rápido) ==="
echo "(Espere ~5s no recreate; ~${N} POSTs em seguida.)"
OTEL_SAMPLE_RATIO="${RATIO}" compose up -d --no-deps --force-recreate gateway
sleep 4
# health
for _ in $(seq 1 20); do
  curl -sf http://127.0.0.1:8110/health >/dev/null 2>&1 && break
  sleep 1
done

echo "=== enviando ${N} POSTs (tag=${TAG}) ==="
for i in $(seq 1 "${N}"); do
  curl -sS -o /dev/null -X POST http://127.0.0.1:8110/provas \
    -H 'Content-Type: application/json' \
    -d "{\"aluno\":\"${TAG}-${i}\",\"arquivo\":\"a.pdf\"}" || true
done
sleep 5

echo "=== Tempo: traces gateway (limit=${N}) ==="
FOUND=$(curl -sG 'http://127.0.0.1:3200/api/search' \
  --data-urlencode 'tags=service.name=gateway' \
  --data-urlencode "limit=${N}" | python3 -c "import sys,json; print(len(json.load(sys.stdin).get('traces',[])))")

echo "=== Loki: linhas com a tag (log NÃO amostrado) ==="
# janela ~2 min
START_NS=$(( ($(date +%s) - 120) * 1000000000 ))
END_NS=$(( $(date +%s) * 1000000000 ))
LOG_HITS=$(curl -sG "http://127.0.0.1:3102/loki/api/v1/query_range" \
  --data-urlencode "query={job=\"portal\"} |= \"${TAG}\"" \
  --data-urlencode "start=${START_NS}" \
  --data-urlencode "end=${END_NS}" \
  --data-urlencode "limit=5000" | python3 -c "
import sys,json
d=json.load(sys.stdin)
n=0
for s in d.get('data',{}).get('result',[]):
  n += len(s.get('values',[]))
print(n)
" 2>/dev/null || echo "0")

echo "Requests enviados: ${N}"
echo "Traces gateway (amostra Tempo, até ${N}): ${FOUND}"
echo "Linhas Loki com tag ${TAG}: ${LOG_HITS}"
python3 - <<PY
n, found, logs, ratio = int("${N}"), int("${FOUND}"), int("${LOG_HITS}"), float("${RATIO}")
esperado = n * ratio
print(f"Esperado ~{esperado:.0f} traces (~{100*ratio:.0f}% de {n}) — binomial, N finito varia")
if found >= n * 0.8:
    print("AVISO: quase todos os traces — confira OTEL_SAMPLE_RATIO no gateway.")
elif found < n:
    print("OK didático: bem menos traces que requests.")
if logs >= n:
    print("OK: logs cobrem os requests (sampling não corta Loki neste lab).")
print("Conclusão: sampling barateia TRACE; use log+trace_id para os casos quentes.")
PY

echo ""
echo "=== restaurando OTEL_SAMPLE_RATIO=1.0 (só gateway) ==="
OTEL_SAMPLE_RATIO=1.0 compose up -d --no-deps --force-recreate gateway
sleep 3
echo "Pronto. Papel: ./scripts/quiz-sampling.sh · real: este script."

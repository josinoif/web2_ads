#!/usr/bin/env bash
# Experimento leve de amplificação de carga (ponte com o módulo 05).
# Mostra: requests >> N, wall clock do lote, e latência p50/p95/max na API.
#
# Uso (sala: N=4 padrão; subir se a máquina aguentar):
#   ./scripts/amplificar-carga.sh           # 4 clientes, jitter ON
#   JITTER=0 ./scripts/amplificar-carga.sh  # thundering herd (retries sincronizados)
#   N=8 HOLD_MS=2000 ./scripts/amplificar-carga.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
N="${N:-4}"
HOLD_MS="${HOLD_MS:-2000}"
MAX_TIME="${MAX_TIME:-1}"
RETRIES="${RETRIES:-3}"
JITTER="${JITTER:-1}"
TS="$(date +%s)"
LOGDIR="$(mktemp -d)"

echo "=== amplificação: N=${N} HOLD_MS=${HOLD_MS} MAX_TIME=${MAX_TIME} RETRIES=${RETRIES} JITTER=${JITTER} ==="
curl -s -X POST http://127.0.0.1:8092/admin/cb_reset \
  -H 'Content-Type: application/json' -d '{}' >/dev/null || true
"${ROOT}/scripts/provocar-lento.sh" "${HOLD_MS}" >/dev/null

req0="$(curl -s http://127.0.0.1:8092/admin/config | python3 -c "import json,sys; print(json.load(sys.stdin)['stats'].get('requests',0))")"

t0="$(date +%s%N)"
pids=()
for i in $(seq 1 "${N}"); do
  (
    HOLD_MS= MAX_TIME="${MAX_TIME}" RETRIES="${RETRIES}" JITTER="${JITTER}" \
      "${ROOT}/scripts/matricular-com-retry.sh" SD-101 "amp-${TS}-${i}" \
      >"${LOGDIR}/c${i}.log" 2>&1 || true
  ) &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "${p}" || true; done
t1="$(date +%s%N)"

"${ROOT}/scripts/provocar-lento.sh" 0 >/dev/null

curl -s http://127.0.0.1:8092/admin/config >"${LOGDIR}/cfg.json"
curl -s 'http://127.0.0.1:8092/matriculas?disciplina_id=SD-101' >"${LOGDIR}/mat.json"

python3 - "${LOGDIR}/cfg.json" "${LOGDIR}/mat.json" "${req0}" "${N}" "${JITTER}" "${t0}" "${t1}" <<'PY'
import json, sys
cfg = json.load(open(sys.argv[1]))
mat = json.load(open(sys.argv[2]))
req0, n, jitter = int(sys.argv[3]), sys.argv[4], sys.argv[5]
t0, t1 = int(sys.argv[6]), int(sys.argv[7])
wall_s = (t1 - t0) / 1e9
req1 = cfg["stats"].get("requests", 0)
lat = cfg.get("latencia") or {}
print("--- resultado ---")
print(f"clientes paralelos (N): {n}")
print(f"jitter: {jitter}")
print(f"wall_clock_lote_s: {wall_s:.2f}")
print(f"requests na API: {req1 - req0} (antes={req0}, depois={req1})")
print(
    f"latencia API (janela): n={lat.get('n')} "
    f"p50_ms={lat.get('p50_ms')} p95_ms={lat.get('p95_ms')} max_ms={lat.get('max_ms')}"
)
print(f"matriculas (disciplina): {mat.get('matriculas')}")
print(f"auditoria_tentativas: {mat.get('auditoria_tentativas')}")
print("Esperado: requests >> N; com HOLD alto, p95/max sobem (workers ocupados).")
print("Compare JITTER=1 vs JITTER=0: sem jitter os retries batem mais juntos (thundering herd).")
print("Ponte [05]: resiliência sem capacidade ainda satura o gargalo.")
PY
rm -rf "${LOGDIR}"

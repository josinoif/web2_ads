#!/usr/bin/env bash
# Compara RPS: 1 API direta (:8091) vs 3 APIs via nginx (:8089).
# LIGHT=1 → N=120 C=24 (notebook fraco; ganho pode ser menor, mas costuma >1,2×).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ "${LIGHT:-0}" == "1" ]]; then
  N="${N:-120}"
  CONCURRENCY="${CONCURRENCY:-24}"
  echo "(modo LIGHT: N=${N} CONCURRENCY=${CONCURRENCY})"
else
  N="${N:-240}"
  CONCURRENCY="${CONCURRENCY:-48}"
fi

echo "=== 1) camada app = 1 instância (api1 :8091) ==="
N="${N}" CONCURRENCY="${CONCURRENCY}" API="http://localhost:8091" \
  "${ROOT}/scripts/medir-rps.sh" | tee /tmp/sd05-rps-1.txt

echo
echo "=== 2) camada app = 3 instâncias (nginx :8089) ==="
N="${N}" CONCURRENCY="${CONCURRENCY}" API="http://localhost:8089" \
  "${ROOT}/scripts/medir-rps.sh" | tee /tmp/sd05-rps-3.txt

rps1="$(grep -oE 'rps_aprox=[0-9.]+' /tmp/sd05-rps-1.txt | tail -1 | cut -d= -f2)"
rps3="$(grep -oE 'rps_aprox=[0-9.]+' /tmp/sd05-rps-3.txt | tail -1 | cut -d= -f2)"

echo
echo "=== interprete ==="
if [[ -n "${rps1}" && -n "${rps3}" ]]; then
  python3 - "${rps1}" "${rps3}" <<'PY'
import sys
a, b = float(sys.argv[1]), float(sys.argv[2])
ganho = (b / a) if a > 0 else float("inf")
print(f"rps_1_api={a}  rps_3_apis={b}  ganho_aprox={ganho:.2f}x")
print("Ganho 1→3: escala na CAMADA DE APLICAÇÃO.")
if ganho < 1.2:
    print("Ganho pequeno: rode sem LIGHT=1 (N=240 C=48) ou veja aproximar-teto.sh.")
else:
    print("RPS subiu com N APIs — capacidade na camada app.")
PY
else
  echo "Ganho 1→3: escala na CAMADA DE APLICAÇÃO."
  echo "Notebook fraco: LIGHT=1 ./scripts/comparar-escala.sh"
fi

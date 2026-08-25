#!/usr/bin/env bash
# Contrasta timeout só no cliente vs deadline propagation na API.
# HOLD=5000 sem deadline → cliente estoura, API continua ~5s.
# Com X-Deadline-Ms=1000 → API aborta rápido (504), libera worker.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== A) SEM deadline (falso negativo clássico) ==="
"${ROOT}/scripts/provocar-lento.sh" 5000 >/dev/null
t0="$(date +%s%N)"
set +e
MAX_TIME=1 "${ROOT}/scripts/matricular.sh" SD-101 "dl-sem-$(date +%s)"
set -e
t1="$(date +%s%N)"
echo "wall_cliente_s=$(python3 -c "print(round((${t1}-${t0})/1e9, 3))")  (≈1s no cliente; API ainda pode estar no hold)"

echo
echo "=== aguarde hold restante (~4s) para não misturar ==="
sleep 4

echo
echo "=== B) COM X-Deadline-Ms=1000 (propagation) ==="
"${ROOT}/scripts/provocar-lento.sh" 5000 >/dev/null
t0="$(date +%s%N)"
set +e
MAX_TIME=3 DEADLINE_MS=1000 "${ROOT}/scripts/matricular.sh" SD-101 "dl-com-$(date +%s)"
ec=$?
set -e
t1="$(date +%s%N)"
echo "wall_cliente_s=$(python3 -c "print(round((${t1}-${t0})/1e9, 3))") exit=${ec} (espere 54=504 rápido)"
curl -s http://127.0.0.1:8092/admin/config | python3 -c "
import json,sys
c=json.load(sys.stdin)
print('deadline_abort=', c['stats'].get('deadline_abort'))
"

"${ROOT}/scripts/provocar-lento.sh" 0 >/dev/null
echo "Ponto: timeout na borda não libera o worker; deadline na API sim."

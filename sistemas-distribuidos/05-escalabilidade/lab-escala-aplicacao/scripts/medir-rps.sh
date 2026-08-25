#!/usr/bin/env bash
# Mede RPS e latências aproximadas (p50/p99) contra GET /boletim.
set -euo pipefail
API="${API:-http://localhost:8089}"
N="${N:-80}"
CONCURRENCY="${CONCURRENCY:-8}"
ALUNO="${ALUNO:-aluno-1}"

echo "=== medir-rps | N=${N} concurrency=${CONCURRENCY} | ${API} ==="
echo

TMP="$(mktemp)"
START_NS="$(date +%s%N)"

seq 1 "${N}" | xargs -P "${CONCURRENCY}" -I{} bash -c "
  t0=\$(date +%s%N)
  code=\$(curl -sS -o /dev/null -w '%{http_code}' --max-time 30 \
    '${API}/boletim?aluno_id=${ALUNO}' || echo 000)
  t1=\$(date +%s%N)
  ms=\$(( (t1 - t0) / 1000000 ))
  echo \"\$code \$ms\"
" > "${TMP}"

END_NS="$(date +%s%N)"
ELAPSED_MS=$(( (END_NS - START_NS) / 1000000 ))
OK="$(awk '$1==200 {c++} END{print c+0}' "${TMP}")"
FAIL=$((N - OK))

python3 - "${TMP}" "${OK}" "${FAIL}" "${ELAPSED_MS}" <<'PY'
import sys
path, ok, fail, elapsed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
vals = []
with open(path) as f:
    for line in f:
        parts = line.split()
        if len(parts) == 2 and parts[0] == "200":
            vals.append(int(parts[1]))
vals.sort()
if not vals:
    print("nenhuma resposta 200")
else:
    def pct(p):
        i = min(len(vals) - 1, max(0, int(round((p / 100) * (len(vals) - 1)))))
        return vals[i]
    print(
        f"n={len(vals)}  min={vals[0]}  p50={pct(50)}  "
        f"p95={pct(95)}  p99={pct(99)}  max={vals[-1]}"
    )
rps = round(ok / max(elapsed / 1000, 0.001), 2)
print(f"ok={ok} fail={fail} elapsed_ms={elapsed} rps_aprox={rps}")
PY

echo
curl -sS "${API}/escala/status" | python3 -m json.tool
rm -f "${TMP}"

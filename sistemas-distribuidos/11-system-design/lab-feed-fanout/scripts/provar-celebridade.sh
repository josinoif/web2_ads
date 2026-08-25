#!/usr/bin/env bash
# POST comum vs celebridade nas duas topologias (fan-out inline no write).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"

echo "=== garantir inline no write ==="
curl -s -X POST http://127.0.0.1:8150/admin/config \
  -H "Content-Type: application/json" \
  -d '{"fanout_mode":"inline","fanout_ms_per_follower":5}' | python3 -m json.tool

postar() {
  local base="$1"
  local author="$2"
  echo
  echo "--- POST ${base} author=${author} ---"
  curl -s -X POST "${base}/posts" \
    -H "Content-Type: application/json" \
    -d "{\"author\":\"${author}\",\"text\":\"exp-celeb ${author} $(date +%s)\"}" \
    | python3 -m json.tool
}

echo "======== WRITE (fan-out on write) ========"
postar "http://127.0.0.1:8150" "u1"
postar "http://127.0.0.1:8150" "celeb"

echo
echo "======== READ (fan-out on read) ========"
postar "http://127.0.0.1:8151" "u1"
postar "http://127.0.0.1:8151" "celeb"

echo
echo "Observe: no WRITE, tempo_ms da celeb ≫ u1 (N seguidores × 5 ms). No READ, os dois POSTs são baratos."
echo "Interprete: celebrity problem é custo de *escrita* no fan-out on write. Ponte [05] hot key + [10] EDA."

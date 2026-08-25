#!/usr/bin/env bash
# Grafo sintético via POST /admin/seed (rápido) nas duas topologias.
set -euo pipefail
N="${N:-40}"

seed_one() {
  local base="$1"
  echo "=== seed ${base} N=${N} ==="
  curl -s -X POST "$base/admin/config" \
    -H "Content-Type: application/json" \
    -d '{"fanout_mode":"inline","fanout_ms_per_follower":5}' >/dev/null
  curl -s -X POST "$base/admin/seed" \
    -H "Content-Type: application/json" \
    -d "{\"n\":${N}}" | python3 -m json.tool
  echo "progress: ${N}/${N} users + follows"
  echo "celeb:"
  curl -s "$base/users/celeb" | python3 -m json.tool
  echo "u1:"
  curl -s "$base/users/u1" | python3 -m json.tool
  echo "leitor:"
  curl -s "$base/users/leitor" | python3 -m json.tool
}

seed_one "http://127.0.0.1:8150"
seed_one "http://127.0.0.1:8151"
echo "seed ok"

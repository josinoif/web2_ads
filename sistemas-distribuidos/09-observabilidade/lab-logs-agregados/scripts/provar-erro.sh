#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

echo "=== health ANTES (deve ser 200) ==="
curl -sS http://127.0.0.1:8100/health | python3 -m json.tool
curl -sS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8100/health

./scripts/set-inject.sh 0 1

echo "=== health COM inject de erro (ainda 200 — health mentiroso) ==="
curl -sS http://127.0.0.1:8100/health | python3 -m json.tool
curl -sS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8100/health

echo "=== POST com error_rate=1 (deve falhar) ==="
curl -sS -X POST http://127.0.0.1:8100/provas \
  -H 'Content-Type: application/json' \
  -d '{"aluno":"erro-inj","arquivo":"x.pdf"}' | python3 -m json.tool || true
curl -sS -o /dev/null -w "HTTP %{http_code}\n" -X POST http://127.0.0.1:8100/provas \
  -H 'Content-Type: application/json' \
  -d '{"aluno":"erro-inj2","arquivo":"x.pdf"}' || true

echo "=== restaurando inject 0 0 ==="
./scripts/set-inject.sh 0 0
echo "Loki (Last 15m): {job=\"portal\"} |= \"falha injetada\"  ou  |= \"erro-inj\""
echo "Conclusão: /health verde ≠ POST ok."

#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

echo "=== health (deve ser 200) ==="
curl -sS http://127.0.0.1:8110/health | python3 -m json.tool
curl -sS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8110/health

./scripts/set-inject.sh 0 1

echo "=== health COM inject (ainda 200) ==="
curl -sS http://127.0.0.1:8110/health | python3 -m json.tool
curl -sS -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:8110/health

echo "=== POST com error_rate=1 ==="
curl -sS -X POST http://127.0.0.1:8110/provas \
  -H 'Content-Type: application/json' \
  -d '{"aluno":"erro-apm","arquivo":"x.pdf"}' | python3 -m json.tool || true
curl -sS -o /dev/null -w "HTTP %{http_code}\n" -X POST http://127.0.0.1:8110/provas \
  -H 'Content-Type: application/json' \
  -d '{"aluno":"erro-apm2","arquivo":"x.pdf"}' || true

./scripts/set-inject.sh 0 0
echo "Grafana: error rate sobe · Tempo: span ERROR · Loki |= \"falha injetada\""
echo "Conclusão: /health verde ≠ POST ok."

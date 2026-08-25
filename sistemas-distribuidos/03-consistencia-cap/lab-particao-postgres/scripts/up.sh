#!/usr/bin/env bash
# Sobe o lab e liga sync CP (um comando — evita esquecer ativar-sync).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

echo "=== docker compose up ==="
docker compose up -d --build

echo "=== aguardando API /health ==="
for i in $(seq 1 45); do
  if curl -sf http://localhost:8085/health >/dev/null 2>&1; then
    echo "API ok"
    break
  fi
  sleep 2
  if [[ "$i" -eq 45 ]]; then
    echo "ERRO: timeout em http://localhost:8085/health" >&2
    docker compose ps >&2 || true
    exit 1
  fi
done

"${ROOT}/scripts/ativar-sync.sh"
"${ROOT}/scripts/verificar-modo-cp.sh"
echo
echo "Lab pronto. Tutorial: ../tutorial-particao-postgres.md"

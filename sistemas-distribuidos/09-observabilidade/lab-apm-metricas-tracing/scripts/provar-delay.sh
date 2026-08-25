#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"
DELAY="${1:-2000}"
./scripts/set-inject.sh "${DELAY}" 0
echo "=== POST com delay ${DELAY}ms na análise ==="
./scripts/enviar.sh delay-demo
echo "No Grafana: Dashboards → Portal RED (p95 sobe) · Explore → Tempo (span analisar longo)"
echo "Restaurando inject..."
./scripts/set-inject.sh 0 0

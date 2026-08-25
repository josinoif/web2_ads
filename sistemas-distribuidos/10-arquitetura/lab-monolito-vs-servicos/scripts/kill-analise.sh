#!/usr/bin/env bash
# Para o container de análise (serviços). Gateway deve continuar vivo.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
compose stop analise
echo "analise parado. Teste: curl gateway /health e POST /provas"

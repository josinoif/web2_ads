#!/usr/bin/env bash
# Para o monólito inteiro — health e POST somem juntos.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
compose stop monolito
echo "monolito parado. Teste: curl :8120/health"

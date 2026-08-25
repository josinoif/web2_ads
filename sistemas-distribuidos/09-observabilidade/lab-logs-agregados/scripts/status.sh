#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"

echo "=== gateway /admin/config ==="
curl -s http://127.0.0.1:8100/admin/config | python3 -m json.tool
echo "=== analise /admin/config ==="
compose exec -T analise wget -qO- http://127.0.0.1:8000/admin/config 2>/dev/null \
  || compose exec -T analise python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/admin/config').read().decode())"
echo "=== compose ps ==="
compose ps
echo "=== últimas linhas dos logs (volume) ==="
compose exec -T gateway sh -c 'tail -n 3 /var/log/app/*.log 2>/dev/null || true'

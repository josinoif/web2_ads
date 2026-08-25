#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=/dev/null
source "${ROOT}/scripts/_compose.sh"
cd "${ROOT}"
echo "=== gateway config ==="
curl -s http://127.0.0.1:8110/admin/config | python3 -m json.tool
echo "=== analise inject ==="
compose exec -T analise python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/admin/config').read().decode())"
echo "=== prometheus targets (via API) ==="
curl -s http://127.0.0.1:9091/api/v1/targets | python3 -c "import sys,json; d=json.load(sys.stdin); print([(t['labels'].get('instance'), t['health']) for t in d['data']['activeTargets']])"
echo "=== compose ps ==="
compose ps

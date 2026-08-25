#!/usr/bin/env bash
# Demonstra TTL de Idempotency-Key: após expirar, a mesma key não faz replay.
# Uso: ./scripts/provar-idempotency-ttl.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEY="${IDEM_KEY:-key-ttl-$(date +%s)}"
TTL="${TTL_SEC:-3}"
ALUNO="aluno-ttl-$(date +%s)"

echo "=== TTL=${TTL}s key=${KEY} ==="
curl -sS -X POST http://127.0.0.1:8092/admin/idem_ttl_sec \
  -H 'Content-Type: application/json' -d "{\"sec\": ${TTL}}" | python3 -m json.tool

echo
echo "=== 1) primeira matrícula (grava key) ==="
IDEM_KEY="${KEY}" "${ROOT}/scripts/matricular.sh" SD-101 "${ALUNO}"

echo
echo "=== 2) replay imediato (idempotent_replay=true) ==="
IDEM_KEY="${KEY}" "${ROOT}/scripts/matricular.sh" SD-101 "${ALUNO}"

echo
echo "=== 3) aguarda TTL (${TTL}s + 1) ==="
sleep $((TTL + 1))

echo
echo "=== 4) mesma key após expiry — não é replay; tende a 409 (já matriculado) ==="
set +e
IDEM_KEY="${KEY}" "${ROOT}/scripts/matricular.sh" SD-101 "${ALUNO}"
ec=$?
set -e
echo "(exit=${ec}; confira stats.idem_expired em /admin/config)"
curl -s http://127.0.0.1:8092/admin/config | python3 -c "
import json,sys
c=json.load(sys.stdin)
print('idem_ttl_sec=', c.get('idem_ttl_sec'))
print('idem_expired=', c['stats'].get('idem_expired'))
print('idem_hit=', c['stats'].get('idem_hit'))
"

# restaura TTL padrão de lab
curl -sS -X POST http://127.0.0.1:8092/admin/idem_ttl_sec \
  -H 'Content-Type: application/json' -d '{"sec": 3600}' >/dev/null

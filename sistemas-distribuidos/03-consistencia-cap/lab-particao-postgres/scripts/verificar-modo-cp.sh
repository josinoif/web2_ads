#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
API="${API:-http://localhost:8085}"

STATUS=$(curl -sS "${API}/consistencia/status")
echo "${STATUS}" | python3 -m json.tool
SYNC=$(echo "${STATUS}" | python3 -c "
import sys, json
r = json.load(sys.stdin).get('replicas', [])
ok = any(x.get('sync_state') in ('sync', 'quorum') for x in r)
print('sync' if ok else 'NO_SYNC')
")
if [[ "${SYNC}" != "sync" ]]; then
  echo "sync ainda não ativo — tentando ./scripts/ativar-sync.sh …"
  "${ROOT}/scripts/ativar-sync.sh"
  STATUS=$(curl -sS "${API}/consistencia/status")
  echo "${STATUS}" | python3 -m json.tool
  SYNC=$(echo "${STATUS}" | python3 -c "
import sys, json
r = json.load(sys.stdin).get('replicas', [])
ok = any(x.get('sync_state') in ('sync', 'quorum') for x in r)
print('sync' if ok else 'NO_SYNC')
")
fi
if [[ "${SYNC}" != "sync" ]]; then
  echo "ERRO: sync_state não está sync/quorum — docker compose logs postgres-replica" >&2
  exit 1
fi
echo "OK: modo CP (sync replication ativo; sync_state=sync|quorum)"

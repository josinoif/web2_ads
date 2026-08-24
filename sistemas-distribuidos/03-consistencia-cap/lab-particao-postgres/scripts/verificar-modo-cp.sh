#!/usr/bin/env bash
set -euo pipefail
API="${API:-http://localhost:8085}"
STATUS=$(curl -sS "${API}/consistencia/status")
echo "${STATUS}" | python3 -m json.tool
SYNC=$(echo "${STATUS}" | python3 -c "import sys,json; r=json.load(sys.stdin).get('replicas',[]); print('sync' if any(x.get('sync_state')=='sync' for x in r) else 'NO_SYNC')")
if [[ "${SYNC}" != "sync" ]]; then
  echo "ERRO: sync_state não está sync — recrie o lab ou aguarde a réplica."
  exit 1
fi
echo "OK: modo CP (sync replication ativo)"

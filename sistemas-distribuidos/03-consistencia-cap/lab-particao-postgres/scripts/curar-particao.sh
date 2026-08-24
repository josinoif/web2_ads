#!/usr/bin/env bash
# Restaura link primary ↔ réplica na rede repl_net.
set -euo pipefail
cd "$(dirname "$0")/.."
NET="sd03-particao-postgres_repl_net"
CONTAINER="sd03-particao-postgres-postgres-replica-1"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  CID=$(docker compose ps -q postgres-replica | head -1)
  if [[ -z "${CID}" ]]; then
    echo "réplica não encontrada"
    exit 1
  fi
  CONTAINER=$(docker inspect -f '{{.Name}}' "${CID}" | sed 's|^/||')
fi

if docker inspect "${CONTAINER}" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q "${NET}"; then
  echo "réplica já conectada a ${NET}"
else
  docker network connect "${NET}" "${CONTAINER}"
  echo "partição CURADA: ${CONTAINER} reconectado a ${NET}"
fi

echo "Aguarde alguns segundos e confira sync_state:"
echo "  curl -s http://localhost:8085/consistencia/status | python3 -m json.tool"

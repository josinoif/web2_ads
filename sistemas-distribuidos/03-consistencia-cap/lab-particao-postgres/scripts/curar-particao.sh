#!/usr/bin/env bash
# Restaura link primary ↔ réplica na rede repl_net.
# Importante: reconnect COM --alias postgres-replica — sem isso o DNS some
# (Podman/Docker) e a API deixa de resolver a réplica após particionar/curar.
set -euo pipefail
cd "$(dirname "$0")/.."
NET="sd03-particao-postgres_repl_net"
ALIAS="postgres-replica"
CONTAINER="sd03-particao-postgres-postgres-replica-1"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  CID=$(docker compose ps -q postgres-replica | head -1)
  if [[ -z "${CID}" ]]; then
    echo "réplica não encontrada"
    exit 1
  fi
  CONTAINER=$(docker inspect -f '{{.Name}}' "${CID}" | sed 's|^/||')
fi

conectado() {
  docker inspect "${CONTAINER}" \
    --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' \
    | grep -q "${NET}"
}

tem_alias() {
  docker inspect "${CONTAINER}" --format '{{json .NetworkSettings.Networks}}' \
    | python3 -c "
import json,sys
nets=json.load(sys.stdin)
n=nets.get('${NET}') or {}
aliases=n.get('Aliases') or []
sys.exit(0 if '${ALIAS}' in aliases else 1)
" 2>/dev/null
}

if conectado && tem_alias; then
  echo "réplica já conectada a ${NET} com alias ${ALIAS}"
else
  if conectado; then
    docker network disconnect "${NET}" "${CONTAINER}"
  fi
  docker network connect --alias "${ALIAS}" "${NET}" "${CONTAINER}"
  echo "partição CURADA: ${CONTAINER} reconectado a ${NET} (alias ${ALIAS})"
fi

echo "Aguarde alguns segundos e confira sync_state:"
echo "  curl -s http://localhost:8085/consistencia/status | python3 -m json.tool"

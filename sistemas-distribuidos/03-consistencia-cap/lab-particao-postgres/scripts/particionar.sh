#!/usr/bin/env bash
# Simula partição: réplica perde o link de replicação com o primary (rede repl_net).
set -euo pipefail
cd "$(dirname "$0")/.."
NET="sd03-particao-postgres_repl_net"
CONTAINER="sd03-particao-postgres-postgres-replica-1"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  CONTAINER=$(docker compose ps -q postgres-replica | head -1)
  if [[ -z "${CONTAINER}" ]]; then
    echo "réplica não encontrada — suba o lab: docker compose up -d --build"
    exit 1
  fi
  CONTAINER=$(docker inspect -f '{{.Name}}' "${CONTAINER}" | sed 's|^/||')
fi

if docker inspect "${CONTAINER}" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q "${NET}"; then
  docker network disconnect "${NET}" "${CONTAINER}"
  echo "partição ATIVA: ${CONTAINER} desconectado de ${NET}"
else
  echo "partição já estava ativa (réplica fora de ${NET})"
fi

echo "Confira: curl -s http://localhost:8085/consistencia/status | python3 -m json.tool"

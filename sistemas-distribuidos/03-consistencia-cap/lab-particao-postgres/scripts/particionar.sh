#!/usr/bin/env bash
# Simula partição: corta a réplica da repl_net e mata walsenders no primary.
# Só disconnect de rede (Podman/Docker) pode deixar TCP half-open — sync ainda “ACK”
# e o Experimento 3 falha (201 em vez de 503). Por isso também terminamos backends de replicação.
set -euo pipefail
cd "$(dirname "$0")/.."
NET="sd03-particao-postgres_repl_net"
CONTAINER="sd03-particao-postgres-postgres-replica-1"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
  CONTAINER=$(docker compose ps -q postgres-replica | head -1)
  if [[ -z "${CONTAINER}" ]]; then
    echo "réplica não encontrada — suba o lab: ./scripts/up.sh"
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

# Encerra conexões de replicação ainda listadas em pg_stat_replication (half-open).
PRIMARY_CID=$(docker compose ps -q postgres-primary | head -1)
if [[ -n "${PRIMARY_CID}" ]]; then
  docker exec -e PGPASSWORD=portaladmin "${PRIMARY_CID}" \
    psql -U postgres -d portal -v ON_ERROR_STOP=1 -c \
    "SELECT pg_terminate_backend(pid) FROM pg_stat_replication;" \
    >/dev/null 2>&1 || true
  echo "walsenders no primary encerrados (evita ACK fantasma)"
fi

echo "Confira: curl -s http://localhost:8085/consistencia/status | python3 -m json.tool"
echo "Depois: ./scripts/matricular.sh BD-201 sob-particao  → 503 (sync_ativo=false)"

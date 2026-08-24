#!/usr/bin/env bash
# Isola secondaries do primary na rede rs_net (partição parcial).
set -euo pipefail
cd "$(dirname "$0")/.."
NET="sd03-consistencia-mongodb_rs_net"

for svc in mongo2 mongo3; do
  CID=$(docker compose ps -q "${svc}")
  if [[ -z "${CID}" ]]; then
    echo "${svc} não encontrado"
    exit 1
  fi
  NAME=$(docker inspect -f '{{.Name}}' "${CID}" | sed 's|^/||')
  if docker inspect "${NAME}" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q "${NET}"; then
    docker network disconnect "${NET}" "${NAME}"
    echo "desconectado: ${NAME} de ${NET}"
  else
    echo "já isolado: ${NAME}"
  fi
done

echo "Confira: curl -s http://localhost:8086/consistencia/status | python3 -m json.tool"

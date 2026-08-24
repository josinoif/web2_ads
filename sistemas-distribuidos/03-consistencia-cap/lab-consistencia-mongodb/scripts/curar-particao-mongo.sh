#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
NET="sd03-consistencia-mongodb_rs_net"

for svc in mongo2 mongo3; do
  CID=$(docker compose ps -q "${svc}")
  [[ -z "${CID}" ]] && continue
  NAME=$(docker inspect -f '{{.Name}}' "${CID}" | sed 's|^/||')
  if docker inspect "${NAME}" --format '{{range $k,$v := .NetworkSettings.Networks}}{{$k}} {{end}}' | grep -q "${NET}"; then
    echo "já conectado: ${NAME}"
  else
    docker network connect "${NET}" "${NAME}"
    echo "reconectado: ${NAME} em ${NET}"
  fi
done

echo "Aguarde catch-up e teste GET /avisos com readConcern=majority"

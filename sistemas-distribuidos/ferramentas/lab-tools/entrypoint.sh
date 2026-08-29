#!/bin/bash
# Roda o script do lab num bash Linux. Reescreve localhost → host.docker.internal
# nos argumentos do curl/wget (o script continua usando BASE_URL=http://localhost:PORT).
set -euo pipefail

curl() {
  local -a out=()
  local x
  for x in "$@"; do
    x="${x//http:\/\/localhost/http:\/\/host.docker.internal}"
    x="${x//http:\/\/127.0.0.1/http:\/\/host.docker.internal}"
    out+=("$x")
  done
  command curl "${out[@]}"
}

wget() {
  local -a out=()
  local x
  for x in "$@"; do
    x="${x//http:\/\/localhost/http:\/\/host.docker.internal}"
    x="${x//http:\/\/127.0.0.1/http:\/\/host.docker.internal}"
    out+=("$x")
  done
  command wget "${out[@]}"
}

export -f curl wget
exec bash --noprofile --norc "$@"

#!/usr/bin/env bash
# shellcheck shell=bash
_podman_sock="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/podman/podman.sock"

if [[ -n "${SD_COMPOSE:-}" ]]; then
  :
elif docker ps >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  SD_COMPOSE="docker compose"
elif [[ -S "${_podman_sock}" ]] && DOCKER_HOST="unix://${_podman_sock}" DOCKER_CONTEXT=default docker ps >/dev/null 2>&1; then
  export DOCKER_HOST="unix://${_podman_sock}"
  export DOCKER_CONTEXT=default
  SD_COMPOSE="docker compose"
elif podman ps >/dev/null 2>&1 && podman compose version >/dev/null 2>&1; then
  SD_COMPOSE="podman compose"
else
  SD_COMPOSE="docker compose"
fi
compose() {
  # shellcheck disable=SC2086
  ${SD_COMPOSE} "$@"
}

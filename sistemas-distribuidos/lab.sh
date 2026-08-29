#!/usr/bin/env bash
# Executor de scripts dos labs — Linux, macOS e Windows (Git Bash / MSYS).
#
# Na pasta do lab (atalho lab.sh ao lado do docker-compose.yml):
#   ./lab.sh enviar-lote 10
#   ./lab.sh cliente sincrono
#
# Linux/macOS: roda o bash nativo (curl em localhost).
# Windows (Git Bash): sobe aulas-ads-lab-tools e chama o mesmo .sh.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
LAB="$(pwd)"

if [[ ! -f "$LAB/docker-compose.yml" ]]; then
  echo "rode este comando na pasta do lab (precisa existir docker-compose.yml)" >&2
  exit 2
fi

if [[ $# -lt 1 ]]; then
  echo "uso: $0 NOME-DO-SCRIPT [args...]" >&2
  echo "  exemplo: $0 enviar-lote 10" >&2
  echo "  exemplo: $0 cliente sincrono" >&2
  exit 2
fi

TARGET="$1"
shift
case "$TARGET" in
  *.sh) SCRIPT="$TARGET" ;;
  scripts/*) SCRIPT="$TARGET" ;;
  *) SCRIPT="scripts/${TARGET}.sh" ;;
esac

if [[ ! -f "$LAB/$SCRIPT" ]]; then
  echo "não achei $LAB/$SCRIPT" >&2
  exit 2
fi

# Unix nativo: o .sh já foi escrito para este ambiente
uname_s="$(uname -s 2>/dev/null || echo unknown)"
case "$uname_s" in
  Linux|Darwin)
    exec bash "$LAB/$SCRIPT" "$@"
    ;;
esac

# Windows (Git Bash / MSYS) ou fallback: mesmo caminho do lab.ps1
IMAGE="aulas-ads-lab-tools"
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  docker build -t "$IMAGE" "$ROOT/ferramentas/lab-tools"
fi

PROJECT="$(basename "$LAB")"
DOCKER_ENV=()
while IFS='=' read -r k _; do
  [[ -z "$k" ]] && continue
  case "$k" in
    PATH|HOME|USER|PWD|OLDPWD|SHELL|TERM|HOSTNAME|SHLVL|_|COMPOSE_PROJECT_NAME) continue ;;
  esac
  if [[ "$k" =~ ^[A-Z][A-Z0-9_]*$ ]]; then
    DOCKER_ENV+=(-e "$k")
  fi
done < <(env)

docker run --rm \
  -v "${LAB}:/work" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -w /work \
  -e "COMPOSE_PROJECT_NAME=${PROJECT}" \
  --add-host=host.docker.internal:host-gateway \
  "${DOCKER_ENV[@]}" \
  "$IMAGE" \
  "/work/${SCRIPT}" "$@"

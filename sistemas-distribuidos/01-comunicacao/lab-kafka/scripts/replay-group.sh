#!/usr/bin/env bash
# Replay: novo consumer group lê o tópico desde o início (earliest).
# Uso: ./scripts/replay-group.sh [N]
# Pré-requisito: stack no ar + eventos já publicados.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
N="${1:-8}"

docker compose run --rm --no-deps \
  -e GROUP_ID="metricas-replay-$$" \
  -e KAFKA_BOOTSTRAP=kafka:9092 \
  -e TOPIC_PROVAS=provas.enviadas \
  -e MAX_MSGS="$N" \
  --entrypoint python \
  worker replay_once.py

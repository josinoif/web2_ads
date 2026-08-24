#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
docker compose run --rm --entrypoint python grpc-server /app/run-client.py "$@"

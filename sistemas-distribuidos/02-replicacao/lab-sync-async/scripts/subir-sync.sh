#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose down -v 2>/dev/null || true
docker compose -f docker-compose.yml -f docker-compose.sync.yml up -d --build
echo "Modo: sync — API http://localhost:8084 (modo_lab=sync)"

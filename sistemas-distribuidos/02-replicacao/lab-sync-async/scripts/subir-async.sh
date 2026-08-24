#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
docker compose down -v 2>/dev/null || true
docker compose up -d --build
echo "Modo: async — API http://localhost:8084 (modo_lab=async)"

#!/usr/bin/env bash
# Uso: ./scripts/baixar.sh <id> [api_port]
set -euo pipefail
ID="${1:?uso: baixar.sh <id> [porta]}"
PORT="${2:-8090}"
curl -sS -D - "http://127.0.0.1:${PORT}/entregas/${ID}/arquivo" -o "/tmp/entrega-${ID}.bin" | tee /tmp/entrega-${ID}.hdr
echo
echo "salvo em /tmp/entrega-${ID}.bin"
grep -iE '^(HTTP/|X-Servido|X-Storage|X-Sha256|X-Integridade)' /tmp/entrega-${ID}.hdr || true
ls -la "/tmp/entrega-${ID}.bin"

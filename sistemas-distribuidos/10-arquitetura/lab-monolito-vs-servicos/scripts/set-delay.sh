#!/usr/bin/env bash
# Uso: ./scripts/set-delay.sh <ms>
set -euo pipefail
MS="${1:-0}"
echo "=== monólito :8120 ==="
curl -sf -X POST http://127.0.0.1:8120/admin/inject \
  -H "Content-Type: application/json" \
  -d "{\"delay_ms\":${MS}}" | python3 -m json.tool
echo "=== analise :8122 ==="
curl -sf -X POST http://127.0.0.1:8122/admin/inject \
  -H "Content-Type: application/json" \
  -d "{\"delay_ms\":${MS}}" | python3 -m json.tool
echo "delay_ms=${MS} aplicado nos dois modos"

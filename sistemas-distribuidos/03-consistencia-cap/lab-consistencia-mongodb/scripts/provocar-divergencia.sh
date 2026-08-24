#!/usr/bin/env bash
# Sob partição: publica com w1, compara leitura majority vs local (divergência possível).
set -euo pipefail
API="${API:-http://localhost:8086}"

echo "=== 1) publicar com w1 (passa com primary isolado do quórum) ==="
WC=w1 ./scripts/publicar-aviso.sh "Aviso w1 sob partição"

echo
echo "=== 2) leitura majority (primary) ==="
curl -sS "${API}/avisos?dest=primary&readConcern=majority&limit=5" | python3 -m json.tool

echo
echo "=== 3) leitura local (secondary) — aviso pode faltar OU 503 se secondary fora da rede ==="
curl -sS "${API}/avisos?dest=secondary&readConcern=local&limit=5" | python3 -m json.tool || echo "(503 na secondary também é efeito AP-ish — compare leitura no primary acima)"

echo
echo "Depois de curar-particao-mongo.sh, repita comparar-concerns.sh — feeds devem convergir."

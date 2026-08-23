#!/usr/bin/env bash
# Envia N provas para a API e mostra o tamanho da fila.
# Uso: ./scripts/enviar-lote.sh 15

set -euo pipefail
N="${1:-10}"
BASE="${BASE_URL:-http://localhost:8080}"

echo "Enviando lote de ${N} provas para ${BASE} ..."
curl -s -X POST "${BASE}/provas/lote?n=${N}" | python3 -m json.tool
echo
echo "Tamanho atual da fila:"
curl -s "${BASE}/fila" | python3 -m json.tool

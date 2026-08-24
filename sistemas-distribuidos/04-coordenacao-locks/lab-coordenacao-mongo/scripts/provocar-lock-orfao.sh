#!/usr/bin/env bash
# Segura lock por hold_seconds (simula holder lento / órfão após TTL).
set -euo pipefail
API="${API:-http://localhost:8088}"
DISC="${DISC:-BD-201}"
HOLD="${HOLD:-12}"

echo "=== lock órfão: hold ${HOLD}s (TTL default 10s — não é estendido) ==="
echo
echo "ABRA OUTRO TERMINAL agora. Espere ~11s (TTL expirar) e rode:"
echo
echo "  curl -s -X POST '${API}/reservar?mode=redis-lock' \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"outro\"}' | python3 -m json.tool"
echo
echo "Nos primeiros 10s o T2 recebe 409 (lock ativo). Depois do TTL: 201."
echo "Este terminal bloqueia ${HOLD}s; o holder deve acordar com 409 (fencing)."
echo

curl -sS --max-time "$((HOLD + 10))" \
  -X POST "${API}/reservar?mode=redis-lock&hold_seconds=${HOLD}" \
  -H 'Content-Type: application/json' \
  -d "{\"disciplina_id\":\"${DISC}\",\"aluno_id\":\"holder-lento\"}" \
  | python3 -m json.tool || echo "(timeout esperado se hold > client timeout)"

echo
echo "=== locks ativos (TTL deve cair para -2 após expirar) ==="
curl -sS "${API}/coordenacao/status" | python3 -m json.tool

#!/usr/bin/env bash
# Compara primary vs réplica logo após um POST (demonstra lag/stale read).
set -euo pipefail
ALUNO="${1:-aluno-lag}"
DISC="${2:-SD}"
VALOR="${3:-9.9}"
BASE="${BASE_URL:-http://localhost:8082}"

echo "== gravando no primary =="
curl -s -X POST "${BASE}/notas" \
  -H "Content-Type: application/json" \
  -d "{\"aluno_id\":\"${ALUNO}\",\"disciplina\":\"${DISC}\",\"valor\":${VALOR}}" \
  | python3 -m json.tool

echo ""
echo "== leitura imediata primary =="
curl -s "${BASE}/notas/${ALUNO}?dest=primary" | python3 -m json.tool

echo ""
echo "== leitura imediata replica =="
curl -s "${BASE}/notas/${ALUNO}?dest=replica" | python3 -m json.tool

echo ""
echo "== lag (pg_stat_replication) =="
curl -s "${BASE}/replicacao/lag" | python3 -m json.tool

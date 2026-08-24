#!/usr/bin/env bash
# Com réplica parada: async confirma rápido; sync bloqueia ou falha (demonstra RPO).
set -euo pipefail
BASE="${BASE_URL:-http://localhost:8084}"
COMPOSE="${COMPOSE_CMD:-docker compose}"
ALUNO="${1:-aluno-rpo}"
DISC="${2:-SD}"

echo "== status antes =="
curl -s "${BASE}/replicacao/status" | python3 -m json.tool

echo ""
echo "== parando réplica =="
${COMPOSE} stop postgres-replica

echo ""
echo "== POST com réplica down (pode demorar ou falhar em modo sync) =="
date +%H:%M:%S
curl -s --max-time 90 -X POST "${BASE}/notas" \
  -H "Content-Type: application/json" \
  -d "{\"aluno_id\":\"${ALUNO}\",\"disciplina\":\"${DISC}\",\"valor\":9.9}" \
  | python3 -m json.tool || echo "(timeout ou erro — esperado em sync)"
date +%H:%M:%S

echo ""
echo "== subindo réplica =="
${COMPOSE} start postgres-replica
sleep 15
curl -s "${BASE}/replicacao/status" | python3 -m json.tool

#!/usr/bin/env bash
# Demonstra stale read: para a réplica, grava no primary, compara leituras.
# Uso: ./scripts/provocar-stale.sh [aluno_id] [disciplina] [valor_novo]
set -euo pipefail

ALUNO="${1:-aluno-stale}"
DISC="${2:-SD}"
VALOR="${3:-9.9}"
BASE="${BASE_URL:-http://localhost:8082}"
COMPOSE="${COMPOSE_CMD:-docker compose}"

echo "== 1) valor inicial no primary =="
curl -s -X POST "${BASE}/notas" \
  -H "Content-Type: application/json" \
  -d "{\"aluno_id\":\"${ALUNO}\",\"disciplina\":\"${DISC}\",\"valor\":8.0}" \
  | python3 -m json.tool

echo ""
echo "== 2) aguardando réplica sincronizar =="
sleep 3
curl -s "${BASE}/notas/${ALUNO}?dest=replica" | python3 -m json.tool

echo ""
echo "== 3) parando réplica (primary segue recebendo writes) =="
${COMPOSE} stop postgres-replica

echo ""
echo "== 4) gravando valor novo no primary (réplica parada) =="
curl -s -X POST "${BASE}/notas" \
  -H "Content-Type: application/json" \
  -d "{\"aluno_id\":\"${ALUNO}\",\"disciplina\":\"${DISC}\",\"valor\":${VALOR}}" \
  | python3 -m json.tool

echo ""
echo "== 5) leitura primary (valor novo) vs réplica (ainda parada — esperado erro ou indisponível) =="
echo "--- primary ---"
curl -s "${BASE}/notas/${ALUNO}?dest=primary" | python3 -m json.tool
echo "--- replica (container parado) ---"
curl -s "${BASE}/notas/${ALUNO}?dest=replica" | python3 -m json.tool || true

echo ""
echo "== 6) subindo réplica de novo =="
${COMPOSE} start postgres-replica

echo "Aguardando catch-up (15–60 s)..."
for i in $(seq 1 30); do
  REPLICA_OK=$(
    curl -s "${BASE}/replicacao/status" \
      | python3 -c "import sys,json; r=json.load(sys.stdin).get('replica',{}); print('1' if r.get('ok') else '0')" \
      2>/dev/null || echo "0"
  )
  if [[ "${REPLICA_OK}" == "1" ]]; then
    VALOR_REPLICA=$(
      curl -s "${BASE}/notas/${ALUNO}?dest=replica" \
        | python3 -c "import sys,json; n=json.load(sys.stdin).get('notas',[]); print(n[0]['valor'] if n else '')" \
        2>/dev/null || echo ""
    )
    if [[ "${VALOR_REPLICA}" == "${VALOR}" ]]; then
      break
    fi
  fi
  sleep 2
done

echo ""
echo "== 7) após catch-up: primary vs réplica devem coincidir =="
echo "--- primary ---"
curl -s "${BASE}/notas/${ALUNO}?dest=primary" | python3 -m json.tool
echo "--- replica ---"
curl -s "${BASE}/notas/${ALUNO}?dest=replica" | python3 -m json.tool

echo ""
echo "Compare: entre os passos 4 e 7 a réplica ficou atrás (stale) ou indisponível."

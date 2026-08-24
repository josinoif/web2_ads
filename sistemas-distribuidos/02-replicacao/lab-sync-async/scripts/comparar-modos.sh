#!/usr/bin/env bash
# Compara async vs sync: sobe cada modo, mede escrita, derruba (demora ~5–8 min).
set -euo pipefail
DIR="$(dirname "$0")/.."
cd "${DIR}"

echo "########## MODO ASYNC ##########"
./scripts/subir-async.sh
echo "Aguardando réplica (poll status)..."
for i in $(seq 1 60); do
  OK=$(curl -s http://localhost:8084/replicacao/status 2>/dev/null \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print('1' if d.get('replica_acessivel') else '0')" \
    2>/dev/null || echo "0")
  [[ "${OK}" == "1" ]] && break
  sleep 5
done
./scripts/medir-escrita.sh aluno-async "SD" 7.0
docker compose down -v

echo ""
echo "########## MODO SYNC ##########"
./scripts/subir-sync.sh
echo "Aguardando réplica (poll status)..."
for i in $(seq 1 60); do
  OK=$(curl -s http://localhost:8084/replicacao/status 2>/dev/null \
    | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('replicas',[{}]); print('1' if r and r[0].get('sync_state')=='sync' else '0')" \
    2>/dev/null || echo "0")
  REPLICA=$(curl -s http://localhost:8084/replicacao/status 2>/dev/null \
    | python3 -c "import sys,json; print('1' if json.load(sys.stdin).get('replica_acessivel') else '0')" \
    2>/dev/null || echo "0")
  [[ "${REPLICA}" == "1" ]] && break
  sleep 5
done
./scripts/medir-escrita.sh aluno-sync "SD" 8.0
docker compose down -v

echo ""
echo "Compare duracao_commit_ms e sync_state entre os dois modos."

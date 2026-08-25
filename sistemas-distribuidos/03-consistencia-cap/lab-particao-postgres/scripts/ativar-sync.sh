#!/usr/bin/env bash
# Ativa 1 standby síncrono depois que primary + réplica já estão de pé.
# Necessário porque boot com NUM_SYNCHRONOUS_REPLICAS=1 deadlocks o init SQL do Bitnami.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"

# Superuser Bitnami (POSTGRESQL_POSTGRES_PASSWORD no compose)
psql_admin() {
  docker compose exec -T -e PGPASSWORD=portaladmin postgres-primary \
    /opt/bitnami/postgresql/bin/psql -U postgres -d portal -v ON_ERROR_STOP=1 "$@"
}

echo "=== garantindo privilégios de stats ao portal ==="
psql_admin -c "GRANT pg_read_all_stats TO portal;" || true

echo "=== aguardando réplica streaming ==="
for i in $(seq 1 40); do
  out="$(psql_admin -tAc "SELECT count(*) FROM pg_stat_replication WHERE state='streaming'" 2>/dev/null || echo 0)"
  out="${out//[[:space:]]/}"
  if [[ "${out}" =~ ^[1-9] ]]; then
    echo "streaming ok (count=${out})"
    break
  fi
  sleep 2
  if [[ "$i" -eq 40 ]]; then
    echo "ERRO: réplica não entrou em streaming. docker compose logs postgres-replica" >&2
    exit 1
  fi
done

echo "=== ativando synchronous_standby_names (ANY 1) ==="
psql_admin -c "ALTER SYSTEM SET synchronous_standby_names = 'ANY 1 (*)';"
psql_admin -c "SELECT pg_reload_conf();"

sleep 2
echo "=== conferindo sync_state ==="
psql_admin -c "SELECT application_name, state, sync_state FROM pg_stat_replication;"

echo "OK: sync CP ativo. Rode ./scripts/verificar-modo-cp.sh"

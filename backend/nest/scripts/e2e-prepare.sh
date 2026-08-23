#!/usr/bin/env bash
# Prepara Postgres + schema (se necessário) + seed completo antes de npm run test:e2e
# Uso: a partir de backend/nest/ → bash scripts/e2e-prepare.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ -f "$SCRIPT_DIR/../docker-compose.postgres.yml" ]]; then
  ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
  LOJA_API="$ROOT/loja-api"
elif [[ -f "$SCRIPT_DIR/../../docker-compose.postgres.yml" ]]; then
  ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
  LOJA_API="$(cd "$SCRIPT_DIR/.." && pwd)"
else
  echo "ERRO: não encontrei docker-compose.postgres.yml (rode a partir de backend/nest/ ou loja-api/scripts/)." >&2
  exit 1
fi

cd "$ROOT"

docker compose -f docker-compose.postgres.yml up -d
echo "Aguardando Postgres..."
for _ in $(seq 1 30); do
  if docker exec loja-postgres pg_isready -U loja -d loja >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

ensure_schema() {
  local has_users
  has_users="$(docker exec loja-postgres psql -U loja -d loja -tAc "SELECT to_regclass('public.users')" 2>/dev/null | tr -d '[:space:]')"
  if [[ -n "$has_users" ]]; then
    echo "Schema OK (tabela users existe)."
    return 0
  fi

  if [[ ! -f "$LOJA_API/src/app.module.ts" ]]; then
    echo "ERRO: tabela users ausente e loja-api não encontrado em $LOJA_API" >&2
    echo "Suba a API manualmente (npm run start:dev) até o cap. 6+, depois rode este script." >&2
    exit 1
  fi

  if [[ ! -f "$LOJA_API/.env" && -f "$ROOT/.env.example" ]]; then
    echo "AVISO: copie $ROOT/.env.example para $LOJA_API/.env"
  fi

  if curl -sf http://localhost:3000/health >/dev/null 2>&1; then
    echo "ERRO: porta 3000 ocupada (ex.: npm run start:dev ainda rodando)." >&2
    echo "Pare a API antes deste script — o sync sobe node dist/main.js na mesma porta." >&2
    exit 1
  fi

  echo "Sincronizando schema (API sobe brevemente para o TypeORM criar tabelas)..."
  (cd "$LOJA_API" && npm run build)
  (cd "$LOJA_API" && node dist/main.js) &
  local app_pid=$!
  for _ in $(seq 1 60); do
    if curl -sf http://localhost:3000/health >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  kill "$app_pid" 2>/dev/null || true
  wait "$app_pid" 2>/dev/null || true
  echo "Schema sincronizado."
}

ensure_schema

docker exec -i loja-postgres psql -U loja -d loja < seed/seed.sql
bash seed/verify-seed.sh

echo "Pronto: Ana/Cli no banco. Em loja-api/: npm run test:e2e"

#!/usr/bin/env bash
# Aproxima o teto da camada de dados (store compartilhado) de forma didática.
# Não é stress test de CPU do Postgres: usa DB_SLOTS (pool/conexões escassas por API).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=_compose.sh
source "${ROOT}/scripts/_compose.sh"
# Defaults alinhados ao busy-wait (WORK_MS) — com C baixo o ganho 1→3 some.
N="${N:-240}"
CONCURRENCY="${CONCURRENCY:-48}"
SLOTS="${SLOTS:-1}"
HOLD="${HOLD:-40}"

# Em app-bound, resetar WORK_MS para o padrão do lab (15)

fail_exec() {
  local svc="$1"
  echo "ERRO: não consegui configurar ${svc} via ${SD_COMPOSE} exec." >&2
  echo "Checklist rápido:" >&2
  echo "  1) cd ${ROOT} && ${SD_COMPOSE} ps   # api1, api2, api3 = running" >&2
  echo "  2) curl -sf http://localhost:8089/health" >&2
  echo "  3) ${SD_COMPOSE} up -d --build" >&2
  echo "Ver também: ../troubleshooting.md § Aproximar teto" >&2
  exit 1
}

post_svc() {
  local svc="$1"
  local path="$2"
  local json_body="$3"
  local out
  if ! out="$(
    cd "${ROOT}" && compose exec -T "${svc}" python -c "
import json, urllib.request
body = json.loads('''${json_body}''')
req = urllib.request.Request(
    'http://127.0.0.1:8000${path}',
    data=json.dumps(body).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
print(urllib.request.urlopen(req, timeout=10).read().decode())
" 2>&1
  )"; then
    echo "${out}" >&2
    fail_exec "${svc}"
  fi
  echo "${svc} ${out}"
}

post_all() {
  local path="$1"
  local json_body="$2"
  local svc
  for svc in api1 api2 api3; do
    post_svc "${svc}" "${path}" "${json_body}"
  done
}

echo "=== pré-checagem: api1/api2/api3 up? (provider: ${SD_COMPOSE}) ==="
apis_up="$(
  cd "${ROOT}" && compose ps --format '{{.Service}} {{.State}}' 2>/dev/null \
    | awk '$1 ~ /^api[123]$/ && $2 ~ /running|Up/ {print $1}' | sort -u | wc -l
)"
apis_up="${apis_up// /}"
if [[ "${apis_up}" != "3" ]]; then
  if curl -sf http://localhost:8089/health >/dev/null 2>&1 \
    && (cd "${ROOT}" && compose exec -T api1 true) 2>/dev/null \
    && (cd "${ROOT}" && compose exec -T api2 true) 2>/dev/null \
    && (cd "${ROOT}" && compose exec -T api3 true) 2>/dev/null; then
    apis_up=3
  fi
fi
if [[ "${apis_up}" != "3" ]]; then
  echo "ERRO: preciso de api1, api2 e api3 running (achei ${apis_up:-0})." >&2
  (cd "${ROOT}" && compose ps) || true
  fail_exec "api1/api2/api3"
fi

echo "=== A) app-bound: WORK_MS=15, DB_SLOTS=0, STORE_HOLD=0 ==="
post_all /admin/work_ms '{"ms": 15}'
post_all /admin/db_slots '{"slots": 0}'
post_all /admin/store_hold_ms '{"ms": 0}'
N="${N}" CONCURRENCY="${CONCURRENCY}" API="http://localhost:8089" \
  "${ROOT}/scripts/medir-rps.sh" | tee /tmp/sd05-teto-app.txt

echo
echo "=== B) store-bound: WORK_MS=0, DB_SLOTS=${SLOTS}, STORE_HOLD=${HOLD}ms ==="
echo "(CPU da app desligada; cada acesso ao store segura o slot por HOLD ms)"
post_all /admin/work_ms '{"ms": 0}'
post_all /admin/db_slots "{\"slots\": ${SLOTS}}"
post_all /admin/store_hold_ms "{\"ms\": ${HOLD}}"
N="${N}" CONCURRENCY="${CONCURRENCY}" API="http://localhost:8089" \
  "${ROOT}/scripts/medir-rps.sh" | tee /tmp/sd05-teto-db.txt

echo
echo "=== reset (WORK_MS=15, DB_SLOTS=0, STORE_HOLD=0) ==="
post_all /admin/work_ms '{"ms": 15}'
post_all /admin/db_slots '{"slots": 0}'
post_all /admin/store_hold_ms '{"ms": 0}'

rps_a="$(grep -oE 'rps_aprox=[0-9.]+' /tmp/sd05-teto-app.txt | tail -1 | cut -d= -f2)"
rps_b="$(grep -oE 'rps_aprox=[0-9.]+' /tmp/sd05-teto-db.txt | tail -1 | cut -d= -f2)"
echo
echo "=== interprete ==="
echo "A (app-bound) rps=${rps_a:-?} | B (store-bound) rps=${rps_b:-?}"
if [[ -n "${rps_a:-}" && -n "${rps_b:-}" ]]; then
  python3 - "${rps_a}" "${rps_b}" <<'PY'
import sys
a, b = float(sys.argv[1]), float(sys.argv[2])
print(f"razao_B_sobre_A={b/a:.2f}" if a > 0 else "razao_B_sobre_A=?")
if a > 0 and b >= a * 0.9:
    print("AVISO: RPS B não caiu claramente — confira DB_SLOTS nas 3 APIs (/escala/status) e rode de novo.")
else:
    print("OK didático: store limitado derrubou o RPS — gargalo na CAMADA DE DADOS.")
PY
fi
echo "Com DB_SLOTS limitado, o RPS tende a cair mesmo com 3 APIs — gargalo na CAMADA DE DADOS."
echo "Próximo passo realista: réplica de leitura (02) ou partição (tutorial-escala-dados)."
echo "Isto NÃO mede CPU máxima do Postgres; simula teto de acesso ao store único."

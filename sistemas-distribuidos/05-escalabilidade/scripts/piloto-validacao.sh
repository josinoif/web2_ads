#!/usr/bin/env bash
# Piloto professor: sobe lab app, mede ganho + teto (+ worker lento); sobe lab dados; imprime Validação local.
# Uso: ./scripts/piloto-validacao.sh
# Aceita Docker ou Podman (compose).
set -euo pipefail
ROOT_MOD="$(cd "$(dirname "$0")/.." && pwd)"
LAB_APP="${ROOT_MOD}/lab-escala-aplicacao"
LAB_DADOS="${ROOT_MOD}/lab-escala-dados"
DATA="$(date -Iseconds)"
SO="$(uname -srm 2>/dev/null || echo unknown)"
WITH_WORKER="${WITH_WORKER:-1}"

detect_compose() {
  local sock="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/podman/podman.sock"
  if docker ps >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    echo "docker compose"
    return 0
  fi
  if [[ -S "${sock}" ]] && DOCKER_HOST="unix://${sock}" DOCKER_CONTEXT=default docker ps >/dev/null 2>&1; then
    export DOCKER_HOST="unix://${sock}" DOCKER_CONTEXT=default
    echo "docker compose"
    return 0
  fi
  if podman ps >/dev/null 2>&1 && podman compose version >/dev/null 2>&1; then
    echo "podman compose"
    return 0
  fi
  return 1
}

if ! COMPOSE="$(detect_compose)"; then
  echo "ERRO: nem Docker nem Podman com compose estão utilizáveis." >&2
  echo "Dicas: inicie Docker Desktop; ou use Podman; ver troubleshooting.md § Docker / daemon." >&2
  exit 1
fi
echo "=== compose provider: ${COMPOSE} ==="

compose() {
  # shellcheck disable=SC2086
  (cd "$1" && shift && ${COMPOSE} "$@")
}

wait_health() {
  local url="$1"
  local i
  for i in $(seq 1 45); do
    curl -sf "${url}" >/dev/null 2>&1 && return 0
    sleep 2
  done
  echo "ERRO: timeout em ${url}" >&2
  return 1
}

echo "=== lab aplicação ==="
compose "${LAB_DADOS}" down -v >/dev/null 2>&1 || true
compose "${LAB_APP}" down -v >/dev/null 2>&1 || true
compose "${LAB_APP}" up -d --build
wait_health "http://localhost:8089/health"

(cd "${LAB_APP}" && ./scripts/comparar-escala.sh) | tee /tmp/sd05-piloto-comparar.txt
GANHO="$(grep -oE 'ganho_aprox=[0-9.]+x' /tmp/sd05-piloto-comparar.txt | tail -1 || true)"
RPS1="$(grep -oE 'rps_1_api=[0-9.]+' /tmp/sd05-piloto-comparar.txt | tail -1 || true)"
RPS3="$(grep -oE 'rps_3_apis=[0-9.]+' /tmp/sd05-piloto-comparar.txt | tail -1 || true)"

WORKER_NOTE="pulado (WITH_WORKER=0)"
if [[ "${WITH_WORKER}" == "1" ]]; then
  echo "=== worker lento (p99) ==="
  (cd "${LAB_APP}" && ./scripts/worker-lento.sh 80)
  (cd "${LAB_APP}" && API=http://localhost:8089 N=60 CONCURRENCY=8 ./scripts/medir-rps.sh) | tee /tmp/sd05-piloto-worker.txt
  (cd "${LAB_APP}" && ./scripts/worker-lento.sh 0)
  WORKER_NOTE="$(grep -oE 'p99=[0-9]+' /tmp/sd05-piloto-worker.txt | tail -1 || echo 'ver /tmp/sd05-piloto-worker.txt')"
fi

(cd "${LAB_APP}" && ./scripts/aproximar-teto.sh) | tee /tmp/sd05-piloto-teto.txt
TETO_LINE="$(grep -E 'A \(app-bound\)|B \(store-bound\)' /tmp/sd05-piloto-teto.txt | tr '\n' ' ; ' || true)"
if [[ -z "${TETO_LINE}" ]]; then
  RA="$(grep -oE 'rps_aprox=[0-9.]+' /tmp/sd05-teto-app.txt 2>/dev/null | tail -1 || echo '?')"
  RB="$(grep -oE 'rps_aprox=[0-9.]+' /tmp/sd05-teto-db.txt 2>/dev/null | tail -1 || echo '?')"
  TETO_LINE="A ${RA} ; B ${RB}"
fi

echo
echo "=== lab dados ==="
compose "${LAB_APP}" down -v >/dev/null 2>&1 || true
compose "${LAB_DADOS}" up -d --build
wait_health "http://localhost:8090/health"

(cd "${LAB_DADOS}" && N=40 ./scripts/medir-writes.sh) | tee /tmp/sd05-piloto-writes.txt
HOT_SHARDS="$(grep -A12 'writes HOT' -A12 /tmp/sd05-piloto-writes.txt | grep -E '"A"|"B"|avisos' | head -10 | tr '\n' ' ' || true)"
SPREAD_NOTE="hot B≈0 / spread A≈B — ver /tmp/sd05-piloto-writes.txt"

compose "${LAB_DADOS}" down -v >/dev/null 2>&1 || true

ENGINE_VER="?"
if [[ "${COMPOSE}" == docker\ compose ]]; then
  ENGINE_VER="$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo '?')"
else
  ENGINE_VER="podman $(podman --version 2>/dev/null | awk '{print $3}')"
fi

echo
echo "========== cole em troubleshooting.md → Validação local =========="
cat <<EOF
| Campo | Valor |
|-------|-------|
| **Data** | ${DATA} |
| **SO / Docker** | ${SO}; compose=\`${COMPOSE}\`; engine=${ENGINE_VER} |
| **comparar-escala (ganho)** | ${GANHO:-?} (${RPS1:-?} → ${RPS3:-?}) |
| **aproximar-teto (A vs B)** | ${TETO_LINE} |
| **medir-writes (shards)** | ${SPREAD_NOTE} |
| **worker lento (p99)** | ${WORKER_NOTE} |
| **Observações** | Piloto via scripts/piloto-validacao.sh |
EOF
echo "=================================================================="

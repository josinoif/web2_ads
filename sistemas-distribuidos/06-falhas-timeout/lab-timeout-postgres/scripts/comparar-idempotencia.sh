#!/usr/bin/env bash
# Compara retry sem chave vs com chave (dois alunos distintos + hold).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TS="$(date +%s)"
HOLD_MS="${HOLD_MS:-2500}"
MAX_TIME="${MAX_TIME:-1}"

echo "======== A) SEM Idempotency-Key ========"
HOLD_MS="${HOLD_MS}" MAX_TIME="${MAX_TIME}" RETRIES=3 \
  "${ROOT}/scripts/matricular-com-retry.sh" SD-101 "aluno-dup-${TS}"

echo
echo "======== B) COM Idempotency-Key ========"
HOLD_MS="${HOLD_MS}" MAX_TIME="${MAX_TIME}" RETRIES=3 IDEM_KEY="idem-${TS}" \
  "${ROOT}/scripts/matricular-idempotente.sh" SD-101 "aluno-safe-${TS}"

"${ROOT}/scripts/provocar-lento.sh" 0 >/dev/null
echo
echo "Feito."
echo "  A) matriculas=1 e auditoria_tentativas>1 (≈ e-mails duplicados; unique salvou o negócio)."
echo "  B) replay com Idempotency-Key; auditoria não sobe no cache."
echo "  Scripts param em 409 e resetam HOLD ao sair."

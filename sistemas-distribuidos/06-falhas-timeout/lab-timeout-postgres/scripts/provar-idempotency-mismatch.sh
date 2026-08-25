#!/usr/bin/env bash
# Demonstra: mesma Idempotency-Key + corpo diferente → HTTP 422 (não é replay).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEY="${IDEM_KEY:-key-mismatch-$(date +%s)}"

echo "=== 1) matrícula com key=${KEY} aluno=aluno-a ==="
IDEM_KEY="${KEY}" "${ROOT}/scripts/matricular.sh" SD-101 aluno-a-mismatch || true

echo
echo "=== 2) mesma key, outro aluno (corpo diferente) — espere 422 ==="
set +e
IDEM_KEY="${KEY}" "${ROOT}/scripts/matricular.sh" SD-101 aluno-b-mismatch
ec=$?
set -e
if [[ "${ec}" -eq 42 ]]; then
  echo "(ok didático: exit 42 = HTTP 422 idempotency mismatch)"
else
  echo "(esperado exit 42; obteve ${ec} — rebuild/down -v se schema antigo)"
fi

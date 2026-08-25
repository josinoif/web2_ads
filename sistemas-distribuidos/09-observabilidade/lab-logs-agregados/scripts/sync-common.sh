#!/usr/bin/env bash
# Mantém common.py idêntico em gateway / analise / store (lab A — logs).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/gateway/common.py"
for d in analise store; do
  cp "${SRC}" "${ROOT}/${d}/common.py"
  echo "synced → ${d}/common.py"
done
echo "Canônico: gateway/common.py — rode após editar logs/propagação no lab A."
echo "Não copie este common.py para o lab B (lá há OTel)."

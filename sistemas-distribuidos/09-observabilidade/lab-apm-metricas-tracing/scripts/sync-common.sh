#!/usr/bin/env bash
# Mantém common.py OTel idêntico em gateway / analise / store (lab B).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="${ROOT}/gateway/common.py"
for d in analise store; do
  cp "${SRC}" "${ROOT}/${d}/common.py"
  echo "synced → ${d}/common.py"
done
echo "Canônico: gateway/common.py — rode após editar OTel/logs no lab B."
echo "Lab A é separado (sem OTel); não misture common.py entre A e B."

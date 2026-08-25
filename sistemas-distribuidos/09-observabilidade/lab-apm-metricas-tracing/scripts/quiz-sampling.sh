#!/usr/bin/env bash
# Demo numérica de amostragem de traces (sem mudar o lab = 100%).
set -euo pipefail

QPS="${1:-1000}"
SAMPLE_PCT="${2:-1}"

python3 - <<PY
qps = float("${QPS}")
pct = float("${SAMPLE_PCT}")
kept = qps * (pct / 100.0)
per_day = kept * 86400
print("=== Demo: amostragem de traces ===")
print(f"Tráfego: {qps:.0f} req/s")
print(f"Sampling: {pct:g}%")
print(f"Traces guardados: ~{kept:.1f}/s  →  ~{per_day:,.0f}/dia")
print()
print("Se sampling=100% com o mesmo QPS:")
print(f"  ~{qps * 86400:,.0f} traces/dia (custo de storage/APM sobe linear)")
print()
print("Trade-off:")
print("  + sampling barato; ainda vê padrões e p95")
print("  - pode perder o request raro do aluno X")
print("Mitigação: logs com trace_id (alta cardinalidade no LOG, não na métrica).")
print()
print("Neste lab usamos ~100% (QPS baixo). Em produção, combine sampling + Loki.")
print("Relacione com decisoes.md cenário 4.")
PY

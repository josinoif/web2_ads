#!/usr/bin/env bash
# Quiz de cardinalidade — responda; rubrica no final (só depois de tentar).
set -euo pipefail

cat <<'EOF'
=== Quiz: cardinalidade ===

Proposta ruim:
  http_requests_total{aluno_id="aluno-01"}   # um label por aluno

1) 10_000 alunos × 5 rotas × 4 status ≈ quantas séries? (ordem de grandeza)
2) O que acontece com memória/CPU do Prometheus?
3) Onde "aluno" já vive neste lab sem explodir métrica?
4) Por que service/route/method/status são labels seguros aqui?

Escreva as respostas. Depois role até a rubrica.
EOF

echo ""
echo "Métricas reais do gateway (baixa cardinalidade):"
curl -s http://127.0.0.1:8110/metrics 2>/dev/null | grep -E '^http_requests_total\{' | head -n 5 || echo "(gateway fora do ar — rode após ./scripts/up.sh)"

cat <<'EOF'

--- Rubrica (abrir só depois) ---
1) ~200_000 séries só nessa métrica (10k×5×4).
2) Cardinalidade alta → mais RAM, scrape lento, queries caras; pode derrubar o Prometheus.
3) Campo no log JSON e/ou atributo de span — não label de métrica.
4) Conjuntos pequenos e estáveis (poucos serviços/rotas/códigos).
Critério pronto: explicar (1)+(3) em uma frase cada.
EOF

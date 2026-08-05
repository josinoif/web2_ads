# Parte 5 — Incidente simulado, postmortem e CI

## Objetivos

- Provocar um incidente reproduzível via `make incident`.
- Observar a cadeia completa: detecção → alerta → diagnóstico → mitigação.
- Escrever postmortem blameless com timeline, causa-raiz, ações.
- Fechar o pipeline CI validando regras, alertas e dashboards.
- Escrever ADRs das decisões principais.

---

## Tarefas

### 5.1 Script de incidente

`scripts/incidente.sh`:

```bash
#!/usr/bin/env bash
# Provoca incidente controlado.
#
# Use um dos cenarios:
#   ./scripts/incidente.sh deploy-bug      # imagem com bug proposital
#   ./scripts/incidente.sh netpol-deny     # NetworkPolicy bloqueia downstream
#   ./scripts/incidente.sh kill-rotas      # Escala rotas para 0

set -euo pipefail

case "${1:-deploy-bug}" in
  deploy-bug)
    kubectl -n logisgo set image deployment/pedidos pedidos=logisgo/pedidos:bug-0.3.0
    echo "Deploy com bug aplicado."
    ;;
  netpol-deny)
    kubectl -n logisgo apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: bloqueia-rotas
spec:
  podSelector:
    matchLabels:
      app: pedidos
  policyTypes: [Egress]
  egress: []
EOF
    echo "NetworkPolicy aplicada: pedidos nao chega em nenhum egress."
    ;;
  kill-rotas)
    kubectl -n logisgo scale deployment/rotas --replicas=0
    echo "Rotas com 0 replicas."
    ;;
  *)
    echo "Cenario desconhecido: $1"
    exit 2
    ;;
esac
```

Ação simétrica `scripts/recuperacao.sh`:

```bash
#!/usr/bin/env bash
# Reverte o cenario de incidente.
set -euo pipefail

case "${1:-deploy-bug}" in
  deploy-bug)
    kubectl -n logisgo set image deployment/pedidos pedidos=logisgo/pedidos:0.2.0
    ;;
  netpol-deny)
    kubectl -n logisgo delete networkpolicy bloqueia-rotas --ignore-not-found
    ;;
  kill-rotas)
    kubectl -n logisgo scale deployment/rotas --replicas=2
    ;;
esac
```

Adicione ao `Makefile`:

```makefile
incident:
	bash scripts/incidente.sh $(scenario)

recover:
	bash scripts/recuperacao.sh $(scenario)
```

Uso:

```bash
make incident scenario=netpol-deny
```

Para o cenário `deploy-bug`, gere uma imagem `logisgo/pedidos:bug-0.3.0` cujo handler de `POST /orders` lança exceção em 40% dos casos (edite uma cópia da app e importe).

### 5.2 Exercício: viver o incidente

Antes de rodar `make incident`:

1. Certifique-se que sua stack está estável (Watchdog firing, sem outros alertas).
2. Mantenha `scripts/load.sh` rodando em terminal separado.
3. Abra três telas: Grafana (dashboard RED), Alertmanager UI, Loki Explore.

Execute:

```bash
make incident scenario=netpol-deny
# comece a contar o tempo!
```

Observe:

- **MTTD**: quanto tempo até `PedidosSLOBurnRateFast` disparar? (Esperado: 2-5 min.)
- **Detecção via métricas**: taxa de erro sobe primeiro no Grafana.
- **Diagnóstico via traces**: entre no Tempo; os traces de `POST /orders` agora terminam com erro logo após o span `pedidos`, sem conseguir alcançar `rotas`.
- **Correlação com logs**: Loki mostra `ECONNREFUSED` ou timeouts ao tentar chamar `rotas`.

Aplicar mitigação:

```bash
make recover scenario=netpol-deny
```

Confirme volta do verde no dashboard; alerta resolve em ~5 min.

### 5.3 Postmortem

Escreva `docs/postmortem-simulado.md` usando o template do Bloco 4. Deve conter, no mínimo:

- Timeline real (horários anotados à mão durante o game day).
- MTTD e MTTR aferidos.
- Causa-raiz técnica + sistêmica.
- 3 ações, com responsável e prazo, **pelo menos 1 já implementada** no entregável.

### 5.4 ADRs

Crie `docs/adr/001-cardinalidade.md`:

```markdown
# ADR 001 — Regras de cardinalidade em labels de métricas

## Status
Aceito em 2026-04-21.

## Contexto
Sem regras, métricas têm explosão de cardinalidade (ex.: `order_id` como label).

## Decisão
- Labels de métrica: apenas valores de **conjunto fechado**.
- IDs livres (user_id, order_id, trace_id) ficam em **logs estruturados**.
- Toda nova métrica passa pelo `metrics_audit.py` no CI.

## Consequências
- Prometheus permanece saudável.
- Para investigar por ID, usamos Loki/Tempo, não métrica.
```

Idem para:
- `docs/adr/002-slo-burn-rate.md` — por que multi-window burn-rate em vez de thresholds estáticos.
- `docs/adr/003-stack-grafana.md` — por que stack Grafana (Loki, Tempo) em vez de Elastic ou Jaeger.

### 5.5 Pipeline CI

`.github/workflows/observability.yml`:

```yaml
name: observability-ci

on:
  pull_request:
    paths:
      - 'k8s/prometheusrules/**'
      - 'grafana/dashboards/**'
      - 'tests/**'
      - 'app/**'

jobs:
  validar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Dependencies
        run: pip install pyyaml

      - name: promtool
        run: |
          PROM_VER=2.54.1
          curl -sL https://github.com/prometheus/prometheus/releases/download/v${PROM_VER}/prometheus-${PROM_VER}.linux-amd64.tar.gz | tar xz
          sudo install prometheus-${PROM_VER}.linux-amd64/promtool /usr/local/bin/

      - name: Lint regras
        run: promtool check rules k8s/prometheusrules/*.yaml

      - name: Teste regras
        run: promtool test rules tests/rules_test.yaml

      - name: Sanity check
        run: python devops/08-observabilidade/bloco-4/alerts_sanity.py k8s/prometheusrules/*.yaml

      - name: Valida dashboards JSON
        run: |
          for f in grafana/dashboards/*.json; do
            python -m json.tool "$f" > /dev/null
          done
```

`tests/rules_test.yaml` — crie ao menos 3 casos:

```yaml
rule_files:
  - ../k8s/prometheusrules/pedidos-sli.yaml
  - ../k8s/prometheusrules/pedidos-alerts.yaml

evaluation_interval: 30s

tests:
  - name: dispara burn rate rapido quando taxa de erro ~15%
    interval: 30s
    input_series:
      - series: 'http_requests_total{service="pedidos",route="/orders",method="POST",status="200"}'
        values: '0 500 1000 1500 2000 2500 3000 3500 4000 4500 5000 5500'
      - series: 'http_requests_total{service="pedidos",route="/orders",method="POST",status="500"}'
        values: '0 100 200 300 400 500 600 700 800 900 1000 1100'
      - series: 'http_request_duration_seconds_bucket{service="pedidos",route="/orders",method="POST",le="0.5"}'
        values: '0 400 800 1200 1600 2000 2400 2800 3200 3600 4000 4400'
    alert_rule_test:
      - eval_time: 10m
        alertname: PedidosSLOBurnRateFast
        exp_alerts:
          - exp_labels:
              severity: critical
              slo: pedidos-criar
            exp_annotations:
              summary: "SLO pedidos-criar: queima 14.4x (5m e 1h)"
              description: "Taxa de erro + latência fora do SLO há 5m e 1h. Budget acaba em horas."
              runbook_url: "https://runbooks.logisgo/pedidos-slo-burn-fast"

  - name: watchdog sempre firing
    interval: 30s
    alert_rule_test:
      - eval_time: 1m
        alertname: Watchdog
        exp_alerts:
          - exp_labels:
              severity: info
            exp_annotations:
              summary: "Watchdog always firing"
              description: "Prova que pipeline de alertas está viva."
              runbook_url: "https://runbooks.logisgo/watchdog"

  - name: zero pedidos por 10 min dispara alerta
    interval: 1m
    input_series:
      - series: 'orders_created_total{tenant_tier="free",channel="api"}'
        values: '100x15'
    alert_rule_test:
      - eval_time: 20m
        alertname: PedidosNenhumCriado10m
        exp_alerts:
          - exp_labels:
              severity: critical
              domain: business
            exp_annotations:
              summary: "Nenhum pedido criado nos últimos 10 minutos"
              description: "Alarme de negócio. Checar dependências (DB, fila)."
              runbook_url: "https://runbooks.logisgo/zero-orders"
```

### 5.6 README final

Em `README.md` do repositório, consolide:

- Diagrama da arquitetura.
- `make up`, `make apply`, `make incident`, `make recover`, `make test-rules`.
- Credenciais do Grafana local.
- Tour guiado: "para ver X, vá em Y".
- Lista de runbooks com links.
- Tabela: SLO → alerta → runbook.
- Seção de **limitações conhecidas** (stack single-node, retenção curta, sem backup etcd, etc.).

---

## Validação da parte 5

- [ ] `make incident scenario=netpol-deny` e 5 min depois o alerta `PedidosSLOBurnRateFast` está firing.
- [ ] Postmortem existe, contém timeline, causa-raiz técnica e sistêmica, 3 ações.
- [ ] 3 ADRs escritos no formato Michael Nygard.
- [ ] Pipeline CI verde em PR limpo.
- [ ] `promtool test rules` passa.
- [ ] README final consolida tudo.

---

## Entregáveis

- `scripts/incidente.sh`, `scripts/recuperacao.sh`.
- `docs/postmortem-simulado.md`.
- `docs/adr/001-*.md`, `docs/adr/002-*.md`, `docs/adr/003-*.md`.
- `.github/workflows/observability.yml`.
- `tests/rules_test.yaml` com ≥ 3 testes.
- README final polido.

---

## Aprendizado consolidado

Ao final da parte 5, reflita e escreva em `docs/aprendizados.md`:

- O que foi mais **fácil** de colocar em pé? Por quê?
- O que foi mais **difícil**? O que ajudaria da próxima vez?
- Qual mudança você implementaria **antes** de rodar o próximo incidente simulado?
- Se a LogisGo tivesse 10× mais tráfego, qual a primeira parte desta stack que quebraria?

Essa é a pedra de toque do módulo — **observabilidade é prática contínua, não entrega única**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 4 — SLOs, alertas burn-rate e runbooks](parte-4-slos-e-alertas.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Entrega avaliativa — Módulo 8 (Observabilidade)](../entrega-avaliativa.md) |

<!-- nav:end -->

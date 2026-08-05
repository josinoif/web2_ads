# Parte 4 — SLOs, alertas burn-rate e runbooks

## Objetivos

- Definir 2 SLOs formais para a LogisGo (criar pedido, consultar pedido).
- Escrever recording rules para SLI.
- Escrever alertas SLO-based multi-window / multi-burn-rate.
- Configurar Alertmanager com rotas, agrupamento, inibição e Watchdog.
- Escrever runbooks para os alertas críticos.

---

## Tarefas

### 4.1 Definir SLOs (`docs/slos.md`)

Exemplo:

```markdown
# SLOs da LogisGo

## Jornada 1 — Criar pedido

- **SLI**: razão de `POST /orders` que retorna 2xx E dura < 500ms.
- **SLO**: 99% em 28 dias.
- **Responsável**: squad Orders.
- **Error budget**: 1% → ~120 minutos de indisponibilidade no mês.
- **Política**: se budget queima 50% em < 7 dias, trigger freeze parcial.

## Jornada 2 — Consultar pedido

- **SLI**: razão de `GET /orders/{id}` que retorna 2xx em < 200ms.
- **SLO**: 99.5% em 28 dias.
- **Responsável**: squad Orders.
- **Error budget**: 0.5%.
```

### 4.2 Recording rules

`k8s/prometheusrules/pedidos-sli.yaml`:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: pedidos-sli
  namespace: monitoring
  labels:
    release: monitoring
spec:
  groups:
    - name: pedidos.sli.criar_pedido
      interval: 30s
      rules:
        - record: sli:pedidos_criar:good:5m
          expr: |
            sum(rate(http_request_duration_seconds_bucket{service="pedidos", route="/orders", method="POST", le="0.5"}[5m]))
            -
            sum(rate(http_requests_total{service="pedidos", route="/orders", method="POST", status=~"5.."}[5m]))
        - record: sli:pedidos_criar:valid:5m
          expr: sum(rate(http_requests_total{service="pedidos", route="/orders", method="POST"}[5m]))

        - record: sli:pedidos_criar:ratio:5m
          expr: sli:pedidos_criar:good:5m / sli:pedidos_criar:valid:5m

        # Janelas adicionais
        - record: sli:pedidos_criar:ratio:30m
          expr: |
            (sum(rate(http_request_duration_seconds_bucket{service="pedidos", route="/orders", method="POST", le="0.5"}[30m]))
             - sum(rate(http_requests_total{service="pedidos", route="/orders", method="POST", status=~"5.."}[30m])))
            /
            sum(rate(http_requests_total{service="pedidos", route="/orders", method="POST"}[30m]))

        - record: sli:pedidos_criar:ratio:1h
          expr: |
            (sum(rate(http_request_duration_seconds_bucket{service="pedidos", route="/orders", method="POST", le="0.5"}[1h]))
             - sum(rate(http_requests_total{service="pedidos", route="/orders", method="POST", status=~"5.."}[1h])))
            /
            sum(rate(http_requests_total{service="pedidos", route="/orders", method="POST"}[1h]))

        - record: sli:pedidos_criar:ratio:6h
          expr: |
            (sum(rate(http_request_duration_seconds_bucket{service="pedidos", route="/orders", method="POST", le="0.5"}[6h]))
             - sum(rate(http_requests_total{service="pedidos", route="/orders", method="POST", status=~"5.."}[6h])))
            /
            sum(rate(http_requests_total{service="pedidos", route="/orders", method="POST"}[6h]))
```

### 4.3 Alertas burn-rate

`k8s/prometheusrules/pedidos-alerts.yaml`:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: pedidos-alerts
  namespace: monitoring
  labels:
    release: monitoring
spec:
  groups:
    - name: pedidos.slo.alerts
      interval: 30s
      rules:
        - alert: PedidosSLOBurnRateFast
          expr: |
            (1 - sli:pedidos_criar:ratio:5m)  > 14.4 * (1 - 0.99)
            and
            (1 - sli:pedidos_criar:ratio:1h)  > 14.4 * (1 - 0.99)
          for: 2m
          labels:
            severity: critical
            slo: pedidos-criar
          annotations:
            summary: "SLO pedidos-criar: queima 14.4x (5m e 1h)"
            description: "Taxa de erro + latência fora do SLO há 5m e 1h. Budget acaba em horas."
            runbook_url: "https://runbooks.logisgo/pedidos-slo-burn-fast"

        - alert: PedidosSLOBurnRateSlow
          expr: |
            (1 - sli:pedidos_criar:ratio:30m) > 3 * (1 - 0.99)
            and
            (1 - sli:pedidos_criar:ratio:6h)  > 3 * (1 - 0.99)
          for: 15m
          labels:
            severity: warning
            slo: pedidos-criar
          annotations:
            summary: "SLO pedidos-criar: queima 3x (30m e 6h)"
            description: "Queima prolongada. Abrir investigação."
            runbook_url: "https://runbooks.logisgo/pedidos-slo-burn-slow"

    - name: pedidos.business
      rules:
        - alert: PedidosNenhumCriado10m
          expr: rate(orders_created_total[10m]) == 0
          for: 10m
          labels:
            severity: critical
            domain: business
          annotations:
            summary: "Nenhum pedido criado nos últimos 10 minutos"
            description: "Alarme de negócio. Checar dependências (DB, fila)."
            runbook_url: "https://runbooks.logisgo/zero-orders"

    - name: infra.watchdog
      rules:
        - alert: Watchdog
          expr: vector(1)
          labels:
            severity: info
          annotations:
            summary: "Watchdog always firing"
            description: "Prova que pipeline de alertas está viva."
            runbook_url: "https://runbooks.logisgo/watchdog"
```

### 4.4 Configurar Alertmanager

Com o chart kube-prometheus-stack, customize em `values-kps.yaml`:

```yaml
alertmanager:
  config:
    global:
      resolve_timeout: 5m
    route:
      group_by: ['service', 'severity']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 4h
      receiver: default
      routes:
        - matchers:
            - alertname="Watchdog"
          receiver: watchdog
          repeat_interval: 5m
          group_wait: 0s
          continue: false
        - matchers:
            - severity="critical"
          receiver: critical
          continue: true
        - matchers:
            - severity="warning"
          receiver: warnings
    inhibit_rules:
      - source_matchers:
          - severity="critical"
        target_matchers:
          - severity="warning"
        equal: ['service']
    receivers:
      - name: default
        webhook_configs:
          - url: http://incident-webhook.monitoring.svc.cluster.local/alerts
      - name: critical
        webhook_configs:
          - url: http://incident-webhook.monitoring.svc.cluster.local/critical
      - name: warnings
        webhook_configs:
          - url: http://incident-webhook.monitoring.svc.cluster.local/warnings
      - name: watchdog
        webhook_configs:
          - url: http://incident-webhook.monitoring.svc.cluster.local/watchdog
```

Implemente um **webhook receiver** local simples para receber tudo:

`incident-webhook/main.py`:

```python
from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/{route:path}")
async def receber(route: str, req: Request):
    corpo = await req.json()
    print(f"[{route}] {json.dumps(corpo)}")
    return {"ok": True}
```

Containerize e implante como `incident-webhook` em `monitoring`. Útil para game days.

Para integração real (Slack/Discord) em bônus: altere o receiver apropriado.

### 4.5 Runbooks

Crie `docs/runbooks/pedidos-slo-burn-fast.md` e `docs/runbooks/zero-orders.md`, seguindo o template do Bloco 4. Link em cada alerta via `runbook_url`.

### 4.6 Sanity check

```bash
python devops/08-observabilidade/bloco-4/alerts_sanity.py k8s/prometheusrules/*.yaml
```

Corrija o que aparecer.

---

## Validação da parte 4

- [ ] `kubectl -n monitoring get prometheusrule` lista suas regras.
- [ ] UI Prometheus em `/rules` mostra todas verdes (sem erro de expressão).
- [ ] `Watchdog` aparece em `firing` no Alertmanager.
- [ ] `alerts_sanity.py` retorna 0 achados.
- [ ] `docs/slos.md` existe com 2 SLOs formais.
- [ ] Runbooks existem, contêm passos de diagnóstico e ações.
- [ ] Receiver `incident-webhook` recebe o Watchdog a cada ~5 min.

---

## Entregáveis

- `k8s/prometheusrules/pedidos-sli.yaml`
- `k8s/prometheusrules/pedidos-alerts.yaml`
- `values-kps.yaml` atualizado com Alertmanager config.
- `docs/slos.md`
- `docs/runbooks/pedidos-slo-burn-fast.md`
- `docs/runbooks/zero-orders.md`
- Código do `incident-webhook` (mini FastAPI) + Deployment + Service.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Traces distribuídos com OpenTelemetry + Tempo](parte-3-traces-otel.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Parte 5 — Incidente simulado, postmortem e CI](parte-5-incidente-e-postmortem.md) |

<!-- nav:end -->

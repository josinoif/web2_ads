# Parte 3 — Traces distribuídos com OpenTelemetry + Tempo

## Objetivos

- Adicionar um segundo serviço (`rotas`) para demonstrar traces que atravessam serviços.
- Instrumentar ambos com OpenTelemetry (métricas já existentes + traces novos).
- Subir Tempo + OpenTelemetry Collector.
- Configurar propagação W3C Trace Context entre `pedidos` e `rotas`.
- Correlacionar logs ↔ traces no Grafana.

---

## Tarefas

### 3.1 Criar serviço `rotas`

`app/src/rotas.py` (novo, serviço separado):

```python
from __future__ import annotations
import random
import time
from fastapi import FastAPI

from app.src.obs.logging import log  # reusar config com SERVICE_NAME=rotas via env
from app.src.obs.metrics import middleware_metrics, metrics_endpoint

app = FastAPI(title="rotas")
app.middleware("http")(middleware_metrics)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return metrics_endpoint()


@app.post("/routes/optimize")
def otimizar(payload: dict):
    log.info("otimizando rota", order_id=payload.get("order_id"))
    time.sleep(random.uniform(0.05, 0.25))
    if random.random() < 0.02:
        raise RuntimeError("solver estourou tempo")
    return {"eta_minutes": random.randint(15, 45), "distance_km": round(random.uniform(2, 15), 1)}
```

Crie um Dockerfile e manifestos similares ao de `pedidos`, mas com `SERVICE_NAME=rotas`.

### 3.2 Instrumentar OpenTelemetry

Adicione ao `app/requirements.txt`:

```
opentelemetry-api==1.28.0
opentelemetry-sdk==1.28.0
opentelemetry-instrumentation-fastapi==0.49b0
opentelemetry-instrumentation-httpx==0.49b0
opentelemetry-instrumentation-logging==0.49b0
opentelemetry-exporter-otlp-proto-grpc==1.28.0
httpx==0.27.2
```

Crie `app/src/obs/tracing.py` (código completo na seção 3.3.3 do Bloco 3).

No `main.py` do `pedidos`, adicione:

```python
from app.src.obs.tracing import configurar_tracing
import httpx
import os

configurar_tracing(app)
ROTAS_URL = os.environ.get("ROTAS_URL", "http://rotas.logisgo.svc.cluster.local/routes/optimize")

@app.post("/orders")
async def criar(payload: dict):
    log.info("criando pedido", tier=payload.get("tier", "free"))
    time.sleep(random.uniform(0.02, 0.10))
    # Chamada downstream - traceparent e injetado automaticamente
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(ROTAS_URL, json={"order_id": f"o-{random.randint(1000,9999)}"})
        route = resp.json() if resp.status_code == 200 else {}
    if random.random() < 0.03:
        log.error("erro interno simulado", source="payment-gateway")
        raise HTTPException(status_code=500, detail="erro interno simulado")
    ORDERS_CREATED.labels(tenant_tier=payload.get("tier","free"), channel="api").inc()
    log.info("pedido criado", route=route)
    return {"id": f"o-{random.randint(1000,9999)}", "route": route}
```

No `rotas.py`, também chame `configurar_tracing(app)` — ambos os serviços precisam estar instrumentados para spans encadearem.

### 3.3 Deploy do OpenTelemetry Collector

`k8s/stack/otel-collector-values.yaml`:

```yaml
mode: deployment
replicaCount: 1
image:
  repository: otel/opentelemetry-collector-contrib
config:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318
  processors:
    batch: {}
    memory_limiter:
      limit_mib: 400
      check_interval: 1s
  exporters:
    otlp/tempo:
      endpoint: tempo.monitoring.svc.cluster.local:4317
      tls:
        insecure: true
  service:
    pipelines:
      traces:
        receivers: [otlp]
        processors: [memory_limiter, batch]
        exporters: [otlp/tempo]
ports:
  otlp:
    enabled: true
    containerPort: 4317
    servicePort: 4317
  otlp-http:
    enabled: true
    containerPort: 4318
    servicePort: 4318
```

Adicione ao `Makefile`:

```makefile
tempo:
	helm upgrade --install tempo grafana/tempo \
	  --namespace monitoring

otel:
	helm upgrade --install otel-collector open-telemetry/opentelemetry-collector \
	  --namespace monitoring \
	  --values k8s/stack/otel-collector-values.yaml

traces: tempo otel
```

Adicione `helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts` em `stack`.

### 3.4 Injetar variável `OTEL_EXPORTER_OTLP_ENDPOINT` nos Deployments

Edite os manifestos de `pedidos` e `rotas`:

```yaml
env:
  - name: SERVICE_NAME
    value: "pedidos"    # em rotas, "rotas"
  - name: APP_ENV
    value: "dev"
  - name: APP_VERSION
    value: "0.2.0"
  - name: OTEL_EXPORTER_OTLP_ENDPOINT
    value: "http://otel-collector.monitoring.svc.cluster.local:4317"
  - name: OTEL_TRACES_SAMPLER
    value: "parentbased_traceidratio"
  - name: OTEL_TRACES_SAMPLER_ARG
    value: "1.0"   # 100% em dev; reduzir em prod
  - name: ROTAS_URL
    value: "http://rotas.logisgo.svc.cluster.local/routes/optimize"
```

### 3.5 Adicionar Tempo como datasource

ConfigMap similar ao de Loki:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-ds-tempo
  namespace: monitoring
  labels:
    grafana_datasource: "1"
data:
  tempo.yaml: |
    apiVersion: 1
    datasources:
      - name: Tempo
        type: tempo
        access: proxy
        url: http://tempo.monitoring.svc.cluster.local:3100
        jsonData:
          tracesToLogsV2:
            datasourceUid: loki
            spanStartTimeShift: "-1m"
            spanEndTimeShift: "1m"
            tags:
              - key: service.name
                value: service
            filterByTraceID: true
          tracesToMetrics:
            datasourceUid: prometheus
          serviceMap:
            datasourceUid: prometheus
```

### 3.6 Testar correlação

Com carga rodando, em Grafana → Explore → Tempo:

```
{ service.name = "pedidos" }
{ service.name = "pedidos" && duration > 200ms }
```

Selecione um trace. Confirme:
- Span raiz em `pedidos` (`POST /orders`).
- Span filho em `rotas` (`POST /routes/optimize`), mesma `trace_id`.
- Link "Logs for this span" leva para Loki com os logs daquele `trace_id`.

---

## Validação da parte 3

- [ ] Cluster tem pods `rotas`, `pedidos`, `tempo`, `otel-collector`.
- [ ] Traces do `pedidos` aparecem no Tempo após carga.
- [ ] Traces encadeiam `pedidos → rotas` (2 spans visíveis).
- [ ] Logs em Loki incluem `trace_id` e `span_id`.
- [ ] No Grafana, a partir de um trace consegue-se pular para os logs correspondentes.

---

## Entregáveis

- `app/src/obs/tracing.py` + `app/src/rotas.py` + Dockerfile do `rotas`.
- Manifestos `k8s/manifests/rotas.yaml`.
- `k8s/stack/otel-collector-values.yaml`.
- ConfigMap do datasource Tempo.
- Screenshot (em `docs/traces-exemplo.md`) de um trace com spans em 2 serviços.
- Atualização em `docs/queries-uteis.md` com 3+ exemplos de TraceQL.

---

## Pontos de atenção

- Se traces não aparecem, verifique logs do `otel-collector` (erros de conexão com Tempo) e variável `OTEL_EXPORTER_OTLP_ENDPOINT` nas apps.
- `LoggingInstrumentor` precisa rodar **antes** do `structlog.configure()` final, ou os logs sairão sem `trace_id`.
- Amostragem 100% em produção real explode custo. Reduza gradualmente; mantenha *tail sampling* para erros/latência alta.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — Logs estruturados com Loki](parte-2-logs-estruturados.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Parte 4 — SLOs, alertas burn-rate e runbooks](parte-4-slos-e-alertas.md) |

<!-- nav:end -->

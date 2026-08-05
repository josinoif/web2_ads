# Parte 1 — Stack observabilidade + métricas RED

## Objetivos

- Provisionar cluster local `k3d` e instalar `kube-prometheus-stack` via Helm.
- Instrumentar um serviço FastAPI `pedidos` com `prometheus_client` (Golden Signals / RED).
- Expor `/metrics` via `Service` + `ServiceMonitor` para coleta automática.
- Ter um dashboard Grafana provisionado como código exibindo RED.

---

## Tarefas

### 1.1 Repositório e cluster local

Crie a árvore inicial:

```
logisgo-obs/
├── Makefile
├── README.md
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── main.py
│       └── obs/
│           └── metrics.py
├── k8s/
│   ├── manifests/
│   ├── prometheusrules/
│   └── stack/
├── grafana/
│   └── dashboards/
└── docs/
```

Script `scripts/k3d-up.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

CLUSTER=obs-lab
k3d cluster delete "$CLUSTER" 2>/dev/null || true
k3d cluster create "$CLUSTER" \
  --agents 1 \
  --port "80:80@loadbalancer" \
  --port "3000:30300@agent:0"

kubectl cluster-info
kubectl create namespace logisgo
kubectl create namespace monitoring
```

`Makefile` inicial:

```makefile
.PHONY: up down stack app apply

up:
	bash scripts/k3d-up.sh
	$(MAKE) stack

down:
	k3d cluster delete obs-lab

stack:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo add grafana https://grafana.github.io/helm-charts
	helm repo update
	helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
	  --namespace monitoring \
	  --values k8s/stack/values-kps.yaml \
	  --wait

apply:
	kubectl apply -n logisgo -f k8s/manifests/
	kubectl apply -n monitoring -f k8s/prometheusrules/ || true
```

### 1.2 Valores do kube-prometheus-stack

`k8s/stack/values-kps.yaml`:

```yaml
grafana:
  adminPassword: admin
  service:
    type: NodePort
    nodePort: 30300
  sidecar:
    dashboards:
      enabled: true
      searchNamespace: ALL
      label: grafana_dashboard
      labelValue: "1"
  defaultDashboardsEnabled: true

prometheus:
  prometheusSpec:
    retention: 7d
    serviceMonitorSelector:
      matchLabels:
        release: monitoring
    serviceMonitorNamespaceSelector: {}

alertmanager:
  enabled: true
  alertmanagerSpec:
    replicas: 1
```

Aplicar:

```bash
make up
```

Valide: `kubectl -n monitoring get pods` — todos `Running`. Grafana em `http://localhost:3000` (admin/admin).

### 1.3 App `pedidos` instrumentada

`app/requirements.txt`:

```
fastapi==0.115.4
uvicorn[standard]==0.32.0
prometheus-client==0.21.0
```

`app/src/obs/metrics.py`:

```python
from __future__ import annotations
import time
from fastapi import Request
from prometheus_client import Counter, Histogram, REGISTRY, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

REQUESTS = Counter(
    "http_requests_total",
    "Total de requisicoes HTTP.",
    ["service", "route", "method", "status"],
)

DURATION = Histogram(
    "http_request_duration_seconds",
    "Latencia das requisicoes HTTP em segundos.",
    ["service", "route", "method"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

ORDERS_CREATED = Counter(
    "orders_created_total",
    "Pedidos criados com sucesso.",
    ["tenant_tier", "channel"],
)

SERVICE = "pedidos"


async def middleware_metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    route = request.scope.get("route").path if request.scope.get("route") else request.url.path
    REQUESTS.labels(service=SERVICE, route=route, method=request.method, status=str(response.status_code)).inc()
    DURATION.labels(service=SERVICE, route=route, method=request.method).observe(elapsed)
    return response


def metrics_endpoint() -> Response:
    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
```

`app/src/main.py`:

```python
from __future__ import annotations
import random
import time
from fastapi import FastAPI, HTTPException
from app.src.obs.metrics import (
    middleware_metrics,
    metrics_endpoint,
    ORDERS_CREATED,
)

app = FastAPI(title="pedidos")
app.middleware("http")(middleware_metrics)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return metrics_endpoint()


@app.post("/orders")
def criar(payload: dict):
    # Simula latencia variavel
    time.sleep(random.uniform(0.02, 0.30))
    if random.random() < 0.03:
        raise HTTPException(status_code=500, detail="erro interno simulado")
    ORDERS_CREATED.labels(tenant_tier=payload.get("tier", "free"), channel="api").inc()
    return {"id": f"o-{random.randint(1000,9999)}", "status": "created"}


@app.get("/orders/{oid}")
def detalhe(oid: str):
    time.sleep(random.uniform(0.005, 0.05))
    return {"id": oid, "status": "in_transit"}
```

`app/Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /srv/app/src/
EXPOSE 8000
CMD ["uvicorn", "app.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build e importe no k3d:

```bash
docker build -t logisgo/pedidos:0.1.0 app/
k3d image import logisgo/pedidos:0.1.0 -c obs-lab
```

### 1.4 Manifestos K8s

`k8s/manifests/pedidos.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pedidos
  namespace: logisgo
  labels:
    app: pedidos
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pedidos
  template:
    metadata:
      labels:
        app: pedidos
    spec:
      containers:
        - name: pedidos
          image: logisgo/pedidos:0.1.0
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 8000
          readinessProbe:
            httpGet:
              path: /healthz
              port: http
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /healthz
              port: http
            periodSeconds: 15
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 300m
              memory: 256Mi
---
apiVersion: v1
kind: Service
metadata:
  name: pedidos
  namespace: logisgo
  labels:
    app: pedidos
spec:
  selector:
    app: pedidos
  ports:
    - name: http
      port: 80
      targetPort: http
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: pedidos
  namespace: monitoring
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app: pedidos
  namespaceSelector:
    matchNames:
      - logisgo
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
```

Aplicar: `make apply`.

Valide: Prometheus UI → `/targets` — `pedidos` deve estar `UP`.

### 1.5 Carga sintética e dashboard

`scripts/load.sh`:

```bash
#!/usr/bin/env bash
# Gera carga sintetica para popular metricas
while true; do
  curl -s http://localhost/orders -X POST -d '{"tier":"pro"}' -H 'Content-Type: application/json' > /dev/null
  curl -s http://localhost/orders/abc > /dev/null
  sleep 0.1
done
```

Rode em terminal separado. Exponha a app no Ingress (reuse do Módulo 7) ou `kubectl port-forward svc/pedidos 8080:80 -n logisgo`.

### 1.6 Dashboard Grafana RED

Crie `grafana/dashboards/pedidos-red.json` usando o construtor do Grafana (import manual funciona; exporte o JSON) OU use como base o dashboard [Microservices RED](https://grafana.com/grafana/dashboards/14538). Ajuste as queries para:

- **Rate**: `sum by (route) (rate(http_requests_total{service="pedidos"}[5m]))`
- **Errors**: `sum by (route) (rate(http_requests_total{service="pedidos", status=~"5.."}[5m])) / sum by (route) (rate(http_requests_total{service="pedidos"}[5m]))`
- **p95**: `histogram_quantile(0.95, sum by (le, route) (rate(http_request_duration_seconds_bucket{service="pedidos"}[5m])))`

Versione como ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dash-pedidos-red
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  pedidos-red.json: |
    <cole aqui o JSON exportado>
```

---

## Validação da parte 1

Execute e checque:

```bash
make up
make apply
bash scripts/load.sh &
python devops/08-observabilidade/bloco-2/metrics_audit.py --url http://localhost:8080/metrics
```

- [ ] `kubectl -n monitoring get pods` tudo `Running`.
- [ ] `http://localhost:3000` abre Grafana (admin/admin).
- [ ] Prometheus UI mostra `pedidos` como target `UP`.
- [ ] Dashboard "RED - pedidos" mostra latência/taxa/erro em tempo real.
- [ ] `metrics_audit.py` reporta cardinalidade saudável (cada métrica com < 100 séries).

---

## Entregáveis

- `app/` com código instrumentado.
- `k8s/manifests/pedidos.yaml`, `k8s/stack/values-kps.yaml`.
- `grafana/dashboards/pedidos-red.json` + ConfigMap.
- `Makefile` com `up`, `down`, `stack`, `apply`.
- `docs/arquitetura.md` — diagrama inicial (use a do README do Módulo 8 como ponto de partida).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Progressivos — Módulo 8 (Observabilidade)](README.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Parte 2 — Logs estruturados com Loki](parte-2-logs-estruturados.md) |

<!-- nav:end -->

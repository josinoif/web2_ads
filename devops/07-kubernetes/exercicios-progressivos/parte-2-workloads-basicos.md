# Parte 2 — Workloads básicos da StreamCast

**Tempo estimado:** 120 min
**Pré-requisitos:** Parte 1 concluída.

---

## Contexto

Demonstrado que o cluster sobe e recebe manifestos, é hora do **primeiro serviço real** da StreamCast. Você escolherá **`auth`** (Python + FastAPI) como vanguarda, com suas dependências: **Postgres** (StatefulSet) e **Redis** (Deployment).

---

## Objetivos

- Construir imagem real do `auth` a partir do código Python.
- Criar manifests K8s do `auth`, Postgres e Redis.
- Subir tudo em `streamcast-dev`, validar `/health/ready`.
- Produzir baseline "pré-endurecimento" — propositalmente sem probes perfeitas, sem limits, sem RBAC — para a Parte 3 corrigir.

---

## Tarefas

### 2.1 App `auth` em Python

Crie `app/auth/` com:

```
app/auth/
├── Dockerfile
├── pyproject.toml
├── src/
│   └── main.py
└── tests/
    └── test_health.py
```

**`pyproject.toml`:**

```toml
[project]
name = "streamcast-auth"
version = "1.0.0"
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.29",
  "psycopg[binary]>=3.2",
  "redis>=5.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "httpx>=0.27"]
```

**`src/main.py`:** reuse o código do Bloco 2 (importa `psycopg`, `redis`, endpoints `/health/live` e `/health/ready`).

**`tests/test_health.py`:**

```python
from fastapi.testclient import TestClient
import os

def test_live_sem_chave(monkeypatch):
    # Sem JWT_SIGNING_KEY, main deve levantar em startup.
    monkeypatch.delenv("JWT_SIGNING_KEY", raising=False)
    # Aqui apenas validamos import; runtime será coberto em integração.
    import importlib
    import src.main as m
    importlib.reload(m)
```

Rode:

```bash
cd app/auth
pip install -e .[dev]
pytest
```

**`Dockerfile`:**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir "fastapi>=0.110" "uvicorn[standard]>=0.29" \
    "psycopg[binary]>=3.2" "redis>=5.0"
COPY src/ ./src/
EXPOSE 8000
USER 1000:1000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build e import no k3d:

```bash
docker build -t streamcast/auth:1.0 app/auth
k3d image import streamcast/auth:1.0 -c streamcast
```

### 2.2 Namespace e manifests

`k8s/streamcast-dev/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: streamcast-dev
  labels:
    env: dev
```

`k8s/streamcast-dev/redis.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: redis, namespace: streamcast-dev }
spec:
  replicas: 1
  selector:
    matchLabels: { app: redis }
  template:
    metadata: { labels: { app: redis } }
    spec:
      containers:
        - name: redis
          image: redis:7.2-alpine
          ports: [{ containerPort: 6379 }]
---
apiVersion: v1
kind: Service
metadata: { name: redis, namespace: streamcast-dev }
spec:
  selector: { app: redis }
  ports: [{ port: 6379, targetPort: 6379 }]
```

`k8s/streamcast-dev/postgres.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata: { name: postgres-secrets, namespace: streamcast-dev }
type: Opaque
stringData:
  POSTGRES_PASSWORD: "postgres-demo"
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: postgres, namespace: streamcast-dev }
spec:
  replicas: 1
  selector:
    matchLabels: { app: postgres }
  template:
    metadata: { labels: { app: postgres } }
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          ports: [{ containerPort: 5432 }]
          env:
            - { name: POSTGRES_USER,     value: auth }
            - { name: POSTGRES_DB,       value: auth }
            - name: POSTGRES_PASSWORD
              valueFrom: { secretKeyRef: { name: postgres-secrets, key: POSTGRES_PASSWORD } }
---
apiVersion: v1
kind: Service
metadata: { name: postgres, namespace: streamcast-dev }
spec:
  selector: { app: postgres }
  ports: [{ port: 5432, targetPort: 5432 }]
```

`k8s/streamcast-dev/auth.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata: { name: auth-config, namespace: streamcast-dev }
data:
  LOG_LEVEL: "info"
  REDIS_URL: "redis://redis:6379/0"
  DB_URL:    "postgresql://auth:postgres-demo@postgres:5432/auth"
---
apiVersion: v1
kind: Secret
metadata: { name: auth-secrets, namespace: streamcast-dev }
type: Opaque
stringData:
  JWT_SIGNING_KEY: "dev-not-real"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth
  namespace: streamcast-dev
  labels: { app: auth }
spec:
  replicas: 2
  selector:
    matchLabels: { app: auth }
  template:
    metadata: { labels: { app: auth } }
    spec:
      containers:
        - name: auth
          image: streamcast/auth:1.0
          imagePullPolicy: IfNotPresent
          ports: [{ containerPort: 8000 }]
          envFrom:
            - configMapRef: { name: auth-config }
            - secretRef:    { name: auth-secrets }
---
apiVersion: v1
kind: Service
metadata: { name: auth, namespace: streamcast-dev }
spec:
  selector: { app: auth }
  ports: [{ port: 80, targetPort: 8000 }]
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: streamcast
  namespace: streamcast-dev
spec:
  rules:
    - host: dev.streamcast.localhost
      http:
        paths:
          - path: /api/auth
            pathType: Prefix
            backend:
              service: { name: auth, port: { number: 80 } }
```

### 2.3 Aplicar

```bash
kubectl apply -f k8s/streamcast-dev/namespace.yaml
kubectl apply -f k8s/streamcast-dev/
kubectl -n streamcast-dev get all
kubectl -n streamcast-dev get pods -w
```

Teste:

```bash
curl -H "Host: dev.streamcast.localhost" \
     http://localhost:8080/api/auth/
# {"service":"auth","log_level":"info"}

curl -H "Host: dev.streamcast.localhost" \
     http://localhost:8080/api/auth/health/ready
# {"status":"ready"}
```

### 2.4 Baseline de "antes"

**Intencionalmente** esses manifestos **não** têm probes, nem limits, nem SA dedicada. Rode:

```bash
python scripts/check_deployment.py -n streamcast-dev auth
# Deve listar vários ERROR: sem requests, sem limits, sem probes.

python scripts/k8s_audit.py -n streamcast-dev
# Deve listar várias AUD-001/002/004.
```

**Copie a saída** em `docs/estado-inicial.md` como **baseline "pré-endurecimento"**. Essa é a evidência do "antes" para contar a história da migração.

### 2.5 Atualizar o Makefile

```makefile
APP ?= streamcast/auth:1.0

build:
	docker build -t $(APP) app/auth
	k3d image import $(APP) -c streamcast

deploy:
	kubectl apply -f k8s/streamcast-dev/namespace.yaml
	kubectl apply -f k8s/streamcast-dev/

audit:
	python scripts/explore_cluster.py -n streamcast-dev
	python scripts/check_deployment.py -n streamcast-dev auth
	python scripts/k8s_audit.py -n streamcast-dev

clean:
	-kubectl delete ns streamcast-dev --wait=false
```

### 2.6 Experimento de rolling update

Faça uma mudança trivial no `main.py` (ex.: retornar `{"service": "auth", "version": "1.1"}`):

```bash
docker build -t streamcast/auth:1.1 app/auth
k3d image import streamcast/auth:1.1 -c streamcast
kubectl -n streamcast-dev set image deployment/auth auth=streamcast/auth:1.1
kubectl -n streamcast-dev rollout status deploy/auth
```

Documente em `docs/observacoes-parte2.md`:

- Tempo observado do rollout.
- Se houve algum `ImagePullBackOff` inicial (esqueceu `k3d image import`?).
- Se endpoint ficou indisponível em algum instante (com `maxUnavailable: 0` default, não deveria).

---

## Entregáveis da Parte 2

- [ ] `app/auth/` com código e Dockerfile; `pytest` passa.
- [ ] Imagem construída e importada no k3d.
- [ ] Namespace `streamcast-dev` com `auth + postgres + redis + Ingress`.
- [ ] `/health/ready` responde 200.
- [ ] `docs/estado-inicial.md` com saída dos scripts (baseline "pré-endurecimento").
- [ ] `Makefile` atualizado com `build`, `deploy`, `audit`.
- [ ] `docs/observacoes-parte2.md` com relatos.

---

## Critérios de aceitação

- `kubectl -n streamcast-dev get pods` mostra todos `Running`.
- `curl` no Ingress retorna JSON do `auth`.
- Rolling update de 1.0 → 1.1 conclui sem downtime observável.
- Baseline de auditoria documentado (com erros esperados — vamos corrigir na Parte 3).

---

## Próximo passo

Avance para a **[Parte 3 — Resiliência e operações](parte-3-resiliencia.md)**: probes, limits, HPA, Ingress, NetworkPolicy, RBAC, PDB — zerar os achados do `k8s_audit.py`.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — Cluster local + primeiros manifests](parte-1-cluster-local.md) | **↑ Índice**<br>[Módulo 7 — Kubernetes](../README.md) | **Próximo →**<br>[Parte 3 — Resiliência e operações](parte-3-resiliencia.md) |

<!-- nav:end -->

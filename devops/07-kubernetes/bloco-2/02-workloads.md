# Bloco 2 — Workloads: do Compose ao Cluster

**Tempo estimado de leitura:** 90 min
**Pré-requisitos:** Bloco 1 (fundamentos), Módulo 5 (containers)

---

## 1. Objetivo

Neste bloco, **migramos o primeiro serviço da StreamCast** — o `auth` — de Docker Compose para Kubernetes, empilhando manifestos progressivamente:

1. **Pod** cru (para ver a unidade básica).
2. **Deployment** (réplicas + rolling update).
3. **Service** (endpoint estável).
4. **ConfigMap** e **Secret** (configuração e credenciais).
5. **Probes** (para o cluster saber quando Pod está vivo/pronto).
6. **Rolling update** e **rollback** (promessa central).

Ao final, você terá a `auth` rodando no k3d com a mesma qualidade de operação de uma equipe madura.

---

## 2. O serviço `auth` como referência

Uma versão simplificada do `auth` em FastAPI:

```python
# app/auth/src/main.py
from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from redis import Redis
from redis.exceptions import RedisError

DB_URL = os.environ.get("DB_URL", "postgresql://auth:auth@postgres:5432/auth")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
JWT_KEY = os.environ.get("JWT_SIGNING_KEY", "")
LOG_LEVEL = os.environ.get("LOG_LEVEL", "info")

_start = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not JWT_KEY:
        raise RuntimeError("JWT_SIGNING_KEY obrigatória")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health/live")
def live() -> dict:
    return {"status": "alive", "uptime_s": round(time.time() - _start, 1)}


@app.get("/health/ready")
def ready() -> dict:
    try:
        with psycopg.connect(DB_URL, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"db down: {exc}") from exc
    try:
        Redis.from_url(REDIS_URL, socket_timeout=2).ping()
    except RedisError as exc:
        raise HTTPException(status_code=503, detail=f"redis down: {exc}") from exc
    return {"status": "ready"}


@app.get("/")
def root() -> dict:
    return {"service": "auth", "log_level": LOG_LEVEL}
```

Dockerfile (revendo Módulo 5):

```dockerfile
# app/auth/Dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir "fastapi>=0.110" "uvicorn[standard]>=0.29" \
    "psycopg[binary]>=3.2" "redis>=5.0"
COPY src/ ./src/
EXPOSE 8000
USER 1000:1000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build no k3d:

```bash
docker build -t streamcast/auth:1.0 ./app/auth
k3d image import streamcast/auth:1.0 -c streamcast
# Importa a imagem para dentro do cluster k3d sem precisar de registry externo.
```

---

## 3. O Pod cru — só para entender

```yaml
# k8s/auth/pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: auth-demo
  labels:
    app: auth
spec:
  containers:
    - name: auth
      image: streamcast/auth:1.0
      ports:
        - containerPort: 8000
      env:
        - name: JWT_SIGNING_KEY
          value: "demo-only-never-real"
```

```bash
kubectl apply -f k8s/auth/pod.yaml
kubectl get pod auth-demo
kubectl describe pod auth-demo
kubectl logs auth-demo
```

**Problema:** se esse Pod morrer, **ninguém o recria**. Pod é unidade de agendamento, não de gerenciamento. Em produção, **nunca** crie Pods crus.

Antes de seguir, remova:

```bash
kubectl delete pod auth-demo
```

---

## 4. Deployment — a forma correta

`Deployment` = "quero **N réplicas** desse Pod, atualize com rolling update, saiba fazer rollback".

```yaml
# k8s/auth/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth
  labels:
    app: auth
spec:
  replicas: 3
  revisionHistoryLimit: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1          # 1 Pod a mais durante update
      maxUnavailable: 0    # 0 Pods fora do ar durante update
  selector:
    matchLabels:
      app: auth
  template:
    metadata:
      labels:
        app: auth
    spec:
      containers:
        - name: auth
          image: streamcast/auth:1.0
          ports:
            - containerPort: 8000
          env:
            - name: JWT_SIGNING_KEY
              value: "demo-only"
```

Aplicar e observar a reconciliação em tempo real:

```bash
kubectl apply -f k8s/auth/deployment.yaml
kubectl rollout status deployment/auth
kubectl get pods -l app=auth -w
```

### Rolando uma nova versão

Build da v2 e import:

```bash
docker build -t streamcast/auth:2.0 ./app/auth
k3d image import streamcast/auth:2.0 -c streamcast
```

Atualizar imagem declarativamente (alterando o YAML e aplicando de novo) **ou** imperativamente:

```bash
kubectl set image deployment/auth auth=streamcast/auth:2.0
kubectl rollout status deployment/auth
kubectl rollout history deployment/auth
```

Algoritmo do rolling update (com `maxSurge=1, maxUnavailable=0`):

```mermaid
sequenceDiagram
    participant RSold as ReplicaSet v1 (3 Pods)
    participant RSnew as ReplicaSet v2 (0 Pods)
    participant SVC as Service

    Note over RSold,RSnew: Deployment cria RSnew com replicas=1 (surge)
    RSnew->>SVC: 1 novo Pod Ready, entra no pool
    Note over RSold,RSnew: Deployment escala RSold para 2
    RSold->>SVC: 1 Pod antigo sai do pool
    Note over RSold,RSnew: novo Pod v2 Ready, pool = 2v1 + 1v2
    RSnew->>SVC: +1 Pod v2
    Note over RSold,RSnew: segue até RSold=0, RSnew=3
```

**Rollback em 1 comando:**

```bash
kubectl rollout undo deployment/auth
# ou para uma revisão específica:
kubectl rollout undo deployment/auth --to-revision=2
```

O histórico é mantido por `revisionHistoryLimit` (padrão 10; baixei para 5 para enxugar etcd).

---

## 5. Service — endpoint estável

```yaml
# k8s/auth/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: auth
  labels:
    app: auth
spec:
  type: ClusterIP
  selector:
    app: auth
  ports:
    - name: http
      port: 80            # porta do Service
      targetPort: 8000    # porta do container
```

Aplicar e testar:

```bash
kubectl apply -f k8s/auth/service.yaml
kubectl get svc auth
# NAME   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)   AGE
# auth   ClusterIP   10.43.123.45   <none>        80/TCP    5s

# Chamar de dentro do cluster (spawna um debug pod):
kubectl run -it --rm curl --image=curlimages/curl --restart=Never -- curl -s http://auth/
# {"service":"auth","log_level":"info"}
```

### DNS interno

Dentro de um Pod, `auth` resolve para o ClusterIP graças ao **CoreDNS**. Nome completo qualificado (FQDN):

```
auth.<namespace>.svc.cluster.local
```

- Pod no mesmo namespace: usa apenas `auth`.
- Pod em outro namespace: usa `auth.streamcast-dev`.
- Pod em outro cluster: precisa de gateway (fora do escopo).

### Endpoints

Kubernetes mantém um objeto **`EndpointSlice`** (ou `Endpoints`, legado) por Service, listando os IPs dos Pods casados pelo selector:

```bash
kubectl get endpoints auth
# NAME   ENDPOINTS                                   AGE
# auth   10.42.0.12:8000,10.42.0.13:8000,10.42.0.14:8000
```

Quando um Pod fica `NotReady` (falha na `readinessProbe`), seu IP **sai** do Endpoints — tráfego não chega até ele.

---

## 6. ConfigMap — configuração não sensível

```yaml
# k8s/auth/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: auth-config
data:
  LOG_LEVEL: "info"
  AUTH_TTL_MIN: "60"
  FEATURE_MFA: "false"
```

Injetando no Pod:

```yaml
# dentro do template do Deployment
env:
  - name: LOG_LEVEL
    valueFrom:
      configMapKeyRef:
        name: auth-config
        key: LOG_LEVEL
# Ou de uma vez:
envFrom:
  - configMapRef:
      name: auth-config
```

**Importante:** mudar um ConfigMap **não reinicia** automaticamente o Pod. Soluções:

1. Explicitar um hash em anotação do template (`checksum/config: <sha256 do CM>`) — força rolling update quando muda. Helm faz isso naturalmente.
2. `kubectl rollout restart deployment/auth` após mudar.

---

## 7. Secret — credenciais

```yaml
# k8s/auth/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: auth-secrets
type: Opaque
stringData:           # stringData = texto plano; K8s converte para base64 ao salvar
  JWT_SIGNING_KEY: "super-secret-change-me"
  DB_PASSWORD: "postgres-senha-demo"
```

Uso no Pod:

```yaml
env:
  - name: JWT_SIGNING_KEY
    valueFrom:
      secretKeyRef:
        name: auth-secrets
        key: JWT_SIGNING_KEY
```

**Fatos desconfortáveis que você precisa saber:**

1. `Secret` é **base64**, não criptografia. Quem lê o YAML lê o segredo em texto trivial (`base64 -d`).
2. Por padrão, etcd **não encripta** Secrets em disco. Habilita-se via [EncryptionConfiguration](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/) no apiserver.
3. Qualquer Pod com permissão de leitura em Secrets daquele namespace lê o conteúdo — daí a importância de RBAC (Bloco 3).
4. Nunca `kubectl apply -f secret.yaml` em repo público. Use **Sealed Secrets** ou **External Secrets** (Módulo 9).

Em desenvolvimento local (como aqui), `stringData` direto basta. Produção exige cifra extra.

---

## 8. Consolidando `auth` com tudo

```yaml
# k8s/auth/all.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: auth-config
data:
  LOG_LEVEL: "info"
  AUTH_TTL_MIN: "60"
---
apiVersion: v1
kind: Secret
metadata:
  name: auth-secrets
type: Opaque
stringData:
  JWT_SIGNING_KEY: "super-secret-change-me"
  DB_PASSWORD: "postgres-demo"
---
apiVersion: v1
kind: Service
metadata:
  name: auth
spec:
  type: ClusterIP
  selector: { app: auth }
  ports:
    - name: http
      port: 80
      targetPort: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth
  labels: { app: auth }
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  selector:
    matchLabels: { app: auth }
  template:
    metadata:
      labels: { app: auth }
    spec:
      containers:
        - name: auth
          image: streamcast/auth:1.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef: { name: auth-config }
          env:
            - name: JWT_SIGNING_KEY
              valueFrom:
                secretKeyRef: { name: auth-secrets, key: JWT_SIGNING_KEY }
            - name: DB_URL
              value: "postgresql://auth:$(DB_PASSWORD)@postgres:5432/auth"
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef: { name: auth-secrets, key: DB_PASSWORD }
            - name: REDIS_URL
              value: "redis://redis:6379/0"
          resources:
            requests: { cpu: "100m", memory: "128Mi" }
            limits:   { cpu: "500m", memory: "256Mi" }
          startupProbe:
            httpGet: { path: /health/live, port: 8000 }
            periodSeconds: 5
            failureThreshold: 8
          readinessProbe:
            httpGet: { path: /health/ready, port: 8000 }
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet: { path: /health/live, port: 8000 }
            periodSeconds: 20
            failureThreshold: 3
```

```bash
kubectl apply -f k8s/auth/all.yaml
kubectl get pods -l app=auth
kubectl logs -l app=auth --tail=20
```

---

## 9. Dependências: Postgres e Redis

Para `auth` ficar `Ready`, precisa de Postgres e Redis alcançáveis. Em aprendizado local, basta um `Deployment` efêmero:

```yaml
# k8s/infra/redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels: { app: redis }
  template:
    metadata: { labels: { app: redis } }
    spec:
      containers:
        - name: redis
          image: redis:7-alpine
          ports: [{ containerPort: 6379 }]
          resources:
            requests: { cpu: "50m",  memory: "64Mi" }
            limits:   { cpu: "200m", memory: "128Mi" }
---
apiVersion: v1
kind: Service
metadata: { name: redis }
spec:
  selector: { app: redis }
  ports: [{ port: 6379, targetPort: 6379 }]
```

Para Postgres, um `StatefulSet` + `PVC` é o ideal, mas para este bloco um `Deployment` simples já demonstra (o Bloco 3 entra em `StatefulSet` e storage apropriadamente):

```yaml
# k8s/infra/postgres.yaml
apiVersion: v1
kind: Secret
metadata: { name: postgres-secrets }
type: Opaque
stringData:
  POSTGRES_PASSWORD: "postgres-demo"
---
apiVersion: apps/v1
kind: Deployment
metadata: { name: postgres }
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
            - name: POSTGRES_USER
              value: auth
            - name: POSTGRES_DB
              value: auth
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef: { name: postgres-secrets, key: POSTGRES_PASSWORD }
          resources:
            requests: { cpu: "100m", memory: "128Mi" }
            limits:   { cpu: "500m", memory: "256Mi" }
---
apiVersion: v1
kind: Service
metadata: { name: postgres }
spec:
  selector: { app: postgres }
  ports: [{ port: 5432, targetPort: 5432 }]
```

Aplicar tudo:

```bash
kubectl apply -f k8s/infra/
kubectl apply -f k8s/auth/all.yaml
```

Verificar:

```bash
kubectl get pods
# NAME                        READY   STATUS    RESTARTS   AGE
# auth-7b4d...-x              1/1     Running   0          30s
# auth-7b4d...-y              1/1     Running   0          30s
# auth-7b4d...-z              1/1     Running   0          30s
# postgres-6c...-a            1/1     Running   0          1m
# redis-5d...-b               1/1     Running   0          1m

# Validar endpoint:
kubectl run -it --rm curl --image=curlimages/curl --restart=Never -- curl -s http://auth/health/ready
# {"status":"ready"}
```

---

## 10. Dissecando `imagePullPolicy`

Em `Deployment.spec.template.spec.containers[].imagePullPolicy`:

| Valor | Quando aplica | Comportamento |
|-------|---------------|---------------|
| `Always` | default se tag for `:latest` ou ausente | Puxa toda vez que cria container |
| `IfNotPresent` | default para tags explícitas | Puxa só se imagem não estiver no node |
| `Never` | sempre (explícito) | Assume que imagem já está local; falha se não |

**Armadilha**: se você sobrescrever a mesma tag (`auth:1.0`) com novo conteúdo, Pods antigos podem continuar com a imagem antiga em cache. **Sempre** use tag nova por build (digest ou `:v1.2.3`) — reforço do Módulo 5.

No k3d, `k3d image import` coloca a imagem em todos os nodes, permitindo `IfNotPresent` funcionar sem registry externo. Em cluster real, use **GHCR** (Módulo 5).

---

## 11. Script de apoio: cliente Python interagindo com o cluster

Expandimos o que vimos no Bloco 1 com uma rotina que **audita** um Deployment quanto a boas práticas observadas no próprio manifesto após aplicado.

### `check_deployment.py`

```python
"""
check_deployment.py — audita um Deployment contra boas práticas.

Verifica:
  - resources.requests/limits presentes
  - readinessProbe e livenessProbe presentes
  - imagePullPolicy consistente com tag
  - strategy.rollingUpdate com maxUnavailable <= 25%
  - réplicas >= 2 (para HA)

Uso:
  python check_deployment.py -n default auth
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Iterable

from kubernetes import client, config


SEVERIDADES = ("INFO", "WARN", "ERROR")


@dataclass(frozen=True)
class Achado:
    severidade: str
    codigo: str
    mensagem: str


def _checar_container(c) -> Iterable[Achado]:
    if c.resources is None or not c.resources.requests:
        yield Achado("ERROR", "K8S-RES-REQ",
                     f"{c.name}: sem resources.requests")
    if c.resources is None or not c.resources.limits:
        yield Achado("ERROR", "K8S-RES-LIM",
                     f"{c.name}: sem resources.limits")
    if c.readiness_probe is None:
        yield Achado("ERROR", "K8S-RD-PROBE",
                     f"{c.name}: sem readinessProbe")
    if c.liveness_probe is None:
        yield Achado("WARN", "K8S-LV-PROBE",
                     f"{c.name}: sem livenessProbe")
    if c.image and c.image.endswith(":latest"):
        yield Achado("ERROR", "K8S-IMG-LATEST",
                     f"{c.name}: imagem usa :latest ({c.image})")
    pull = c.image_pull_policy
    if c.image and c.image.endswith(":latest") and pull != "Always":
        yield Achado("WARN", "K8S-IMG-PULL",
                     f"{c.name}: :latest deveria ter imagePullPolicy=Always")


def _checar_deployment(dep) -> list[Achado]:
    achados: list[Achado] = []
    if (dep.spec.replicas or 0) < 2:
        achados.append(Achado("WARN", "K8S-REPL",
                              f"replicas={dep.spec.replicas} < 2 (sem HA)"))
    strategy = dep.spec.strategy
    if strategy and strategy.type == "RollingUpdate":
        mu = strategy.rolling_update.max_unavailable if strategy.rolling_update else None
        if mu not in (0, "0", "0%"):
            achados.append(Achado("INFO", "K8S-MAXUNAV",
                                  f"maxUnavailable={mu} pode causar redução durante update"))
    for c in dep.spec.template.spec.containers:
        achados.extend(_checar_container(c))
    return achados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("nome", help="nome do Deployment")
    parser.add_argument("-n", "--namespace", default="default")
    args = parser.parse_args(argv)

    try:
        config.load_kube_config()
    except Exception as exc:
        print(f"Falha ao carregar kubeconfig: {exc}", file=sys.stderr)
        return 2

    api = client.AppsV1Api()
    try:
        dep = api.read_namespaced_deployment(args.nome, args.namespace)
    except client.exceptions.ApiException as exc:
        print(f"Deployment '{args.nome}' no namespace '{args.namespace}' "
              f"não encontrado: {exc.reason}", file=sys.stderr)
        return 2

    achados = _checar_deployment(dep)
    achados.sort(key=lambda a: SEVERIDADES.index(a.severidade), reverse=True)

    if not achados:
        print(f"OK — {args.nome} passou nas checagens básicas.")
        return 0

    for a in achados:
        print(f"[{a.severidade:5s}] {a.codigo:14s} {a.mensagem}")

    return 1 if any(a.severidade == "ERROR" for a in achados) else 0


if __name__ == "__main__":
    sys.exit(main())
```

**Uso:**

```bash
python check_deployment.py auth
# [INFO ] K8S-MAXUNAV    maxUnavailable=0 pode causar redução durante update
# (sem ERROR — passa com exit 0)

python check_deployment.py demo  # o nginx do exercício 1.6
# [ERROR] K8S-RES-REQ    nginx: sem resources.requests
# [ERROR] K8S-RES-LIM    nginx: sem resources.limits
# [ERROR] K8S-RD-PROBE   nginx: sem readinessProbe
# [WARN ] K8S-LV-PROBE   nginx: sem livenessProbe
```

Esse script:

- Integra com o **cliente oficial Kubernetes for Python** (`pip install kubernetes`).
- Retorna **exit-code não-zero** em violações graves (integra com CI do Bloco 4).
- Documenta políticas por código (`K8S-*`), facilitando rastreabilidade.

---

## 12. Rolling update na prática — exercício rápido

```bash
# v1 rodando:
kubectl get pods -l app=auth
# 3 Pods, todos com image auth:1.0

# Lançar v2 (já importada no cluster):
kubectl set image deployment/auth auth=streamcast/auth:2.0
kubectl rollout status deployment/auth

# Histórico:
kubectl rollout history deployment/auth
# deployment.apps/auth
# REVISION  CHANGE-CAUSE
# 1         <none>
# 2         <none>

# Se algo dá errado:
kubectl rollout undo deployment/auth
```

Registrar "change-cause" ao aplicar ajuda operação:

```bash
kubectl annotate deployment/auth kubernetes.io/change-cause="release 2.0 — JWT com RS256"
```

---

## 13. Anti-padrões comuns (e como fugir)

| Anti-padrão | Por que é ruim | Alternativa |
|-------------|----------------|-------------|
| Pod cru em produção | Sem reconciliação nem restart de nó | `Deployment` / `StatefulSet` |
| `:latest` em imagens | Rollback impossível, cache enganador | Tag imutável `:1.4.2` + digest |
| Secret em ConfigMap | Texto claro em qualquer lugar | `Secret` (mesmo com limites) |
| Sem `resources.limits` | 1 Pod pode derrubar node | Definir sempre |
| `replicas: 1` para API stateless | Downtime a cada crash, sem HA | ≥ 2 + `PodDisruptionBudget` |
| `livenessProbe` checando DB | Restart-loop cascateado na queda do DB | Liveness = processo; Readiness = dependência |
| `exec` com scripts externos em probe | Fragilidade + tempo de arranque | `httpGet` sempre que possível |
| Hardcode de URL do banco no env | Rotação difícil | ConfigMap (URL) + Secret (senha) |
| Montar Secret como env var de tudo | Vazamento por logs/erros de lib | Montar como arquivo em `/var/run/secrets/...` para dados realmente sensíveis |

---

## 14. Resumo visual

```mermaid
flowchart LR
    CM[ConfigMap<br/>auth-config] -->|envFrom| POD[Pod auth-X]
    SEC[Secret<br/>auth-secrets] -->|secretKeyRef| POD
    POD -->|labels<br/>app=auth| EP[Endpoints]
    SVC[Service auth] -->|selector<br/>app=auth| EP
    DEP[Deployment auth] -->|cria| RS[ReplicaSet]
    RS -->|cria/mantém| POD
    CLIENT[outros Pods] -->|DNS auth.ns| SVC

    style DEP fill:#fff3cd
    style POD fill:#c8e6c9
    style SVC fill:#bbdefb
```

---

## 15. Check-list do bloco

- [ ] Tenho um Deployment aplicado, com 3 Pods rodando.
- [ ] Tenho um Service ClusterIP que balanceia para esses Pods.
- [ ] Extraí configuração para ConfigMap e credenciais para Secret.
- [ ] Defini `requests`/`limits` e todas as probes.
- [ ] Executei rolling update (`kubectl set image`) e acompanhei `rollout status`.
- [ ] Executei `kubectl rollout undo` e confirmei rollback.
- [ ] Rodei `check_deployment.py` contra o `auth` e entendi os achados.

---

## 16. Próximos passos

- Resolva [02-exercicios-resolvidos.md](02-exercicios-resolvidos.md).
- Avance para o [Bloco 3 — Operações](../bloco-3/03-operacoes-cluster.md): Namespace, RBAC, NetworkPolicy, HPA, Ingress, PVC.

**Leituras complementares:**

- *Kubernetes Up & Running*, Caps. 6–10.
- [kubernetes.io/docs/concepts/workloads/controllers/deployment/](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).
- [kubernetes.io/docs/concepts/configuration/configmap/](https://kubernetes.io/docs/concepts/configuration/configmap/).
- [kubernetes.io/docs/concepts/configuration/secret/](https://kubernetes.io/docs/concepts/configuration/secret/).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — Exercícios Resolvidos](../bloco-1/01-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 7 — Kubernetes](../README.md) | **Próximo →**<br>[Bloco 2 — Exercícios Resolvidos](02-exercicios-resolvidos.md) |

<!-- nav:end -->

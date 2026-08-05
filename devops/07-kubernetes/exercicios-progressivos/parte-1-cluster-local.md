# Parte 1 — Cluster local + primeiros manifests

**Tempo estimado:** 90 min
**Pré-requisitos:** Blocos 1–2; ambiente validado (ver README dos progressivos).

---

## Contexto

Você foi contratado como **engenheiro de plataforma** da StreamCast EDU. Antes de migrar qualquer serviço, a CTO quer ver você demonstrar **competência operacional** com Kubernetes em um cluster local descartável. Resultado desta parte: 1 cluster k3d reproduzível + 1 serviço trivial rodando + um diagnóstico formal do cenário atual.

---

## Objetivos

- Criar cluster k3d reproduzível via script idempotente.
- Implantar um `Deployment + Service + Ingress` de teste (`nginx` + `traefik`).
- Validar com os scripts Python do Bloco 1 (`explore_cluster.py`).
- Documentar a decisão entre `k3d`, `kind` e `minikube` em um ADR.
- Inventariar os sintomas da StreamCast em matriz mapeada a primitivas K8s.

---

## Tarefas

### 1.1 Repositório

Crie um repositório vazio (`streamcast-k8s`) com `README.md` inicial descrevendo o objetivo do projeto (2-3 parágrafos referenciando o cenário).

### 1.2 Script de bootstrap do cluster

Crie `scripts/k3d-up.sh`:

```bash
#!/usr/bin/env bash
# scripts/k3d-up.sh — sobe cluster k3d "streamcast" idempotentemente.
set -euo pipefail

CLUSTER_NAME="${CLUSTER_NAME:-streamcast}"
AGENTS="${AGENTS:-2}"

if k3d cluster list | awk 'NR>1 {print $1}' | grep -qx "$CLUSTER_NAME"; then
  echo "Cluster '$CLUSTER_NAME' já existe. Usando o atual."
else
  echo "Criando cluster '$CLUSTER_NAME' com $AGENTS agents..."
  k3d cluster create "$CLUSTER_NAME" \
      --agents "$AGENTS" \
      --port "8080:80@loadbalancer" \
      --port "8443:443@loadbalancer" \
      --k3s-arg "--disable=traefik@server:*" \
      --wait
fi

echo "Instalando Traefik (sem os defaults do k3d para ter versão controlada)..."
helm repo add traefik https://traefik.github.io/charts >/dev/null 2>&1 || true
helm repo update >/dev/null
helm upgrade --install traefik traefik/traefik \
    --namespace kube-system \
    --set service.type=LoadBalancer \
    --wait

echo
echo "Cluster pronto:"
kubectl get nodes -o wide
```

E `scripts/k3d-down.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
k3d cluster delete "${CLUSTER_NAME:-streamcast}"
```

Torne executáveis:

```bash
chmod +x scripts/k3d-up.sh scripts/k3d-down.sh
```

**Rode:**

```bash
./scripts/k3d-up.sh
kubectl get nodes
# 3 nós (1 server + 2 agents) Ready.
```

### 1.3 Ambiente Python

Crie `requirements.txt` com o conteúdo do módulo (ou reuse `devops/07-kubernetes/requirements.txt`).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copie os scripts do módulo para `scripts/`:

- `explore_cluster.py` (Bloco 1)
- `check_deployment.py` (Bloco 2)
- `k8s_audit.py` (Bloco 3)
- `helm_drift.py` (Bloco 4)

### 1.4 Primeiro Deployment

`k8s/demo/nginx.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: demo
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello
  namespace: demo
spec:
  replicas: 2
  selector:
    matchLabels: { app: hello }
  template:
    metadata:
      labels: { app: hello }
    spec:
      containers:
        - name: nginx
          image: nginx:1.27-alpine
          ports: [{ containerPort: 80 }]
          resources:
            requests: { cpu: 50m,  memory: 32Mi }
            limits:   { cpu: 200m, memory: 64Mi }
          readinessProbe:
            httpGet: { path: /, port: 80 }
            periodSeconds: 5
          livenessProbe:
            httpGet: { path: /, port: 80 }
            periodSeconds: 20
---
apiVersion: v1
kind: Service
metadata: { name: hello, namespace: demo }
spec:
  selector: { app: hello }
  ports: [{ port: 80, targetPort: 80 }]
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: hello
  namespace: demo
spec:
  rules:
    - host: hello.localhost
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service: { name: hello, port: { number: 80 } }
```

```bash
kubectl apply -f k8s/demo/nginx.yaml
kubectl -n demo get all
curl -H "Host: hello.localhost" http://localhost:8080
# <!DOCTYPE html>... página default do nginx
```

### 1.5 Rodar `explore_cluster.py`

```bash
python scripts/explore_cluster.py --all-namespaces
python scripts/explore_cluster.py --namespace demo
```

Anote em `docs/estado-inicial.md` os valores observados: N° de namespaces, nodes, Pods por status. Use isso como "baseline" para comparar depois.

### 1.6 Rodar `check_deployment.py`

```bash
python scripts/check_deployment.py -n demo hello
```

Resultado esperado: **0 ERROR** (já temos limits e probes). Se houver, corrija os manifests.

### 1.7 Destrua e recrie

Para provar reprodutibilidade:

```bash
./scripts/k3d-down.sh
./scripts/k3d-up.sh
kubectl apply -f k8s/demo/nginx.yaml
# Tudo de volta < 2 min
```

### 1.8 ADR 001 — k3d vs kind vs minikube

`docs/adr/001-k3d-vs-kind.md`, usando template Nygard:

```markdown
# ADR 001 — Escolha da distribuição K8s local para laboratório

## Status
Aceito — 2026-04-21

## Contexto
Precisamos de um cluster Kubernetes local para desenvolver, validar chart e
exercitar operações. Precisa ser rápido subir (< 2 min), descartável,
compatível com CNI que suporte NetworkPolicy, e próximo da experiência prod.

Alternativas avaliadas:
- **k3d**: k3s-in-docker, rápido, multi-node trivial, Traefik default.
- **kind**: Kubernetes oficial em Docker, usado pela SIG Cluster Lifecycle,
  bom para testes CI, precisa instalar CNI robusto manualmente.
- **minikube**: maduro, mais pesado, virtualização opcional, IDE integrations.

## Decisão
Usar **k3d** como default.

## Consequências
- Positivas: arranque em ~30s, multi-node simples, controladores leves.
- Negativas: k3s não é idêntico ao upstream (omite alguns componentes);
  CNI padrão (flannel) não suporta NetworkPolicy — precisamos trocar por
  Calico ou Cilium em partes seguintes.
- Mitigação: `kind` disponível como alternativa para quem precisar testar
  conformidade estrita com K8s upstream.
```

### 1.9 Matriz de sintomas → primitivas K8s

`docs/matriz-sintomas.md`:

```markdown
# Matriz sintoma → primitiva K8s

| # | Sintoma StreamCast                   | Primitiva K8s que endereça                 |
|---|--------------------------------------|---------------------------------------------|
| 1 | Picos 8h/14h/19h                     | HorizontalPodAutoscaler                     |
| 2 | Transcoder afoga VM                  | resources.limits, namespaces, ResourceQuota |
| 3 | Downtime em deploy                   | Deployment.strategy.rollingUpdate + probes  |
| 4 | Sem self-heal                        | ReplicaSet controller + probes              |
| 5 | Escala manual                        | HPA (+ min/maxReplicas)                     |
| 6 | Tenant abusivo afeta outros          | ResourceQuota por namespace                 |
| 7 | Secrets em .env                      | Secret + (Sealed/External Secrets - Módulo 9) |
| 8 | Rollback = restaurar snapshot        | kubectl rollout undo / helm rollback        |
| 9 | Rede plana                           | NetworkPolicy                               |
|10 | Onboarding 3 dias                    | ApplicationSet + GitOps + Helm values       |
```

Este mapa é "matéria prima" para a entrega avaliativa e argumenta **por que** o módulo existe.

### 1.10 Makefile inicial

`Makefile`:

```makefile
.PHONY: up down deploy audit clean

up:
	./scripts/k3d-up.sh

down:
	./scripts/k3d-down.sh

deploy:
	kubectl apply -f k8s/demo/nginx.yaml

audit:
	python scripts/explore_cluster.py --all-namespaces

clean: down
```

Teste:

```bash
make up
make deploy
make audit
make clean
```

---

## Entregáveis da Parte 1

- [ ] Repositório iniciado, com README objetivo.
- [ ] `scripts/k3d-up.sh` e `k3d-down.sh` operando idempotentemente.
- [ ] `k8s/demo/nginx.yaml` aplicado, acessível via `curl -H "Host: hello.localhost"`.
- [ ] Scripts Python copiados para `scripts/` e executados sem erro.
- [ ] `docs/estado-inicial.md` com baseline de inventário.
- [ ] `docs/adr/001-k3d-vs-kind.md` redigido.
- [ ] `docs/matriz-sintomas.md` completo.
- [ ] `Makefile` com alvos mínimos.

---

## Critérios de aceitação

- `./scripts/k3d-up.sh` é idempotente (roda duas vezes sem erro).
- `python scripts/explore_cluster.py` produz saída coerente.
- `python scripts/check_deployment.py -n demo hello` sai com `exit 0`.
- ADR é conciso (≤ 1 página) e honesto quanto a consequências.

---

## Próximo passo

Avance para a **[Parte 2 — Workloads básicos](parte-2-workloads-basicos.md)**, onde substituímos o `nginx` pelo serviço real `auth` em FastAPI + Postgres + Redis.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Progressivos — Módulo 7](README.md) | **↑ Índice**<br>[Módulo 7 — Kubernetes](../README.md) | **Próximo →**<br>[Parte 2 — Workloads básicos da StreamCast](parte-2-workloads-basicos.md) |

<!-- nav:end -->

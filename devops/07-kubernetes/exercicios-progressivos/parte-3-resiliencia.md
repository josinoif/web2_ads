# Parte 3 — Resiliência e operações

**Tempo estimado:** 150 min
**Pré-requisitos:** Parte 2 concluída (baseline sem probes, sem limits, sem RBAC, sem NetPol).

---

## Contexto

Os manifestos existem e funcionam no "caminho feliz". Agora vamos **endurecer**: probes, limits, SA, NetworkPolicy, HPA, Ingress multi-tenant, PodDisruptionBudget. O alvo é fazer `k8s_audit.py` sair **sem ERROR**.

---

## Objetivos

- Adicionar probes (`startupProbe`, `readinessProbe`, `livenessProbe`).
- Definir `resources.requests/limits` em todos os containers.
- Criar `ServiceAccount` dedicada por serviço, sem token montado.
- Instalar Calico (ou equivalente) para habilitar NetworkPolicy.
- Aplicar `NetworkPolicy default-deny` + allows específicos.
- Configurar HPA no `auth`.
- Aplicar `PodDisruptionBudget` nos serviços críticos.
- Converter Postgres para `StatefulSet` com PVC.
- Rodar `k8s_audit.py` e validar 0 ERROR.

---

## Tarefas

### 3.1 Instalar CNI com suporte a NetworkPolicy

k3d vem com **Flannel** (sem NetworkPolicy). Troque para **Calico**:

```bash
./scripts/k3d-down.sh
k3d cluster create streamcast \
    --agents 2 \
    --port "8080:80@loadbalancer" \
    --port "8443:443@loadbalancer" \
    --k3s-arg "--flannel-backend=none@server:*" \
    --k3s-arg "--disable-network-policy@server:*" \
    --no-lb=false \
    --wait

# Instalar Calico
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml

kubectl -n kube-system rollout status daemonset/calico-node --timeout=300s
```

Ajuste `scripts/k3d-up.sh` para refletir isso — o cluster precisa ser **reprodutível**.

### 3.2 Endurecer `auth.yaml`

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: auth
  namespace: streamcast-dev
automountServiceAccountToken: false
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth
  namespace: streamcast-dev
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  selector:
    matchLabels: { app: auth }
  template:
    metadata:
      labels: { app: auth }
      annotations:
        checksum/config: "PLACEHOLDER"  # Helm preencherá na Parte 4
    spec:
      serviceAccountName: auth
      automountServiceAccountToken: false
      securityContext:
        runAsUser: 1000
        runAsNonRoot: true
        fsGroup: 1000
      containers:
        - name: auth
          image: streamcast/auth:1.0
          imagePullPolicy: IfNotPresent
          ports: [{ containerPort: 8000 }]
          envFrom:
            - configMapRef: { name: auth-config }
            - secretRef:    { name: auth-secrets }
          resources:
            requests: { cpu: 100m, memory: 128Mi }
            limits:   { cpu: 500m, memory: 256Mi }
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

### 3.3 StatefulSet do Postgres

Substitua `postgres.yaml` por versão com `StatefulSet`:

```yaml
apiVersion: v1
kind: Secret
metadata: { name: postgres-secrets, namespace: streamcast-dev }
type: Opaque
stringData:
  POSTGRES_PASSWORD: "postgres-demo"
---
apiVersion: v1
kind: Service
metadata: { name: postgres-headless, namespace: streamcast-dev }
spec:
  clusterIP: None
  selector: { app: postgres }
  ports: [{ port: 5432, targetPort: 5432 }]
---
apiVersion: v1
kind: Service
metadata: { name: postgres, namespace: streamcast-dev }
spec:
  selector: { app: postgres }
  ports: [{ port: 5432, targetPort: 5432 }]
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: postgres, namespace: streamcast-dev }
spec:
  serviceName: postgres-headless
  replicas: 1
  selector:
    matchLabels: { app: postgres }
  template:
    metadata: { labels: { app: postgres } }
    spec:
      securityContext:
        runAsUser: 999
        fsGroup: 999
        runAsNonRoot: true
      containers:
        - name: postgres
          image: postgres:16-alpine
          ports: [{ containerPort: 5432 }]
          env:
            - { name: POSTGRES_USER, value: auth }
            - { name: POSTGRES_DB, value: auth }
            - { name: PGDATA, value: /var/lib/postgresql/data/pgdata }
            - name: POSTGRES_PASSWORD
              valueFrom: { secretKeyRef: { name: postgres-secrets, key: POSTGRES_PASSWORD } }
          volumeMounts:
            - { name: data, mountPath: /var/lib/postgresql/data }
          resources:
            requests: { cpu: 200m, memory: 256Mi }
            limits:   { cpu: "1",  memory: "1Gi"  }
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "auth", "-d", "auth"]
            periodSeconds: 10
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        resources: { requests: { storage: 5Gi } }
        storageClassName: local-path
```

> O `Deployment` antigo de postgres **deve ser deletado** antes de aplicar o StatefulSet (`kubectl delete deploy/postgres -n streamcast-dev`), pois o nome é o mesmo.

### 3.4 NetworkPolicy

`k8s/streamcast-dev/networkpolicies.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: streamcast-dev }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns, namespace: streamcast-dev }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
          podSelector:
            matchLabels: { k8s-app: kube-dns }
      ports:
        - { protocol: UDP, port: 53 }
        - { protocol: TCP, port: 53 }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: auth-egress, namespace: streamcast-dev }
spec:
  podSelector:
    matchLabels: { app: auth }
  policyTypes: [Egress]
  egress:
    - to:
        - podSelector: { matchLabels: { app: postgres } }
      ports: [{ protocol: TCP, port: 5432 }]
    - to:
        - podSelector: { matchLabels: { app: redis } }
      ports: [{ protocol: TCP, port: 6379 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: auth-ingress, namespace: streamcast-dev }
spec:
  podSelector:
    matchLabels: { app: auth }
  policyTypes: [Ingress]
  ingress:
    # permite o Ingress Controller (Traefik) em kube-system falar com auth
    - from:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
      ports: [{ protocol: TCP, port: 8000 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: db-ingress, namespace: streamcast-dev }
spec:
  podSelector:
    matchLabels: { app: postgres }
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector: { matchLabels: { app: auth } }
      ports: [{ protocol: TCP, port: 5432 }]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: redis-ingress, namespace: streamcast-dev }
spec:
  podSelector:
    matchLabels: { app: redis }
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector: { matchLabels: { app: auth } }
      ports: [{ protocol: TCP, port: 6379 }]
```

**Teste a NetworkPolicy:**

```bash
# Dentro de um pod sem labels, auth deveria estar inalcançável:
kubectl -n streamcast-dev run hacker --image=curlimages/curl \
    --restart=Never -it --rm -- curl -m 3 http://auth
# curl: (28) Connection timed out

# Dentro do pod auth, postgres deve responder:
AUTH_POD=$(kubectl -n streamcast-dev get pod -l app=auth -o name | head -1)
kubectl -n streamcast-dev exec $AUTH_POD -- sh -c \
    'pg_isready -h postgres -U auth -d auth'
# postgres:5432 - accepting connections
```

### 3.5 HPA + PDB

`k8s/streamcast-dev/hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: auth, namespace: streamcast-dev }
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: auth
  minReplicas: 2
  maxReplicas: 8
  metrics:
    - type: Resource
      resource:
        name: cpu
        target: { type: Utilization, averageUtilization: 60 }
  behavior:
    scaleDown: { stabilizationWindowSeconds: 120 }
    scaleUp:   { stabilizationWindowSeconds: 10 }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: auth, namespace: streamcast-dev }
spec:
  minAvailable: 1
  selector:
    matchLabels: { app: auth }
```

### 3.6 ResourceQuota e LimitRange

`k8s/streamcast-dev/quota.yaml`:

```yaml
apiVersion: v1
kind: ResourceQuota
metadata: { name: dev-quota, namespace: streamcast-dev }
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "20"
---
apiVersion: v1
kind: LimitRange
metadata: { name: container-defaults, namespace: streamcast-dev }
spec:
  limits:
    - type: Container
      default:        { cpu: 500m, memory: 256Mi }
      defaultRequest: { cpu: 100m, memory: 128Mi }
      max:            { cpu: "2",  memory: "2Gi"   }
```

### 3.7 Reaplicar tudo

```bash
kubectl -n streamcast-dev delete deployment postgres  # tinha sido deploy
kubectl apply -f k8s/streamcast-dev/
kubectl -n streamcast-dev rollout status deploy/auth
kubectl -n streamcast-dev rollout status statefulset/postgres
```

Teste de ponta a ponta:

```bash
curl -H "Host: dev.streamcast.localhost" \
     http://localhost:8080/api/auth/health/ready
# {"status":"ready"}
```

### 3.8 Auditoria final

```bash
python scripts/k8s_audit.py -n streamcast-dev
# Deve sair "Sem achados" OU apenas WARN residuais (justificáveis)

python scripts/check_deployment.py -n streamcast-dev auth
# OK
```

Se ainda houver ERROR, itere até zerar.

### 3.9 Testes de carga e HPA

```bash
# Em aba A:
kubectl -n streamcast-dev get hpa auth -w

# Em aba B:
kubectl -n streamcast-dev run -it --rm load --image=busybox \
    --restart=Never -- \
    sh -c 'while true; do wget -q -O- http://auth/ > /dev/null; done'
```

Documente em `docs/observacoes-parte3.md`:

- Quantos segundos até HPA subir de 2 para 4.
- Pico de réplicas.
- Tempo até descer de volta para 2 após parar a carga.

### 3.10 Atualizar `docs/estado-inicial.md`

Adicione uma seção **"Depois da Parte 3"** com a saída do `k8s_audit.py` zerada — evidência de progresso.

---

## Entregáveis da Parte 3

- [ ] Calico instalado e funcional.
- [ ] Manifestos endurecidos: SA, securityContext, probes, limits.
- [ ] Postgres como `StatefulSet` com PVC de 5Gi.
- [ ] NetworkPolicy `default-deny` + allows específicos, testadas.
- [ ] HPA e PDB em `auth`.
- [ ] ResourceQuota e LimitRange no namespace.
- [ ] `k8s_audit.py` sem ERROR.
- [ ] `docs/observacoes-parte3.md` com dados do HPA.

---

## Critérios de aceitação

- `curl` pelo Ingress continua funcionando com todas as policies aplicadas.
- Pod sem labels é bloqueado (comprovado em timeout).
- HPA escala observavelmente sob carga.
- Auditoria zerada.

---

## Próximo passo

Avance para a **[Parte 4 — Helm chart](parte-4-helm.md)**: empacote esses ~10 YAMLs em um chart parametrizável com `values-dev.yaml` e `values-stg.yaml`.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — Workloads básicos da StreamCast](parte-2-workloads-basicos.md) | **↑ Índice**<br>[Módulo 7 — Kubernetes](../README.md) | **Próximo →**<br>[Parte 4 — Empacotamento com Helm](parte-4-helm.md) |

<!-- nav:end -->

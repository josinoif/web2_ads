# Parte 4 — Empacotamento com Helm

**Tempo estimado:** 120 min
**Pré-requisitos:** Parte 3 concluída (todos os manifests aplicados e auditados).

---

## Contexto

Você tem ~10 YAMLs funcionais em `k8s/streamcast-dev/`. Agora precisamos:

- **Parametrizar** para criar um `streamcast-stg` sem copiar e colar.
- **Versionar** entregas.
- **Rollback em 1 comando**.

Solução: Helm chart único cobrindo todos os serviços. E manter um segundo ambiente `stg` com recursos maiores e Ingress com host distinto.

---

## Objetivos

- Criar `charts/streamcast/` com template genérico para os serviços.
- Parametrizar tudo em `values.yaml` + overrides por ambiente.
- Conseguir `helm install` / `helm upgrade` / `helm rollback` funcionais.
- Documentar ADR 002 (Helm vs Kustomize).

---

## Tarefas

### 4.1 Estrutura

```
charts/streamcast/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-stg.yaml
├── .helmignore
└── templates/
    ├── _helpers.tpl
    ├── namespace.yaml            # opcional (se syncOptions CreateNamespace)
    ├── serviceaccount.yaml
    ├── configmap.yaml
    ├── secret.yaml
    ├── deployment.yaml           # loop por serviço
    ├── service.yaml              # loop por serviço
    ├── hpa.yaml
    ├── pdb.yaml
    ├── postgres-statefulset.yaml
    ├── redis-deployment.yaml
    ├── networkpolicy.yaml
    ├── quota.yaml
    └── ingress.yaml
```

### 4.2 `Chart.yaml` e `values.yaml`

```yaml
# Chart.yaml
apiVersion: v2
name: streamcast
description: StreamCast EDU — plataforma multi-serviço
type: application
version: 0.1.0
appVersion: "1.0"
```

```yaml
# values.yaml
environment: dev

global:
  imageRegistry: streamcast
  imagePullPolicy: IfNotPresent

services:
  auth:
    enabled: true
    replicaCount: 2
    image:
      repository: auth
      tag: "1.0"
    config:
      LOG_LEVEL: info
      REDIS_URL: "redis://redis:6379/0"
      DB_URL:    "postgresql://auth:postgres-demo@postgres:5432/auth"
    secrets:
      JWT_SIGNING_KEY: "dev-only"
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits:   { cpu: 500m, memory: 256Mi }
    hpa:
      enabled: true
      minReplicas: 2
      maxReplicas: 8
      targetCPU: 60
    pdb:
      enabled: true
      minAvailable: 1

postgres:
  enabled: true
  password: "postgres-demo"
  persistence:
    storageClassName: local-path
    size: 5Gi
  resources:
    requests: { cpu: 200m, memory: 256Mi }
    limits:   { cpu: "1",  memory: "1Gi"  }

redis:
  enabled: true
  resources:
    requests: { cpu: 50m,  memory: 64Mi }
    limits:   { cpu: 200m, memory: 128Mi }

ingress:
  enabled: true
  host: dev.streamcast.localhost

networkPolicy:
  enabled: true

resourceQuota:
  enabled: true
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4"
    limits.memory: 8Gi
    pods: "20"
```

### 4.3 Overrides por ambiente

`values-dev.yaml`:

```yaml
environment: dev

services:
  auth:
    replicaCount: 2
    hpa: { enabled: false }

ingress:
  host: dev.streamcast.localhost
```

`values-stg.yaml`:

```yaml
environment: stg

services:
  auth:
    replicaCount: 3
    resources:
      requests: { cpu: 200m, memory: 256Mi }
      limits:   { cpu: "1",  memory: 512Mi }

postgres:
  persistence: { size: 10Gi }

ingress:
  host: stg.streamcast.localhost

resourceQuota:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "40"
```

### 4.4 `_helpers.tpl`

```gotmpl
{{- define "streamcast.labels" -}}
app.kubernetes.io/name: streamcast
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: streamcast
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "streamcast.serviceLabels" -}}
{{ include "streamcast.labels" . }}
app: {{ .svcName }}
app.kubernetes.io/component: {{ .svcName }}
{{- end -}}
```

### 4.5 Template de Deployment (loop)

```gotmpl
{{/* templates/deployment.yaml */}}
{{- range $svcName, $svc := .Values.services }}
{{- if $svc.enabled }}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ $svcName }}
  labels:
    {{- include "streamcast.serviceLabels" (dict "Release" $.Release "Chart" $.Chart "svcName" $svcName) | nindent 4 }}
spec:
  {{- if not $svc.hpa.enabled }}
  replicas: {{ $svc.replicaCount }}
  {{- end }}
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  selector:
    matchLabels:
      app: {{ $svcName }}
  template:
    metadata:
      labels:
        {{- include "streamcast.serviceLabels" (dict "Release" $.Release "Chart" $.Chart "svcName" $svcName) | nindent 8 }}
      annotations:
        checksum/config: {{ tpl (toYaml $svc.config) $ | sha256sum }}
    spec:
      serviceAccountName: {{ $svcName }}
      automountServiceAccountToken: false
      securityContext:
        runAsUser: 1000
        runAsNonRoot: true
        fsGroup: 1000
      containers:
        - name: {{ $svcName }}
          image: "{{ $.Values.global.imageRegistry }}/{{ $svc.image.repository }}:{{ $svc.image.tag }}"
          imagePullPolicy: {{ $.Values.global.imagePullPolicy }}
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef: { name: {{ $svcName }}-config }
            - secretRef:    { name: {{ $svcName }}-secrets }
          resources:
            {{- toYaml $svc.resources | nindent 12 }}
          startupProbe:
            httpGet: { path: /health/live, port: 8000 }
            periodSeconds: 5
            failureThreshold: 8
          readinessProbe:
            httpGet: { path: /health/ready, port: 8000 }
            periodSeconds: 10
          livenessProbe:
            httpGet: { path: /health/live, port: 8000 }
            periodSeconds: 20
{{- end }}
{{- end }}
```

Idem para `service.yaml`, `configmap.yaml`, `secret.yaml`, `serviceaccount.yaml`, `hpa.yaml`, `pdb.yaml` — faça loops análogos.

### 4.6 Postgres e Redis

`postgres-statefulset.yaml` e `redis-deployment.yaml` são objetos singleton — não precisam de loop. Parametrize apenas `enabled`, `image`, `persistence`, `resources`, `password`.

### 4.7 Instalar no `streamcast-dev`

Antes, limpe manifestos antigos:

```bash
kubectl delete ns streamcast-dev --wait=true
```

Agora via Helm:

```bash
helm lint charts/streamcast
helm template streamcast charts/streamcast -f charts/streamcast/values-dev.yaml | less

helm upgrade --install streamcast charts/streamcast \
    -n streamcast-dev --create-namespace \
    -f charts/streamcast/values-dev.yaml \
    --wait --timeout 3m

helm list -n streamcast-dev
kubectl -n streamcast-dev get all
```

### 4.8 Instalar no `streamcast-stg`

```bash
helm upgrade --install streamcast charts/streamcast \
    -n streamcast-stg --create-namespace \
    -f charts/streamcast/values-stg.yaml \
    --wait --timeout 3m
```

Valide:

```bash
kubectl -n streamcast-stg get pods
# auth-xxx com 3 réplicas (override do values-stg)

curl -H "Host: stg.streamcast.localhost" http://localhost:8080/api/auth/health/ready
# {"status":"ready"}
```

### 4.9 Upgrade + rollback

```bash
helm upgrade streamcast charts/streamcast \
    -n streamcast-dev -f charts/streamcast/values-dev.yaml \
    --set services.auth.image.tag=1.1

helm history streamcast -n streamcast-dev
helm rollback streamcast 1 -n streamcast-dev
```

### 4.10 `helm_drift.py`

```bash
python scripts/helm_drift.py streamcast -n streamcast-dev
# Sem drift.

# Edite manualmente algo:
kubectl -n streamcast-dev scale deployment/auth --replicas=7
python scripts/helm_drift.py streamcast -n streamcast-dev
# Detecta drift em replicas.

# Re-sync:
helm upgrade streamcast charts/streamcast \
    -n streamcast-dev -f charts/streamcast/values-dev.yaml
python scripts/helm_drift.py streamcast -n streamcast-dev
# Sem drift.
```

### 4.11 ADR 002 — Helm vs Kustomize

`docs/adr/002-helm-vs-kustomize.md`:

```markdown
# ADR 002 — Empacotamento: Helm vs Kustomize

## Status
Aceito — 2026-04-21

## Contexto
Temos ~15 manifests YAML que precisam variar por ambiente (dev, stg, prod, e
futuramente por tenant). Alternativas maduras:

- **Helm**: DSL de templates Go, lifecycle (install/upgrade/rollback),
  repositórios, ecossistema amplo.
- **Kustomize**: overlays por patches, sem DSL, integrado ao kubectl.

## Decisão
**Helm** como padrão. Justificativas principais:

1. **Lifecycle nativo** (rollback em 1 comando, histórico), ausente em Kustomize.
2. **Integração nativa** com ArgoCD (Parte 5).
3. **Ecossistema**: charts de terceiros (postgres-operator, cert-manager,
   ArgoCD, Traefik) acelerarão dev.
4. **Parametrização expressiva**: loops/conditions necessários para nosso
   multi-serviço em um chart único.

## Consequências
- Positivas: lifecycle, ecossistema, ArgoCD integration.
- Negativas: DSL custom de templates (curva inicial); manipulação de YAML
  como strings é feia em casos complexos; limites de helpers.
- Mitigação: adotar convenções (`_helpers.tpl`, labels padrão);
  `helm lint` como gate em CI; considerar Kustomize como complemento apenas se
  surgir caso (ex.: overlay mínimo para namespace operacional).
```

### 4.12 Atualizar Makefile

```makefile
install-dev:
	helm upgrade --install streamcast charts/streamcast \
	    -n streamcast-dev --create-namespace \
	    -f charts/streamcast/values-dev.yaml --wait

install-stg:
	helm upgrade --install streamcast charts/streamcast \
	    -n streamcast-stg --create-namespace \
	    -f charts/streamcast/values-stg.yaml --wait

drift:
	python scripts/helm_drift.py streamcast -n streamcast-dev
```

---

## Entregáveis da Parte 4

- [ ] `charts/streamcast/` completo, `helm lint` passa.
- [ ] `values-dev.yaml` e `values-stg.yaml`.
- [ ] `streamcast-dev` e `streamcast-stg` instalados via Helm, ambos funcionais.
- [ ] `helm upgrade --set image.tag=...` funciona.
- [ ] `helm rollback` funciona.
- [ ] `helm_drift.py` detecta drift quando existente.
- [ ] `docs/adr/002-helm-vs-kustomize.md` redigido.

---

## Critérios de aceitação

- `helm template` renderiza sem erro.
- 2 releases (`dev` e `stg`) coexistem sem colidir.
- `curl` nos dois Ingress hosts responde 200.

---

## Próximo passo

Avance para a **[Parte 5 — GitOps com ArgoCD + plano](parte-5-gitops-e-plano.md)**: instalar ArgoCD, sincronizar do git, escrever runbook, ADRs finais, plano de migração dos demais serviços.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Resiliência e operações](parte-3-resiliencia.md) | **↑ Índice**<br>[Módulo 7 — Kubernetes](../README.md) | **Próximo →**<br>[Parte 5 — GitOps com ArgoCD + plano de migração](parte-5-gitops-e-plano.md) |

<!-- nav:end -->

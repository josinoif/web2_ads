# Bloco 2 — Exercícios Resolvidos

Consolidando Workloads no cluster. Todos os exercícios sobre a **StreamCast EDU**.

---

## Exercício 2.1 — Do `docker-compose.yml` ao Deployment

**Tempo:** 30 min · **Tipo:** tradução prática

### Enunciado

Dado o trecho Compose abaixo (versão simplificada atual da StreamCast), escreva os **manifestos K8s equivalentes**: `Deployment`, `Service`, `ConfigMap`, `Secret`, com probes e limits.

```yaml
# docker-compose.yml (atual)
services:
  auth:
    image: streamcast/auth:1.0
    environment:
      LOG_LEVEL: info
      JWT_SIGNING_KEY: ${JWT_SIGNING_KEY}
      DB_URL: postgresql://auth:${DB_PASSWORD}@postgres:5432/auth
    ports:
      - "8000:8000"
    depends_on:
      - postgres
```

### Solução comentada

```yaml
# configmap
apiVersion: v1
kind: ConfigMap
metadata: { name: auth-config }
data:
  LOG_LEVEL: "info"
---
# secret
apiVersion: v1
kind: Secret
metadata: { name: auth-secrets }
type: Opaque
stringData:
  JWT_SIGNING_KEY: "demo-key"
  DB_PASSWORD: "postgres-demo"
---
# deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth
  labels: { app: auth }
spec:
  replicas: 3          # Compose tinha 1; em K8s, 3 já dá HA.
  selector:
    matchLabels: { app: auth }
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  template:
    metadata: { labels: { app: auth } }
    spec:
      containers:
        - name: auth
          image: streamcast/auth:1.0
          ports: [{ containerPort: 8000 }]
          envFrom:
            - configMapRef: { name: auth-config }
          env:
            - name: JWT_SIGNING_KEY
              valueFrom: { secretKeyRef: { name: auth-secrets, key: JWT_SIGNING_KEY } }
            - name: DB_PASSWORD
              valueFrom: { secretKeyRef: { name: auth-secrets, key: DB_PASSWORD } }
            - name: DB_URL
              value: "postgresql://auth:$(DB_PASSWORD)@postgres:5432/auth"
          resources:
            requests: { cpu: "100m", memory: "128Mi" }
            limits:   { cpu: "500m", memory: "256Mi" }
          readinessProbe:
            httpGet: { path: /health/ready, port: 8000 }
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet: { path: /health/live, port: 8000 }
            periodSeconds: 20
            failureThreshold: 3
---
# service
apiVersion: v1
kind: Service
metadata: { name: auth }
spec:
  type: ClusterIP     # não exponha NodePort em produção
  selector: { app: auth }
  ports:
    - { name: http, port: 80, targetPort: 8000 }
```

**Diferenças conceituais importantes:**

| Compose | K8s | Comentário |
|---------|-----|------------|
| `depends_on: postgres` | **Nada equivalente direto** | K8s não orquestra ordem; use `readinessProbe` que checa DB. Pod só entra no pool quando DB está pronto. |
| `ports: 8000:8000` | `Service` tipo `ClusterIP` + `Ingress` | Compose expõe para o host; K8s separa "rede do cluster" de "entrada externa". |
| `environment:` inline | `ConfigMap` + `Secret` | Separar sensível de não sensível é obrigatório no mundo K8s. |
| 1 réplica padrão | `replicas: 3` | K8s torna HA trivial; 1 réplica em produção é desperdício. |

---

## Exercício 2.2 — Diagnosticando Pods que não sobem

**Tempo:** 25 min · **Tipo:** troubleshooting

### Enunciado

Você aplicou o Deployment do `auth` e vê:

```
NAME                    READY   STATUS             RESTARTS   AGE
auth-5d7f9b4-abcde      0/1     ImagePullBackOff   0          2m
auth-5d7f9b4-fghij      0/1     ImagePullBackOff   0          2m
auth-5d7f9b4-klmno      0/1     ImagePullBackOff   0          2m
```

Depois corrige e vê:

```
auth-6b8f...            0/1     CrashLoopBackOff   5          8m
```

E por fim:

```
auth-7c2e...            0/1     Running            0          30s  (READY 0/1)
# Mas nunca fica 1/1.
```

Para cada um dos três sintomas, descreva **o que verificar** com quais comandos e **qual provável causa** está no cenário StreamCast.

### Solução comentada

### (a) `ImagePullBackOff`

**Causas possíveis:**
1. Tag inexistente no registry.
2. Registry privado sem `imagePullSecrets`.
3. Node offline de internet.
4. No k3d, imagem não importada (`k3d image import` esquecido).

**Verificação:**

```bash
kubectl describe pod auth-5d7f9b4-abcde
# Na seção Events:
# Warning  Failed  kubelet  Failed to pull image "streamcast/auth:1.0":
#     rpc error: code = Unknown desc = ... not found
```

**Na StreamCast (cluster local k3d):** provavelmente faltou `k3d image import streamcast/auth:1.0 -c streamcast`. No k3d, o cluster não enxerga o daemon Docker do host por padrão — imagens locais precisam ser importadas para os nodes.

**Correção:**

```bash
docker build -t streamcast/auth:1.0 app/auth
k3d image import streamcast/auth:1.0 -c streamcast
```

O rollout retoma automaticamente (kubelet retenta periodicamente).

### (b) `CrashLoopBackOff`

**Causas possíveis:**
1. App explode no boot (exceção).
2. App retorna exit != 0 em uso normal.
3. `livenessProbe` mata o processo antes de estabilizar (faltou `startupProbe`).
4. Config errada (env var ausente).

**Verificação:**

```bash
kubectl logs auth-6b8f... --previous
# RuntimeError: JWT_SIGNING_KEY obrigatória
```

**Na StreamCast:** provavelmente o `Secret` não foi aplicado ou a chave não está correta. Na aplicação `auth`, o `lifespan` valida `JWT_SIGNING_KEY` e levanta exceção — o Pod crasha imediatamente; Kubernetes reinicia; crasha de novo; backoff aumenta.

**Correção:**

```bash
kubectl apply -f k8s/auth/secret.yaml
# ou
kubectl create secret generic auth-secrets \
    --from-literal=JWT_SIGNING_KEY=demo-key \
    --from-literal=DB_PASSWORD=postgres-demo
```

### (c) `Running` mas nunca `1/1 READY`

**Causas possíveis:**
1. `readinessProbe` falha — dependência (DB/Redis) indisponível.
2. Probe aponta porta/caminho errados.
3. App demora a iniciar e `initialDelaySeconds` é curto demais, sem `startupProbe`.

**Verificação:**

```bash
kubectl describe pod auth-7c2e...
# Events:
# Warning Unhealthy: Readiness probe failed: HTTP probe failed with statuscode: 503
# Body: db down: connection refused
```

Também útil:

```bash
kubectl logs auth-7c2e...
# INFO ... starting
# (sem erro, mas readiness 503)
kubectl exec auth-7c2e... -- curl -s localhost:8000/health/ready
# {"detail":"db down: connection refused"}
```

**Na StreamCast:** ou o Postgres ainda não subiu (aguarde alguns segundos), ou o Service `postgres` não existe, ou o Secret com senha do Postgres está errado.

**Correção típica:**

```bash
kubectl get pods -l app=postgres   # postgres Running?
kubectl get svc postgres           # Service existe?
kubectl logs -l app=postgres       # DB subiu limpo?
```

---

## Exercício 2.3 — Rolling update sem downtime

**Tempo:** 25 min · **Tipo:** hands-on + observação

### Enunciado

1. Com o `auth` rodando (`replicas: 3`, `maxUnavailable: 0`), abra **duas** abas de terminal:
   - Aba A: `watch -n 0.5 "kubectl get pods -l app=auth"`
   - Aba B: loop de requisições:
     ```bash
     while true; do curl -s -o /dev/null -w "%{http_code}\n" \
         http://<INGRESS_OU_PORTFWD>/health/live; sleep 0.2; done
     ```
   (Dica: se não tiver Ingress ainda, use `kubectl port-forward svc/auth 8080:80` e aponte para `localhost:8080`.)

2. Execute:
   ```bash
   kubectl set image deployment/auth auth=streamcast/auth:2.0
   ```

3. Anote:
   - Quantos códigos HTTP diferentes de `200` apareceram?
   - Quanto tempo o Deployment levou para concluir o rollout (`kubectl rollout status`)?

4. Agora repita o experimento com **má configuração**:
   - Altere `maxUnavailable: 2, maxSurge: 0`.
   - Mude para `auth:3.0` (faça nova imagem).
   - Observe se aparecem `503` ou connection refused.

### Solução comentada

**Com `maxSurge: 1, maxUnavailable: 0`:**

- Aba A mostra **sempre** 3 Pods `Ready` ou mais (no pico, 4).
- Aba B mostra **100% `200`**.
- `kubectl rollout status` conclui em ~30-60s (depende do `readinessProbe.failureThreshold`).

**Com `maxSurge: 0, maxUnavailable: 2`:**

- Aba A tem momentos com apenas **1 Pod Ready**.
- Aba B pode mostrar **connection refused** ou `503` se o único Pod readyficar brevemente saturado — **ou** 100% OK se o tráfego for leve (depende do hardware).
- Pior: se `auth:3.0` quebrar e crashar, você tem **2 Pods simultaneamente indisponíveis** e só 1 serving — se o terceiro também quebrar, outage completa.

**Lição:**

- **Nunca** use `maxUnavailable > 0` para APIs críticas stateless.
- `maxSurge: 1, maxUnavailable: 0` é o padrão seguro. Custa 1 Pod extra temporariamente.
- Para workloads batch/processing, às vezes faz sentido `maxUnavailable: 25%` para economizar recursos.

**Dado observado tipicamente em laboratório:**

| Estratégia | Códigos != 200 | Tempo rollout |
|------------|----------------|----------------|
| `maxSurge:1, maxUnavail:0` | 0 | ~45s |
| `maxSurge:0, maxUnavail:2` | ~10-50 (connection refused durante janelas) | ~35s |

---

## Exercício 2.4 — Rollback sob pressão

**Tempo:** 20 min · **Tipo:** ensaio de incidente

### Enunciado

Simule um deploy ruim e o rollback:

1. Crie a imagem `streamcast/auth:3-broken` que propositalmente crasha no boot:
   ```python
   # main_broken.py
   raise RuntimeError("bug proposital")
   ```
2. Import no k3d e aplique:
   ```bash
   kubectl set image deployment/auth auth=streamcast/auth:3-broken
   ```
3. Observe: o rollout **não** completa porque os Pods novos entram em `CrashLoopBackOff`. Mas graças ao `maxUnavailable: 0`, os Pods antigos **não são derrubados** — o tráfego continua indo para eles.
4. Execute o rollback:
   ```bash
   kubectl rollout undo deployment/auth
   ```
5. Anote: quanto tempo levou para os Pods novos serem removidos e o Deployment voltar ao verde?

### Solução comentada

**Estado durante o deploy ruim:**

```
NAME                  READY   STATUS             RESTARTS   AGE
auth-old-xxx1         1/1     Running            0          10m
auth-old-xxx2         1/1     Running            0          10m
auth-old-xxx3         1/1     Running            0          10m
auth-new-yyy1         0/1     CrashLoopBackOff   3          40s
```

- `maxSurge: 1`: criou 1 Pod novo.
- Pod novo crasha; readiness nunca passa; permanece `NotReady`.
- `maxUnavailable: 0`: Deployment **não** remove antigos enquanto novo não Ready.
- **Tráfego para usuários segue 100% servido pelos antigos.** 🎯

**Rollback:**

```bash
kubectl rollout undo deployment/auth
deployment.apps/auth rolled back
kubectl rollout status deployment/auth
# deployment "auth" successfully rolled out   (1-2s)
```

O tempo é mínimo porque:

- Os Pods antigos **ainda estão Ready**.
- A única ação é deletar o Pod novo quebrado e atualizar a imagem do Deployment.

**Lição central:**

> Configurações corretas (`maxSurge: 1, maxUnavailable: 0` + probes decentes) transformam deploys ruins em **eventos invisíveis** para o usuário. Rollback é rápido porque nunca se ficou vulnerável.

Compare com o sintoma #8 da StreamCast atual: rollback era restaurar snapshot de VM (~30min + perda de dados). Com K8s, `rollout undo` leva segundos e não perde nada.

---

## Exercício 2.5 — Config vs Secret vs env-var-hardcoded

**Tempo:** 20 min · **Tipo:** decisão e segurança

### Enunciado

Para cada variável abaixo do `auth`, decida: **ConfigMap, Secret ou hardcoded no Deployment**? Justifique.

1. `LOG_LEVEL` (info/debug/warn)
2. `DB_URL` sem senha (`postgresql://auth@postgres:5432/auth`)
3. `DB_PASSWORD`
4. `JWT_SIGNING_KEY`
5. `JWT_ALGORITHM` (RS256 fixo para toda a empresa)
6. `FEATURE_MFA` (liga/desliga MFA)
7. `CORS_ORIGINS` (lista de domínios permitidos — varia por ambiente)
8. `PORT` (fixo 8000, nunca muda)
9. `SENTRY_DSN` (URL com token para APM)
10. `AUTH_TTL_MIN` (60 em prod, 5 em dev para facilitar teste)

### Solução comentada

| # | Var | Destino | Motivo |
|---|-----|---------|--------|
| 1 | `LOG_LEVEL` | **ConfigMap** | Varia por ambiente; não é segredo. |
| 2 | `DB_URL` (sem senha) | **ConfigMap** + composto com Secret | Parte pública no CM; senha vem de Secret; o Deployment monta `$(DB_PASSWORD)` interpolado. |
| 3 | `DB_PASSWORD` | **Secret** | Sensível, rotacionável. |
| 4 | `JWT_SIGNING_KEY` | **Secret** | Sensível crítico — assina tokens. |
| 5 | `JWT_ALGORITHM` | **hardcoded** (no Deployment) **ou ConfigMap** | Fixo na empresa; hardcoded é aceitável. Colocar em CM permite mudar sem rebuild. |
| 6 | `FEATURE_MFA` | **ConfigMap** | Feature flag não sensível; liga/desliga por ambiente. |
| 7 | `CORS_ORIGINS` | **ConfigMap** | Varia por ambiente; não é segredo. |
| 8 | `PORT` | **hardcoded** | Invariante da app; fixar torna o contrato óbvio. |
| 9 | `SENTRY_DSN` | **Secret** | Contém token; leak permite injeção de eventos de APM. |
| 10 | `AUTH_TTL_MIN` | **ConfigMap** | Varia por ambiente. |

**Regras operativas que emergem:**

1. **Hardcoded** quando é invariante e público.
2. **ConfigMap** quando varia por ambiente e NÃO é sensível.
3. **Secret** quando contém credencial/token/chave.
4. **Nunca** misture (ex.: URL completa com senha em CM). **Componha** em tempo de env var.

**Trecho final tipico de YAML:**

```yaml
env:
  - name: PORT
    value: "8000"                      # hardcoded
  - name: JWT_ALGORITHM
    value: "RS256"                     # hardcoded ok
  - name: LOG_LEVEL                    # CM
    valueFrom:
      configMapKeyRef: { name: auth-config, key: LOG_LEVEL }
  - name: DB_USER                      # CM
    valueFrom:
      configMapKeyRef: { name: auth-config, key: DB_USER }
  - name: DB_PASSWORD                  # Secret
    valueFrom:
      secretKeyRef: { name: auth-secrets, key: DB_PASSWORD }
  - name: DB_URL                       # composto
    value: "postgresql://$(DB_USER):$(DB_PASSWORD)@postgres:5432/auth"
  - name: JWT_SIGNING_KEY              # Secret
    valueFrom:
      secretKeyRef: { name: auth-secrets, key: JWT_SIGNING_KEY }
```

---

## Exercício 2.6 — Usar `check_deployment.py` em pipeline

**Tempo:** 25 min · **Tipo:** integração com CI

### Enunciado

1. Aplique o `auth` com probes e limits completos, e outro Deployment "ruim" (sem limits, sem probes).
2. Rode `check_deployment.py` contra os dois.
3. Transforme a execução em um **passo de CI** via GitHub Actions que:
   - Sobe um cluster `kind` temporário.
   - Aplica manifestos.
   - Roda o script.
   - Falha o workflow se houver `ERROR`.

Forneça o arquivo de workflow.

### Solução comentada

**Saída esperada:**

```bash
$ python check_deployment.py auth
OK — auth passou nas checagens básicas.
$ echo $?
0

$ python check_deployment.py demo
[ERROR] K8S-RES-REQ    nginx: sem resources.requests
[ERROR] K8S-RES-LIM    nginx: sem resources.limits
[ERROR] K8S-RD-PROBE   nginx: sem readinessProbe
[WARN ] K8S-LV-PROBE   nginx: sem livenessProbe
[ERROR] K8S-IMG-LATEST nginx: imagem usa :latest (nginx:latest)
$ echo $?
1
```

**Workflow `.github/workflows/k8s-lint.yml`:**

```yaml
name: k8s-lint

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint-and-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with: { python-version: "3.12" }

      - name: Install dependencies
        run: |
          pip install -r devops/07-kubernetes/requirements.txt

      - name: Setup kind cluster
        uses: helm/kind-action@v1
        with:
          cluster_name: ci

      - name: Apply manifests
        run: |
          kubectl create namespace streamcast-dev
          kubectl -n streamcast-dev apply -f k8s/infra/
          kubectl -n streamcast-dev apply -f k8s/auth/
          kubectl -n streamcast-dev rollout status deploy/auth --timeout=120s

      - name: Audit Deployments
        run: |
          python devops/07-kubernetes/scripts/check_deployment.py -n streamcast-dev auth
          python devops/07-kubernetes/scripts/check_deployment.py -n streamcast-dev postgres
          python devops/07-kubernetes/scripts/check_deployment.py -n streamcast-dev redis
```

**Pontos didáticos:**

- `kind` (ou `k3d`) no CI permite validar **contra um cluster real**, não apenas templates.
- O workflow falha se `check_deployment.py` retorna `exit 1`, bloqueando PR com regressão.
- Em um pipeline completo você adicionaria:
  - **`kubeconform`** para validar YAML contra schemas.
  - **`kube-score`** para boas práticas gerais.
  - **`trivy config`** para scan de segurança.

Esse padrão estabelece a base da **política como código para K8s** que o Bloco 4 expande.

---

## Próximo passo

Avance para o **[Bloco 3 — Operações](../bloco-3/03-operacoes-cluster.md)**: namespaces, RBAC, NetworkPolicy, HPA, Ingress e PVC — os elementos que transformam um Deployment funcional num sistema **operável em produção**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Workloads: do Compose ao Cluster](02-workloads.md) | **↑ Índice**<br>[Módulo 7 — Kubernetes](../README.md) | **Próximo →**<br>[Bloco 3 — Operações: isolamento, segurança, escala e entrada](../bloco-3/03-operacoes-cluster.md) |

<!-- nav:end -->

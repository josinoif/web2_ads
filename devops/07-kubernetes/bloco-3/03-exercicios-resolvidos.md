# Bloco 3 — Exercícios Resolvidos

Operações em nível de cluster. Foco em isolamento, segurança e escala da StreamCast EDU.

---

## Exercício 3.1 — Topologia de Namespaces

**Tempo:** 25 min · **Tipo:** decisão arquitetural

### Enunciado

A StreamCast tem:

- **3 ambientes**: dev, stg, prod.
- **30 universidades tenants**, com tráfego e dados completamente separados.
- **8 serviços** (`auth`, `catalog`, `player`, `transcoder`, `live`, `billing`, `notify`, `api-gateway`).
- **Componentes de operação** (log collector, ArgoCD, observabilidade).

Proponha 3 topologias de Namespaces candidatas com **prós e contras** cada. Escolha **uma** e justifique.

### Solução comentada

#### Opção A — 1 namespace por ambiente, 30 tenants compartilhando

```
streamcast-dev    → auth, catalog, ... rodando com label tenant=<id>
streamcast-stg    → idem
streamcast-prod   → idem
streamcast-ops    → ArgoCD, observability (compartilhado)
```

**Prós:** fácil gerir (3 namespaces); dedup de Pods (1 `auth` serve todos tenants, filtra internamente).
**Contras:** 1 tenant abusivo afeta outros (pouca proteção via quota); RBAC por tenant impossível; blast-radius enorme num bug de vazamento.

#### Opção B — 1 namespace por tenant, por ambiente

```
tenant-ufpb-dev, tenant-ufpb-stg, tenant-ufpb-prod
tenant-usp-dev,  tenant-usp-stg,  tenant-usp-prod
... (30 × 3 = 90 namespaces + ops)
```

**Prós:** isolamento máximo; RBAC, NetworkPolicy, Quota por tenant; blast-radius pequeno.
**Contras:** **90+ namespaces**; manutenção operacional pesada; custo de recursos (cada ns tem seu CoreDNS-cache, seus Secrets, seus Pods idênticos); upgrade de versão replicado 90x; exagero para tenants pequenos.

#### Opção C — ambientes + tenants com **NetworkPolicy por label**

```
streamcast-dev, streamcast-stg, streamcast-prod (um por ambiente)
Dentro, cada Pod tem labels: app=auth, tenant=ufpb
NetworkPolicy por tenant + ResourceQuota por tenant via LimitRange customizado
```

**Prós:** menor overhead de namespaces; ainda consegue isolamento por labels.
**Contras:** **`ResourceQuota` é por namespace, não por label** — não consegue quota por tenant dessa forma. Policy por label dá isolamento de rede, mas não de CPU/mem.

#### Escolha recomendada — híbrido

Para a StreamCast:

- **3 namespaces por ambiente** (`streamcast-{dev,stg,prod}`) para **serviços de plataforma** (auth, catalog, etc) → dedupação + escala + simplicidade.
- **N namespaces por tenant**, criados sob demanda, apenas para **tenants que justificam isolamento forte** (plano enterprise, compliance específico): `tenant-ufpb-prod`. Tenants pequenos ficam na plataforma compartilhada com labels.
- **1 namespace `streamcast-ops`** para ArgoCD, kube-state-metrics, log collector.

**Resultado:** ~5-10 namespaces típicos, não 90. Cresce linearmente com tenants enterprise, não total.

**ADR elementar:**

> Usamos topologia híbrida: namespaces por ambiente para serviços multi-tenant compartilhados e namespaces dedicados por tenant apenas para contratos enterprise. Tenants padrão são isolados por `NetworkPolicy` por label; tenants enterprise têm namespace dedicado com `ResourceQuota` e `NetworkPolicy` isolada. Justificativa: balanço entre custo operacional e isolamento proporcional ao risco do cliente.

---

## Exercício 3.2 — RBAC minimalista

**Tempo:** 30 min · **Tipo:** segurança

### Enunciado

Modele em YAML:

1. Uma `ServiceAccount` para o `auth` **sem nenhuma permissão** (e sem token montado).
2. Uma `ServiceAccount` para um CI deployer, capaz de fazer `get/list/patch` em `deployments` apenas no namespace `streamcast-stg`.
3. Uma `ServiceAccount` para o time de SRE que pode ver tudo (`view`) em **todos** os namespaces mas **não modificar** nada.

Teste cada uma com `kubectl auth can-i`.

### Solução comentada

```yaml
# 1) SA sem permissão, sem token montado
apiVersion: v1
kind: ServiceAccount
metadata:
  name: auth
  namespace: streamcast-dev
automountServiceAccountToken: false
---
# 2) SA deployer para o stg
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ci-deployer
  namespace: streamcast-ops
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployer
  namespace: streamcast-stg
rules:
  - apiGroups: ["apps"]
    resources: ["deployments", "deployments/scale"]
    verbs: ["get", "list", "patch", "update"]
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list"]     # para debug
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ci-can-deploy-stg
  namespace: streamcast-stg
subjects:
  - kind: ServiceAccount
    name: ci-deployer
    namespace: streamcast-ops
roleRef:
  kind: Role
  name: deployer
  apiGroup: rbac.authorization.k8s.io
---
# 3) SA SRE "view everywhere"
apiVersion: v1
kind: ServiceAccount
metadata:
  name: sre-observer
  namespace: streamcast-ops
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: sre-can-view-all
subjects:
  - kind: ServiceAccount
    name: sre-observer
    namespace: streamcast-ops
roleRef:
  kind: ClusterRole
  name: view               # ClusterRole embutida do K8s
  apiGroup: rbac.authorization.k8s.io
```

**Testes:**

```bash
# 1) auth não lê nada
kubectl auth can-i list pods \
  --as=system:serviceaccount:streamcast-dev:auth \
  -n streamcast-dev
# no

# 2) ci-deployer pode patchar deployment do stg
kubectl auth can-i patch deployment \
  --as=system:serviceaccount:streamcast-ops:ci-deployer \
  -n streamcast-stg
# yes

# 2b) ...mas NÃO do prod
kubectl auth can-i patch deployment \
  --as=system:serviceaccount:streamcast-ops:ci-deployer \
  -n streamcast-prod
# no

# 2c) ...e NÃO consegue criar secrets nem no stg
kubectl auth can-i create secrets \
  --as=system:serviceaccount:streamcast-ops:ci-deployer \
  -n streamcast-stg
# no

# 3) SRE pode listar tudo, mas não patchar
kubectl auth can-i list secrets \
  --as=system:serviceaccount:streamcast-ops:sre-observer \
  -n streamcast-prod
# yes

kubectl auth can-i delete pod \
  --as=system:serviceaccount:streamcast-ops:sre-observer \
  -n streamcast-prod
# no
```

**Lições didáticas:**

- **`ClusterRole` embutidas** (`view`, `edit`, `admin`, `cluster-admin`) são ótimos atalhos — não reinvente. Apenas leia o que cada uma libera.
- `Role` no namespace alvo + `RoleBinding` com SA de outro namespace é o padrão para "CI que deploya em outro ambiente".
- Nunca dê `cluster-admin` a SAs de aplicação. Isso é a receita para incidentes irreparáveis.

---

## Exercício 3.3 — NetworkPolicy default-deny + allow

**Tempo:** 25 min · **Tipo:** hands-on

### Enunciado

1. Instale Calico (ou use cluster com Cilium) para habilitar NetworkPolicy.
2. No namespace `streamcast-dev`, aplique:
   - `default-deny` para todos os Pods.
   - Allow: Pods `app=auth` podem fazer egress para `app=postgres` na porta 5432 e para `app=redis` na 6379, e DNS kube-system:53.
   - Allow: Pods `app=auth` aceitam ingress de qualquer Pod com label `role=gateway`.
3. Teste: dentro de um Pod sem labels, tente acessar `http://auth` → deve **timeout**. Dentro de um Pod com `role=gateway`, deve funcionar.

### Solução comentada

```yaml
# default-deny
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: streamcast-dev
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
# permite DNS para todos
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
  namespace: streamcast-dev
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - { protocol: UDP, port: 53 }
        - { protocol: TCP, port: 53 }
---
# auth pode egressar para postgres e redis
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: auth-egress-db-cache
  namespace: streamcast-dev
spec:
  podSelector:
    matchLabels: { app: auth }
  policyTypes: [Egress]
  egress:
    - to:
        - podSelector:
            matchLabels: { app: postgres }
      ports: [{ protocol: TCP, port: 5432 }]
    - to:
        - podSelector:
            matchLabels: { app: redis }
      ports: [{ protocol: TCP, port: 6379 }]
---
# auth aceita ingress de role=gateway
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: auth-ingress-gateway
  namespace: streamcast-dev
spec:
  podSelector:
    matchLabels: { app: auth }
  policyTypes: [Ingress]
  ingress:
    - from:
        - podSelector:
            matchLabels: { role: gateway }
      ports: [{ protocol: TCP, port: 8000 }]
```

**Testes:**

```bash
# Pod sem label role=gateway tenta acessar auth:
kubectl -n streamcast-dev run -it --rm noaccess --image=curlimages/curl \
    --restart=Never -- curl -m 3 http://auth/
# curl: (28) Connection timed out after 3001 ms

# Pod COM label role=gateway:
kubectl -n streamcast-dev run gw --image=curlimages/curl --restart=Never \
    --labels=role=gateway --command -- sleep 3600

kubectl -n streamcast-dev exec gw -- curl -s http://auth/
# {"service":"auth","log_level":"info"}
kubectl -n streamcast-dev delete pod gw
```

**Caso clássico de bug:** esquecer de permitir DNS. A `auth` começa a falhar em operações que resolvem nomes (chamada ao Postgres por DNS quebra). Sempre libere DNS em egress quando aplicar `default-deny`.

---

## Exercício 3.4 — HPA sob carga

**Tempo:** 30 min · **Tipo:** hands-on

### Enunciado

1. Configure HPA no `auth` com `min=2`, `max=8`, meta de 60% de CPU.
2. Rode um gerador de carga:
   ```bash
   kubectl run -it --rm load --image=busybox --restart=Never -- \
       sh -c 'while true; do wget -q -O- http://auth/ > /dev/null; done'
   ```
3. Abra duas abas: `watch kubectl top pods` e `watch kubectl get hpa`.
4. Documente: em quanto tempo escalou? Quantas réplicas estabilizaram? Mate o gerador e observe o scale-down.

### Solução comentada

**HPA:**

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: auth
  namespace: streamcast-dev
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
        target:
          type: Utilization
          averageUtilization: 60
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 120
    scaleUp:
      stabilizationWindowSeconds: 10
```

**Observação típica em laboratório (notebook i7, 16GB):**

| Tempo | CPU % | Réplicas |
|-------|-------|----------|
| t=0s (pré-carga) | 3% | 2 |
| t=30s (carga ativa) | 210% | 2 |
| t=60s | 180% | 4 |
| t=120s | 110% | 6 |
| t=180s | 75% | 8 (teto max) |
| ---- carga encerrada ---- | | |
| t=0 | 60% → 5% | 8 |
| t=120s | 3% | 8 (janela de estabilidade) |
| t=240s | 3% | 4 |
| t=360s | 3% | 2 (mínimo) |

**Observações didáticas:**

- **Subida é rápida** (30s): `scaleUp.stabilizationWindowSeconds: 10`.
- **Descida é lenta** (2-3 min): `scaleDown.stabilizationWindowSeconds: 120`. **Correto**: evita flapping quando carga oscila.
- **HPA é reativo**, não preditivo. Para picos de 8h da manhã (sintoma #1 da StreamCast), considere:
  - `minReplicas` mais alto em horário comercial (ajuste por CronJob, ou usar KEDA com cron trigger).
  - Pre-warming antes do horário conhecido.
- **Janela de métricas é de ~15s**. Se sua app faz picos muito curtos, HPA não reage (e nem deveria).

---

## Exercício 3.5 — `StatefulSet` com backup

**Tempo:** 30 min · **Tipo:** design

### Enunciado

Desenhe para o Postgres da StreamCast:

1. `StatefulSet` com 1 réplica + PVC de 20Gi.
2. `Service headless` (`postgres-headless`) para DNS por Pod.
3. `Service` normal (`postgres`) para clients.
4. `CronJob` que todo dia às 3h faz `pg_dump` e copia para MinIO.
5. Mencione como restaurar em desastre.

### Solução comentada

```yaml
# StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: streamcast-dev
spec:
  serviceName: postgres-headless
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
            - { name: POSTGRES_USER, value: auth }
            - { name: POSTGRES_DB, value: auth }
            - { name: POSTGRES_PASSWORD, valueFrom: { secretKeyRef: { name: postgres-secrets, key: POSTGRES_PASSWORD } } }
            - { name: PGDATA, value: /var/lib/postgresql/data/pgdata }
          volumeMounts:
            - { name: data, mountPath: /var/lib/postgresql/data }
          resources:
            requests: { cpu: "200m", memory: "512Mi" }
            limits:   { cpu: "2",    memory: "2Gi"   }
          readinessProbe:
            exec:
              command: ["pg_isready", "-U", "auth", "-d", "auth"]
            periodSeconds: 10
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: [ReadWriteOnce]
        resources: { requests: { storage: 20Gi } }
        storageClassName: local-path
---
# Services
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
# CronJob de backup
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: streamcast-dev
spec:
  schedule: "0 3 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 5
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: dump
              image: postgres:16-alpine
              command:
                - /bin/sh
                - -c
                - |
                  set -e
                  STAMP=$(date +%F-%H%M)
                  pg_dump -h postgres -U auth -d auth \
                      --format=custom > /tmp/auth-$STAMP.dump
                  mc alias set mn http://minio:9000 "$MINIO_ACCESS" "$MINIO_SECRET"
                  mc cp /tmp/auth-$STAMP.dump mn/backups/auth/
              env:
                - { name: PGPASSWORD, valueFrom: { secretKeyRef: { name: postgres-secrets, key: POSTGRES_PASSWORD } } }
                - { name: MINIO_ACCESS, valueFrom: { secretKeyRef: { name: minio-secrets, key: ACCESS_KEY } } }
                - { name: MINIO_SECRET, valueFrom: { secretKeyRef: { name: minio-secrets, key: SECRET_KEY } } }
```

**Restauração em desastre:**

```bash
# 1) Suba um Pod com tools:
kubectl -n streamcast-dev run restore --rm -it --image=postgres:16-alpine \
    --env PGPASSWORD=<senha> -- sh

# 2) Baixe o dump do MinIO (mc installed no mesmo pod ou em sidecar):
mc cp mn/backups/auth/auth-2026-04-15-0300.dump /tmp/

# 3) Restaure:
pg_restore -h postgres -U auth -d auth -c /tmp/auth-2026-04-15-0300.dump
```

**Pontos de realidade:**

- `pg_dump` é backup **lógico**; para bases grandes (>100GB) considere **WAL archiving + pgbackrest** ou snapshot do PVC.
- `StatefulSet` não backup-a sozinho. `CronJob` é quem orquestra.
- **RTO** (tempo de recuperação): depende do tamanho do dump + throughput de MinIO. Para 20Gi, ordem de minutos.
- **RPO** (perda máxima aceitável): com backup diário, até 24h de dados perdidos. Se inaceitável, use WAL shipping (incremental contínuo).
- Em produção real: **Postgres operator** (Zalando, CrunchyData) automatiza HA, backup, restore, upgrade.

---

## Exercício 3.6 — Rodando `k8s_audit.py` e fechando gaps

**Tempo:** 30 min · **Tipo:** auditoria completa

### Enunciado

1. No cluster com `auth`, `postgres`, `redis` já aplicados (ainda sem todas as boas práticas), rode `python k8s_audit.py`.
2. Para cada achado, **corrija** os manifestos correspondentes.
3. Rode de novo até sair `Sem achados`.
4. Documente as mudanças aplicadas em um `CHANGELOG.md` curto.

### Solução comentada

**Primeira execução — típica:**

```
Total: 11 achados  ERROR=5 · WARN=6
 ERROR AUD-001 streamcast-dev pod/auth-xxx            container auth sem resources.limits  (se não configurado)
 ERROR AUD-002 streamcast-dev pod/redis-yyy           container redis usa :latest
 WARN  AUD-003 streamcast-dev pod/postgres-0          container postgres sem runAsUser
 WARN  AUD-004 streamcast-dev pod/auth-xxx            usa SA 'default'
 WARN  AUD-005 streamcast-dev namespace               sem ResourceQuota
 WARN  AUD-006 streamcast-dev namespace               sem NetworkPolicy default-deny
 ...
```

**Correções iterativas:**

| Achado | Correção |
|--------|----------|
| AUD-001 | Adicionar `resources.requests/limits` em `auth`, `redis`, `postgres`. |
| AUD-002 | Fixar `redis:7.2-alpine` (não `latest`). Idem para outras imagens. |
| AUD-003 | Adicionar `securityContext.runAsUser: 999` (postgres usa UID 999) e `runAsNonRoot: true`. |
| AUD-004 | Criar `ServiceAccount: auth` e referenciar no Deployment. |
| AUD-005 | Criar `ResourceQuota` com limites realistas para o namespace. |
| AUD-006 | Criar `default-deny` NetworkPolicy + policies específicas. |

**Patch no Deployment de `auth`:**

```yaml
spec:
  template:
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
          # ... resources e probes já antes
```

**Patch em `postgres` (StatefulSet):**

```yaml
spec:
  template:
    spec:
      securityContext:
        runAsUser: 999      # UID do user postgres na imagem oficial
        fsGroup: 999        # garantir que o volume seja legível
        runAsNonRoot: true
      containers:
        - name: postgres
          # ...
```

**`CHANGELOG.md`:**

```markdown
# CHANGELOG operacional

## 2026-04-21 — Hardening inicial

### Adicionado
- ResourceQuota no namespace streamcast-dev (4 CPU / 8GiB)
- NetworkPolicy default-deny + allows específicos
- ServiceAccount dedicada para auth (sem token)
- securityContext em todos os Pods com runAsNonRoot

### Alterado
- Imagens passaram a usar tag explícita (auth:1.0, redis:7.2-alpine, postgres:16-alpine)
- Todos os containers agora têm requests/limits

### Removido
- Uso de SA 'default' pelos Pods de aplicação
```

**Última execução:**

```
Sem achados. Cluster passa nos checks básicos.
```

**Valor pedagógico do exercício:**

- Demonstra que **operar K8s é uma sequência de pequenos hardenings**, não 1 deploy mágico.
- Mostra como **auditoria automatizada** cria pressão virtuosa por qualidade.
- Dá intimidade com `securityContext`, SA, Quotas.

---

## Próximo passo

Avance para o **[Bloco 4 — Produção, Helm e GitOps](../bloco-4/04-producao-helm-gitops.md)**, onde todos esses YAMLs são empacotados como **Helm chart** parametrizável e sincronizados via **ArgoCD** a partir do git.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Operações: isolamento, segurança, escala e entrada](03-operacoes-cluster.md) | **↑ Índice**<br>[Módulo 7 — Kubernetes](../README.md) | **Próximo →**<br>[Bloco 4 — Produção: Helm, GitOps e os limites do K8s](../bloco-4/04-producao-helm-gitops.md) |

<!-- nav:end -->

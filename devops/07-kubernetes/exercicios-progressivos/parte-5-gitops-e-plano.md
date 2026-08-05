# Parte 5 — GitOps com ArgoCD + plano de migração

**Tempo estimado:** 150 min
**Pré-requisitos:** Partes 1–4 concluídas.

---

## Contexto

O chart Helm funciona. Falta o **controle automático de reconciliação**: ArgoCD observando o repositório e aplicando continuamente. Após isso, você fecha a entrega com **plano de migração**, **runbook de onboarding de tenant**, **ADR sobre GitOps**, e **reconhecimento honesto dos limites** do Kubernetes.

---

## Objetivos

- Instalar ArgoCD no cluster.
- Subir repositório (GitHub ou gitea local) com chart + `argocd/apps/`.
- Criar 2 `Application`: `streamcast-dev` e `streamcast-stg`, ambos `Healthy + Synced`.
- Observar auto-sync + selfHeal funcionando.
- Adicionar CI: lint, `helm lint`, `k8s_audit.py` em cluster kind efêmero.
- Documentar runbook de onboarding de tenant (meta: ≤ 1h).
- Documentar plano de migração dos 8 serviços da StreamCast.
- Escrever ADR 003 (ArgoCD vs Flux).
- Escrever `docs/limites-reconhecidos.md`.

---

## Tarefas

### 5.1 Instalar ArgoCD

Opção A (upstream):

```bash
kubectl create namespace argocd
kubectl apply -n argocd \
    -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd wait --for=condition=available deploy --all --timeout=180s
```

Opção B (chart Helm):

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm upgrade --install argocd argo/argo-cd \
    -n argocd --create-namespace --wait
```

Recomendo **Opção B** por ser consistente com sua filosofia (tudo Helm).

Ative port-forward e anote senha:

```bash
kubectl port-forward -n argocd svc/argocd-server 8443:443 &
kubectl -n argocd get secret argocd-initial-admin-secret \
    -o jsonpath="{.data.password}" | base64 -d; echo
```

Acesse https://localhost:8443 — user `admin`.

### 5.2 Repositório de infra no git

Se você estiver usando GitHub, `git init` no diretório `streamcast-k8s`, push para um repo público ou privado (com PAT de read-only cadastrado no ArgoCD para privados).

Para totalmente offline, suba um **gitea** no próprio cluster:

```bash
helm repo add gitea-charts https://dl.gitea.com/charts
helm upgrade --install gitea gitea-charts/gitea \
    -n gitea --create-namespace \
    --set gitea.admin.username=admin \
    --set gitea.admin.password=Admin@123 \
    --set gitea.admin.email=admin@example.com \
    --set postgresql-ha.enabled=false \
    --set postgresql.enabled=true \
    --set redis-cluster.enabled=false \
    --set redis.enabled=true
```

### 5.3 Applications ArgoCD

`argocd/apps/streamcast-dev.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: streamcast-dev
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/<seu-user>/streamcast-k8s.git
    targetRevision: main
    path: charts/streamcast
    helm:
      valueFiles: [values-dev.yaml]
  destination:
    server: https://kubernetes.default.svc
    namespace: streamcast-dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
    retry:
      limit: 5
      backoff: { duration: 10s, factor: 2, maxDuration: 3m }
```

`argocd/apps/streamcast-stg.yaml`: idem, alterando `namespace: streamcast-stg`, `valueFiles: [values-stg.yaml]`, `name: streamcast-stg`.

Aplique:

```bash
kubectl apply -f argocd/apps/streamcast-dev.yaml
kubectl apply -f argocd/apps/streamcast-stg.yaml
argocd app list
# streamcast-dev   Synced   Healthy
# streamcast-stg   Synced   Healthy
```

### 5.4 Prova de vida do GitOps

Fluxo 1 — mudança via git:

```bash
# Edite values-dev.yaml: services.auth.replicaCount: 2 → 3
git commit -am "scale auth in dev to 3"
git push

# ArgoCD detecta em ~3 min (ou force refresh):
argocd app sync streamcast-dev

kubectl -n streamcast-dev get deploy/auth
# REPLICAS 3 ← reconciliou
```

Fluxo 2 — selfHeal:

```bash
kubectl -n streamcast-dev scale deploy/auth --replicas=10
sleep 20
kubectl -n streamcast-dev get deploy/auth
# REPLICAS 3 ← ArgoCD reverteu

# Também aparece em argocd UI → Events: "Sync automatic: applied"
```

Documente em `docs/observacoes-parte5.md` os tempos observados.

### 5.5 CI mínimo no repo

`.github/workflows/ci.yml`:

```yaml
name: ci

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }

      - name: Install deps
        run: pip install -r requirements.txt

      - name: Setup Helm
        uses: azure/setup-helm@v4

      - name: Helm lint
        run: helm lint charts/streamcast

      - name: Helm template (dev)
        run: helm template streamcast charts/streamcast -f charts/streamcast/values-dev.yaml > /tmp/dev.yaml

      - name: Helm template (stg)
        run: helm template streamcast charts/streamcast -f charts/streamcast/values-stg.yaml > /tmp/stg.yaml

      - name: Validate with kubeconform
        run: |
          wget -q https://github.com/yannh/kubeconform/releases/latest/download/kubeconform-linux-amd64.tar.gz
          tar xf kubeconform-linux-amd64.tar.gz
          ./kubeconform -summary /tmp/dev.yaml
          ./kubeconform -summary /tmp/stg.yaml

  audit-on-kind:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements.txt

      - uses: helm/kind-action@v1
        with: { cluster_name: ci }

      - name: Install chart
        run: |
          kubectl create namespace streamcast-dev
          helm upgrade --install streamcast charts/streamcast \
              -n streamcast-dev -f charts/streamcast/values-dev.yaml \
              --wait --timeout 3m

      - name: Audit
        run: |
          python scripts/k8s_audit.py -n streamcast-dev
          python scripts/check_deployment.py -n streamcast-dev auth
```

### 5.6 ADR 003 — ArgoCD vs Flux

`docs/adr/003-argocd-vs-flux.md`:

```markdown
# ADR 003 — GitOps controller: ArgoCD vs Flux

## Status
Aceito — 2026-04-21

## Contexto
Precisamos de um operador GitOps no cluster para reconciliar continuamente
estado desejado (git) e real (cluster). As duas opções maduras da CNCF:
- **ArgoCD** (graduated): UI web rica, Application CRD, ApplicationSet para
  multi-tenant, integração com SSO empresarial, foco em operadores.
- **Flux v2** (graduated): arquitetura mais modular (source-controller,
  kustomize-controller, helm-controller), CLI-first, integração Terraform
  e GitOps Toolkit mais extensível.

## Decisão
**ArgoCD** para o MVP. Justificativas:
1. **UI web** ajuda no aprendizado e operação por times mistos.
2. **ApplicationSet** com matrix cobre naturalmente 30 tenants × 3 ambientes.
3. **Onboarding mais rápido** para dev júnior — a UI explica sync/drift
   visualmente.
4. Maior volume de material/comunidade em português hoje.

## Consequências
- Positivas: UI, ApplicationSet, SSO, comunidade.
- Negativas: mais "opinado" (Application CRD é pesada); CLI é menos poderosa
  que a de Flux.
- Mitigação: revisitar em 6 meses se a escala multi-cluster exigir recursos
  avançados de Flux (ex.: políticas em `OCIRepository`).
```

### 5.7 Runbook de onboarding de tenant

`docs/runbook-onboarding-tenant.md`:

```markdown
# Runbook — Onboarding de novo tenant (universidade)

Meta: **≤ 1 hora** da solicitação à universidade operante no ambiente `dev`.

## Pré-requisitos
- Responsável de plataforma com permissão push no repo `streamcast-k8s`.
- Dados do tenant: nome, subdomínio pretendido (ex.: `ufpb.streamcast.edu.br`).
- Credenciais iniciais geradas (via `openssl rand`), armazenadas em Bitwarden/Vault.

## Passo a passo

### 1. Criar arquivo de values do tenant
`charts/streamcast/tenants/ufpb.yaml`:
```yaml
tenant:
  id: ufpb
  name: "UFPB"
  host: ufpb.streamcast.localhost
  # credenciais específicas
```

### 2. Atualizar ApplicationSet
Adicionar `{tenant: "ufpb"}` ao `ApplicationSet` matrix generator no arquivo
`argocd/appset-tenants.yaml`.

### 3. Abrir PR
Título: `onboard: tenant UFPB`
Descrição: usar template PR que inclui checklist.

### 4. Revisão
- SRE confirma quota.
- Segurança confirma separação de credentials.
- Aprovação.

### 5. Merge
- ArgoCD detecta alterações em ~3 min (ou via webhook).
- 3 Applications são criadas: `ufpb-dev`, `ufpb-stg`, `ufpb-prod` (esta última
  pode exigir approval manual).

### 6. Validação
- `kubectl get ns | grep ufpb`
- `curl -H "Host: ufpb.streamcast.localhost" http://.../api/auth/health/ready`
- Tenant admin recebe URL e credencial via canal seguro.

## Cronometragem de referência
| Passo                  | Tempo alvo |
|-----------------------|------------|
| Editar values         | 5 min      |
| PR e review           | 15-30 min  |
| ArgoCD sync           | 5 min      |
| Validação + handoff   | 10 min     |
| **Total**             | **~45 min** |
```

### 5.8 Plano de migração

`docs/plano-migracao.md`:

```markdown
# Plano de migração da StreamCast EDU para Kubernetes

## Ondas

### Onda 0 — Preparação (atual, Partes 1–5)
- Cluster local reproduzível (k3d + Calico).
- Serviço `auth` em Kubernetes, com Helm + ArgoCD.
- Equipe familiar com probes, HPA, NetworkPolicy, RBAC.

### Onda 1 — Stateless APIs (2 semanas)
Migrar: `auth`, `catalog`, `api-gateway`, `notify`.
- Já estão próximas do 12-factor.
- Mantém Postgres e Redis em VMs por enquanto (externalName Services).
- Sucesso = 50% do tráfego servido por K8s, 0 downtime.

### Onda 2 — Workers e jobs (2 semanas)
Migrar: `billing` (CronJob), `transcoder` (Deployment + HPA por fila Redis via KEDA).
- Preserva VMs de banco ainda.
- Sucesso = jobs do `billing` 100% em K8s.

### Onda 3 — Streaming ao vivo (3 semanas)
Migrar: `live`, `player`.
- `live` tem WebSocket + ingest RTMP — requer Ingress especial (stream proxy).
- Envolve rede UDP, mais pegadinhas.
- Sucesso = aulas ao vivo 100% em K8s.

### Onda 4 — Dados (6 semanas)
Migrar Postgres + Redis:
- Postgres: usar Zalando Postgres-Operator (ou RDS se nuvem).
- Redis: usar Redis Operator.
- **Backup + replicação multi-AZ** antes de cortar.
- Sucesso = VMs de `vm-data` desligadas.

### Onda 5 — Descomissionamento (1 semana)
- Desligar `vm-app-1` e `vm-app-2`.
- Auditoria final.
- Retrospectiva.

## Riscos e mitigações
| Risco | Mitigação |
|-------|-----------|
| Custo cloud inesperado | Cluster on-premises primeiro; medir. |
| Downtime em migração de Postgres | Replicação lógica (pglogical), cutover em janela de manutenção. |
| Regressão de latência | Canary por tenant, comparando p95. |
| Time não dominar K8s | Pair programming + plantão dedicado nas Ondas 1–2. |

## Métricas de sucesso
- SLA > 99.5% durante e após migração.
- DORA: Lead Time ↓ 50%, Change Failure Rate ↓ 30%.
- Onboarding de tenant ≤ 1 hora.
- 0 incidentes críticos relacionados a migração.
```

### 5.9 Limites reconhecidos

`docs/limites-reconhecidos.md`:

```markdown
# Limites reconhecidos do Kubernetes na StreamCast

Kubernetes é um **meio**, não um **fim**. Ele **não resolve**:

1. **Bugs de aplicação.** Memory leaks, loops infinitos, race conditions
   continuam existindo. Cluster só os torna mais visíveis.

2. **Dados.** `kubectl delete pvc` mata Postgres. Backup (pg_dump + Velero)
   é **nossa** responsabilidade.

3. **Segurança em profundidade.** K8s dá primitivas (RBAC, NetworkPolicy,
   Pod Security Standards). CVEs em imagens, image signing, supply chain
   segurança, segredos rotacionados — **ainda precisam ser resolvidos**
   (Módulo 9).

4. **Observabilidade.** Logs/metrics/tracing reais exigem stack adicional
   (Prometheus, Grafana, Loki, Tempo) — Módulo 8.

5. **Custo.** Cluster operado bem custa: 2-3 engenheiros + infraestrutura.
   Para cargas pequenas, Docker Compose + monitoramento simples pode ser
   melhor.

6. **Latência de arranque.** Cold-start de Pods é de segundos, não ms.
   Para cargas extremas de FaaS, considere Knative ou lambdas nativas.

7. **Aplicações legado.** Apps que dependem de estado local, IP fixo,
   cron interno, `ps` para monitorar "outros processos" — exigem
   refatoração. Lift-and-shift cego fracassa.

8. **Cultura.** Processo de PR, revisão, testes, observabilidade, SRE —
   **precisa existir**. K8s não substitui o "The Three Ways" (Módulo 1).

## O que ainda precisa ser feito para ir a produção real
- Upgrade do cluster para **control plane em HA** (etcd 3 nós, apiserver 3 réplicas).
- **cert-manager + Let's Encrypt** para TLS automático.
- **Velero** com backup multi-região.
- **Prometheus + Grafana + Alertmanager** (Módulo 8).
- **Sealed Secrets + Vault** em produção (Módulo 9).
- **CIS Benchmark** e hardening revisado.
- **Políticas OPA Gatekeeper** ou Kyverno como guard-rails no admission controller.
- **Chaos engineering** (Litmus ou similar) para validar self-healing.
- **SRE playbooks** — Runbook por serviço, SLO por serviço, escalação.
```

### 5.10 README final

Atualize o `README.md` do repo com:

- Descrição do projeto.
- Arquitetura (diagrama Mermaid).
- Como usar (`make up && make install-dev`).
- Prints do ArgoCD UI (Healthy + Synced).
- Prints de `k8s_audit.py` sem ERROR.
- Links para ADRs e plano.

---

## Entregáveis da Parte 5

- [ ] ArgoCD instalado e acessível.
- [ ] 2 Applications (`streamcast-dev`, `streamcast-stg`) Healthy + Synced.
- [ ] Workflow de CI verde no GitHub.
- [ ] `docs/adr/003-argocd-vs-flux.md`.
- [ ] `docs/runbook-onboarding-tenant.md`.
- [ ] `docs/plano-migracao.md`.
- [ ] `docs/limites-reconhecidos.md`.
- [ ] README com arquitetura + evidências.

---

## Critérios de aceitação

- Outro dev consegue `git clone`, `make up`, `make install-dev` e ver tudo funcional em **< 10 min** do zero.
- Runbook executado por terceiro (colega) em **≤ 1 hora** para onboardar tenant fake.
- Plano de migração é **defensável** por ondas — riscos e mitigações claros.
- Limites reconhecidos são **honestos** — a entrega não vende "K8s resolve tudo".

---

## Próximo passo: entrega avaliativa

Com as 5 partes finalizadas, consolide o repositório final conforme a **[Entrega Avaliativa](../entrega-avaliativa.md)** e submeta o link para o professor.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 4 — Empacotamento com Helm](parte-4-helm.md) | **↑ Índice**<br>[Módulo 7 — Kubernetes](../README.md) | **Próximo →**<br>[Entrega Avaliativa do Módulo 7](../entrega-avaliativa.md) |

<!-- nav:end -->

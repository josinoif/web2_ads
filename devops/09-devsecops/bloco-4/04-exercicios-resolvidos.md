# Bloco 4 — Exercícios resolvidos

> Leia [04-k8s-producao.md](./04-k8s-producao.md) antes. Os exercícios exigem um cluster local k3d funcionando.

---

## Exercício 1 — Migrar para PSS `restricted`

**Enunciado.** O namespace `medvault-prod` não tem PSS. Descreva o plano de migração para `restricted` sem quebrar produção, em 4 passos.

**Resposta.**

1. **Observar** (1 sprint): aplicar labels `pod-security.kubernetes.io/warn=restricted` e `audit=restricted` no namespace. Não bloqueia, mas emite warn no apply e preenche audit log.
2. **Inventariar violações** via warn/audit; listar Deployments com `runAsNonRoot: false`, `readOnlyRootFilesystem: false`, `capabilities` não dropadas.
3. **Corrigir incrementalmente** (1–2 sprints): PR por Deployment ajustando `securityContext`, adicionando `emptyDir` para `/tmp`, `resources.limits`. Rodar testes para confirmar que a aplicação ainda funciona.
4. **Enforce** quando warn parar de aparecer por 2 semanas seguidas. Upgrade do label para `enforce=restricted`. Manter `warn` e `audit` para continuar auditando exceções.

Observação: workloads legados que **genuinamente** não conseguem rodar em restricted (raro, mas existe — ex.: Prometheus node-exporter) ficam em namespace separado, com label `baseline` e documentação explícita.

---

## Exercício 2 — NetworkPolicy default-deny

**Enunciado.** Aplique `default-deny-all` em `medvault-prod` e depois libere apenas (a) prontuario → postgres na porta 5432, (b) DNS. Teste que curl para `google.com` de dentro de um Pod dê timeout.

**Resposta.**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny-all, namespace: medvault-prod }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-prontuario-egress, namespace: medvault-prod }
spec:
  podSelector: { matchLabels: { app: prontuario } }
  policyTypes: [Egress]
  egress:
    - to:
        - podSelector: { matchLabels: { app: postgres } }
      ports:
        - { protocol: TCP, port: 5432 }
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
          podSelector: { matchLabels: { k8s-app: kube-dns } }
      ports:
        - { protocol: UDP, port: 53 }
```

Validação:

```bash
kubectl -n medvault-prod run test --rm -it --image=alpine \
  --labels=app=prontuario -- sh
# dentro:
apk add -q curl
curl -m 3 http://google.com     # timeout
nslookup postgres               # deve funcionar (DNS liberado)
nc -zv postgres 5432            # deve conectar
```

Se qualquer um desses resultados não acontecer:

- DNS não funciona → faltou regra para kube-dns.
- `google.com` conecta → o CNI não está aplicando policy; confirmar Calico/Cilium em vez de kindnet.

---

## Exercício 3 — Auditoria RBAC

**Enunciado.** Execute `python rbac_audit.py` (ou `--namespace medvault-prod`) no cluster e interprete os achados. Proponha ações para os 3 piores achados.

**Resposta esperada.**

Saída simulada:

```
Auditoria RBAC
id        severidade  alvo                             descricao
RBAC-001  high        default/integrador               SA tem cluster-admin via int-admin-bind
RBAC-002  medium      editor-tudo                      regra com verbs=['*']: {...}
RBAC-003  medium      editor-tudo                      regra com resources=['*']: {...}
RBAC-004  medium      medvault-prod/prontuario-worker  Deployment usa default ServiceAccount
```

Ações:

1. **RBAC-001**: remover `ClusterRoleBinding` e recriar SA `integrador` com `Role` específica (apenas `get,list,watch` em `ConfigMaps` e `Secrets` do seu ns). Se `integrador` realmente precisa escrever em múltiplos ns, use `RoleBinding` por ns, **não** `cluster-admin`.
2. **RBAC-002/003**: substituir `editor-tudo` por `Role`s por recurso; em ~90% dos casos o app precisa apenas de `get/list/watch` em `ConfigMap`/`Secret`/`Pod`. Wildcard no verbo ou recurso sinaliza que ninguém fez due diligence.
3. **RBAC-004**: criar ServiceAccount `prontuario-worker` específica, `RoleBinding` mínima, e alterar o Deployment: `spec.template.spec.serviceAccountName: prontuario-worker`.

---

## Exercício 4 — Migrar de ConfigMap para Sealed Secrets

**Enunciado.** Auditoria encontrou `DATABASE_URL` em ConfigMap. Descreva passos do plano de remediação com Sealed Secrets (instalação já feita).

**Resposta.**

1. **Rotacionar** a senha **antes** de qualquer coisa. ConfigMap é public-ish (qualquer SA com permissão de ns lê). Considere comprometido.
2. **Criar Secret local** (arquivo não commitado):
   ```bash
   kubectl create secret generic db-creds \
     --from-literal=DATABASE_URL='postgres://user:NOVASENHA@host/db' \
     --dry-run=client -o yaml > /tmp/db-creds.yaml
   ```
3. **Selar**:
   ```bash
   kubeseal --format yaml < /tmp/db-creds.yaml > k8s/medvault-prod/db-creds.sealed.yaml
   rm /tmp/db-creds.yaml
   ```
4. **Ajustar Deployment** para consumir o Secret em vez do ConfigMap:
   ```yaml
   envFrom:
     - secretRef: { name: db-creds }
   ```
   (remover `configMapRef` anterior)
5. **Commit**: o arquivo `.sealed.yaml` é seguro no git; o original nunca esteve.
6. **Apply**: ArgoCD/`kubectl apply -f` → controller descriptografa e cria o Secret real.
7. **Remover o ConfigMap legado** com `kubectl delete cm`.
8. **Auditar** via `rg`/`git log -p -- k8s/` que `DATABASE_URL` não aparece em claro em nenhum commit **atual** (passado já foi: considere comprometido, ver item 1).

---

## Exercício 5 — Audit log e detecção

**Enunciado.** Uma madrugada, Grafana mostra spike de `kubectl exec` contra `medvault-prod`. Sem ser requisitado, audit log é o que te salva. Escreva uma consulta LogQL que mostra, do audit log, quem fez `exec` fora do horário comercial (19h–6h) na última semana.

**Resposta.**

```logql
{job="k8s-audit"}
  | json
  | objectRef_resource="pods"
  | objectRef_subresource="exec"
  | user_username != ""
  | __error__=""
  | line_format "{{.requestReceivedTimestamp}} {{.user_username}} -> {{.objectRef_namespace}}/{{.objectRef_name}}"
```

Para filtrar por horário, a maneira mais robusta é transformar `requestReceivedTimestamp` e filtrar via `| label_format` + `label_filter`:

```logql
{job="k8s-audit"}
  | json
  | objectRef_resource="pods"
  | objectRef_subresource="exec"
  | label_format hora=`{{ (toDate "2006-01-02T15:04:05Z" .requestReceivedTimestamp).Hour }}`
  | hora < 6 or hora >= 19
```

Alternativa: exportar via `logcli` e filtrar em Python.

Ações derivadas:

- Alerta no Alertmanager: `sum(rate(audit_log_exec_total[5m])) > 0 and ON() hour() < 6`.
- Runbook: IR lead confirma ação com dono da SA; se não autorizado, isolar o namespace, rotacionar tokens, abrir incidente.

---

## Exercício 6 — Postmortem de incidente de segurança

**Enunciado.** Contexto: chave AWS foi commitada e detectada por bot em 12 minutos. Atacante usou por 40 minutos para iniciar instâncias EC2 (custo ~ US$ 400). Escreva (em 10 linhas) as seções **Timeline**, **Root cause** e **Actions** de um postmortem blameless.

**Resposta.**

**Timeline (UTC-3):**

- `02:14` Dev `alice` faz `git push` com `.env` commitado (bug em script `setup-local.sh`).
- `02:26` Bot externo encontra a chave via GitHub search API.
- `02:27` Uso indevido inicia: `RunInstances` em `us-east-1`.
- `03:07` Alerta de billing AWS dispara (gasto > baseline).
- `03:11` On-call confirma anomalia; revoga chave em IAM; para instâncias.
- `03:20` Incidente contido. Custo final: US$ 402,30.

**Root cause:**

O script `setup-local.sh`, herdado de 2022, gera `.env` local a partir de template; em 2024 alguém alterou o path para dentro do repositório por engano; ausência de pre-commit hook para `.env`; ausência de `.gitignore` no novo diretório. Três barreiras (hook, `.gitignore`, revisão humana da PR anterior) estavam ausentes simultaneamente.

**Actions:**

| # | Ação | Dono | Prazo |
|---|------|------|-------|
| 1 | Adicionar pre-commit `gitleaks` obrigatório no repo e onboarding | @bob | 1 semana |
| 2 | `.gitignore` global (root) com `.env`, `.env.*`, `*.pem` | @carol | 2 dias |
| 3 | `setup-local.sh` escreve `.env` em `/tmp/medvault/` (fora do repo) | @alice | 1 semana |
| 4 | Ativar GitHub secret scanning push protection | @bob | 1 dia |
| 5 | Criar cota de billing com alerta imediato (gatilho < 15 min) | @diego | 3 dias |

Tom blameless: *"o problema foi no processo, não na pessoa — alice não precisava ser a última barreira."*

---

## Autoavaliação

- [ ] Aplico PSS `restricted` sem quebrar prod.
- [ ] Configuro NetworkPolicy default-deny + allows precisos e testo negativamente.
- [ ] Faço auditoria RBAC regular (`rbac_audit.py`).
- [ ] Migro segredos para Sealed Secrets ou ESO, sem deixar ConfigMap com credenciais.
- [ ] Configuro audit log e consulto via LogQL para detecção.
- [ ] Escrevo postmortem blameless com timeline, root cause e ações datadas.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Segurança do cluster em produção](04-k8s-producao.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](../README.md) | **Próximo →**<br>[Exercícios progressivos — Módulo 9 (DevSecOps)](../exercicios-progressivos/README.md) |

<!-- nav:end -->

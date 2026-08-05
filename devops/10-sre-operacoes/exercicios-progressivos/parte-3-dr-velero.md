# Parte 3 — Disaster Recovery real com Velero

> **Meta.** DR deixa de ser "temos backup" e vira "temos **restore validado** por game day, com RPO e RTO medidos".

---

## Contexto

Do PBL, achado #4 (nunca fizemos DR real). Após essa parte, PagoraPay pode afirmar — com evidência — que recupera do pior cenário em tempo aceitável.

---

## Passo 1 — Instalar Velero + MinIO

Siga o [Bloco 3](../bloco-3/03-disaster-recovery.md). Valide:

```bash
velero version
velero backup-location get  # deve estar "Available"
```

Copie `dr_simulator.py` do Bloco 3 para `scripts/`.

## Passo 2 — App de exemplo em `pagora` com dados

```bash
kubectl create ns pagora

# DB de exemplo com PVC
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pg-data
  namespace: pagora
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 1Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ledger-db
  namespace: pagora
spec:
  replicas: 1
  selector: { matchLabels: { app: ledger-db } }
  template:
    metadata:
      labels: { app: ledger-db }
    spec:
      containers:
        - name: pg
          image: postgres:15-alpine
          env:
            - { name: POSTGRES_PASSWORD, value: "pg" }
            - { name: POSTGRES_DB, value: "app" }
          ports: [{ containerPort: 5432 }]
          volumeMounts:
            - { name: data, mountPath: /var/lib/postgresql/data }
      volumes:
        - name: data
          persistentVolumeClaim:
            claimName: pg-data
---
apiVersion: v1
kind: Service
metadata: { name: ledger-db, namespace: pagora }
spec:
  ports: [{ port: 5432, targetPort: 5432 }]
  selector: { app: ledger-db }
EOF

# Insere dados
kubectl -n pagora wait --for=condition=Ready pod -l app=ledger-db --timeout=120s
kubectl -n pagora exec deploy/ledger-db -- \
  psql -U postgres -d app -c \
  "CREATE TABLE movimentos(id SERIAL PRIMARY KEY, valor NUMERIC);
   INSERT INTO movimentos(valor) SELECT random()*1000 FROM generate_series(1,1000);"
```

Confirme: `SELECT count(*) FROM movimentos;` → 1000.

## Passo 3 — Backup agendado

`k8s/velero-schedule.yaml`:

```yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: pagora-daily
  namespace: velero
spec:
  schedule: "0 2 * * *"
  template:
    includedNamespaces: [pagora]
    ttl: "168h"
    defaultVolumesToFsBackup: true
```

Aplicar:

```bash
kubectl apply -f k8s/velero-schedule.yaml
```

Backup imediato para teste:

```bash
velero backup create pagora-manual --include-namespaces pagora \
  --default-volumes-to-fs-backup --wait
velero backup describe pagora-manual --details
```

## Passo 4 — DR Drill (exercício de restauração)

Marque a hora e simule o desastre:

```bash
DRILL_START=$(date +%s)

# Desastre simulado
kubectl delete ns pagora

# Restore em namespace alternativo (pagora-dr)
velero restore create pagora-dr-drill \
  --from-backup pagora-manual \
  --namespace-mappings pagora:pagora-dr \
  --wait

# Validar
kubectl -n pagora-dr wait --for=condition=Ready pod -l app=ledger-db --timeout=180s
kubectl -n pagora-dr exec deploy/ledger-db -- \
  psql -U postgres -d app -c "SELECT count(*) FROM movimentos;"

DRILL_END=$(date +%s)
echo "RTO observado: $((DRILL_END - DRILL_START)) segundos"
```

Registre o RTO em `docs/dr-playbook.md`.

## Passo 5 — `docs/dr-playbook.md`

Conteúdo:

1. **Visão geral** — padrões escolhidos por sistema (Backup/Pilot/Warm/Active).
2. **Cenários** (≥ 3):
   - Cluster K8s perdido.
   - DB corrompido.
   - Região inteira fora.
3. Para cada cenário:
   - RPO alvo, RTO alvo.
   - **RPO medido, RTO medido** (preenchido após drill).
   - Procedimento passo a passo (runbook compact).
   - Plano B.
4. **Calendário de testes** (mínimo mensal).

## Passo 6 — Validar com `dr_simulator.py`

Crie `scripts/dr-cenarios.yaml`:

```yaml
cenarios:
  - nome: "cluster-perdido"
    rpo_fonte_min: 5
    etapas:
      - { nome: "detectar", minutos: 5 }
      - { nome: "decidir DR", minutos: 5 }
      - { nome: "provisionar cluster", minutos: 10 }
      - { nome: "velero restore", minutos: 12 }
      - { nome: "validar", minutos: 5 }

  - nome: "db-corrompido"
    rpo_fonte_min: 1
    etapas:
      - { nome: "detectar", minutos: 2 }
      - { nome: "diagnostico", minutos: 8 }
      - { nome: "PITR", minutos: 20 }
      - { nome: "validar", minutos: 5 }
```

```bash
python scripts/dr_simulator.py scripts/dr-cenarios.yaml \
  --rpo-alvo-min 5 --rto-alvo-min 60
```

Inclua a saída em `docs/dr-playbook.md`.

## Passo 7 — Runbook dedicado

`docs/runbooks/dr-cluster-lost.md`:

```markdown
# Runbook: Perda total do cluster pagora-prod

## Pre-condicoes
- Backup Velero mais recente = Completed.
- Credenciais MinIO/S3 validas.
- IaC (OpenTofu/Pulumi) aplicavel.

## Passo 1 - Provisionar cluster novo
    cd infra/tofu && tofu apply -auto-approve
    kubectl config use-context pagora-dr

## Passo 2 - Reinstalar Velero
    velero install --from-backup <params>

## Passo 3 - Restore
    velero restore create pagora-restore \
      --from-backup pagora-$(date -d yesterday +%Y%m%d-0200) \
      --wait

## Passo 4 - Migrations
    kubectl -n pagora run migrate --rm -it \
      --image=ledger:v1.4.2 -- python -m alembic upgrade head

## Passo 5 - DNS e LB
    # Atualizar DNS externo para apontar ao novo LB.

## Criterio de sucesso
    curl -f https://pagora.example/healthz x3 com intervalo 30s.

## Plano B
Restore manual de dump Postgres (scripts/pg-restore.sh) + `kubectl apply -k`.

## Ultima execucao
<preencha apos drill>
```

## Passo 8 — Makefile

```makefile
.PHONY: dr-backup dr-restore dr-simulate

dr-backup:
	velero backup create pagora-$(shell date +%Y%m%d-%H%M) \
	  --include-namespaces pagora \
	  --default-volumes-to-fs-backup --wait

dr-restore:
	@echo "Uso: make dr-restore BACKUP=<name> TARGET_NS=<ns>"
	velero restore create --from-backup $(BACKUP) \
	  --namespace-mappings pagora:$(TARGET_NS) --wait

dr-simulate:
	python scripts/dr_simulator.py scripts/dr-cenarios.yaml \
	  --rpo-alvo-min 5 --rto-alvo-min 60
```

Commit:

```bash
git add -A && git commit -m "feat(sre-p3): velero + dr playbook + drill + simulator"
```

---

## Entrega

- Velero instalado + MinIO + Schedule diário.
- DR drill executado (namespaces `pagora` → `pagora-dr`) com RTO registrado.
- `docs/dr-playbook.md` com cenários, RPO/RTO **medidos**.
- `docs/runbooks/dr-cluster-lost.md`.
- `scripts/dr-cenarios.yaml` + saída do simulator.
- Makefile com alvos `dr-backup`, `dr-restore`, `dr-simulate`.

## Critérios de aceitação

- [ ] Restore traz **dados reais** (count de `movimentos` = 1000) — não só manifests vazios.
- [ ] RTO do drill está documentado e condiz com alvo (ou discrepância explicada).
- [ ] `dr_simulator.py` identifica gaps (cenários que excedem alvo).
- [ ] Runbook tem critério de sucesso objetivo.
- [ ] Schedule está ativo (`velero schedule get`).

## Bônus

- Configurar **pgBackRest** sidecar para WAL streaming → reduzir RPO para < 1 min.
- Backup para bucket S3 **real** (AWS/Backblaze B2/Cloudflare R2) além de MinIO local.
- Drill entre **clusters k3d diferentes** (simular outra região).
- Playbook de migração DNS documentado (TTL baixo, quem aciona).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — Programa de Chaos Engineering](parte-2-chaos-engineering.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Parte 4 — Incident Command System + Tabletop](parte-4-incident-command.md) |

<!-- nav:end -->

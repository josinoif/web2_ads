# Tutorial — Catálogo com deduplicação (MongoDB + MinIO)

**Lab:** [lab-catalogo-mongodb](lab-catalogo-mongodb/) · API `http://127.0.0.1:8092`  
**Teoria:** [teoria.md](teoria.md) §5–8 · [glossario](glossario.md)

> **Caminho completo** após o [tutorial Postgres](tutorial-entrega-postgres.md).  
> **Mesmo portal de entregas** — agora a dor é espaço (turma manda o mesmo PDF) e RPO do volume.

---

## Parte A — Tecnologia (o essencial)

| Peça | Papel |
|------|--------|
| MinIO | Bytes com key `sha256/<hash>` (CAS **definido pela app**) |
| Mongo `blobs` | Índice do hash + `n_referencias` |
| Mongo `entregas` | Registro lógico (aluno, disciplina, status) |
| Dedup | Mesmo SHA → não re-Put (ou head já existe); incrementa refcount |
| `read_from_secondary_sim` | **Analogia** de catálogo atrasado (snapshot local) — **não** é replica set Mongo nem propriedade do MinIO |
| `X-Integridade` | Soft (padrão): reporta `ok`/`falha` e ainda envia o body; `REJECT_ON_INTEGRITY_FAIL=1` → **409** (paridade com lab Postgres) |

```text
POST /entregas
  sha = SHA-256(bytes)
  se blob existe → n_referencias++
  senão → PutObject + insert blobs
  insert entregas
```

> **Simplificações:** refcount sem GC atrasado / sem DELETE concorrente; sem corrida no primeiro Put do mesmo hash; MinIO single-node sem dedup nativa.  
> Soft verify: se `X-Integridade: falha`, o lab ainda envia o arquivo. Com `./scripts/set-reject-integrity.sh 1` → **409**. Experimento completo de corrupção: lab Postgres (`provar-integridade-falha.sh`).

---

## Parte B — Contexto

Turma inteira manda o PDF modelo. Sem dedup na app, o bucket multiplica o mesmo arquivo. Com CAS, um objeto serve N entregas — e “apaguei minha entrega” só remove o blob quando ninguém mais referencia.

Listagem do catálogo pode atrasar (ponte leve ao [03](../03-consistencia-cap/)): **listagem desatualizada ≠ arquivo perdido**. O blob já pode estar no MinIO.

---

## Parte C — Lab

### C.1 Subir

Encerre o lab Postgres se estiver no ar (`docker compose down -v` lá).

```bash
cd sistemas-distribuidos/08-armazenamento-arquivos/lab-catalogo-mongodb
./scripts/up.sh
./scripts/status.sh
```

### C.2 Experimento 1 — Dedup (prova de escala de storage)

```bash
./scripts/provar-dedup.sh
```

**Esperado:** segundo upload com `deduplicado: true`; `n_objetos_minio` = **1**; `n_referencias` = **2**.  
Anote: **N entregas, 1 objeto** — a dedup foi da **aplicação**.

### C.3 Experimento 2 — Refcount ao apagar

```bash
./scripts/provar-refcount.sh
```

**Esperado:** primeiro `DELETE` → `removeu_objeto_minio: false`; segundo → `true`.

### C.4 Experimento 3 — Listagem “stale” (catálogo atrasado)

```bash
./scripts/provar-listagem-stale.sh
```

**Esperado:** com sim ligada, `leitura: stale_sim` **não** mostra o upload novo; ao desligar, listagem completa. O blob **já** estava no MinIO.

> Isto **não** simula secondary do Mongo nem listagem eventual do S3 — só a ideia “catálogo atrasado ≠ arquivo perdido”.

### C.5 Experimento 4 — Perda do volume (**RPO** / sem backup)

```bash
./scripts/provar-perda-volume.sh
```

**Esperado:** entregas ainda no Mongo; download **404** “blob ausente”. Metadado sozinho não recupera o PDF.

> Depois deste Exp. o bucket está vazio — rode o Exp. 5 **ou** `docker compose down -v && ./scripts/up.sh` antes de outros testes.

### C.6 Experimento 5 — Backup → wipe → restore (**prova positiva** de proteção)

```bash
./scripts/provar-backup-restore.sh
```

**Esperado:** após wipe, 404; após `mc mirror` do backup, download **200** com `X-Integridade: ok`.  
Isto **não** é cluster/erasure — é o mínimo didático de “backup do storage reduz RPO”.

> **`mc`:** cliente da linha de comando MinIO, rodado via serviço Compose `minio-init` (sem instalar no host).  
> **Produção:** o mesmo tipo de cópia costuma ser **agendada** (cron/job) — o lab faz um mirror pontual sob demanda.

> Se o lab ficou inconsistente: `docker compose down -v && ./scripts/up.sh`.

---

## O que anotar

1. Dedup = um blob, N metadados — **na app**.  
2. Refcount evita apagar arquivo ainda referenciado.  
3. Catálogo atrasado ≠ perda do arquivo; volume sem backup = perda real (RPO).  
4. Com backup do bucket, dá para **recuperar** após wipe (prova positiva leve).  
5. Desacoplamento da API (lab Postgres) ≠ durabilidade do MinIO.  
6. Produção (cluster, pre-signed, multipart): [teoria §9](teoria.md) — o lab single-node basta para o *modelo*.

**Fechamento:** [decisoes.md](decisoes.md) cenários 3–7 · [tecnologias-e-escolhas.md](tecnologias-e-escolhas.md)
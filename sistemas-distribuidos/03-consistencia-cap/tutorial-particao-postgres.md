# Tutorial — Lab Postgres: partição e matrícula CP

**Módulo:** [03 — Consistência/CAP](README.md) · **Lab:** [lab-particao-postgres/](lab-particao-postgres/)  
**Tempo sugerido:** tecnologia 15 min + lab ~2 h  
**Pré-requisito:** [00 — Ambiente Docker](../00-ambiente-docker/) · [02 — Replicação](../02-replicacao/) (sync/async na teoria) · [teoria.md](teoria.md) §1–6  
**Apoio:** [glossario.md](glossario.md) · [troubleshooting.md](troubleshooting.md)  
**Próximo:** [Mongo — concerns](tutorial-consistencia-mongodb.md)

> Leia A e B *antes* do Compose. No lab: rode → observe → anote.

**Arco narrativo:** passos **2–3** (crise CP + alívio) · [README](README.md)

**Protagonista deste lab:** o **aluno** tenta matricular na **última vaga** enquanto o link primary↔réplica pode **cair** — o portal deve **recusar** matrícula silenciosa inválida (tendência **CP**).

---

## Parte A — A tecnologia: partição + replicação síncrona

> CAP, partição e CP estão em [teoria.md](teoria.md). Aqui: o que **este lab** isola.

### Em uma frase

**Replicação síncrona** faz o commit **esperar** a standby. Se a rede entre primary e réplica **parte**, a escrita **não confirma** rápido — tendência **CP** (consistência > disponibilidade de escrita).

### Funcionalidades que importam

| Mecanismo | Para quê no lab |
|-----------|-----------------|
| `synchronous_commit = on` | Commit só retorna após ack sync |
| `pg_stat_replication.sync_state` | Ver se standby está `sync` |
| Duas redes Docker | API↔primary vs primary↔réplica |
| `statement_timeout` na API | Evitar HTTP pendurado para sempre |
| Transação `FOR UPDATE` | Impedir overbooking **no primary** |

### Vantagens / custos

**Ganha:** “matriculado com sucesso” implica réplica confirmou (com sync); menos risco de perda pós-commit.  
**Paga:** latência; **escrita indisponível** sob partição; operação de rede/HA.

### vs módulo 02

| | [02 sync-async](../02-replicacao/tutorial-sync-async.md) | Este lab |
|--|----------------------------------------------------------|----------|
| Pergunta | RPO após “ok”? | O que acontece se **link** cair? |
| Partição | Não simula | `particionar.sh` |
| Domínio | Notas | Matrícula / vagas |

### Cloud / produção vs este lab

| Promessa típica | Neste lab (Bitnami Compose) |
|-----------------|----------------------------|
| Patroni / RDS Multi-AZ com failover automático | Primary + 1 standby; **sem** promoção guiada |
| Partição entre AZ/regiões | `docker network disconnect` na `repl_net` |
| Sync replication configurável por workload | Boot com 0 sync + `./scripts/ativar-sync.sh` → `sync`/`quorum` |
| API roteada por região | Uma API; primary único |

Use a tabela na Parte C: o lab é **pequeno** de propósito para **ver** sync + partição sem Patroni no meio. O `ativar-sync.sh` evita deadlock do Bitnami no init (`NUM_SYNCHRONOUS_REPLICAS=1` no boot trava o SQL de schema).

---

## Parte B — Contexto de uso

### A dor

Disciplina **SD-101** tem **1 vaga**. O portal tem **uma API** e **um Postgres primary** (como na produção típica). A **replicação síncrona** exige que a standby confirme antes do commit.

Se o **link primary↔réplica cai** (partição na rede de replicação), o risco não é “dois campi com dois bancos” neste lab — é o primary **confirmar matrícula** enquanto a cópia sync **não acompanha**, ou o commit **travar** até você decidir (CP).

**Overbooking com dois nós isolados** (multi-primary) é cenário de [decisoes §1](decisoes.md) e módulo [04 — locks](../04-coordenacao-locks/) — **fora** deste lab. Aqui você prova:

1. **Transação** (`FOR UPDATE`) — só **uma** matrícula na última vaga no **mesmo** primary.  
2. **Sync commit** — sob partição, **503/timeout** em vez de “ok” sem garantia na réplica.

**Pergunta-guia:** prefere **“tente novamente”** ou **“matriculado” sem cópia confirmada na standby**?

```mermaid
sequenceDiagram
    actor A as Aluno
    participant API
    participant P as Primary
    participant R as Réplica

    Note over P,R: partição no link de replicação
    P x--x R
    A->>API: POST matricular
    API->>P: BEGIN … COMMIT sync
    Note over P: espera standby…
    P-->>API: timeout / erro
    API-->>A: 503 — não confirmado
```

| Peça | Lab |
|------|-----|
| Primary | `:5436` |
| Réplica | `:5437` |
| API | `:8085` |
| Partição | `./scripts/particionar.sh` |

Schema: `disciplinas(vagas_restantes)` + `matriculas`. Código: [`lab-particao-postgres/`](lab-particao-postgres/).

---

## Parte C — Lab prático

> Relacione cada experimento à teoria. Travou? [troubleshooting.md](troubleshooting.md).

### C.1 Subir o ambiente

```bash
cd sistemas-distribuidos/03-consistencia-cap/lab-particao-postgres
./scripts/up.sh
curl -s http://localhost:8085/health | python3 -m json.tool
```

Espere réplica pronta (1–3 min no primeiro boot). Poll: [troubleshooting § Postgres](troubleshooting.md#enquanto-espera-a-réplica).

Resposta **esperada** em `/consistencia/status` (saudável):

```json
{
  "modo_lab": "sync_cp",
  "sync_ativo": true,
  "replica_acessivel": true,
  "replicas": [{ "sync_state": "sync|quorum", "state": "streaming" }],
  "interpretacao": "CP na escrita: commit sync exige réplica; partição tende a bloquear ou falhar"
}
```

Valores exatos podem variar; o essencial é `sync_ativo: true`, `replica_acessivel: true` e `sync_state` em **`sync` ou `quorum`**.

### C.2 Experimento 1 — Disputa pela última vaga (sem partição)

Com volumes **frescos**, SD-101 tem **1 vaga**. Rode **antes** de matricular nela em outros experimentos:

```bash
./scripts/provocar-disputa-vaga.sh
```

**Observe:** **uma** matrícula 201, outra 409 (`sem vagas`). **Zero** overbooking — prova a **transação** no primary (não é multi-campus).

> O script envia dois POST **em sequência**. Para simular clique no mesmo segundo: `./scripts/provocar-disputa-vaga.sh --paralelo` (opcional).

### C.3 Experimento 2 — Sem partição: sync primary/replica

Use disciplina com vagas sobrando (**BD-201**, 30 vagas):

```bash
./scripts/matricular.sh BD-201 aluno-teste
curl -s 'http://localhost:8085/disciplinas/BD-201?dest=primary' | python3 -m json.tool
curl -s 'http://localhost:8085/disciplinas/BD-201?dest=replica' | python3 -m json.tool
```

**Observe:** `vagas_restantes` e `matriculados` **iguais** em primary e réplica após commit sync.

| Pergunta | Sua anotação |
|----------|--------------|
| `sync_state` em `/consistencia/status`? | |
| Latência `duracao_commit_ms`? | |

### C.4 Experimento 3 — Partição: escrita CP

Com lab saudável (volumes frescos ou disciplina BD-201 com vagas):

```bash
./scripts/particionar.sh
curl -s http://localhost:8085/consistencia/status | python3 -m json.tool
# sync_ativo=false → 503 imediato (API recusa escrita sem réplica sync)
./scripts/matricular.sh BD-201 sob-particao
```

**Observe:** HTTP **503** e `sync_ativo: false` — **não** 201. A API consulta `pg_stat_replication` antes do commit: sem standby sync/quorum, recusa (política CP). O Postgres puro sem essa guarda ficaria em espera `SyncRep` indefinida (`statement_timeout` não cancela essa espera).

Enquanto confere o 503: [troubleshooting — commit sob partição (Exp. 3)](troubleshooting.md#enquanto-espera-commit-sob-partição-experimento-3).

> **Leitura na réplica durante partição:** `GET ?dest=replica` tende a **503** (réplica fora da rede) — isso **não** contradiz CP; só indica que a cópia está inacessível enquanto o link está cortado.

### C.5 Experimento 4 — Curar partição e catch-up

```bash
./scripts/curar-particao.sh
sleep 5
curl -s http://localhost:8085/consistencia/status | python3 -m json.tool
curl -s 'http://localhost:8085/disciplinas/BD-201?dest=replica' | python3 -m json.tool
```

**Observe:** `sync_state` volta a `sync`; contagem na réplica **alcança** o primary.

### C.6 Experimento 5 (opcional) — Contraste mental com async

Sem subir outro lab: releia [02 sync-async](../02-replicacao/tutorial-sync-async.md). Se você rodou aquele lab, compare o `duracao_commit_ms` anotado lá com o **503** deste Exp. 3.

| Modo | Sob partição, POST provável |
|------|----------------------------|
| Async (02) | 201 rápido; RPO pior |
| Sync (este lab) | 503 / timeout; RPO menor |

---

## Tabela de fechamento

| Experimento | O que provou | Objetivo |
|-------------|--------------|----------|
| 1 | Transação evita overbooking no primary | 6 |
| 2 | Sync mantém primary/replica alinhados | 5 |
| 3 | Partição bloqueia/falha escrita sync | 2, 4 |
| 4 | Reconciliação após cura | 7 |
| 5 | Async vs sync sob P | liga 02↔03 |

### Dois mecanismos — não confunda na redação

| Mecanismo | O que garante | Onde viu |
|-----------|-----------------|----------|
| **`FOR UPDATE` + PK** | Só **uma** matrícula na última vaga **no primary** | Exp. 1 |
| **Sync commit + partição** | Não retorna “ok” se a **standby sync** não confirmar | Exp. 3 |

Sync **não** substitui transação (overbooking local). Transação **não** substitui sync (RPO / mentira pós-commit).

---

## Encerrar

```bash
docker compose down -v
```

**Próximo (caminho completo):** [tutorial-consistencia-mongodb.md](tutorial-consistencia-mongodb.md) — feed de avisos com concerns.  
**Workshop:** [decisoes.md](decisoes.md) — cenários **1–2** (mínimo) ou **1–3** (completo).

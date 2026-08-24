# Tecnologias e escolhas — Consistência

**Módulo:** [03 — Consistência/CAP](README.md)  
**Pré-leitura:** [teoria.md](teoria.md) · [02 — tecnologias](../02-replicacao/tecnologias-e-escolhas.md)  
**Objetivo:** ligar **CP/AP** e **níveis de consistência** a Postgres, MongoDB e padrões de produto.

---

## 1. Onde a consistência é decidida

| Camada | Exemplos |
|--------|----------|
| **Negócio** | “Última vaga não pode duplicar” |
| **Aplicação** | Transação, idempotência, sticky read |
| **Banco / middleware** | Sync rep, concerns, quórum |
| **UX** | Erro vs banner “desatualizado” |

Não jogue tudo no banco — mas **não** prometa strong consistency na UI se o banco está em modo eventual.

---

## 2. PostgreSQL — tendência CP na escrita sync

| Mecanismo | Efeito | Lab |
|-----------|--------|-----|
| `synchronous_commit = on` + standby sync | Commit espera réplica | [partição](lab-particao-postgres/) |
| Transação + `FOR UPDATE` | Exclusão na **mesma** instância | Matrícula |
| Read replica async | Leitura eventual (02) | [02 Postgres](../02-replicacao/lab-postgres/) |

**Quando usar:** matrícula, saldo, estoque, qualquer **contador finito** crítico.

**Custo:** latência de escrita; **indisponibilidade de escrita** se standby sumir (partição).

---

## 3. MongoDB — concerns por operação

| Config | Comportamento | Fluxo típico |
|--------|---------------|--------------|
| `writeConcern: majority` | Quórum confirma | Aviso importante, config |
| `writeConcern: w:1` | Primary confirma | Métricas, rascunho |
| `readConcern: majority` | Lê dados majoritários | Pós-publicação |
| `readConcern: local` + secondary | Baixa latência, stale possível | Feed, timeline |

**Quando usar AP-ish:** feed, notificações, contadores aproximados.

**Custo:** divergência temporária; reconciliação e copy clara na UI.

---

## 4. Comparativo rápido (este módulo)

| | Postgres sync (lab) | Mongo majority | Mongo w1 + local read |
|--|---------------------|----------------|------------------------|
| Partição primary↔réplica | Escrita bloqueia/503 | Majority write falha | Escrita/leitura seguem |
| Overbooking | Transação no primary | Depende de app + concern | Risco se só w:1 |
| Domínio lab | Matrícula | Avisos (majority) | Avisos (rápido) |

---

## 5. Padrões além do banco único

| Padrão | Consistência | Partição |
|--------|--------------|----------|
| **Strong em um primary** | Alta no nó | CP se exigir sync/quórum |
| **Read-your-writes (sticky)** | Sessão vê própria escrita | AP na leitura global |
| **Saga / eventual entre serviços** | Eventual entre bounded contexts | AP entre serviços; CP local |
| **CRDT / LWW offline** | Eventual com regras de merge | AP offline |

Box: *Migrating to Microservice Databases* — sagas sem 2PC global.

---

## 6. Matriz de decisão (portal acadêmico)

| Fluxo | Sugestão inicial | Evidência no curso |
|-------|------------------|-------------------|
| Matrícula / vagas | CP + transação | Lab Postgres 03 |
| Boletim massivo | AP leitura + stale OK | Lab Postgres 02 |
| Feed avisos | AP + majority opcional | Lab Mongo 03 |
| Nota em tempo real | Read primary pós-escrita | [02 decisões §2](../02-replicacao/decisoes.md) |

---

## 7. O que monitorar

| Sistema | Métrica / comando |
|---------|-------------------|
| Postgres sync | `sync_state`, `pg_stat_replication` |
| Mongo | `replSetGetStatus`, election counters |
| Produto | Taxa 503 em matrícula; lag de avisos; reclamações overbooking |

---

## 8. Erros comuns

1. **CAP como rótulo de produto** — configure e meça.  
2. **Confundir lag (02) com partição (03)** — lag converge; partição força escolha.  
3. **Async read replica para matrícula** — escala leitura, não protege escrita crítica.  
4. **Ignorar UX** — CP sem mensagem clara vira “bug intermitente”.

**Validação em sala:** antes da turma, rode o [checklist professor](troubleshooting.md#checklist-professor-antes-da-turma) e preencha **Validação local** no mesmo arquivo.

Próximo passo operacional: [04 — locks](../04-coordenacao-locks/) quando precisar exclusão mútua **entre** serviços.

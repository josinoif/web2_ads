# Tecnologias e escolhas — Coordenação

**Módulo:** [04 — Coordenação/locks](README.md)  
**Pré-leitura:** [teoria.md](teoria.md) · [03 — tecnologias](../03-consistencia-cap/tecnologias-e-escolhas.md)  
**Objetivo:** ligar **exclusão mútua** a Postgres, MongoDB, Redis e padrões de produto.

---

## 1. Onde a coordenação é decidida

| Camada | Exemplos |
|--------|----------|
| **Negócio** | “1 vaga global”, “job batch único” |
| **Aplicação** | RMW vs transação; retry com backoff |
| **Banco** | `FOR UPDATE`, `findOneAndUpdate` |
| **Coordenação externa** | Redis lock, etcd, fila single-consumer |
| **UX** | “Tente novamente”, “Conflito — vaga preenchida” |

Não prometa “strong consistency” na UI se o código usa `mode=broken`.

---

## 2. PostgreSQL — exclusão no primary

| Mecanismo | Efeito | Lab |
|-----------|--------|-----|
| Transação + `FOR UPDATE` | Row lock na vaga/disciplina | `mode=transaction` |
| `pg_advisory_xact_lock` | Lock por recurso lógico | `mode=advisory` |
| Coluna `version` | Optimistic concurrency | `mode=optimistic` |
| RMW sem lock | **Lost update** — o lab grava o valor **lido** (stale), não `coluna - 1` | `mode=broken` |

**Quando usar:** várias APIs, **um** Postgres primary compartilhado.

**Limite:** não coordena **dois primaries** isolados (cenário multi-campus).

---

## 3. MongoDB — atomicidade no documento

| Padrão | Comportamento | Fluxo |
|--------|---------------|-------|
| RMW na app | Corrida possível | Anti-exemplo lab |
| `findOneAndUpdate` + filtro `$gt: 0` | Decremento atômico | Fila de reserva |
| Multi-documento transaction | ACID multi-doc (4.0+) | Fora do lab — cite |

**Quando usar:** estado da reserva/fila em **um documento**.

**Custo:** documento grande; hot key no `_id` da disciplina.

---

## 4. Redis — lock distribuído

| Comando / padrão | Uso |
|------------------|-----|
| `SET key token NX EX ttl` | Adquirir lock |
| Lua unlock compare-and-del | Soltar **só** se token confere |
| `INCR fencing:*` | Token monotônico para storage |

**Quando usar:** vários serviços, passos separados, ou stores diferentes.

**Custo:** Redis down → matrícula para?; contenção; operação do cluster Redis.

---

## 5. Alternativas ao lock

| Padrão | Ideia | Módulo |
|--------|-------|--------|
| **Fila single-consumer** | Um worker processa matrículas | [01](../01-comunicacao/) |
| **Saga + compensação** | Reserva + confirma + estorno | Teoria / decisões §4 |
| **Primary centralizado** | Um writer CP | [03](../03-consistencia-cap/) |
| **Particionar recurso** | Lock por shard de disciplina | [05](../05-escalabilidade/) |

---

## 6. Matriz rápida

| Se você tem… | Comece com… |
|--------------|-------------|
| N APIs, 1 Postgres | Transação / `FOR UPDATE` |
| Estado em documento Mongo | `findOneAndUpdate` |
| Passos em serviços diferentes | Redis lock ou saga |
| Job batch idempotente | Lock + TTL ou fila |
| Hot key extremo | Fila + sorteio / shard |

---

## 7. Cloud vs lab

| Produção | Lab Compose |
|----------|-------------|
| Redis Cluster / ElastiCache | Redis single node |
| Patroni / RDS Multi-AZ | Postgres Bitnami simples |
| 3+ pods K8s | nginx + api1/2/3 |
| Redlock / etcd | `SET NX` didático |

---

## 8. Validação local

Antes da aula, rode o checklist em [troubleshooting.md](troubleshooting.md) e preencha o bloco **Validação local** (data, SO, resultado Exp. 1–2 Postgres e Exp. 1–3 Mongo).

# Tecnologias e escolhas — Escalabilidade

**Módulo:** [05 — Escalabilidade](README.md)  
**Pré-leitura:** [teoria.md](teoria.md)

---

## 1. Onde a escala é decidida

| Camada | Alavancas |
|--------|-----------|
| **Aplicação** | Réplicas, LB, filas, workers, pool de conexões |
| **Dados** | Réplicas de leitura, partição/shard, (depois) cache |
| **Operação** | Métricas RPS/p99, conexões DB, tamanho por shard |
| **Produto** | Aceitar eventual? Relatório global em tempo real? |

---

## 2. Camada de aplicação (lab Postgres)

| Peça | Papel |
|------|-------|
| nginx | Balanceador round-robin |
| api1..3 | Instâncias stateless |
| Postgres único | Store compartilhado (`postgres:16-alpine`) |
| `WORK_MS` | CPU sintética **busy-wait** (ganho 1→3 mensurável) |
| `DB_SLOTS` + `STORE_HOLD_MS` | Teto didático do store (`aproximar-teto.sh`) |
| `medir-rps.sh` / `comparar-escala.sh` | Evidência numérica + ganho (default N=240 C=48) |

**Quando:** CPU/concorrência da API é o gargalo.  
**Não resolve sozinho:** primary derretendo; hot key; lock global.

---

## 3. Camada de dados

| Técnica | Tecnologia no curso | Lab / módulo |
|---------|---------------------|--------------|
| Réplica de leitura | Postgres / Mongo RS | [02](../02-replicacao/) |
| Partição por chave | Dois Mongo + router | [lab-escala-dados](lab-escala-dados/) |
| Lock / exclusão | Redis / SQL | [04](../04-coordenacao-locks/) — **limita** escrita |

**Lab 05 dados:** *não* é Atlas Shard Cluster — é o **conceito** de shard key com dois stores.  
Evidência do lab: **distribuição** hot/spread (+ tempo com `WRITE_MS`); fan-out com `READ_SHARD_MS`.

### Quando particionar (e quando não)

| Partição faz sentido | Partição prematura |
|----------------------|--------------------|
| Escrita alta e **espalhada** por chave natural (campus, tenant) | Ainda dá para crescer com vertical + N APIs + réplica de leitura |
| Isolamento por unidade de negócio importa | Shard key incerta / muda com frequência |
| Hot key identificada e redesenho possível | Relatório global em tempo real é o caso dominante (fan-out dói) |
| Time aceita ops de multi-store | Um Postgres bem indexado ainda ocioso |

---

## 4. Matriz rápida

| Sintoma | Comece por |
|---------|------------|
| API a 100% CPU, DB ocioso | Escala **aplicação** |
| DB a 100%, APIs ociosas | Escala **dados** (réplica ou partição) |
| Pool/conexões no teto | Ajuste pool **ou** escala dados — não só `replicas++` |
| Uma disciplina/campus satura | Hot key — particionar ou redesign |
| p99 ruim, p50 ok | Worker lento / health check → [06](../06-falhas-timeout/) |
| Mesmos dados relidos | Cache → [07](../07-cache-distribuido/) |

---

## 5. Cloud vs lab

| Produção | Lab |
|----------|-----|
| ALB/NLB + autoscaling | nginx + 3 containers fixos |
| Read replica gerenciada | Ponte ao lab 02 |
| MongoDB sharded cluster | mongo-a + mongo-b + router |
| Connection pool / PgBouncer | `DB_SLOTS` (simulação didática) |
| APM / Prometheus | Scripts RPS + `/escala/status` |

---

## 6. Validação local

Checklist e bloco em [troubleshooting.md](troubleshooting.md) — preencher após piloto (`comparar-escala` + `aproximar-teto` + `medir-writes`).

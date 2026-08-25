# Tutorial — Cache boletim (Postgres + Redis)

**Lab:** [lab-cache-postgres](lab-cache-postgres/) · API `http://127.0.0.1:8094`  
**Teoria:** [teoria.md](teoria.md) §1–5 · [glossario](glossario.md)

> **Caminho mínimo:** C.1 → Exp. 1–4.  
> **Caminho completo:** + Exp. 5 (stampede) · 5b (jitter) · 5c (SPOF Redis, opcional).

---

## Parte A — Tecnologia (o essencial)

| Peça | Papel |
|------|--------|
| Postgres | Fonte da verdade (`fonte_dados: postgres`) |
| Redis | Cache compartilhado (`boletim:{aluno}`) |
| `servido_de` | De onde **esta** resposta saiu: `postgres` · `redis` · `local` |
| `cache` | `hit` / `miss` / `off` |
| `STORE_HOLD_MS` | Atraso sintético na **leitura da fonte** |
| `CACHE_BACKEND` | `redis` · `local` · `off` |
| `INVALIDATE_ON_WRITE` | `1` → `DEL` após PUT; `0` → stale até TTL |

> **Não confunda:** `fonte_dados` = SoT; `servido_de` = quem atendeu *agora*. No hit: `fonte_dados: postgres` + `servido_de: redis`.

> **Simplificações do lab:** 1 chave por aluno; `DEL` simples; lock de stampede didático — ver [teoria §9](teoria.md).

---

## Parte B — Contexto

Dia do boletim: milhares de `GET` da mesma nota. Sem cache, o Postgres vira o teto ([05](../05-escalabilidade/)). Com cache, latência **e** `store_reads` caem — até alguém **atualizar a nota** e o aluno ainda ver o valor antigo.

Pergunta de política: *aceito responder rápido com dado velho, ou invalido e pago o miss?*

---

## Parte C — Lab

### C.1 Subir

> Volume antigo (nota/avisos de runs anteriores): se o seed “não bate”, faça `docker compose down -v` **antes** do `up`.

```bash
cd sistemas-distribuidos/07-cache-distribuido/lab-cache-postgres
# opcional, lab limpo:
# docker compose down -v
./scripts/up.sh
./scripts/status.sh
```

### C.2 Experimento 1 — Sem cache (baseline)

```bash
./scripts/set-backend.sh off
./scripts/provocar-lento.sh 800
./scripts/flush.sh
./scripts/benchmark.sh 10 aluno-01
./scripts/provocar-lento.sh 0
```

**Esperado:** `misses ≈ 10`, `store_reads ≈ 10`, `p50_ms` perto de 800, `servido_de` seria postgres em cada GET.

### C.3 Experimento 2 — Cache-aside (hit) + ponte escala

```bash
./scripts/set-backend.sh redis
./scripts/provocar-lento.sh 800
./scripts/flush.sh
./scripts/benchmark.sh 20 aluno-01
./scripts/provocar-lento.sh 0
```

**Esperado:**

| Campo | Valor típico |
|-------|----------------|
| `misses` | **1** |
| `hits` | **19** |
| `store_reads` | **1** (vs 10 no Exp. 1 — alívio de capacidade) |
| `hit_rate` | ≈ 0,95 |
| `p50_ms` | << 800 |

Anote `store_reads` dos Exp. 1 e 2 lado a lado — essa é a ponte com o [05](../05-escalabilidade/).

### C.4 Experimento 3 — Stale sem invalidação

```bash
./scripts/set-backend.sh redis
./scripts/set-invalidate.sh 0
./scripts/flush.sh
./scripts/ler.sh aluno-01          # miss → preenche
./scripts/atualizar.sh aluno-01 9.9
./scripts/ler.sh aluno-01          # hit stale
```

**Esperado (último GET):**

| Campo | Valor |
|-------|--------|
| `nota` | valor **anterior ao PUT** (não 9.9) |
| `cache` | `hit` |
| `servido_de` | `redis` |
| PUT anterior | `invalidou_cache: false` |

### C.5 Experimento 4 — Invalidate-on-write

```bash
./scripts/set-invalidate.sh 1
./scripts/atualizar.sh aluno-01 5.0
./scripts/ler.sh aluno-01          # miss → nota 5.0
./scripts/ler.sh aluno-01          # hit com 5.0
```

**Esperado:**

| Passo | O que ver |
|-------|-----------|
| PUT | `invalidou_cache: true` |
| 1º GET | `cache: miss`, `servido_de: postgres`, `nota: 5.0` |
| 2º GET | `cache: hit`, `servido_de: redis`, `nota: 5.0` |

Isso aproxima **read-your-writes** neste fluxo — não é consistência forte global do cluster ([teoria §4](teoria.md)).

### C.6 Experimento 5 — Stampede *(caminho completo)*

```bash
N=20 ./scripts/provar-stampede.sh
LOCK=1 N=20 ./scripts/provar-stampede.sh
```

**Esperado:** olhe `store_reads_na_rajada` (só a rajada paralela — **não** some o aquecimento).

| LOCK | `store_reads_na_rajada` |
|------|-------------------------|
| 0 | tende a ≈ **N** |
| 1 | **<< N** (fills + waits) |

### C.7 Experimento 5b — TTL jitter *(opcional)*

```bash
./scripts/set-ttl.sh 10
./scripts/set-jitter.sh 3
./scripts/flush.sh
./scripts/ler.sh aluno-01   # veja ttl_sec_aplicado (entre ~7 e 13)
./scripts/set-jitter.sh 0
```

**Ideia:** expires não sincronizam — reduz stampede “em massa” no mesmo segundo.

> **Jitter sozinho não basta no pico.** Ele espalha os expires; no miss quente ainda use **single-flight/lock** (Exp. 5). Em produção costuma-se **combinar** os dois ([teoria §6](teoria.md)).

### C.8 Experimento 5c — Redis como SPOF *(opcional, caminho completo)*

```bash
./scripts/provar-redis-spof.sh
```

**Esperado:** com Redis no ar → miss depois hit; após `stop redis` → HTTP **503** com `"code": "redis_indisponivel"`; após `start` → leitura volta (hit possível — `stop`/`start` preserva dados do container).

> O insight é o **503 com Redis parado** (SPOF). Produção: timeout + fallback à fonte, CB ([06](../06-falhas-timeout/)).

---

## O que anotar

| Exp. | Insight |
|------|---------|
| 1–2 | Cache troca carga (`store_reads`) e latência por cópia |
| 3 | Sem invalidate = leitura eventual / stale |
| 4 | Invalidate aproxima read-your-writes |
| 5 | Expire sem proteção vira stampede no store |
| 5b | Jitter espalha expires — combine com lock no pico |
| 5c | Redis parado = SPOF da camada de cache |

**Próximo:** [tutorial-cache-mongodb.md](tutorial-cache-mongodb.md) ou [decisoes.md](decisoes.md).

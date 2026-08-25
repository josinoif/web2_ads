# Tutorial — Cache avisos (MongoDB + Redis)

**Lab:** [lab-cache-mongodb](lab-cache-mongodb/) · APIs `8095` / `8096`  
**Teoria:** [teoria.md](teoria.md) §2, §4–5, §8–9 · [glossario](glossario.md)

> Faça depois do [tutorial Postgres](tutorial-cache-postgres.md) (caminho completo).  
> **Ordem deste lab:** primeiro o insight **distribuído** (local vs Redis); depois política TTL/invalidate.

---

## Parte A — Tecnologia

| Peça | Papel |
|------|--------|
| MongoDB | Fonte dos avisos (`fonte_dados`) |
| Redis | Cache do feed (`avisos:feed`) |
| **api1 + api2** | Duas réplicas — prova compartilhamento |
| `servido_por` | Qual API atendeu (`api1` / `api2`) |
| `servido_de` | `mongodb` · `redis` · `local` |
| TTL padrão **30 s** | Política “bom o bastante” |
| `INVALIDATE_ON_WRITE` | Padrão **OFF** (contraste com o boletim) |

> Rode os scripts **a partir da pasta do lab** (`cd lab-cache-mongodb`).

---

## Parte B — Contexto

Feed de avisos: leitura frequente, escrita eventual. Produto tolera “aviso novo em até ~30 s”. Eco do fluxo tolerante do [03](../03-consistencia-cap/) — aqui via política de cache, não partição.

---

## Parte C — Lab

### C.1 Subir

> Volume antigo: se o feed “já tem avisos estranhos”, `docker compose down -v` antes do `up`.

```bash
cd sistemas-distribuidos/07-cache-distribuido/lab-cache-mongodb
# encerre o lab Postgres antes se estiver no ar:
#   cd ../lab-cache-postgres && docker compose down -v
# lab Mongo limpo (opcional):
# docker compose down -v
./scripts/up.sh
```

### C.2 Experimento 1 — Local vs Redis compartilhado *(insight do módulo)*

> Rode **a partir desta pasta** (`lab-cache-mongodb`).

```bash
./scripts/comparar-local-vs-redis.sh
```

**Esperado:**

| Backend | api2 após 1ª leitura na api1 |
|---------|------------------------------|
| `redis` | `cache: hit`, `servido_de: redis` (compartilhou) |
| `local` | `cache: miss` de novo, `servido_de: mongodb` (cada API preenche o **próprio** dict) |

> Com N APIs, cache **local** não escala o cluster — precisa Redis (ou equivalente).

### C.3 Experimento 2 — Hit rate no feed (`benchmark.sh`)

```bash
./scripts/set-backend.sh redis
./scripts/provocar-lento.sh 500
./scripts/flush.sh
./scripts/benchmark.sh 15
./scripts/provocar-lento.sh 0
```

> Sempre `flush.sh` **antes** do benchmark se você acabou de rodar o Exp. 1 — senão o Redis já quente mostra `store_reads=0` e parece “bug”.

**Esperado:** `store_reads ≈ 1`, `hits` altos, `p50` cai — mesma ponte de capacidade do lab Postgres.

### C.4 Experimento 3 — Stale com TTL (sem invalidate)

```bash
./scripts/provar-stale-ttl.sh
```

**Esperado:**

| Momento | O que ver |
|---------|-----------|
| Após publish (invalidate OFF) | `cache: hit`, `total` **antigo** |
| Após flush | `cache: miss`, `total` **novo**, título recente |

### C.5 Experimento 4 — Invalidar no publish (contraste)

```bash
./scripts/set-invalidate.sh 1
./scripts/flush.sh
./scripts/ler.sh
./scripts/publicar.sh "Com-invalidate" "aparece no proximo GET"
./scripts/ler.sh
```

**Esperado:** PUT com `invalidou_cache: true`; próximo GET `cache: miss` e aviso novo no topo.

---

## O que anotar

- **Local ≠ compartilhado** é o coração “distribuído” do módulo.  
- Mesmo cache-aside do Postgres; muda a **política** (TTL vs invalidate).  
- Feed tolera stale; boletim exige invalidate mais firme.

**Fechamento:** [decisoes.md](decisoes.md).

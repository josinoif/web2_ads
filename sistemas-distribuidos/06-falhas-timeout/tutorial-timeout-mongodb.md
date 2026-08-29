# Tutorial — Timeout, retry e dedup (MongoDB)

**Lab:** [lab-timeout-mongodb](lab-timeout-mongodb/) · API `http://127.0.0.1:8093`  
**Faça depois** do [tutorial Postgres](tutorial-timeout-postgres.md).  
**Teoria:** [teoria.md](teoria.md) §4 e §8 · ponte CAP [03](../03-consistencia-cap/).  
**SO:** Linux, macOS e Windows — [como rodar os comandos](../ferramentas/linux-e-windows.md).  

---

## Parte A — Tecnologia

| Peça | Papel |
|------|--------|
| `REQUIRE_UNIQUE=0` | `insert` sempre → retry **duplica documentos** |
| `REQUIRE_UNIQUE=1` | upsert + índice unique em `aviso_id` |
| `Idempotency-Key` / `aviso_id` | identidade estável do aviso |
| Backoff + jitter | **0,2 → 0,5 → 1,0 s**; retry só em timeout/503 |
| Índice unique vs upsert | Unique = **invariante**; upsert = **padrão de escrita** (o lab usa os dois juntos) |
| `WRITE_CONCERN` | Só **revisão mental** do 03 — em 1 nó quase não muda o que você vê |

---

## Parte B — Contexto

Coordenação publica “Prova adiada”. Timeout + retry **sem** chave estável → o aluno vê o **mesmo aviso várias vezes** (aqui a duplicata é o próprio documento — contraste com o Postgres, onde unique salvava a matrícula e o retry “só” disparava e-mails extras).

---

## Parte C — Lab

### C.1 Subir

```bash
cd sistemas-distribuidos/06-falhas-timeout/lab-timeout-mongodb
./scripts/up.sh
```

### C.2 Experimento 1 — Retry **sem** unique (duplicata)

```bash
UNIQUE=0 HOLD_MS=2500 MAX_TIME=1 RETRIES=3 \
  AVISO_ID=aviso-dup-demo ./scripts/publicar-com-retry.sh
```

**Observe:** `docs com este aviso_id` **> 1**. Timeout do curl vira JSON `erro: cliente` (não é falha do `json.tool`).

### C.3 Experimento 2 — Retry **com** unique / upsert

> `UNIQUE=1` no script chama `ativar-unique.sh`, que **limpa** a coleção `avisos` (necessário se o Exp. 1 deixou duplicatas — índice unique não sobe com docs repetidos).

```bash
UNIQUE=1 HOLD_MS=2500 MAX_TIME=1 RETRIES=3 \
  AVISO_ID=aviso-safe-demo ./scripts/publicar-com-retry.sh
```

**Observe:** um documento; tentativas seguintes com `idempotent_replay: true` (quando a 1ª já inseriu).

### C.4 WriteConcern — revisão opcional do 03 *(não conta no caminho completo)*

> Em **um** nó Mongo, `majority` ainda completa rápido. **Não espere** diferença dramática. O ponto é só **lembrar** o lab 03 (majority sob partição → falha/demora). **Pule** sem prejuízo.

```bash
curl -s -X POST http://127.0.0.1:8093/admin/write_concern \
  -H 'Content-Type: application/json' -d '{"w":"majority"}' | python3 -m json.tool
MAX_TIME=5 AVISO_ID=aviso-wc ./scripts/publicar.sh "Com majority"
```

### C.5 Encerrar

```bash
docker compose down -v
```

---

## Comparação rápida com Postgres

| | Postgres | Mongo |
|--|----------|-------|
| Efeito de negócio | 1 matrícula (unique) | 1 aviso (`aviso_id`) |
| O que o retry “duplica” sem dedup | `auditoria_tentativas` (≈ e-mails) | **documentos** inteiros |
| Replay | tabela `idempotency_keys` | upsert `$setOnInsert` |

Feche com [decisoes.md](decisoes.md) cenários 3 e 5.

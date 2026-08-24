# Tutorial — Lab Mongo + Redis: reserva e lock distribuído

**Módulo:** [04 — Coordenação/locks](README.md) · **Lab:** [lab-coordenacao-mongo/](lab-coordenacao-mongo/)  
**Tempo sugerido:** tecnologia 15 min + lab ~1,5–2 h  
**Pré-requisito:** [lab Postgres](tutorial-concorrencia-postgres.md) · [teoria.md](teoria.md) §6–7  
**Apoio:** [glossario.md](glossario.md) · [troubleshooting.md](troubleshooting.md)

**Protagonista:** fila de **reserva de vaga** em Mongo — quando RMW quebra, **`findOneAndUpdate`** ou **Redis lock** coordenam.

---

## Parte A — A tecnologia: atomic doc + Redis lock

### Em uma frase

Mongo garante atomicidade **por documento** numa operação. Redis **`SET NX EX`** coordena **entre passos/serviços**; **fencing token** protege contra lock órfão.

### Funcionalidades que importam

| Parâmetro | Efeito |
|-----------|--------|
| `mode=rmw` | Anti-padrão |
| `mode=atomic` | `findOneAndUpdate` condicional |
| `mode=redis-lock` | Lock + atomic + fencing |
| `hold_seconds` | Simula holder lento (TTL) |

### vs lab Postgres

| Postgres lab | Mongo lab |
|--------------|-----------|
| Row lock SQL | Atomic document |
| 3 APIs nginx | 1 API (corrida por threads + `--paralelo`) |
| Sem Redis | Redis lock + fencing |

> **Por que 1 API no Mongo?** A corrida vem de **requisições paralelas** no `ThreadingHTTPServer`. Três pods nginx no lab 1 só tornam visível o `api_instance`. O conceito é o mesmo.

> **Por que Redis lock se `atomic` já basta?** `findOneAndUpdate` resolve **um passo** no mesmo documento. O lock modela **multi-etapa / multi-serviço** (cenário 4 das decisões). O lab encadeia lock + atomic + fencing de propósito — não substitua atomic por lock em operação única.

---

## Parte B — Contexto de uso

Quando matrícula direta no Postgres está cheia, aluno entra na **fila de reserva** (documento Mongo). Fluxo real pode ter:

1. Reserva soft hold  
2. Confirmação / pagamento  
3. Gravação definitiva  

RMW na reserva → **duas reservas na mesma vaga**. Lock Redis envolve passos **multi-serviço** (decisões §4).

| Peça | Lab |
|------|-----|
| API | `:8088` |
| Mongo | `:27118` |
| Redis | `:6380` |

---

## Parte C — Lab prático

### C.1 Subir

```bash
cd sistemas-distribuidos/04-coordenacao-locks/lab-coordenacao-mongo
docker compose up -d --build
for i in $(seq 1 20); do curl -sf http://localhost:8088/health && break; sleep 2; done
curl -s http://localhost:8088/coordenacao/status | python3 -m json.tool
```

Resposta saudável (trecho):

```json
{
  "modo_lab": "coordenacao_mongo_redis",
  "api_instance": "api-coordenacao",
  "modos_validos": ["rmw", "atomic", "redis-lock"],
  "alerta_overbooking_sd101": false
}
```

### C.2 Experimento 1 — RMW

```bash
./scripts/disputa-fila.sh --paralelo --mode rmw
```

**Observe:** `alerta_overbooking_sd101: true` e `total_reservas > 1` (ou `vagas_restantes < 0`) em SD-101.

### C.3 Experimento 2 — Atomic

Reset +:

```bash
docker compose down -v && docker compose up -d --build && sleep 12
./scripts/disputa-fila.sh --paralelo --mode atomic
```

**Observe:** 1 reserva; segundo aluno **409 sem vagas**.

### C.4 Experimento 3 — Redis lock + fencing

Reset +:

```bash
./scripts/disputa-fila.sh --paralelo --mode redis-lock
```

**Observe:** `fencing_token` incrementado; 1 reserva — o **resultado** parece o Exp. 2. O Redis só mostra o **risco** no Exp. 4 (TTL / órfão).

### C.5 Experimento 4 — Lock órfão / TTL

Dois terminais. TTL do lock = **10 s**; o holder segura **12 s**.

**Terminal 1** — o script imprime o curl do T2 **antes** de bloquear:

```bash
./scripts/provocar-lock-orfao.sh
```

**Terminal 2** — espere **~11 s** (lock expirar), depois:

```bash
curl -s -X POST 'http://localhost:8088/reservar?mode=redis-lock' \
  -H 'Content-Type: application/json' \
  -d '{"disciplina_id":"BD-201","aluno_id":"outro"}' | python3 -m json.tool
```

Se rodar o T2 nos primeiros 10 s: `409 lock indisponível` (ainda ativo). Depois do TTL: T2 **201**. O holder lento, ao acordar, deve receber **409** (fencing rejeitado) — o token foi gerado na **aquisição**, não depois do sleep.

### C.6 Experimento 5 (opcional) — Comparar modos

> ~5 min (3 resets). Demo do professor / revisão — não faz parte do caminho mínimo.

```bash
./scripts/comparar-atomico-vs-rmw.sh
```

---

## Fechamento — Dois mecanismos

| Mecanismo | Onde | Exp. |
|-----------|------|------|
| **`findOneAndUpdate`** | Atomicidade no Mongo | 2 |
| **`SET NX` + fencing** | Coordenação multi-etapa | 3–4 |
| **RMW** | Anti-padrão | 1 |

**Ponte:** [05 — escalabilidade](../05-escalabilidade/) · hot key SD-101 · [decisoes §6](decisoes.md).

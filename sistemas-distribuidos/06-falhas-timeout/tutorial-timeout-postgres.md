# Tutorial — Timeout, retry e idempotência (Postgres)

**Lab:** [lab-timeout-postgres](lab-timeout-postgres/) · API `http://127.0.0.1:8092`  
**Teoria:** [teoria.md](teoria.md) §1–5 · [glossario](glossario.md)

> **Caminho mínimo:** C.1 → Exp. 1–4 (inclui 4b).  
> **Caminho completo:** + Exp. 5–6 e opcionais (deadline / 422 / TTL).

---

## Parte A — Tecnologia (o essencial)

| Peça | Papel |
|------|--------|
| `STORE_HOLD_MS` | Atraso sintético (store “lento”) |
| Timeout do cliente | `MAX_TIME` / `NO_MAX_TIME` |
| `auditoria_tentativas` | ≈ e-mail “matrícula confirmada” (side effect sem dedup) |
| `UNIQUE` + `Idempotency-Key` | Negócio único vs resposta/side effect estáveis |

**Referência rápida** (CB / deadline / exits — use quando precisar):

| Peça | Papel |
|------|--------|
| Backoff | **0,2 → 0,5 → 1,0 s**; retry só em timeout/503/504 |
| Após timeout | scripts **serializam** (esperam o hold) — 2ª tentativa mostra 409 ou replay |
| Circuit breaker | Janela + aberto + meio-aberto (**1 sonda**); `CB_OPEN_SEC≈8` |
| `X-Deadline-Ms` | hold > deadline → **504** rápido |
| Exit | `0`=2xx · `28`=timeout · `7`=API fora · `49`=409 · `42`=422 · `53`=503 · `54`=504 |

---

## Parte B — Contexto

Dia da matrícula: o banco atrasa. O app faz timeout e **retry**.

- Com `UNIQUE`, **este aluno** não ganha duas matrículas.  
- Sem `Idempotency-Key`, cada tentativa real ainda grava **auditoria** (outro e-mail).  
- **Olhe sempre a contagem deste aluno**, não o total da disciplina (Exp. 1–2 já enchem o total).

> No código, auditoria roda **antes** do commit (anti-padrão didático). Em produção: outbox **depois**.

---

## Parte C — Lab

### C.1 Subir

> Schema/API novos: `docker compose down -v` antes do `up`.

```bash
cd sistemas-distribuidos/06-falhas-timeout/lab-timeout-postgres
./scripts/up.sh
./scripts/status.sh
```

### C.2 Experimento 1 — Cliente **sem** `--max-time`

```bash
./scripts/provocar-lento.sh 8000
NO_MAX_TIME=1 ./scripts/matricular.sh SD-101 aluno-exp1
./scripts/provocar-lento.sh 0
```

**Observe:** `duracao_ms` ≈ 8000.

### C.3 Experimento 2 — Timeout curto (falso negativo)

```bash
./scripts/provocar-lento.sh 5000
MAX_TIME=1 ./scripts/matricular.sh SD-101 aluno-exp2 || true
./scripts/provocar-lento.sh 0
sleep 5
./scripts/status.sh SD-101 aluno-exp2
```

**Observe:** `curl_exit: 28` (se for **7**, a API está fora — não é o experimento).  
**Esperado:** `aluno-exp2` com `matriculas=1` mesmo após o “erro” do cliente.

> Opcional (completo): `./scripts/provar-deadline.sh`

### C.4 Experimento 3 — Retry **sem** chave

```bash
HOLD_MS=3000 MAX_TIME=1 RETRIES=3 ./scripts/matricular-com-retry.sh SD-101 aluno-exp3
# ou: ./scripts/status.sh SD-101 aluno-exp3
```

O script **serializa** após timeout, **zera o hold** e imprime a contagem **deste aluno**. Na 2ª tentativa você costuma ver **409** (rápido).

| Campo (deste aluno) | Esperado |
|---------------------|----------|
| `matriculas` | **1** |
| `auditoria_tentativas` | **> 1** |

Não use o total da disciplina (`matriculas=3` depois do Exp. 1–2) — isso não é falha do Exp. 3.

### C.5 Experimento 4 — Retry **com** chave (+ 4b replay)

```bash
HOLD_MS=3000 MAX_TIME=1 RETRIES=3 ./scripts/matricular-idempotente.sh SD-101 aluno-exp4
```

Durante os retries: 1ª costuma dar timeout; após serializar, a 2ª pode já trazer `idempotent_replay` ou você vê o **4b** no fim:

1. espera o hold da 1ª tentativa  
2. retries seguintes (replay rápido — key é checada **antes** do hold)  
3. **4b)** confirmação sem hold → `idempotent_replay: true` e auditoria estável  

> Opcionais (completo): `./scripts/provar-idempotency-mismatch.sh` · `./scripts/provar-idempotency-ttl.sh`

### C.6 Experimento 5 — Circuit breaker *(caminho completo)*

```bash
./scripts/provocar-lento.sh 0
./scripts/provocar-erros.sh 100
for i in $(seq 1 8); do ./scripts/matricular.sh SD-101 "cb-$i" || true; done
curl -s http://127.0.0.1:8092/admin/config | python3 -m json.tool
./scripts/matricular.sh SD-101 cb-aberto || true

echo "aguardando janela do circuit (~8s)..."
sleep 9
./scripts/provocar-erros.sh 0
./scripts/matricular.sh SD-101 cb-sonda
curl -s http://127.0.0.1:8092/admin/config | python3 -m json.tool
```

**Observe:** aberto → (após ~8 s + sonda ok) fechado.

### C.7 Experimento 6 — Amplificação *(caminho completo)*

```bash
./scripts/amplificar-carga.sh
JITTER=0 ./scripts/amplificar-carga.sh
```

**Observe:** `requests >> N`, `wall_clock_lote_s`, `p50/p95`.

### C.8 Encerrar

```bash
docker compose down -v
```

---

## Anotações

| Exp. | O que viu |
|------|-----------|
| 1 | duracao_ms ≈ ? |
| 2 | aluno-exp2 commitou? |
| 3 | **deste aluno** auditoria=? matriculas=? |
| 4 + 4b | `idempotent_replay`? auditoria estável? |
| 5 | aberto → sonda → ? |
| 6 | requests vs N; p95 |

Próximo: [tutorial Mongo](tutorial-timeout-mongodb.md) ou [decisoes.md](decisoes.md).

# Tutorial — Lab Postgres: concorrência e matrícula

**Módulo:** [04 — Coordenação/locks](README.md) · **Lab:** [lab-concorrencia-postgres/](lab-concorrencia-postgres/)  
**Tempo sugerido:** tecnologia 15 min + lab ~2 h  
**Pré-requisito:** [03 — CAP](../03-consistencia-cap/) (FOR UPDATE) · [teoria.md](teoria.md) §1–5  
**Apoio:** [glossario.md](glossario.md) · [troubleshooting.md](troubleshooting.md)  
**Próximo:** [Mongo + Redis](tutorial-coordenacao-mongo-redis.md)

> Leia A e B *antes* do Compose. No lab: rode → observe → anote.

**Protagonista:** o portal escala para **3 instâncias de API**; código legado faz **read-modify-write** — a última vaga SD-101 pode **duplicar** matrícula.

---

## Parte A — A tecnologia: exclusão mútua no Postgres

### Em uma frase

Com **um primary compartilhado**, transações com **`FOR UPDATE`** ou **advisory lock** serializam writers. Sem isso, **RMW** perde updates.

### Funcionalidades que importam

| Mecanismo | Para quê no lab |
|-----------|-----------------|
| `?mode=broken` | Anti-padrão RMW + sleep |
| `?mode=transaction` | `FOR UPDATE` (recap 03) |
| `?mode=advisory` | `pg_advisory_xact_lock` |
| `?mode=optimistic` | Coluna `version` |
| nginx + 3 APIs | Writers distintos |

### vs módulo 03

| | [03 partição](../03-consistencia-cap/tutorial-particao-postgres.md) | Este lab |
|--|----------------------------------------------------------------------|----------|
| Pergunta | Sync + partição (CAP) | **Concorrência** multi-API |
| APIs | 1 | **3** (nginx) |
| Partição rede | Sim | Não |

---

## Parte B — Contexto de uso

Matrícula SD-101 — **1 vaga**. DevOps escalou API (`api-1`, `api-2`, `api-3`). Branch legado:

1. `SELECT vagas_restantes`  
2. processa 150 ms  
3. `INSERT` + `UPDATE` **sem** revalidar  

**Pergunta-guia:** o módulo 03 garantiu CP — por que ainda há overbooking?

> CP no 03 = sync + transação **correta**. Código **quebrado** viola exclusão — tema deste módulo.

| Peça | Lab |
|------|-----|
| nginx | `:8087` |
| Postgres | `:5438` |
| APIs | api-1/2/3 (via nginx) |

---

## Parte C — Lab prático

### C.1 Subir o ambiente

```bash
cd sistemas-distribuidos/04-coordenacao-locks/lab-concorrencia-postgres
docker compose up -d --build
# Postgres Bitnami: ~15–40 s. Poll:
for i in $(seq 1 20); do curl -sf http://localhost:8087/health && break; sleep 2; done
curl -s http://localhost:8087/health | python3 -m json.tool
curl -s http://localhost:8087/coordenacao/status | python3 -m json.tool
```

Resposta esperada em `/coordenacao/status`:

```json
{
  "modo_lab": "concorrencia_postgres",
  "api_instance": "api-1",
  "disciplinas": [
    {"id": "SD-101", "vagas_restantes": 1, "matriculados": 0}
  ],
  "alerta_overbooking_sd101": false
}
```

O `mode=broken` grava `vagas_restantes = valor_lido - 1` (não `coluna - 1` no SQL). Sem isso, o `CHECK (>= 0)` abortaria o segundo writer e **esconderia** o overbooking.

### C.2 Experimento 1 — RMW quebrado (overbooking)

Volumes frescos. **Antes** de outros experimentos:

```bash
./scripts/disputa-vaga.sh --paralelo --mode broken
```

**Observe:** `matriculados` deve ser **2**; `alerta_overbooking_sd101: true`. O campo `api_instance` **pode** variar (`api-1`, `api-2`, …) — o nginx não garante duas instâncias em dois requests; o overbooking vale **mesmo na mesma API** (threads). Confirme no `/coordenacao/status`.

### C.3 Experimento 2 — Transação FOR UPDATE

Reset:

```bash
docker compose down -v && docker compose up -d --build
sleep 15
./scripts/disputa-vaga.sh --paralelo --mode transaction
```

**Observe:** **1×201**, **1×409**; `vagas_restantes: 0`; uma matrícula apenas.

### C.4 Experimento 3 — Advisory lock

Reset +:

```bash
docker compose down -v && docker compose up -d --build
sleep 15
./scripts/disputa-vaga.sh --paralelo --mode advisory
```

Comportamento esperado **igual** ao transaction. O lab também usa `FOR UPDATE` depois do advisory (cinto e suspensório); **o advisory sozinho bastaria** para serializar por `disciplina_id`.

### C.5 Experimento 4 (opcional) — Optimistic locking

SD-101 precisa estar **fresca** (1 vaga). Depois do Exp. 3, reset:

```bash
docker compose down -v && docker compose up -d --build
sleep 15
./scripts/disputa-vaga.sh --paralelo --mode optimistic
```

**Observe:** um sucesso, outro **409 conflito de versão**. Sem reset, os dois falham com “sem vagas” e o experimento não mostra `version`.

### C.6 Experimento 5 (opcional) — Comparar tudo

```bash
./scripts/comparar-modos.sh
```

> ~5 min (3 resets Compose). Use em revisão ou demo do professor — **não** no caminho mínimo.

---

## Fechamento — Dois mecanismos

| Mecanismo | O que serializa | Exp. |
|-----------|-----------------|------|
| **RMW quebrado** | Nada — corrida | 1 |
| **`FOR UPDATE` / advisory** | Linha/recurso no primary | 2–3 |
| **Optimistic `version`** | Detecta conflito pós-facto | 4 |

**Ponte:** multi-campus / Mongo → [tutorial Mongo](tutorial-coordenacao-mongo-redis.md) · [decisoes §1](decisoes.md).

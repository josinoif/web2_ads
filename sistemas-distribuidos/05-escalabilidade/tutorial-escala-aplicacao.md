# Tutorial — Escala na camada de aplicação

**Módulo:** [05 — Escalabilidade](README.md) · **Lab:** [lab-escala-aplicacao/](lab-escala-aplicacao/)  
**Tempo sugerido:** ~2 h  
**Pré-requisito:** [teoria.md](teoria.md) §1–4  
**Apoio:** [glossario.md](glossario.md) · [troubleshooting.md](troubleshooting.md)  
**Próximo:** [Escala de dados](tutorial-escala-dados.md)

**Protagonista:** no **dia do boletim**, DevOps sobe réplicas da API — será que o RPS sobe de verdade? Até onde o **store único** deixa?

---

## Parte A — A tecnologia: LB + N APIs

### Em uma frase

Instâncias **stateless** atrás de um **balanceador** aumentam capacidade na **camada de aplicação** — até o **store compartilhado** virar o teto.

### Peças do lab

| Peça | Papel |
|------|-------|
| nginx `:8089` | LB round-robin para api1+2+3 |
| api1 `:8091` | Mesma API exposta (baseline 1 nó) |
| Postgres `:5439` | Um primary — **não** escala neste lab |
| `WORK_MS` | **CPU sintética (busy-wait)** — `sleep` não satura 1 API (libera GIL) |
| `DB_SLOTS` + `STORE_HOLD_MS` | Teto didático do store (Exp. 4 / `aproximar-teto`) |
| `/admin/delay` | Worker lento **só** naquela instância |

> **Por que `WORK_MS`?** Em produção a API gasta CPU em JSON, regras, auth. Aqui usamos **busy-wait** de 15 ms (padrão): `time.sleep` liberaria o GIL e o ganho 1→3 sumiria. Veja `work_ms` em `/escala/status`.

### Mapa rápido dos knobs (não precisa decorar)

| Knob | Quando mexe | Padrão |
|------|-------------|--------|
| `WORK_MS` | Exp. 1–2 (deixe 15) | 15 |
| `/admin/delay` | Exp. 3 worker lento | 0 |
| `DB_SLOTS` + `STORE_HOLD_MS` | **Só** Exp. 4 via `aproximar-teto.sh` | 0 |

O script do Exp. 4 **configura e reseta** sozinho — você não precisa editar `docker-compose.yml`.

### vs módulo 04

| 04 | 05 lab app |
|----|------------|
| 3 APIs para **corrida**/lock | 3 APIs para **capacidade**/métrica |
| Overbooking | RPS / p99 / gargalo móvel |

---

## Parte B — Contexto

Milhares de `GET /boletim`. A API faz um pouco de trabalho + query no Postgres.

**Pergunta-guia:** se eu só multiplicar a API, **qual camada** satura depois?

---

## Parte C — Lab

### C.1 Subir

```bash
cd sistemas-distribuidos/05-escalabilidade/lab-escala-aplicacao
docker compose up -d --build
for i in $(seq 1 20); do curl -sf http://localhost:8089/health && break; sleep 2; done
curl -s http://localhost:8089/escala/status | python3 -m json.tool
```

Espere `"camada": "aplicacao"`, `alunos: 200`, `work_ms: 15`.

### Caderno de resultados

Preencha enquanto roda (números do *seu* host):

| Exp. | O quê | rps_aprox | p50 | p99 | Nota |
|------|-------|-----------|-----|-----|------|
| 1 | 1 API (`:8091`) | | | | |
| 2 | 3 APIs (`:8089`) | | | | ganho ≈ ___× |
| 3 | worker lento api2 | | | | p99 sobe? |
| 4A | app-bound | | | | |
| 4B | store-bound (`DB_SLOTS`) | | | | RPS cai? |

### C.2 Experimento 1 — Baseline (1 API)

```bash
API=http://localhost:8091 ./scripts/medir-rps.sh
# ou defaults do comparar: N=240 CONCURRENCY=48
```

Anote `rps_aprox`, `p50`, `p99` na linha **Exp. 1**.

### C.3 Experimento 2 — Escala de aplicação (3 APIs)

```bash
./scripts/comparar-escala.sh
```

O script imprime `ganho_aprox=…x` (RPS 3 ÷ RPS 1). Defaults: `N=240` `CONCURRENCY=48`. Notebook fraco: `LIGHT=1 ./scripts/comparar-escala.sh`.

**Observe:** RPS com 3 APIs **maior** que com 1 → escala na camada **app**.  
**Interprete:** ganho &lt; ~1,2× → aumente `N`/`CONCURRENCY` ou o store já limita.

### C.4 Experimento 3 — Worker lento (cauda)

Compare **antes/depois** na mesma carga (anote p50 e p99):

```bash
# baseline
API=http://localhost:8089 N=120 CONCURRENCY=24 ./scripts/medir-rps.sh
./scripts/worker-lento.sh 120
API=http://localhost:8089 N=120 CONCURRENCY=24 ./scripts/medir-rps.sh
./scripts/worker-lento.sh 0
```

**Observe:** p50 pode subir pouco; **p99** sobe de forma mais clara — round-robin ainda manda ~1/3 do tráfego ao nó lento.  
**Produção:** health check / tirar o nó do LB (módulo [06](../06-falhas-timeout/)) — não só “mais réplicas”.

### C.5 Experimento 4 — Aproximar o teto do store

Este experimento **não** é stress de CPU do Postgres. Ele mostra o **gargalo móvel** com teto didático (`DB_SLOTS` + `STORE_HOLD_MS`):

```bash
./scripts/aproximar-teto.sh
```

| Fase | Config | O que espera |
|------|--------|--------------|
| A | `WORK_MS=15`, store livre | App-bound — 3 APIs rendem |
| B | `WORK_MS=0`, `DB_SLOTS=1`, `STORE_HOLD=40ms` | Store-bound — RPS **cai** |

**Interprete:** com o store limitado, escalar só a app **não** libera capacidade — o gargalo está na **camada de dados**.  
Próximo passo *realista* no boletim (leitura): **réplica** ([02](../02-replicacao/)) ou cache ([07](../07-cache-distribuido/)). Partição entra no próximo tutorial para **escrita** de avisos.

---

## Fechamento — Duas camadas (mesmo portal, dois fluxos)

| Mecanismo | Camada | Exp. |
|-----------|--------|------|
| 1 → 3 APIs | **Aplicação** | 1–2 |
| Worker lento | App (qualidade sob LB) | 3 |
| `DB_SLOTS` / store único | **Dados** (teto didático) | 4 |

**Mesmo portal, próximo fluxo:** leituras do boletim → réplica/cache; **escritas** de avisos por campus → [tutorial-escala-dados.md](tutorial-escala-dados.md) (partição).  
**Ponte:** [decisoes §1–2](decisoes.md).

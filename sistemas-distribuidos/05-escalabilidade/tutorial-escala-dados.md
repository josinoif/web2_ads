# Tutorial — Escala na camada de dados

**Módulo:** [05 — Escalabilidade](README.md) · **Lab:** [lab-escala-dados/](lab-escala-dados/)  
**Tempo sugerido:** ~1,5–2 h  
**Pré-requisito:** [tutorial-escala-aplicacao.md](tutorial-escala-aplicacao.md) · [teoria.md](teoria.md) §5–6  
**Apoio:** [glossario.md](glossario.md) · [troubleshooting.md](troubleshooting.md)

**Protagonista:** campi **A** e **B** publicam avisos ao mesmo tempo. Um único store de escrita satura — partimos por `campus_id`.

> **Ponte do lab anterior:** no dia do boletim você escalou **leitura** na app (e viu o teto do store). Aqui o fluxo é outro do **mesmo portal**: **escrita** de avisos. Réplica ([02](../02-replicacao/)) escala leitura; **partição** escala escrita quando a carga se espalha pela shard key.

---

## Parte A — A tecnologia: partição (shard key)

### Em uma frase

Dividir dados por **chave** (campus) em stores distintos aumenta capacidade de **escrita** quando a carga é **espalhada** — e cobra **fan-out** em leituras globais.

### Peças do lab

| Peça | Papel |
|------|-------|
| mongo-a / mongo-b | Dois stores (shards didáticos) |
| API router `:8090` | Escolhe o shard pela regra de `campus_id` |
| `GET /avisos` sem campus | Fan-out nos dois |
| `WRITE_MS` / `READ_SHARD_MS` | Custos sintéticos — tornam tempo hot≠spread e fan-out visíveis no notebook |

> **Não** é MongoDB Sharded Cluster de produção — é o **conceito** de shard key.

### O que este lab prova (e o que não)

| Prova (evidência) | Não prova sozinho |
|-------------------|-------------------|
| Hot key: tudo num shard (`B≈0`) | Stress máximo de disco Mongo |
| Spread: ~metade em A e B | “2× RPS” em produção sem medir |
| Fan-out: leitura global mais cara | Latência de datacenter real |

**Evidência principal = contagens em `/escala/status`.** Tempo de lote e `duracao_ms` são apoio (com `WRITE_MS` / `READ_SHARD_MS`).

### Duas técnicas na camada de dados

| Técnica | Onde no curso |
|---------|----------------|
| Réplica de **leitura** | [02](../02-replicacao/) — releia; não repetimos o cluster aqui |
| Partição de **escrita** | Este lab |

---

## Parte B — Contexto

Coordenação publica avisos por campus. Relatório institucional às vezes pede **todos** os campi.

**Pergunta-guia:** se todo mundo publicar no campus A, a partição ajudou?

---

## Parte C — Lab

### C.1 Subir

```bash
cd sistemas-distribuidos/05-escalabilidade/lab-escala-dados
docker compose up -d --build
for i in $(seq 1 20); do curl -sf http://localhost:8090/health && break; sleep 2; done
curl -s http://localhost:8090/escala/status | python3 -m json.tool
```

Espere `"camada": "dados"`, `write_ms` / `read_shard_ms` > 0.

### Caderno de resultados

| Exp. | O quê | Shard A | Shard B | elapsed / duracao_ms | Nota |
|------|-------|---------|---------|----------------------|------|
| 1 | hot | | ≈0 | | partição **não** ajudou |
| 2 | spread | ≈N/2 | ≈N/2 | | costuma ser mais rápido que hot |
| 3 | GET `?campus_id=A` | — | — | | single |
| 3 | GET sem campus | — | — | | fan-out ≥ single |

### C.2 Experimento 1 — Hot key (tudo no campus A)

```bash
N=40 ./scripts/publicar-lote.sh hot
```

**Observe (principal):** shard A ≈ 40; B ≈ 0. Hot shard = partição **não** ajudou.

### C.3 Experimento 2 — Carga espalhada

```bash
docker compose down -v && docker compose up -d --build
sleep 12
N=40 ./scripts/publicar-lote.sh spread
```

**Observe (principal):** A e B ≈ 20 cada — carga **distribuída**.  
**Apoio:** com `WRITE_MS`, o lote spread em paralelo costuma terminar **mais rápido** que hot (dois stores). Se os tempos forem parecidos, confie nas **contagens**.

### C.4 Experimento 3 — Fan-out (leitura global)

```bash
curl -s 'http://localhost:8090/avisos?campus_id=A&limit=5' | python3 -m json.tool
curl -s 'http://localhost:8090/avisos?limit=5' | python3 -m json.tool
```

Compare `duracao_ms` e o campo `modo`. Com `READ_SHARD_MS`, fan-out ≈ **~2×** single (paralelo + **agregação didática** rotulada no JSON — não é latência “mágica” escondida). Em rede real o gap cresce com N shards.

### C.5 Experimento 4 (opcional) — Script completo

```bash
./scripts/medir-writes.sh
```

### C.6 Ponte — réplica de leitura

Sem subir outro Compose: no [02](../02-replicacao/tutorial-postgres.md) você **já** escalou leitura com réplica. Junte as ideias:

| Necessidade | Técnica na camada de dados |
|-------------|----------------------------|
| Muitos `GET` no boletim | Réplica / secondary |
| Muitos `POST` por campus | Partição por chave |
| Ambos | Combinar (e aceitar trade-offs) |

---

## Fechamento — Duas camadas (módulo inteiro)

| Lab | Fluxo do portal | Camada | Mecanismo |
|-----|-----------------|--------|-----------|
| Aplicação | Boletim (leitura) | App (+ teto do store) | N APIs + LB |
| Dados | Avisos (escrita) | Store | Partição por campus |
| (02) | Boletim (leitura) | Store | Réplica |

**Ponte:** [decisoes.md](decisoes.md) · [06 — falhas](../06-falhas-timeout/) · [07 — cache](../07-cache-distribuido/).

# Tecnologias e escolhas — Falhas / timeout

**Módulo:** [06](README.md) · Use no workshop ou quando travar em “onde coloco o timeout?”.

---

## 1. Camadas de timeout

| Camada | Exemplo | Papel |
|--------|---------|--------|
| Cliente (`curl --max-time`, app) | Lab: 1 s (falso negativo) ou 3–5 s saudável | Não prender UI/thread do aluno |
| Deadline (`X-Deadline-Ms`) | Lab: aborta se hold > deadline (504) | Não ocupar worker além do prazo do cliente |
| API (circuit / fail-fast) | CB aberto → 503 | Não martelar store morto |
| Banco | `statement_timeout`, `connect_timeout` | Limitar query individual |

Regra didática: **cliente um pouco maior** que o pior caminho “saudável” da API; nunca “infinito”. Ver orçamento em [teoria §2.1](teoria.md).

---

## 2. Onde implementar idempotência

| Abordagem | Prós | Contras |
|-----------|------|---------|
| Header `Idempotency-Key` + tabela | Resposta idêntica no replay | Precisa **TTL/limpeza** em produção; mesma key + body diferente → **422** (lab) |
| `UNIQUE` no efeito (matrícula) | Simples, forte | Segunda tentativa vira 409 — UX a tratar |
| Upsert por id estável (Mongo) | Natural em documentos | Escolher mal a chave = colisão ou buraco |

No lab Postgres usamos **as duas**: unique no efeito + cache da chave (com fingerprint do corpo + **TTL** configurável).

**Produção (checklist mental):** TTL da key (lab: `IDEM_TTL_SEC` / `POST /admin/idem_ttl_sec`; demo `./scripts/provar-idempotency-ttl.sh`), escopo (método + path + body), e side effects via **outbox após commit**. Demo mismatch: `./scripts/provar-idempotency-mismatch.sh`.

---

## 3. Postgres vs Mongo neste módulo

| | Postgres (lab A) | Mongo (lab B) |
|--|------------------|---------------|
| Escrita crítica | Matrícula | Aviso |
| Dedup | Unique + idempotency table | Unique/`aviso_id` + upsert |
| Ponte CAP | Eco do 03 (CP / 503) | Eco concerns (`w:1` vs majority) — revisão opcional |
| Imagem | `postgres:16-alpine` | `mongo:7` |

Não precisa Bitnami/replicação aqui: o foco é **política de cliente**, não partição de rede.

---

## 4. Circuit breaker: quando vale

| Vale | Não é prioridade |
|------|------------------|
| Dependente falha em rajada e callers saturam | Lab com 1 usuário e erro raro |
| Quer falha **rápida** e previsível | Substituir monitoramento (isso é 09) |

O CB do lab é **mínimo** (falhas em **janela** `CB_WINDOW_SEC` + aberto + **1 sonda** no meio-aberto) — suficiente para ver o efeito, não para produção.

---

## 5. Relação com outros módulos

| Se a dor for… | Vá para… |
|---------------|----------|
| Partição primary↔réplica / CAP | [03](../03-consistencia-cap/) |
| Duas APIs no mesmo recurso | [04](../04-coordenacao-locks/) |
| Pouca capacidade / RPS | [05](../05-escalabilidade/) — veja também Exp. 6 (`amplificar-carga.sh`) |
| Resposta velha em cache | [07](../07-cache-distribuido/) |

---

## 6. Cola rápida

| Sintoma | Primeira pergunta |
|---------|-------------------|
| Hang eterno | Tem timeout no cliente? |
| Duplicatas após “erro” | Tem idempotency / unique? (qual efeito: negócio ou side effect?) |
| Cascata lenta | CB, bulkhead ou isolamento de pool? |
| Tudo lento após falha | Retry amplificando carga? → Exp. 6 / [05](../05-escalabilidade/) |
| 503 sob partição sync | É o 03 — recusar é feature |

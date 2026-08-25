# Glossário — Falhas, timeout e retries

**Módulo:** [06 — Falhas/timeout](README.md)

| Termo | Definição curta |
|-------|-----------------|
| **Falha parcial** | Só parte do sistema falha/atrasa; o resto segue — cenário típico em distribuídos. |
| **Timeout** | Limite de tempo para aguardar resposta; estourar ≠ prova de que a operação não commitou. |
| **Falso negativo** | Cliente acha que falhou, mas o servidor **já** concluiu com sucesso. |
| **Retry** | Nova tentativa após erro/timeout. |
| **Backoff** | Espera crescente entre retries (no lab: **0,2 s → 0,5 s → 1,0 s**). |
| **Jitter** | Aleatoriedade no backoff para evitar retries sincronizados. |
| **Retryable** | Erro que *pode* sumir sozinho (rede, 503, timeout) — **não** 409/400/401. |
| **Idempotência** | N execuções do mesmo pedido = mesmo efeito de 1 execução. |
| **Idempotency-Key** | Identificador do pedido; servidor deduplica / devolve resposta cacheada (lab: com **TTL** + fingerprint). |
| **At-least-once** | Entrega “pelo menos uma vez” — exige idempotência no consumidor/efeito. |
| **At-most-once** | No máximo uma vez — pode perder mensagem (raro em labs desta trilha). |
| **Exactly-once** | Ideal difícil; na prática = at-least-once + idempotência. |
| **Circuit breaker** | Para de chamar dependente após muitas falhas; falha rápido até sondar de novo. |
| **Meio-aberto** | Após a janela, admite **sonda(s)** limitadas; sucesso fecha, falha reabre. |
| **Thundering herd** | Muitos clientes retryam ao mesmo tempo e derrubam o serviço de novo. |
| **Cascata de falha** | Um nó lento/falho satura callers e propaga indisponibilidade. |
| **Orçamento de latência** | Soma de timeouts ao longo do caminho (cliente → API → DB). |
| **Deadline propagation** | Prazo do cliente fluindo para a API (lab: header `X-Deadline-Ms` → 504 se hold não cabe). |
| **statement_timeout** | Limite no Postgres para uma statement SQL. |
| **Bulkhead** | Isolar recursos (pools/threads) por dependência ou rota para falha não contagiar o resto. |
| **Amplificação de carga** | Retries (e fan-out) multiplicam trabalho no gargalo — liga resiliência à escala. |
| **Outbox** | Padrão: gravar evento na mesma tx do negócio e publicar depois — side effect após commit. |
| **writeConcern** | Mongo: quantos nós confirmam a escrita (`w:1`, `majority`, …). |

Ver também: [glossário CAP](../03-consistencia-cap/glossario.md) (CP, AP, partição).

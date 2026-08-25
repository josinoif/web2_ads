# Tecnologias e escolhas — Cache distribuído

**Módulo:** [07](README.md) · Use no workshop ou quando travar em “onde coloco o cache?”.

---

## 1. Onde colocar o cache

| Camada | Exemplo | Quando |
|--------|---------|--------|
| Processo (local) | dict / LRU in-proc | Protótipo; **não** compartilhado entre réplicas |
| Remoto compartilhado | Redis (labs) | N APIs, mesmo valor |
| CDN / borda | CloudFront etc. | Estáticos / HTML — fora deste lab |
| Réplica de leitura | Postgres async ([02](../02-replicacao/)) | Outra forma de “cópia”; também stale |

Neste módulo o foco é **Redis como cache-aside** na API.

---

## 2. TTL vs invalidação

| | TTL | Invalidate (`DEL`) |
|--|-----|---------------------|
| Simplicidade | Alta | Precisa lembrar todas as chaves |
| Stale máximo | = TTL | ≈ 0 após write bem-sucedido |
| Stampede | No expire | No miss após DEL em massa |
| Lab | Avisos (Mongo) | Boletim (Postgres, padrão ON) |

Produção costuma **combinar**: invalidate no write + TTL como rede de segurança.

---

## 3. Postgres vs Mongo neste módulo

| | Postgres (lab A) | Mongo (lab B) |
|--|------------------|---------------|
| Domínio | Boletim / nota | Feed de avisos |
| Política didática | Invalidate default ON | TTL; invalidate default OFF |
| Extra | Stampede lock | 2 APIs · local vs Redis |
| Portas | 8094 / 5441 / 6381 | 8095–96 / 27122 / 6382 |

O padrão de código é o mesmo; muda o **requisito de negócio**.

---

## 4. Stampede: mitigações mínimas

| Técnica | Lab | Nota |
|---------|-----|------|
| Single-flight (`SET NX`) | `provar-stampede.sh` LOCK=1 · olhe `store_reads_na_rajada` | Didático |
| TTL jitter | `./scripts/set-jitter.sh` + Exp. 5b | Espalha expires; **combine** com lock no pico |
| SPOF Redis | `./scripts/provar-redis-spof.sh` (Exp. 5c) | Cache parado → 503; produção = fallback/CB |
| Soft TTL / SWR | Conceito | Servir stale enquanto revalida |

Não confundir com TTL de **Idempotency-Key** do [06](../06-falhas-timeout/).

---

## 5. Relação com outros módulos

| Se a dor for… | Vá para… |
|---------------|----------|
| Partição / CP vs AP na réplica | [03](../03-consistencia-cap/) |
| Overbooking / lock | [04](../04-coordenacao-locks/) |
| RPS / gargalo de camada | [05](../05-escalabilidade/) |
| Timeout/retry sob miss lento | [06](../06-falhas-timeout/) |
| Métricas hit/miss em produção | [09](../09-observabilidade/) (planejado) |

---

## 6. Cola rápida

| Sintoma | Primeira pergunta |
|---------|-------------------|
| Store no 100% com leitura repetida | Tem cache compartilhado? `store_reads` / hit rate? |
| Aluno vê nota antiga após correção | Invalidate no write? TTL longo demais? |
| “Achei que li o Postgres” no hit | Olhe `servido_de` (não só `fonte_dados`) |
| Duas APIs divergem | Cache local? |
| Pico de CPU no store a cada N minutos | Stampede no TTL? |
| Overbooking com “vagas em cache” | **Não** cacheie vagas |

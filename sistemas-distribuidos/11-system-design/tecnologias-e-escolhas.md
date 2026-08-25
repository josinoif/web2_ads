# Tecnologias e escolhas — System Design

**Módulo:** [11 — System Design](README.md)  
**Pré-leitura:** [teoria.md](teoria.md)

Este módulo **não** introduz stack nova de produção. A tabela liga cada bloco de entrevista ao que você **já usou** na trilha.

> **01–10 = evidência · 11 = composição sob relógio.**

---

## 1. Bloco de entrevista → evidência no curso

| Bloco | O que já apareceu | Onde |
|-------|-------------------|------|
| App stateless + LB | N APIs atrás de nginx | [05](../05-escalabilidade/) lab app |
| Réplica líder/seguidores | Lag, sync/async | [02](../02-replicacao/) |
| Consistência vs disponibilidade | Partição, concerns | [03](../03-consistencia-cap/) |
| Lock / unicidade | Reserva, único ID de matrícula | [04](../04-coordenacao-locks/) |
| Gargalo móvel | RPS, teto do banco | [05](../05-escalabilidade/) |
| Timeout, retry, idempotência | Matrícula / avisos | [06](../06-falhas-timeout/) |
| Cache + stale | Redis na frente do boletim | [07](../07-cache-distribuido/); lab A |
| Blob + metadado | MinIO + Postgres/Mongo | [08](../08-armazenamento-arquivos/) |
| Métricas / traces | Grafana, OTel | [09](../09-observabilidade/) |
| Estilo, fila, fan-out | Monólito vs serviços; sync vs eventos | [10](../10-arquitetura/) |
| Encurtador (IDs, 301, cache) | Este módulo | Lab A |
| Feed (write vs read) | Este módulo | Lab B |
| Rate limit + fail policy | Este módulo | Lab C |
| Notificação multi-canal | Este módulo | Lab D |

---

## 2. Lab A — o que cada peça faz

| Peça | Papel didático |
|------|----------------|
| `contador` (:8140) | Código via **INCR** + base62 — sem colisão de hash |
| `hash` (:8141) | Prefixo MD5 curto — **colisão visível** |
| Redis (:6392) | Cache do GET + sequenciador do contador |
| Store no processo | “Banco” com `STORE_HOLD_MS` (atraso injetável) |
| 301 vs 302 | Header `Location`; cacheabilidade no *cliente* |

**Não é** bit.ly de produção. Sem geo-DNS, sem base62 perfeita, sem shard.

---

## 3. Lab B — o que cada peça faz

| Peça | Papel didático |
|------|----------------|
| `write` (:8150) | Fan-out **on write** (inbox); modo inline ou worker |
| `read` (:8151) | Fan-out **on read** (junta following na hora) |
| Redis (:6393) | Grafo, posts, inboxes, fila do worker |
| `worker` | Consome fan-out quando o write não faz inline |
| Celebridade / leitor | POST caro (write) vs GET caro (read) |

**Não é** Twitter. Sem ranking ML, sem grafo real, sem Kafka (ponte: [01](../01-comunicacao/) e lab B do [10](../10-arquitetura/)).

---

## 4. Lab C — o que cada peça faz

| Peça | Papel didático |
|------|----------------|
| `closed` (:8160) | Redis down → **503** (fail-closed) |
| `open` (:8161) | Redis down → **200** (fail-open) |
| Redis (:6394) | Contador `INCR` + TTL — **janela fixa** |
| Cota (default 5 / 10 s) | Estoura → **429** |

**Não é** Kong/Envoy. **Não é** token bucket nem sliding window (cite-os na oral; lab = fixed window).

---

## 5. Lab D — o que cada peça faz

| Peça | Papel didático |
|------|----------------|
| `unico` (:8170) | Uma fila; worker processa e-mail (2 s) **antes** do push |
| `canais` (:8171) | Filas `push` / `email` / `sms` em paralelo |
| Redis (:6395) | Filas (DB 0 = unico, DB 1 = canais) |
| Workers | Simulam latência de gateway por canal |

**Não é** SES/FCM. Sem template, preferências nem DLQ.

---

## 6. Matriz de decisão rápida (entrevista)

| Se você precisa… | Incline para… | Evite… |
|------------------|---------------|--------|
| GET quente, POST raro | Cache + store simples (lab A) | Fila na escrita do redirect |
| POST da celebridade barato | Fan-out on **read** ou híbrido | Copiar inbox para 10 M seguidores síncrono |
| GET do feed em O(1) | Fan-out on **write** | Merge de 5 mil followees na hora |
| Recibo agora, trabalho depois | Fila ([01](../01-comunicacao/), [10](../10-arquitetura/), lab D) | Encadear SMTP no POST |
| Unicidade de ID | Contador/ticket ou Snowflake-like | MD5 truncado em espaço pequeno |
| Proteger API pública | Rate limit na borda (lab C, janela fixa) | “O LB resolve”; chamar o lab de token bucket |
| Limiter Redis down (pagamento) | Fail-**closed** | Deixar tudo passar |
| Limiter Redis down (feed) | Fail-**open** (com métrica) | 503 em toda leitura |
| Push sem esperar e-mail | Fila **por canal** (lab D) | Um worker para três canais |
| Vídeo / PDF grande | Object storage + metadado ([08](../08-armazenamento-arquivos/)) | BYTEA / documento único enorme |

---

## 7. Cloud vs lab

| Produção | Lab 11 |
|----------|--------|
| Postgres / Dynamo / Cassandra | Dict no processo + Redis |
| Kafka / SQS com retenção | Lista Redis (worker pode atrasar) |
| CDN (CloudFront, Fastly) | Não há PoP — só o *conceito* no quadro |
| Consistent hashing em cluster | Ficha + intuição do [05](../05-escalabilidade/) |
| Multi-DC | Compose numa máquina |
| K8s / service mesh | Fora — “escala ≠ só orquestrador” ([05](../05-escalabilidade/)) |

---

## Fora deste módulo

Crawler, autocomplete, proximity, pagamentos, bolsa (Vol. 2): ver apêndice em [casos-entrevista.md](casos-entrevista.md). Aqui: **processo de entrevista** + quatro experimentos observáveis + mocks.

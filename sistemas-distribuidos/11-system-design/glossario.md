# Glossário — System Design

**Módulo:** [11 — System Design](README.md)

| Termo | Definição curta |
|-------|-----------------|
| **System design (entrevista)** | Desenho colaborativo de um produto: escopo, diagrama, gargalo, falha — em ~45 min. |
| **Escopo** | O que entra / sai do problema neste intervalo (passo 1). |
| **Buy-in** | Concordância no desenho alto nível antes do detalhe (passo 2). |
| **Deep dive** | Aprofundar 1–2 gargalos, não todas as caixas (passo 3). |
| **Wrap-up** | SPOF, 10× escala, consistência, métricas (passo 4). |
| **Envelope** | Estimativa de ordem de grandeza (QPS, bytes, máquinas) com premissas escritas. |
| **QPS / RPS** | Queries/requests por segundo; separe leitura e escrita. |
| **DAU** | Daily active users — ponto de partida comum para QPS. |
| **p50 / p99** | Latência mediana vs cauda; a entrevista liga p99 à UX. |
| **SLA / nines** | Alvo de disponibilidade; 99,9% ≠ “nunca cai o worker”. |
| **Building block** | Peça reutilizável (LB, cache, fila, shard, CDN). |
| **Stateless (web tier)** | Instância não guarda sessão local — LB pode espalhar à vontade. |
| **SPOF** | Single point of failure — um nó cuja queda derruba o serviço. |
| **Fan-out on write** | Na escrita, copia o evento para as inboxes dos seguidores. |
| **Fan-out on read** | Na leitura, junta os posts de quem você segue. |
| **Celebrity problem** | Poucos autores com milhões de seguidores; write-fanout explode. |
| **Hot key** | Chave/partição que concentra carga (já no [05](../05-escalabilidade/)). |
| **URL shortener** | POST longa → código curto; GET código → redirect. |
| **301 / 302** | Redirect permanente (cacheável) vs temporário. |
| **Collisão (hash)** | Dois inputs distintos, mesmo código curto. |
| **Rate limiter** | Teto de pedidos por chave (IP, token) por janela. |
| **Fixed window** | Conta na janela `[t0, t0+W)`; lab C (`INCR`+TTL). Armadilha: *edge burst* na virada da janela. |
| **Token bucket** | Saldo de tokens que recarrega; picos curtos ok até esgotar — **não** é o lab C. |
| **Sliding window** | Contagem numa janela que anda no tempo (mais justa, mais cara). |
| **Fail-open / fail-closed** | Sem Redis: deixa passar (**200**) vs rejeita (**503**). Cota estourada com Redis ok = **429**. |
| **Working set** | Subconjunto quente de dados que de fato é acessado (≠ tudo que foi criado). |
| **Unique ID** | Identificador único global (contador, ticketing, relógio+worker). |
| **Consistent hashing** | Anel de chaves; ao sair um nó, só uma fatia remapeia. |
| **CDN** | Cache geográfica na borda; reduz RTT e QPS na origem. |
| **Object storage** | Blob endereçado por chave; metadado mora noutro store ([08](../08-armazenamento-arquivos/)). |
| **Presença (chat)** | Saber quem está online — dado volátil, TTL curto. |
| **Inbox / timeline** | Lista pré-materializada (write) vs montada na hora (read). |

Ver também: [glossário 05](../05-escalabilidade/glossario.md) · [07](../07-cache-distribuido/glossario.md) · [10](../10-arquitetura/glossario.md).

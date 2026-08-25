# Modelo falado — URL shortener (4 passos)

**Módulo:** [11 — System Design](README.md)  

> **Não abra este arquivo na 1ª passagem.**  
> 1) Teoria §1–3 + **folha §3.5** no papel.  
> 2) Lab A (ou ensaio oral sozinho).  
> 3) **Só então** compare com o texto abaixo (idealmente no dia seguinte).

> Tom de **entrevista oral** (~8–12 min condensados). Números = premissas da teoria §3.4.

---

## Passo 1 — Escopo

“Antes de desenhar: é só **encurtar + redirect**, ou também analytics e página de preview?  
Assumo **100 M URLs novas/mês**, leitura:escrita **100:1**, pico **2×**.  
Fora de escopo neste bloco: login, billing, app mobile, QR customizado.  
SLA: GET do redirect com p99 baixo; POST pode ser um pouco mais lento.  
Consistência: se o POST acabou de retornar o código, o GET desse código deve achar — forte o bastante no caminho feliz.”

---

## Passo 2 — High-level + dados + buy-in

“Entidades: `Url { codigo, destino, created_at }`.  
API: `POST /encurtar {url}` → `{codigo}`; `GET /r/{codigo}` → 301/302 + `Location`.  

```text
Cliente → LB → App stateless → Cache → Store
                              ↘ POST grava no Store
```

GET: tenta cache; miss vai ao store. POST: gera ID, grava, opcionalmente aquece cache.  
Está ok seguirmos por aqui e detalhar **geração de ID** e **cache no GET**?”

---

## Passo 3 — Deep dive (escolha um eixo; aqui: os dois em resumo)

**IDs:** “Prefiro **contador** (INCR + base62): unicidade simples. Hash truncado curto **colide** — vimos no lab A. UUID na URL curta é verboso. Em multi-DC depois pensaria em ticket/Snowflake-like.”

**Leitura:** “Com ~4k–8k QPS de GET, o store não aguenta miss em tudo. Cache com TTL; 301 se o destino for estável (cliente para de perguntar) — mas aí trocar o destino fica difícil; 302 se ainda mudamos campanha. Abuso/spam de criação: rate limit no POST ([lab C](lab-rate-limiter/) — janela fixa; ficha para token bucket / sliding window).”

**Idempotência:** “Se o cliente retriar o POST com a mesma URL, posso devolver o mesmo código (dedup por hash da URL no store) para não criar N códigos — liga ao [06](../06-falhas-timeout/).”

---

## Passo 4 — Wrap-up

“SPOF: Redis do contador/cache — réplica + decidir fail-open/closed no GET (stale?) vs POST.  
10× reads: mais cache/CDN na borda, não só mais workers cegos ([05](../05-escalabilidade/)).  
Métricas: QPS GET/POST, p99 lookup, hit rate, taxa de 5xx, colisões se houver hash ([09](../09-observabilidade/)).  
O que eu *não* detalhei: geo-DNS, shard do store, analytics.”

---

## O que o lab A prova / não prova

| Diz na entrevista | Evidência |
|-------------------|-----------|
| Cache tira o store do caminho quente | `medir-leitura.sh` |
| Hash curto colide | `provar-colisao.sh` |
| 301 vs 302 muda cacheabilidade no cliente | `provar-redirect.sh` |
| Redis caiu | `provar-redis-down.sh` |
| Bit.ly global, geo, shard | **Não** — diga que ficou de fora |

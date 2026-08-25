# Troubleshooting — System Design

**Módulo:** [11 — System Design](README.md)

---

## Docker / daemon

| Sintoma | Ação |
|---------|------|
| `failed to connect … docker.sock` | Suba Docker Desktop; ou Podman (abaixo) |
| `permission denied … docker.sock` | Usuário fora do grupo `docker` |
| Podman rootless | Scripts usam `_compose.sh` (mesmo padrão 09/10); ou `export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock DOCKER_CONTEXT=default` |

**Um lab por vez.** `docker compose down -v` antes de trocar A ↔ B ↔ C ↔ D.

---

## Portas

| Lab | Portas |
|-----|--------|
| A — contador | `8140` |
| A — hash | `8141` |
| A — Redis | `6392` |
| B — fan-out write | `8150` |
| B — fan-out read | `8151` |
| B — Redis | `6393` |
| C — fail-closed | `8160` |
| C — fail-open | `8161` |
| C — Redis | `6394` |
| D — fila única | `8170` |
| D — por canal | `8171` |
| D — Redis | `6395` |

Se “address already in use”: `compose down -v` no lab anterior (10 usa 8120–8131 / Redis 6381; 07 usa 6381).

---

## Lab A (`8140` / `8141`)

```bash
cd sistemas-distribuidos/11-system-design/lab-url-shortener
./scripts/up.sh
curl -s http://127.0.0.1:8140/health | python3 -m json.tool
curl -s http://127.0.0.1:8141/health | python3 -m json.tool
```

| Sintoma | Ação |
|---------|------|
| Health 000 | `compose ps`; `./scripts/up.sh` de novo |
| GET não fica mais rápido com cache | `STORE_HOLD_MS` precisa ser alto (ex. 40); limpe o cache no `/admin` ou use URL nova só no miss inicial |
| Colisão zero | `HASH_CHARS=3` (ou 4) e centenas de URLs — `./scripts/provar-colisao.sh` |
| 301 vs 302 iguais no browser | Use `curl -sI`; o lab não controla o cache do Chrome |
| Redirect segue e “some” o 30x | `curl -sI` ou `/lookup/{codigo}` |
| `provar-redis-down` lookup lento | Normal se o cliente Redis espera DNS/timeout; na API há timeout curto (0,5 s). Rebuild se mudou o código |

---

## Lab B (`8150` / `8151`)

```bash
cd sistemas-distribuidos/11-system-design/lab-feed-fanout
./scripts/up.sh
./scripts/seed.sh
```

| Sintoma | Ação |
|---------|------|
| Feed vazio | Rode `seed.sh` **antes** de postar; `celeb` e `u1` existem só depois do seed |
| POST celebridade não está lento | Modo **inline** no write; `FANOUT_MS_PER_FOLLOWER` > 0; seed com N seguidores |
| Worker down mas inbox já cheia | `fanout_mode=worker` **antes** do POST; `compose stop worker` |
| Read GET não dói | Use o usuário `leitor` (segue muita gente), não `u1` |
| Redis connection | Host `6393`; na rede Compose `redis:6379` |

---

## Lab C (`8160` / `8161`)

```bash
cd sistemas-distribuidos/11-system-design/lab-rate-limiter
./scripts/up.sh
./scripts/provar-cota.sh closed
./scripts/provar-redis-down.sh
```

| Sintoma | Ação |
|---------|------|
| Sem 429 | Cota default 5/10 s; use chave nova (`provar-cota.sh` já gera); `/admin/reset` se misturou keys |
| Closed e open iguais com Redis down | Confira `FAIL_MODE` no health; rebuild se mudou o código |
| Redis down mas POST ainda 200 no closed | Aguarde o stop do container; health `redis_ok: false` |
| POST demora ~1–2 s com Redis parado | **Artefato Compose:** DNS do hostname `redis` após `stop` — não é o algoritmo do limiter. Timeouts do cliente Redis são 0,5 s; a resolução de nome pode dominar. |

---

## Lab D (`8170` / `8171`)

```bash
cd sistemas-distribuidos/11-system-design/lab-notificacao-canais
./scripts/up.sh
./scripts/provar-isolamento.sh
```

| Sintoma | Ação |
|---------|------|
| Push rápido também no unico | `EMAIL_DELAY_MS=2000` no `worker-unico`; ordem da fila coloca e-mail antes do push |
| Canais sem diferença | Workers push/email/sms devem estar up (`compose ps`) |
| Evento some | Confira Redis DB 0 (unico) vs DB 1 (canais) |

---

## Checklist professor (piloto)

- [x] Lab A: `medir-leitura.sh` mostra p50 cache ≪ p50 store  
- [x] Lab A: `provar-colisao.sh` conta colisões no hash  
- [x] Lab A: `curl -sI` 301 vs 302  
- [x] Lab A: `provar-redis-down.sh` — contador POST 503; lookup local ok  
- [x] Lab A: `provar-idempotencia.sh` — key/URL dedup; 409 em conflito  
- [x] Lab B: POST `celeb` write ≫ POST `celeb` read  
- [x] Lab B: GET `leitor` read ≫ GET `leitor` write  
- [x] Lab B: worker parado → POST aceito, inbox sem o post novo  
- [x] Lab B: seed via `/admin/seed` (rápido)  
- [x] Lab C: `provar-cota.sh` → 429 após 5 OK  
- [x] Lab C: Redis down → closed 503 · open 200  
- [x] Lab D: `provar-isolamento.sh` → push unico ≫ push canais  

---

## Validação local

| Campo | Valor |
|-------|-------|
| **Data** | 2026-08-25 (piloto agente) |
| **SO / Docker** | Linux fc44; Podman via `DOCKER_HOST=…/podman.sock` |
| **Lab A — cache** | `medir-leitura.sh`: cache_on p50≈0,5 ms (39 hits) · cache_off p50≈40 ms |
| **Lab A — redirect** | `curl -sI`: 302 + `no-store` · 301 + `max-age=86400` |
| **Lab A — colisão** | `HASH_CHARS=3`, N=200 → `colisoes=3` |
| **Lab A — Redis down** | contador POST **503**; lookup de código antigo via store; hash POST ok |
| **Lab B — celebridade** | write: u1≈24 ms / celeb≈226 ms · read POST ≈1 ms |
| **Lab B — leitura** | write GET inbox ≈1 ms · read GET leitor≈232 ms vs u1≈12 ms |
| **Lab B — worker** | worker down → POST enfileirado, `achou_marker False` → start → `True` |
| **Lab B — seed** | `/admin/seed` ≈1 s para N=40 (ambas as bordas) |
| **Lab C — cota** | 5×200 + 3×429 (limit 5/10 s) |
| **Lab C — Redis down** | closed **503** · open **200** `fail_open` |
| **Lab D — isolamento** | unico push ≈2197 ms · canais push ≈116 ms |
| **Observações** | Portas 8140–8171 / Redis 6392–6395. Um Compose por vez. |

---

## Fallback sem Docker

Leia [teoria.md](teoria.md) §1–6, as fichas em [casos-entrevista.md](casos-entrevista.md) e [decisoes.md](decisoes.md). No papel: desenhe encurtador (cache no GET), feed (write vs read), rate limit (fail policy) e notificação (fila por canal).

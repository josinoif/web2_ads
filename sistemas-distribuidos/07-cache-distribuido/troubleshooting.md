# Troubleshooting — Labs do módulo 07

Faça **um lab por vez**. Ao trocar:

```bash
docker compose down -v
```

Encerre labs 02–06 se as portas conflitarem.

---

## Portas deste módulo

| Serviço | Host |
|---------|------|
| API Postgres | **8094** |
| Postgres | **5441** |
| Redis (lab PG) | **6381** |
| API Mongo 1 / 2 | **8095** / **8096** |
| Mongo | **27122** |
| Redis (lab Mongo) | **6382** |

---

## Geral

| Sintoma | O que tentar |
|---------|----------------|
| `Cannot connect to Docker daemon` | Docker Desktop **ou** Podman: `export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock` |
| Porta em uso | `docker ps`; `down -v` no outro lab |
| API 503 no boot | Store/Redis subindo — espere; `./scripts/up.sh` |
| `COMPOSE_FILE` / projeto errado | `unset COMPOSE_FILE COMPOSE_PROJECT_NAME` |
| Scripts `compose: command not found` | Use `_compose.sh` via `./scripts/up.sh` |
| Hit rate estranho após testes | `./scripts/flush.sh` (zera cache + stats) |
| Acho que o hit leu o banco | Confira `servido_de: redis` (e `fonte_dados` = SoT) |

---

## Lab Postgres (`lab-cache-postgres`, :8094)

| Sintoma | O que tentar |
|---------|----------------|
| Exp. 1 sem latência alta | `./scripts/provocar-lento.sh 800` + `set-backend.sh off` |
| Exp. 2 sem hits | `set-backend.sh redis` + `flush.sh` antes do benchmark |
| Exp. 3 não fica stale | `set-invalidate.sh 0` **antes** do atualizar; confirme no JSON `invalidou_cache: false` |
| Exp. 4 ainda stale | `set-invalidate.sh 1`; confira `invalidou_cache: true` |
| Stampede sem diferença | Rebuild API; `N=20`; compare `store_reads_na_rajada` LOCK=0 vs 1 |
| Stampede “N+1” | Total inclui aquecimento — use `store_reads_na_rajada` |
| Jitter não muda TTL | `./scripts/set-jitter.sh 3` + `flush` + `ler.sh` → `ttl_sec_aplicado` |
| Nota / feed “estranho” vs seed | `docker compose down -v` e `./scripts/up.sh` de novo |
| Exp. 3: notei valor X ≠ 7.5 | Normal se o volume já tinha PUT anterior — stale = **antes do PUT**, não “sempre 7.5” |
| SPOF Redis | `./scripts/provar-redis-spof.sh`; JSON com `code: redis_indisponivel`; se Redis ficou parado: `compose start redis` |

---

## Lab Mongo (`lab-cache-mongodb`, :8095/:8096)

| Sintoma | O que tentar |
|---------|----------------|
| Só uma API sobe | `./scripts/up.sh` espera as duas; `compose ps` |
| `comparar-local-vs-redis` falha | **Obrigatório:** `cd lab-cache-mongodb` antes de `./scripts/...` |
| Local também “compartilha” | Confirme `cache_backend: local` nas **duas** APIs (`set-backend.sh local`) |
| Stale não aparece | `set-invalidate.sh 0` + popular cache **antes** de publicar |
| Benchmark com `store_reads=0` e hits altos | Redis ainda quente após Exp. 1 — rode `flush.sh` antes |
| `publicar.sh` JSON quebrado | Use aspas simples no título/corpo sem aspas internas, ou título simples |
| Feed com avisos de aula passada | `docker compose down -v` + `./scripts/up.sh` |

---

## Ponte com outros módulos

| Sintoma “parece 07” | Na verdade… |
|---------------------|-------------|
| Stale em **réplica** Postgres | [02](../02-replicacao/) / [03](../03-consistencia-cap/) |
| Overbooking | [04](../04-coordenacao-locks/) |
| Store no teto sem cache | [05](../05-escalabilidade/) primeiro; depois 07 |

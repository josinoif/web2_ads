# Troubleshooting — Labs do módulo 03

Faça **um lab por vez**. Ao trocar:

```bash
docker compose down -v
```

Encerre labs do **módulo 02** se portas conflitarem (`8082`–`8084`, `5434`–`5435`, `27017`).

---

## Geral

| Sintoma | O que tentar |
|---------|----------------|
| Porta em uso (`8085`, `8086`, `5436`, `5437`, `27117`) | `down -v` no outro lab; `docker ps` |
| API `503` no começo | Banco/replica set ainda subindo — espere 30–90s |
| `Cannot connect to Docker daemon` | Suba o serviço Docker |
| `bitnami/postgresql:16` → `manifest unknown` | Lab Postgres usa `bitnamilegacy/postgresql:16.6.0-debian-12-r2@sha256:af99…` (pin) |
| Partição “não faz efeito” | Confirme nome da rede (`sd03-*`); rode script de novo |
| Lab sobe mas `sync_state` ≠ sync/quorum | Rode `./scripts/ativar-sync.sh` (boot usa 0 sync para o init não deadlockar; `ANY 1` → `quorum`) |
| Primary “travado” no init / Connection refused na réplica | Sintoma do deadlock antigo (`NUM_SYNCHRONOUS_REPLICAS=1` no boot) — `down -v` e suba de novo com o compose atual |
| `permission denied` em ALTER SYSTEM | Confirme `POSTGRESQL_POSTGRES_PASSWORD=portaladmin` no compose; script usa user `postgres` |

---

## Lab Postgres partição (`lab-particao-postgres`, :8085)

| Sintoma | O que tentar |
|---------|----------------|
| `sync_state` não é `sync` | `./scripts/verificar-modo-cp.sh`; recrie volume se async |
| Réplica lenta no boot | Espere 1–3 min (base backup); [poll abaixo](#enquanto-espera-a-réplica) |
| `POST /matricular` → 503 com `sync_ativo=false` | Partição ativa — **esperado** (API recusa sem réplica sync/quorum) |
| Partição “ativa” mas `POST` ainda dá 201 | Walsender half-open — use `particionar.sh` atual (disconnect + `pg_terminate_backend`); rebuild API |
| Após `curar`, DNS `postgres-replica` some | Use `curar-particao.sh` com `--alias postgres-replica` |
| `particionar.sh` falha | `docker compose ps`; confira rede `sd03-particao-postgres_repl_net` |
| `GET ?dest=replica` falha com partição ativa | Esperado — réplica desconectada da `repl_net`; use `dest=primary` ou cure a partição |
| `GET /disciplinas/...?dest=replica` falha sem partição | Confira API em `repl_net`; poll [réplica](#enquanto-espera-a-réplica) |
| Overbooking no Exp. disputa | Recrie volumes (`down -v`); disciplina SD-101 começa com 1 vaga |
| `curl: (56) Connection reset` em :8085 | API ainda subindo — `docker compose logs api` |

### Enquanto espera a réplica

```bash
until curl -s http://localhost:8085/consistencia/status \
  | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d.get('replica_acessivel') else 1)" 2>/dev/null; do
  echo "aguardando réplica (8085)..."
  sleep 10
done
```

Enquanto espera: revise [teoria §2–3](teoria.md) ou [mapa dos 2 labs](README.md#mapa-dos-2-labs--qual-pergunta-cada-um-responde).

### Enquanto espera commit sob partição (Experimento 3)

- O que você **espera** ver: **503 imediato** com `sync_ativo=false`, **não** 201.  
- Leia `interpretacao` em `GET /consistencia/status`.  
- Compare com [módulo 02 sync-async](../02-replicacao/tutorial-sync-async.md): async **passaria** a escrita — qual RPO?  
- Nota: um `COMMIT` sync no Postgres sem réplica fica em `SyncRep` **sem** ser cortado por `statement_timeout`; a API deste lab **recusa antes** (fail-fast CP).

---

## Lab Mongo consistência (`lab-consistencia-mongodb`, :8086)

| Sintoma | O que tentar |
|---------|----------------|
| Replica set não inicia | `docker compose logs mongo-init`; espere health dos 3 nós |
| `writeConcern majority` falha após partição | Esperado — tente `WC=w1 ./scripts/publicar-aviso.sh` |
| Leitura secondary vazia/diferente | `readConcern=local` + partição — compare `./scripts/comparar-concerns.sh` |
| `GET ?dest=secondary` retorna 503 após partição | Esperado — secondaries fora da `rs_net`; leia no **primary** com `readConcern=majority` ou `local` |
| `particionar-mongo.sh` sem efeito | Confirme `sd03-consistencia-mongodb_rs_net`; mongo2/3 desconectados |
| Conflito porta 27017 | Lab 02 usa 27017; este lab usa **27117** |
| Eleição demorada após curar | Espere 10–30s; `GET /consistencia/status` |

### Enquanto espera o replica set

```bash
until curl -s http://localhost:8086/consistencia/status \
  | python3 -c "import sys,json; exit(0 if json.load(sys.stdin).get('primary') else 1)" 2>/dev/null; do
  echo "aguardando primary (8086)..."
  sleep 5
done
```

---

## Fallback se `network disconnect` falhar no seu OS

Alternativa didática equivalente:

```bash
# Postgres — para a réplica (simula réplica inacessível ao sync)
docker compose stop postgres-replica

# Mongo — para secondaries
docker compose stop mongo2 mongo3
```

Documente no relatório da aula qual método usou.

---

## Checklist professor (antes da turma)

- [ ] Rodou tutorial Postgres Exp. 1–4 com Docker ativo  
- [ ] `./scripts/verificar-modo-cp.sh` retorna sync  
- [ ] (Completo) Rodou Mongo Exp. 3 + `provocar-divergencia.sh`  
- [ ] Anotou data da validação abaixo após rodar na máquina de sala

**Validação local:** preencha após o piloto (máquina, Docker, labs OK). Exemplo:

```text
2026-08-24 — Fedora 44 + Podman (DOCKER_HOST=…/podman.sock) —
  lab-particao-postgres: ./scripts/up.sh → sync_state=quorum;
  matrícula OK; particionar (+ terminate walsender) → POST /matricular 503 imediato;
  curar (--alias) → sync de volta; provocar-disputa-vaga.sh → 1 ok + 1 sem vagas
```

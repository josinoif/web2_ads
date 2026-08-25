# Troubleshooting — Labs do módulo 02

Faça **um lab por vez**. Ao trocar:

```bash
docker compose down -v
```

---

## Geral

| Sintoma | O que tentar |
|---------|----------------|
| Porta em uso (`8082`–`8084`, `5432`–`5435`, `27017`) | `down -v` no outro lab; `docker ps` |
| API `503` no começo | Banco/replica ainda subindo — espere 30–90s |
| `Cannot connect to Docker daemon` | Suba o serviço Docker |
| `bitnami/postgresql:16` → `manifest unknown` | Labs usam `bitnamilegacy/postgresql:16.6.0-debian-12-r2@sha256:…` (pin) |
| Porta `5432` / `5433` em uso | Postgres local ou outro container (`web_lab_pg`, etc.) | `docker ps --format '{{.Names}} {{.Ports}}' \| grep 5432`; pare o serviço conflitante **ou** altere temporariamente as portas publicadas no `docker-compose.yml` (ex.: `55432:5432`). A API do lab usa DNS interno — só a porta **do host** muda. |
| Bind mount Permission denied (Podman/SELinux) | Volumes init com `,Z` |

---

## Lab Postgres (`lab-postgres`, :8082)

| Sintoma | O que tentar |
|---------|----------------|
| Réplica não responde | `docker compose logs -f postgres-replica` · [poll abaixo](#enquanto-espera-a-réplica-postgres) |
| `GET /notas/...?dest=replica` falha | `curl -s localhost:8082/replicacao/status` · réplica ainda em base backup |
| Lag sempre zero | Normal em lab local; use `./scripts/provocar-stale.sh` |
| Stale não aparece no Exp. 2 | Rode `./scripts/provocar-stale.sh` |
| Schema missing | Recrie volume: `docker compose down -v && up -d --build` |
| Primary init | Scripts em `primary/init/` rodam só na **primeira** criação do volume |
| Primary parado | Escrita para — **não** é experimento deste lab; failover no [Mongo](../tutorial-mongodb.md) |

---

## Lab sync-async (`lab-sync-async`, :8084)

| Sintoma | O que tentar |
|---------|----------------|
| `sync_state` ainda `async` em modo sync | `./scripts/subir-sync.sh` (não só `docker compose up`); confira `MODO_LAB=sync` no health |
| Troca async ↔ sync sem efeito | **Sempre** `docker compose down -v` antes de trocar modo |
| POST trava em sync | Réplica down — esperado; `curl --max-time 90` ou suba a réplica |
| Porta 5434/5435 em uso | Lab Postgres usa 5432/5433 — ou outro lab sync ainda up |
| `replica_acessivel: false` | Espere base backup (1–3 min); [poll abaixo](#enquanto-espera-a-réplica-postgres-sync-async) |

---

## Enquanto espera a réplica (Postgres)

Primeiro boot: **1–3 min** (base backup). Poll a cada 10 s — **lab-postgres** (:8082):

```bash
until curl -s http://localhost:8082/replicacao/status \
  | python3 -c "import sys,json; exit(0 if json.load(sys.stdin).get('replica',{}).get('ok') else 1)" 2>/dev/null; do
  echo "aguardando réplica (8082)..."
  sleep 10
done
```

Enquanto espera: revise [teoria §1–2](teoria.md) ou o [mapa dos 3 labs](README.md#mapa-dos-3-labs--qual-pergunta-cada-um-responde).

---

## Enquanto espera a réplica (Postgres sync-async)

**lab-sync-async** (:8084):

```bash
until curl -s http://localhost:8084/replicacao/status \
  | python3 -c "import sys,json; exit(0 if json.load(sys.stdin).get('replica_acessivel') else 1)" 2>/dev/null; do
  echo "aguardando réplica (8084)..."
  sleep 10
done
```

Enquanto espera: revise [teoria §3](teoria.md) (sync vs async).

---

## Lab MongoDB (`lab-mongodb`, :8083)

| Sintoma | O que tentar |
|---------|----------------|
| `mongo-init` falhou | `docker compose logs mongo-init` · `docker compose up mongo-init` |
| API não sobe | Espere replica set PRIMARY; `./scripts/status-rs.sh` |
| `not primary` / eleição | Cluster reelegindo — espere 10–30s; repita POST |
| Parou nó errado | `./scripts/status-rs.sh` — pare o host com `stateStr: PRIMARY` |
| Leitura secondary vazia | Lag curto; repita GET ou use `dest=primary` |

---

Voltar: [README](README.md) · [glossario](glossario.md).

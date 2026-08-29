# Lab — Sync vs async (Postgres)

Tutorial: [../tutorial-sync-async.md](../tutorial-sync-async.md)  
Se travar: [../troubleshooting.md](../troubleshooting.md)

**Antes:** `docker compose down -v` nos labs Postgres e Mongo.

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).

## Subir e testar

```bash
./scripts/subir-async.sh
./scripts/medir-escrita.sh
docker compose down -v
./scripts/subir-sync.sh
./scripts/medir-escrita.sh aluno-sync "SD" 8.0
docker compose down -v
```

---

## Referencia rapida

### Comandos

```bash
# modos (sempre down -v ao trocar)
./scripts/subir-async.sh
./scripts/subir-sync.sh
docker compose down -v

# medir
curl -s http://localhost:8084/health | python3 -m json.tool
curl -s http://localhost:8084/replicacao/status | python3 -m json.tool
./scripts/medir-escrita.sh aluno-01 "SD" 9.0
./scripts/comparar-modos.sh
./scripts/provocar-replica-down.sh aluno-rpo "SD"

# encerrar
docker compose down -v
```

### Portas

| Serviço | Porta host |
|---------|------------|
| API | 8084 |
| Primary | 5434 |
| Réplica | 5435 |

### O que olhar no código

| Arquivo | O que ensina |
|---------|----------------|
| [`api/app.py`](api/app.py) | `duracao_commit_ms`; `replica_apos_commit`; status com `sync_state` |
| [`docker-compose.yml`](docker-compose.yml) | `POSTGRESQL_NUM_SYNCHRONOUS_REPLICAS: "0"` |
| [`docker-compose.sync.yml`](docker-compose.sync.yml) | override sync: `NUM_SYNCHRONOUS_REPLICAS=1` |

Leia `upsert_nota` e `status_replicacao`: commit medido + estado síncrono do Postgres.

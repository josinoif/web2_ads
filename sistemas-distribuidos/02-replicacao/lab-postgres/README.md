# Lab — Postgres (primary + réplica)

Tutorial (Partes **A** e **B** antes do Compose): [../tutorial-postgres.md](../tutorial-postgres.md)  
Se travar: [../troubleshooting.md](../troubleshooting.md)

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).

## Subir e testar

```bash
docker compose up -d --build
curl -s http://localhost:8082/health
./scripts/gravar-nota.sh aluno-01 "SD" 8.0
./scripts/ler-notas.sh aluno-01 replica
docker compose down -v
```

---

## Referencia rapida

Mapa de comandos e guia de código (complemento ao [tutorial](../tutorial-postgres.md)).

### Comandos

```bash
# subir / ver / logs
docker compose up -d --build
docker compose ps
docker compose logs -f postgres-primary postgres-replica api

# health e replicação
curl -s http://localhost:8082/health
curl -s http://localhost:8082/replicacao/status | python3 -m json.tool
curl -s http://localhost:8082/replicacao/lag | python3 -m json.tool

# scripts
./scripts/gravar-nota.sh aluno-01 "SD" 9.0
./scripts/ler-notas.sh aluno-01 primary
./scripts/ler-notas.sh aluno-01 replica
./scripts/comparar-lag.sh aluno-lag "Redes" 9.9
./scripts/provocar-stale.sh aluno-stale "SD" 9.9

# POST / GET manual
curl -s -X POST http://localhost:8082/notas \
  -H "Content-Type: application/json" \
  -d '{"aluno_id":"aluno-01","disciplina":"SD","valor":8.0}' | python3 -m json.tool
curl -s "http://localhost:8082/notas/aluno-01?dest=replica" | python3 -m json.tool

# provocar stale read (para réplica, grava, compara)
./scripts/provocar-stale.sh

# provocar falha parcial
docker compose stop postgres-replica
docker compose start postgres-replica

# encerrar (antes do lab Mongo)
docker compose down -v
```

### Portas

| Serviço | Porta host |
|---------|------------|
| API | 8082 |
| Primary | 5432 |
| Réplica | 5433 |

### O que olhar no código

| Arquivo | O que ele ensina |
|---------|------------------|
| [`api/app.py`](api/app.py) | DSN primary/replica; `upsert_nota` só no primary; `dest=` na leitura |
| [`primary/init/01-schema.sql`](primary/init/01-schema.sql) | Tabela `notas` |
| [`docker-compose.yml`](docker-compose.yml) | Bitnami master/slave replication |

Leia `upsert_nota` e `listar_notas`: ali está o roteamento write/read do portal.

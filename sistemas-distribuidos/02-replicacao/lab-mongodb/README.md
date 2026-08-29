# Lab — MongoDB (replica set)

Tutorial (Partes **A** e **B** antes do Compose): [../tutorial-mongodb.md](../tutorial-mongodb.md)  
Se travar: [../troubleshooting.md](../troubleshooting.md)

**Antes de subir:** encerre o lab Postgres (`docker compose down -v` em `lab-postgres/`).

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).

## Subir e testar

```bash
docker compose up -d --build
curl -s http://localhost:8083/health
./scripts/status-rs.sh
./scripts/gravar-nota.sh aluno-m1 "SD" 8.5
docker compose down -v
```

---

## Referencia rapida

### Comandos

```bash
# subir / ver / logs
docker compose up -d --build
docker compose ps
docker compose logs -f mongo1 mongo2 mongo3 api
docker compose logs mongo-init

# health e replica set
curl -s http://localhost:8083/health
./scripts/status-rs.sh
curl -s http://localhost:8083/replicacao/status | python3 -m json.tool

# scripts
./scripts/gravar-nota.sh aluno-m1 "SD" 10.0
./scripts/ler-notas.sh aluno-m1 primary
./scripts/ler-notas.sh aluno-m1 secondary
./scripts/comparar-leitura.sh aluno-cmp "SD" 9.5

# failover (identifique PRIMARY com status-rs antes de parar)
docker compose stop mongo1
sleep 15
./scripts/status-rs.sh
./scripts/gravar-nota.sh aluno-fail "SD" 6.0
docker compose start mongo1

# encerrar
docker compose down -v
```

### Portas

| Serviço | Porta host |
|---------|------------|
| API | 8083 |
| mongo1 | 27017 |

### O que olhar no código

| Arquivo | O que ele ensina |
|---------|------------------|
| [`api/app.py`](api/app.py) | `ReadPreference.SECONDARY_PREFERRED`; write no primary |
| [`docker-compose.yml`](docker-compose.yml) | Três `mongod --replSet rs0`; job `mongo-init` |

Leia `coll_com_dest` e `status_replica_set`: read preference e observabilidade do cluster.

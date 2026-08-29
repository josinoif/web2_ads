# Lab — Filas (Redis)

Tutorial (Partes **A** e **B** antes do Compose): [../tutorial-filas.md](../tutorial-filas.md)  
Se travar: [../troubleshooting.md](../troubleshooting.md)

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).

## Subir e testar

```bash
docker compose up -d --build
curl -s http://localhost:8080/health
./scripts/enviar-lote.sh 10
docker compose down -v
```

---

## Referencia rapida

Mapa de comandos e guia de código (complemento ao [tutorial](../tutorial-filas.md)).

### Comandos

```bash
# subir / ver / logs
docker compose up -d --build
docker compose ps
docker compose logs -f api worker

# usar
curl -s http://localhost:8080/health
curl -s -X POST http://localhost:8080/provas -H "Content-Type: application/json" \
  -d '{"aluno":"maria","arquivo":"maria.pdf"}'
./scripts/enviar-lote.sh 15
./scripts/acompanhar.sh SEU_ID
curl -s http://localhost:8080/fila

# provocar
docker compose stop worker
docker compose start worker
docker compose up -d --scale worker=2 worker
./scripts/provocar-kill.sh

# encerrar
docker compose down -v
```

### O que olhar no código

| Arquivo | O que ele ensina |
|---------|------------------|
| [`api/app.py`](api/app.py) | produtor; `202`; status; contraste `/provas/sincrono` |
| [`worker/worker.py`](worker/worker.py) | consumidor; `BRPOP`; atualização de status |
| [`docker-compose.yml`](docker-compose.yml) | três processos no mesmo “cluster” local |

Leia com calma a função `enfileirar` na API e o loop `while rodando` no worker: ali está o desenho inteiro.

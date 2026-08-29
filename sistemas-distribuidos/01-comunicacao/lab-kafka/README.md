# Lab — Kafka (tópico)

Tutorial (inclui **replay**, `GET /provas/{id}` e `GET /notificacoes`): [../tutorial-kafka.md](../tutorial-kafka.md)  
Se travar: [../troubleshooting.md](../troubleshooting.md)

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).

## Subir e testar

```bash
docker compose up -d --build
curl -s http://localhost:8081/health
curl -s -X POST http://localhost:8081/provas -H "Content-Type: application/json" \
  -d '{"aluno":"maria","arquivo":"maria.pdf"}'
./scripts/acompanhar.sh SEU_ID
./scripts/enviar-lote.sh 6
curl -s "http://localhost:8081/notificacoes?n=10" | python3 -m json.tool
./scripts/replay-group.sh 8
docker compose down -v
```

---

## Referencia rapida

Mapa de comandos e guia de código (complemento ao [tutorial](../tutorial-kafka.md)).

### Comandos

```bash
docker compose up -d --build
curl -s http://localhost:8081/health
curl -s -X POST http://localhost:8081/provas -H "Content-Type: application/json" \
  -d '{"aluno":"maria","arquivo":"maria.pdf"}'
./scripts/acompanhar.sh SEU_ID
./scripts/enviar-lote.sh 6
curl -s "http://localhost:8081/notificacoes?n=10" | python3 -m json.tool
./scripts/replay-group.sh 8
docker compose up -d --scale worker=3 worker
docker compose down -v
```

### O que olhar no código

| Arquivo | O que ele ensina |
|---------|------------------|
| [`api/app.py`](api/app.py) | produtor Kafka; status inicial; `GET /provas/{id}` |
| [`worker/worker.py`](worker/worker.py) | group `analisadores`; compete; grava status |
| [`notifier/notifier.py`](notifier/notifier.py) | group `notificadores`; fan-out; rastro JSONL |
| [`api/status_store.py`](api/status_store.py) | status HTTP em JSON no volume (**não** é feature do broker) |
| [`worker/replay_once.py`](worker/replay_once.py) | consumer group novo + `earliest` |

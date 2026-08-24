# Lab — gRPC (sync + async UX)

Tutorial (leia o box **async ≠ fila**): [../tutorial-grpc.md](../tutorial-grpc.md)  
Se travar: [../troubleshooting.md](../troubleshooting.md)

## Subir e testar

```bash
docker compose up -d --build
./scripts/cliente.sh sincrono
./scripts/cliente.sh async-poll
./scripts/cliente.sh stream
docker compose down -v
```

O `cliente.sh` simula o BFF — não é o browser.

---

## Referencia rapida

Mapa de comandos e guia de código (complemento ao [tutorial](../tutorial-grpc.md)).

### Comandos

```bash
docker compose up -d --build
./scripts/cliente.sh sincrono
./scripts/cliente.sh async-poll
./scripts/cliente.sh stream
./scripts/cliente.sh aceite          # copie SUBMISSION_ID=…
./scripts/cliente.sh status <id>
docker compose stop grpc-server      # experimento C.6
docker compose down -v
```

Experimento C.6 (aceite + restart):

```bash
OUT=$(./scripts/cliente.sh aceite); echo "$OUT"
./scripts/cliente.sh status <SUBMISSION_ID da última linha>
```

### O que olhar no código

| Arquivo | O que ele ensina |
|---------|------------------|
| [`proto/provas.proto`](proto/provas.proto) | contrato; unary vs streaming |
| [`server/server.py`](server/server.py) | sync bloqueante; thread async; estado em memória |
| [`scripts/run-client.py`](scripts/run-client.py) | stub; modos de teste |

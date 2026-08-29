# Mini-lab — RabbitMQ: integração com API externa instável

Tutorial (leia o problema **antes** do Compose): [tutorial.md](tutorial.md)

Se travar: [../../troubleshooting.md](../../troubleshooting.md)

**Linux e Windows:** os comandos abaixo são os mesmos (PowerShell, cmd, bash, zsh). Abra o terminal **nesta pasta**. O `-T` no `exec` evita erro de TTY no Windows. Guia geral dos outros labs: [linux-e-windows.md](../../../ferramentas/linux-e-windows.md).

## Subir e testar

```text
docker compose up -d --build
docker compose exec -T api python lab.py health
```

Painel: [http://localhost:15672](http://localhost:15672) (`guest` / `guest`). No passo 3 do [tutorial](tutorial.md): worker **parado**, fila `carteirinhas` → **Get messages** com *Nack/Reject requeue true* para ver o JSON.

```text
docker compose down -v
```

---

## Referência rápida

| Peça | Porta |
|------|--------|
| Portal (API) | `8082` |
| Emissor mock | `8083` |
| RabbitMQ AMQP | `5672` |
| RabbitMQ Management | `15672` |

### Comandos

```text
docker compose up -d --build
docker compose logs -f api worker emissor

docker compose exec -T api python lab.py ajuda
docker compose exec -T api python lab.py sincrono estavel-maria
docker compose exec -T api python lab.py enviar estavel-ana
docker compose exec -T api python lab.py lote 8
docker compose exec -T api python lab.py fila
docker compose exec -T api python lab.py registros
docker compose exec -T api python lab.py veneno

docker compose exec -T api python lab.py enviar teste-kill
docker compose exec -T api python lab.py esperar-processando SEU_ID
docker compose kill worker
docker compose up -d worker
docker compose exec -T api python lab.py acompanhar SEU_ID

docker compose down -v
```

Evidências (tabela completa): [tutorial.md §4](tutorial.md#evidencias).

### O que olhar no código

| Arquivo | O que ele ensina |
|---------|------------------|
| [`emissor/emissor.py`](emissor/emissor.py) | sistema de fora: lenteza + 500 + aluno `veneno` |
| [`api/app.py`](api/app.py) | 202 vs sincrono; produtor da fila |
| [`worker/worker.py`](worker/worker.py) | ack manual; retry; nack → DLQ |
| [`comum/rabbit.py`](comum/rabbit.py) | fila `carteirinhas` + `carteirinhas.dlq` |
| [`scripts/lab.py`](scripts/lab.py) | cliente HTTP usado no tutorial (roda no container) |

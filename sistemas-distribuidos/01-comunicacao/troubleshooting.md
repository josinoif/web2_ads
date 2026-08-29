# Troubleshooting — Labs do módulo 01

Faça **um lab por vez**. Ao trocar:

```bash
docker compose down -v   # na pasta do lab atual
```

---

## Geral

| Sintoma | O que tentar |
|---------|----------------|
| Porta em uso (`8080`, `8081`, `8082`, `8083`, `8084`, `8085`, `15672`, `5672`, `50051`, `6379`, `9092`) | `down -v` no outro lab; `docker ps` e pare containers órfãos |
| `Cannot connect to Docker daemon` | Suba o Docker Desktop / serviço `docker` |
| Build lento na primeira vez | Normal (imagens Python/Kafka); depois fica em cache |
| CPU no notebook some | Não rode filas + Kafka + gRPC juntos |
| `the input device is not a TTY` | Use `docker compose exec -T` (sem `-it`) |
| `./scripts/foo.sh` no PowerShell | Na pasta do lab: `.\lab.ps1 foo` — [Linux e Windows](../ferramentas/linux-e-windows.md) |
| `curl` no PowerShell vira Invoke-WebRequest | Use `curl.exe` |

---

## Lab filas (`lab-filas`, :8080)

| Sintoma | O que tentar |
|---------|----------------|
| `health` não responde | `docker compose ps` · `docker compose logs -f api` |
| Worker não processa | `docker compose logs -f worker` · `curl -s localhost:8080/fila` |
| Fila “suja” entre experimentos | `docker compose exec redis redis-cli DEL prova:fila` |
| `--scale worker=2` estranho | Volte com `--scale worker=1` e `up -d` de novo |
| Experimento kill (C.5) | `./scripts/provocar-kill.sh` (alternativa ao timing manual) |

---

## Lab Kafka (`lab-kafka`, :8081)

| Sintoma | O que tentar |
|---------|----------------|
| API reinicia / `health` falha no começo | Broker ainda subindo — espere 30–60s; `docker compose logs -f kafka api` |
| `NoBrokersAvailable` nos logs | Espere o Kafka; `docker compose restart api worker notifier` |
| Worker/notifier sem mensagens | Confirme `POST` com `partition`/`offset` no JSON; logs `-f worker notifier` |
| `/notificacoes` vazio | Espere o notifier consumir; confira `docker compose logs notifier` |
| `GET /provas/{id}` em `na_fila` forever | Worker parado? `docker compose logs -f worker` · `./scripts/acompanhar.sh ID` |
| `replay-group.sh` falha | Rode C.3 antes (precisa de eventos no tópico); confira build do worker (`replay_once.py`) |
| Scale worker sem ganho | Há 3 partições — o 4º consumidor no mesmo group fica ocioso |

---

## Tutorial RabbitMQ (`tutoriais/rabbitmq-integracao-externa`, API :8082)

| Sintoma | O que tentar |
|---------|----------------|
| `health` da API falha no começo | RabbitMQ ainda não está `healthy` — espere ~20s; `docker compose ps` · `docker compose logs -f rabbitmq api` |
| Painel `15672` recusa login | usuário/senha `guest` / `guest`; porta de outro RabbitMQ local? |
| Worker não processa | `docker compose logs -f worker` · painel Ready/Unacked · `docker compose exec -T api python lab.py fila` |
| `enviar` ok mas `registros` vazio | worker parado ou ainda nos 3s do emissor; `docker compose logs -f emissor` |
| Após `kill`, Ready vazio | espere 1–2s (unacked volta); confira o painel, não só o `lab.py fila` |
| Veneno não vai à DLQ | 3 tentativas × 3s ≈ 9s; `lab.py acompanhar` até `na_dlq`; fila `carteirinhas.dlq` no painel |
| `the input device is not a TTY` | falta o `-T` no `docker compose exec` (obrigatório no Windows) |
| *Get messages* esvaziou **Ready** | Ack mode estava *requeue false*; `docker compose stop worker` e `lab.py enviar estavel-ana` de novo |
| Painel não mostra o JSON | worker já consumiu (Unacked/0); pare o worker e envie de novo **antes** de *Get messages* |

Roteiro de evidências: [tutorial §4](tutoriais/rabbitmq-integracao-externa/tutorial.md#evidencias).

---

## Tutorial Kafka (`tutoriais/kafka-pedido-pago`, API :8084 · UI :8085)

| Sintoma | O que tentar |
|---------|----------------|
| `health` da API falha no começo | Broker ainda subindo — 20–40s; `docker compose logs -f kafka api` |
| Kafka UI vazio / não abre | `docker compose ps kafka-ui` · `logs -f kafka-ui`; recarregue `:8085` |
| `cadeia` 502 com tudo `up` | Espere os três consumidores; `docker compose logs estoque nota email` |
| `pagar` ok mas `rastreio` vazio | Espere ~2s (TRABALHO_SEGUNDOS=1); logs dos consumers |
| `replay` `total_lido=0` | Publique antes (`pagar` ou `lote`); tópico `pedidos.pagos` no UI |
| `the input device is not a TTY` | falta `-T` no `docker compose exec` |

Roteiro de evidências: [tutorial §4](tutoriais/kafka-pedido-pago/tutorial.md#evidencias).

---

## Lab gRPC (`lab-grpc`, :50051)

| Sintoma | O que tentar |
|---------|----------------|
| `UNAVAILABLE` / cliente não conecta | `docker compose up -d` **antes** de `./scripts/cliente.sh` · `docker compose logs grpc-server` |
| `cliente.sh` falha | Rode de dentro de `lab-grpc/`; server precisa estar `running` |
| `status` / `aceite` | `./scripts/cliente.sh aceite` imprime `SUBMISSION_ID=…` na última linha · `./scripts/cliente.sh status <id>` |
| Latência sync ≠ ~3s | Confira `ANALISE_SEGUNDOS` no Compose |

O CLI (`cliente.sh`) **simula** o BFF/portal — não é o browser. Em produção haveria HTTP na frente falando gRPC por trás.

---

Voltar: [README](README.md) · [glossario](glossario.md).

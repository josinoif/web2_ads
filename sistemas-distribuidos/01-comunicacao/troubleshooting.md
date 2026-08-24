# Troubleshooting — Labs do módulo 01

Faça **um lab por vez**. Ao trocar:

```bash
docker compose down -v   # na pasta do lab atual
```

---

## Geral

| Sintoma | O que tentar |
|---------|----------------|
| Porta em uso (`8080`, `8081`, `50051`, `6379`, `9092`) | `down -v` no outro lab; `docker ps` e pare containers órfãos |
| `Cannot connect to Docker daemon` | Suba o Docker Desktop / serviço `docker` |
| Build lento na primeira vez | Normal (imagens Python/Kafka); depois fica em cache |
| CPU no notebook some | Não rode filas + Kafka + gRPC juntos |

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

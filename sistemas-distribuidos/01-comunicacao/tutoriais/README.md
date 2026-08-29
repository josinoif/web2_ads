# Tutoriais de construção

Complementam os [labs do módulo](../README.md): cada tutorial usa um **problema diferente**, escolhido porque a ferramenta precisa aparecer — não porque “todo mundo usa isso no currículo”.

Os arquivos `tutorial-filas.md`, `tutorial-kafka.md` e `tutorial-grpc.md` na raiz do módulo **continuam** sendo o roteiro dos labs (mesmo domínio: envio de prova).

**Linux e Windows:** [como rodar os comandos](../../ferramentas/linux-e-windows.md). RabbitMQ e Kafka (pedido-pago) usam `docker compose exec -T api python lab.py` (igual nos dois SOs).

| Tutorial | Tecnologia | Problema em miniatura |
|----------|------------|------------------------|
| [rabbitmq-integracao-externa](rabbitmq-integracao-externa/tutorial.md) | RabbitMQ | Matrícula ok; emissor de carteirinha **lento e instável** (ack, retry, DLQ) |
| [kafka-pedido-pago](kafka-pedido-pago/tutorial.md) | Kafka | **Pedido pago**: estoque + NF + e-mail no mesmo fato (fan-out, lag, replay) + [Kafka UI](http://localhost:8085) |

gRPC entra nesta pasta quando o problema estiver fechado.

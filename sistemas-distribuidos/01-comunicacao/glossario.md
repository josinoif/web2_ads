# Glossário — Comunicação (módulo 01)

Termos que aparecem nos textos e labs. Volte aqui quando o inglês técnico travar a leitura.

| Termo | Significado curto |
|-------|-------------------|
| **Ack** | Confirmação de que a mensagem foi recebida/processada; brokers maduros só removem após o ack — diagrama em [teoria §4](teoria.md) |
| **At-least-once** | Entrega “pelo menos uma vez” — pode repetir; exige idempotência |
| **At-most-once** | Entrega “no máximo uma vez” — pode não entregar |
| **BFF** | *Backend for Frontend* — API sob medida para o cliente (web/app) |
| **Broker** | Serviço intermediário de mensagens (RabbitMQ, Kafka, SQS…) |
| **Comando** | Mensagem com intenção (“faça X”) — um responsável; ver [teoria §6](teoria.md) · lab filas |
| **Compete consumers** | Cada mensagem vai para **um** consumidor — [tutorial-kafka Parte A](tutorial-kafka.md) |
| **Consumer group** | No Kafka: compete (mesmo group) ou fan-out (groups distintos) |
| **Contrato** | Formato acordado (JSON, `.proto`, schema de evento) |
| **Coreografia** | Fluxo distribuído sem orquestrador central — cada serviço reage e publica; ver [teoria §5](teoria.md) |
| **DLQ** | *Dead-letter queue* — fila para mensagens que falharam demais |
| **Evento** | Mensagem de fato (“X aconteceu”) — vários podem escutar; ver [teoria §6](teoria.md) · lab Kafka |
| **Exactly-once** | Ideal raro na rede sem protocolo/estado extra |
| **Fan-out** | Um evento chega a **vários** interessados — [tutorial-kafka](tutorial-kafka.md) |
| **Idempotência** | Processar de novo o mesmo id não corrompe o estado |
| **Lag** | Atraso vs ponta do log — [tutorial-kafka C.6](tutorial-kafka.md) |
| **Offset** | Posição de leitura no log Kafka (por group + partição) |
| **Orquestração** | Fluxo centralizado por um mediador que dispara passos — ver [teoria §5](teoria.md) · [decisoes cenário 3](decisoes.md) |
| **Partição** | Fatia de um tópico; base do paralelismo |
| **Pub/sub** | Publicar para tópico; quem assina recebe |
| **Replay** | Reler desde um offset — [tutorial-kafka C.7](tutorial-kafka.md) |
| **RPC** | *Remote Procedure Call* — procedimento em outra máquina |
| **Server streaming** | Uma request → várias responses — [tutorial-grpc C.5](tutorial-grpc.md) |
| **Stub** | Código gerado no cliente que fala com o remoto |
| **Throughput** | Quantidade de trabalho por unidade de tempo |
| **Unary** | Uma request → uma response — [tutorial-grpc C.5](tutorial-grpc.md) |
| **Worker** | Processo consumidor que executa o trabalho pesado |

Ver também: [teoria.md](teoria.md) · [troubleshooting.md](troubleshooting.md).

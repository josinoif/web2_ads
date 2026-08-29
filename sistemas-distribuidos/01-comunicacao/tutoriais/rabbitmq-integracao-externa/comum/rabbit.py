"""
Topologia RabbitMQ deste tutorial.

Aqui nascem as duas filas que você vê no painel (localhost:15672):

- carteirinhas      → trabalho a fazer (emitir carteirinha)
- carteirinhas.dlq  → jobs que falharam demais (dead-letter)

API e worker chamam as mesmas funções no boot: declarar fila duas vezes
é seguro (idempotente). O broker ignora se ela já existe com os mesmos argumentos.
"""

from __future__ import annotations

import json
import time

import pika

FILA = "carteirinhas"
FILA_DLQ = "carteirinhas.dlq"
EXCHANGE_DLX = "dlx"  # exchange só para desviar mensagem rejeitada → DLQ


def publicar_comando(channel: pika.channel.Channel, mensagem: dict) -> None:
    """
    Coloca um comando na fila principal.

    indent=2 e content_type=json existem para o painel Management mostrar
    o Payload legível (passo 3 do tutorial). delivery_mode=2 = persistente.
    """
    body = json.dumps(mensagem, ensure_ascii=False, indent=2).encode("utf-8")
    channel.basic_publish(
        exchange="",  # exchange default: a routing_key É o nome da fila
        routing_key=FILA,
        body=body,
        properties=pika.BasicProperties(
            delivery_mode=2,
            content_type="application/json",
            content_encoding="utf-8",
            type="EmitirCarteirinha",
            message_id=str(mensagem.get("matricula_id", "")),
            correlation_id=str(mensagem.get("matricula_id", "")),
            headers={
                "aluno": str(mensagem.get("aluno", "")),
                "tentativas": int(mensagem.get("tentativas", 1)),
            },
        ),
    )


def declarar_topologia(channel: pika.channel.Channel) -> None:
    """Cria DLX + DLQ + fila de trabalho ligada à DLQ."""
    channel.exchange_declare(exchange=EXCHANGE_DLX, exchange_type="direct", durable=True)
    channel.queue_declare(queue=FILA_DLQ, durable=True)
    channel.queue_bind(queue=FILA_DLQ, exchange=EXCHANGE_DLX, routing_key=FILA_DLQ)

    # Se o worker fizer nack(requeue=False), o broker NÃO apaga:
    # encaminha para este exchange/routing_key (= nossa DLQ).
    channel.queue_declare(
        queue=FILA,
        durable=True,
        arguments={
            "x-dead-letter-exchange": EXCHANGE_DLX,
            "x-dead-letter-routing-key": FILA_DLQ,
        },
    )


def conectar(url: str, tentativas: int = 30) -> tuple[pika.BlockingConnection, pika.channel.Channel]:
    """Espera o broker subir (útil no docker compose) e devolve conexão + canal."""
    ultimo_erro: Exception | None = None
    for _ in range(tentativas):
        try:
            params = pika.URLParameters(url)
            params.heartbeat = 30
            conn = pika.BlockingConnection(params)
            channel = conn.channel()
            declarar_topologia(channel)
            return conn, channel
        except Exception as exc:  # noqa: BLE001 — no boot o broker ainda pode estar subindo
            ultimo_erro = exc
            time.sleep(1)
    raise SystemExit(f"RabbitMQ indisponível: {ultimo_erro}")

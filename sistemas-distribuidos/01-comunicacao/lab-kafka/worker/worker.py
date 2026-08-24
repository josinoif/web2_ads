"""
Worker no consumer group 'analisadores'.

Dentro do mesmo group_id, cada mensagem vai para UM consumidor (compete).
Outro group (notificadores) recebe uma CÓPIA de cada mensagem (fan-out).
"""

from __future__ import annotations

import json
import os
import random
import signal
import socket
import time

from kafka import KafkaConsumer

from status_store import salvar
from kafka.errors import NoBrokersAvailable

KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.environ.get("TOPIC_PROVAS", "provas.enviadas")
GROUP_ID = os.environ.get("GROUP_ID", "analisadores")
WORKER_NAME = os.environ.get("WORKER_NAME") or socket.gethostname()
ANALISE_SEGUNDOS = float(os.environ.get("ANALISE_SEGUNDOS", "3"))

rodando = True


def pedir_parada(signum, frame) -> None:  # noqa: ARG001
    global rodando
    print(f"[{WORKER_NAME}] sinal {signum} — parando...", flush=True)
    rodando = False


signal.signal(signal.SIGTERM, pedir_parada)
signal.signal(signal.SIGINT, pedir_parada)


def main() -> None:
    consumer = None
    for _ in range(60):
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP,
                group_id=GROUP_ID,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda b: json.loads(b.decode("utf-8")),
                key_deserializer=lambda b: b.decode("utf-8") if b else None,
                consumer_timeout_ms=1000,
            )
            break
        except NoBrokersAvailable:
            time.sleep(1)
    if consumer is None:
        raise SystemExit("Kafka indisponível")

    print(
        f"[{WORKER_NAME}] group={GROUP_ID} tópico={TOPIC} — competindo por mensagens",
        flush=True,
    )

    while rodando:
        for msg in consumer:
            evento = msg.value
            sid = evento.get("submission_id", "?")
            print(
                f"[{WORKER_NAME}] part={msg.partition} off={msg.offset} "
                f"analisando {sid} (aluno={evento.get('aluno')})",
                flush=True,
            )
            salvar(
                sid,
                aluno=evento.get("aluno"),
                arquivo=evento.get("arquivo"),
                status="processando",
                worker=WORKER_NAME,
            )
            time.sleep(ANALISE_SEGUNDOS)
            similaridade = random.randint(5, 40)
            salvar(
                sid,
                status="concluido",
                worker=WORKER_NAME,
                relatorio={
                    "similaridade_pct": similaridade,
                    "parecer": "ok para correção manual"
                    if similaridade < 30
                    else "revisar trechos",
                },
            )
            print(f"[{WORKER_NAME}] concluído {sid}", flush=True)
            if not rodando:
                break

    consumer.close()
    print(f"[{WORKER_NAME}] encerrado", flush=True)


if __name__ == "__main__":
    main()

"""
Notifier em OUTRO consumer group ('notificadores').

Recebe TODOS os eventos do tópico — fan-out via consumer groups.
Além do log, grava um rastro em NOTIFICACOES_FILE (volume compartilhado
com a API → GET /notificacoes).
"""

from __future__ import annotations

import json
import os
import signal
import socket
import time
from pathlib import Path

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.environ.get("TOPIC_PROVAS", "provas.enviadas")
GROUP_ID = os.environ.get("GROUP_ID", "notificadores")
NAME = os.environ.get("NOTIFIER_NAME") or socket.gethostname()
NOTIFICACOES_FILE = Path(os.environ.get("NOTIFICACOES_FILE", "/data/notificacoes.jsonl"))

rodando = True


def pedir_parada(signum, frame) -> None:  # noqa: ARG001
    global rodando
    rodando = False


signal.signal(signal.SIGTERM, pedir_parada)
signal.signal(signal.SIGINT, pedir_parada)


def registrar(evento: dict, partition: int, offset: int) -> None:
    registro = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "submission_id": evento.get("submission_id"),
        "aluno": evento.get("aluno"),
        "arquivo": evento.get("arquivo"),
        "partition": partition,
        "offset": offset,
        "notifier": NAME,
    }
    NOTIFICACOES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with NOTIFICACOES_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(registro, ensure_ascii=False) + "\n")


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
                consumer_timeout_ms=1000,
            )
            break
        except NoBrokersAvailable:
            time.sleep(1)
    if consumer is None:
        raise SystemExit("Kafka indisponível")

    print(
        f"[{NAME}] group={GROUP_ID} — fan-out; rastro em {NOTIFICACOES_FILE}",
        flush=True,
    )

    while rodando:
        for msg in consumer:
            evento = msg.value
            registrar(evento, msg.partition, msg.offset)
            print(
                f"[{NAME}] NOTIFICAR aluno={evento.get('aluno')} "
                f"prova={evento.get('submission_id')} "
                f"(part={msg.partition} off={msg.offset})",
                flush=True,
            )
            if not rodando:
                break

    consumer.close()
    print(f"[{NAME}] encerrado", flush=True)


if __name__ == "__main__":
    main()

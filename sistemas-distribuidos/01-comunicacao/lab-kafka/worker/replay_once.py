"""Lê até MAX_MSGS do tópico com um consumer group novo (replay / earliest)."""

from __future__ import annotations

import json
import os
import sys
import time

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.environ.get("TOPIC_PROVAS", "provas.enviadas")
GROUP_ID = os.environ.get("GROUP_ID", "metricas-replay")
MAX_MSGS = int(os.environ.get("MAX_MSGS", "8"))


def main() -> None:
    consumer = None
    for _ in range(40):
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=BOOTSTRAP,
                group_id=GROUP_ID,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                consumer_timeout_ms=10000,
                value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            )
            break
        except NoBrokersAvailable:
            time.sleep(1)
    if consumer is None:
        print("Kafka indisponível", file=sys.stderr)
        sys.exit(1)

    print(f"replay group={GROUP_ID} topic={TOPIC} max={MAX_MSGS}", flush=True)
    n = 0
    for msg in consumer:
        n += 1
        ev = msg.value
        print(
            f"REPLAY id={ev.get('submission_id')} part={msg.partition} off={msg.offset}",
            flush=True,
        )
        if n >= MAX_MSGS:
            break
    print(f"total_lido={n}", flush=True)
    consumer.close()


if __name__ == "__main__":
    main()

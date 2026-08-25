"""Notificador — segundo consumidor via pub/sub (fan-out)."""

from __future__ import annotations

import json
import os
import signal
import sys
import time

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
EVENT_CHANNEL = "prova:eventos"
NOTIF_LIST = "prova:notificacoes"

rodando = True
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def pedir_parada(signum, frame) -> None:  # noqa: ARG001
    global rodando
    rodando = False


signal.signal(signal.SIGTERM, pedir_parada)
signal.signal(signal.SIGINT, pedir_parada)


def main() -> None:
    for _ in range(30):
        try:
            r.ping()
            break
        except redis.exceptions.ConnectionError:
            time.sleep(0.5)
    else:
        print("[notificador] Redis indisponível", flush=True)
        sys.exit(1)

    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(EVENT_CHANNEL)
    print(f"[notificador] inscrito em {EVENT_CHANNEL}", flush=True)

    while rodando:
        msg = pubsub.get_message(timeout=1.0)
        if msg is None:
            continue
        if msg.get("type") != "message":
            continue
        try:
            evento = json.loads(msg["data"])
        except (json.JSONDecodeError, TypeError):
            continue
        registro = {
            "recebido_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "evento": evento,
        }
        r.lpush(NOTIF_LIST, json.dumps(registro, ensure_ascii=False))
        r.ltrim(NOTIF_LIST, 0, 49)
        print(f"[notificador] {evento.get('tipo')} {evento.get('submission_id')}", flush=True)

    print("[notificador] encerrado", flush=True)


if __name__ == "__main__":
    main()

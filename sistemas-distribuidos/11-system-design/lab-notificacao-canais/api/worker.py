"""Worker de notificação.

MODO=canais + CANAL=push|email|sms → consome só sua fila.
MODO=unico  + CANAL=all            → consome fila única; DELAY em jobs de email.
"""

from __future__ import annotations

import json
import os
import time

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
CANAL = os.environ.get("CANAL", "push")  # push|email|sms|all
MODO = os.environ.get("MODO", "canais")
DELAY_MS = int(os.environ.get("DELAY_MS", "0"))
EMAIL_DELAY_MS = int(os.environ.get("EMAIL_DELAY_MS", "0"))

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def fila_name() -> str:
    if MODO == "unico":
        return "fila:unica"
    return f"fila:{CANAL}"


def process(job: dict) -> None:
    canal = job.get("canal", "push")
    delay = DELAY_MS
    if canal == "email" and EMAIL_DELAY_MS:
        delay = EMAIL_DELAY_MS
    if delay:
        time.sleep(delay / 1000.0)
    r.incr(f"sent:{canal}")
    r.lpush(
        f"log:{canal}",
        json.dumps({"event_id": job.get("event_id"), "user": job.get("user"), "t": time.time()}),
    )
    print(f"sent canal={canal} event={job.get('event_id')} delay_ms={delay}", flush=True)


def main() -> None:
    q = fila_name()
    print(
        f"worker canal={CANAL} modo={MODO} fila={q} delay_ms={DELAY_MS} email_delay_ms={EMAIL_DELAY_MS}",
        flush=True,
    )
    while True:
        item = r.brpop(q, timeout=5)
        if not item:
            continue
        _k, raw = item
        process(json.loads(raw))


if __name__ == "__main__":
    main()

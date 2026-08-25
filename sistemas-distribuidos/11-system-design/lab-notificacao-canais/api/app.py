"""Publisher de notificações.

MODO=unico  → uma fila; workers processam em série (e-mail lento bloqueia push).
MODO=canais → filas push / email / sms separadas.
"""

from __future__ import annotations

import json
import os
import time
from http.server import ThreadingHTTPServer

import redis

from common import JsonHandler

PORT = int(os.environ.get("PORT", "8000"))
MODO = os.environ.get("MODO", "canais")  # unico | canais
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)
CANAIS = ("push", "email", "sms")


def fila(canal: str) -> str:
    if MODO == "unico":
        return "fila:unica"
    return f"fila:{canal}"


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self._path()
        if path == "/health":
            filas = {}
            if MODO == "unico":
                filas["unica"] = r.llen("fila:unica")
            else:
                for c in CANAIS:
                    filas[c] = r.llen(f"fila:{c}")
            self._json(
                200,
                {
                    "ok": True,
                    "service": "notificacao",
                    "modo": MODO,
                    "filas": filas,
                    "enviados": {c: int(r.get(f"sent:{c}") or 0) for c in CANAIS},
                },
            )
            return
        if path == "/status":
            self._json(
                200,
                {
                    "modo": MODO,
                    "enviados": {c: int(r.get(f"sent:{c}") or 0) for c in CANAIS},
                    "ultimos": {
                        c: r.lrange(f"log:{c}", 0, 4) for c in CANAIS
                    },
                },
            )
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self._path()
        if path == "/admin/reset":
            for key in list(r.scan_iter("fila:*")) + list(r.scan_iter("sent:*")) + list(r.scan_iter("log:*")):
                r.delete(key)
            self._json(200, {"ok": True})
            return

        if path != "/eventos":
            self._json(404, {"erro": "não encontrado"})
            return

        body = self._read_json()
        event_id = (body.get("id") or f"evt-{int(time.time()*1000)}").strip()
        user = body.get("user") or "anon"
        canais = body.get("canais") or list(CANAIS)
        t0 = time.perf_counter()
        jobs = []
        for canal in canais:
            if canal not in CANAIS:
                continue
            job = {
                "event_id": event_id,
                "user": user,
                "canal": canal,
                "idempotency_key": f"{event_id}:{canal}",
                "ts": time.time(),
            }
            r.lpush(fila(canal), json.dumps(job))
            jobs.append(canal)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        self._json(
            202,
            {
                "aceito": True,
                "event_id": event_id,
                "modo": MODO,
                "canais_enfileirados": jobs,
                "tempo_ms": ms,
            },
        )


def main() -> None:
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"notificacao modo={MODO} port={PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()

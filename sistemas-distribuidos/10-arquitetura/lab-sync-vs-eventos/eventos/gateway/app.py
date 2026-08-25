"""Gateway eventos — aceita rápido e enfileira no Redis."""

from __future__ import annotations

import json
import os
import time
import uuid
from http.server import ThreadingHTTPServer

import redis

from common import JsonHandler

PORT = int(os.environ.get("PORT", "8000"))
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = "prova:fila"
STATUS_PREFIX = "prova:status:"
EVENT_CHANNEL = "prova:eventos"
MODO = "eventos"

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def status_key(sid: str) -> str:
    return f"{STATUS_PREFIX}{sid}"


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "service": "gateway-eventos", "modo": MODO})
            return
        if path == "/admin/config":
            self._json(
                200,
                {
                    "service": "gateway-eventos",
                    "modo": MODO,
                    "fila": QUEUE_KEY,
                    "tamanho_fila": r.llen(QUEUE_KEY),
                },
            )
            return
        if path == "/fila":
            self._json(200, {"fila": QUEUE_KEY, "tamanho": r.llen(QUEUE_KEY)})
            return
        if path.startswith("/provas/"):
            sid = path.split("/", 2)[2]
            raw = r.get(status_key(sid))
            if raw is None:
                self._json(404, {"erro": "não encontrado", "submission_id": sid})
                return
            self._json(200, json.loads(raw))
            return
        if path == "/notificacoes":
            items = r.lrange("prova:notificacoes", 0, 19)
            self._json(200, {"notificacoes": [json.loads(x) for x in items]})
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path != "/provas":
            self._json(404, {"erro": "não encontrado"})
            return

        start = time.perf_counter()
        data = self._read_json()
        submission_id = data.get("submission_id") or f"evt-{uuid.uuid4().hex[:8]}"
        aluno = data.get("aluno") or "anon"
        arquivo = data.get("arquivo") or "prova.pdf"
        agora = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        registro = {
            "submission_id": submission_id,
            "aluno": aluno,
            "arquivo": arquivo,
            "status": "na_fila",
            "enqueued_at": agora,
            "relatorio": None,
        }
        mensagem = {
            "submission_id": submission_id,
            "aluno": aluno,
            "arquivo": arquivo,
            "enqueued_at": agora,
        }
        r.set(status_key(submission_id), json.dumps(registro, ensure_ascii=False))
        r.lpush(QUEUE_KEY, json.dumps(mensagem, ensure_ascii=False))
        # Fan-out: publica fato para outros consumidores (notificador)
        r.publish(EVENT_CHANNEL, json.dumps({"tipo": "prova_enfileirada", **mensagem}))

        lat_ms = round((time.perf_counter() - start) * 1000, 1)
        self._json(
            202,
            {
                "status": "na_fila",
                "modo": MODO,
                "latencia_ms": lat_ms,
                "submission_id": submission_id,
                "aluno": aluno,
                "arquivo": arquivo,
            },
        )


if __name__ == "__main__":
    for _ in range(30):
        try:
            r.ping()
            break
        except redis.exceptions.ConnectionError:
            time.sleep(0.5)
    else:
        raise SystemExit("Redis indisponível")
    print(f"[gateway-eventos] :{PORT} fila={QUEUE_KEY}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

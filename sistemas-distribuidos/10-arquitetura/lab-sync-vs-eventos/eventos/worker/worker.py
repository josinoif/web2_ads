"""Worker — consome fila, analisa, atualiza status."""

from __future__ import annotations

import json
import os
import signal
import socket
import sys
import time

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = "prova:fila"
STATUS_PREFIX = "prova:status:"
EVENT_CHANNEL = "prova:eventos"
WORKER_NAME = os.environ.get("WORKER_NAME") or socket.gethostname()
ANALISE_SEGUNDOS = float(os.environ.get("ANALISE_SEGUNDOS", "2"))

rodando = True
r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def pedir_parada(signum, frame) -> None:  # noqa: ARG001
    global rodando
    print(f"[{WORKER_NAME}] parando…", flush=True)
    rodando = False


signal.signal(signal.SIGTERM, pedir_parada)
signal.signal(signal.SIGINT, pedir_parada)


def status_key(sid: str) -> str:
    return f"{STATUS_PREFIX}{sid}"


def atualizar(sid: str, **campos) -> None:
    raw = r.get(status_key(sid))
    dados = json.loads(raw) if raw else {"submission_id": sid}
    dados.update(campos)
    r.set(status_key(sid), json.dumps(dados, ensure_ascii=False))


def processar(mensagem: dict) -> None:
    sid = mensagem["submission_id"]
    print(f"[{WORKER_NAME}] processando {sid}", flush=True)
    atualizar(sid, status="processando", worker=WORKER_NAME)
    time.sleep(ANALISE_SEGUNDOS)
    relatorio = {"similaridade_pct": 12, "parecer": "ok (eventos)", "worker": WORKER_NAME}
    atualizar(sid, status="concluido", worker=WORKER_NAME, relatorio=relatorio)
    r.publish(
        EVENT_CHANNEL,
        json.dumps(
            {
                "tipo": "prova_concluida",
                "submission_id": sid,
                "aluno": mensagem.get("aluno"),
                "relatorio": relatorio,
            },
            ensure_ascii=False,
        ),
    )
    print(f"[{WORKER_NAME}] concluído {sid}", flush=True)


def main() -> None:
    for _ in range(30):
        try:
            r.ping()
            break
        except redis.exceptions.ConnectionError:
            time.sleep(0.5)
    else:
        print(f"[{WORKER_NAME}] Redis indisponível", flush=True)
        sys.exit(1)

    print(f"[{WORKER_NAME}] escutando {QUEUE_KEY}", flush=True)
    while rodando:
        item = r.brpop(QUEUE_KEY, timeout=2)
        if item is None:
            continue
        _, raw = item
        processar(json.loads(raw))
    print(f"[{WORKER_NAME}] encerrado", flush=True)


if __name__ == "__main__":
    main()

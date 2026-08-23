"""
Worker analisador de provas.

Fica escutando a fila. Quando chega um job, "analisa" (sleep) e atualiza o status.
A API já respondeu ao professor há muito tempo — este processo trabalha depois.
"""

from __future__ import annotations

import json
import os
import random
import signal
import socket
import sys
import time

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
QUEUE_KEY = "prova:fila"
STATUS_PREFIX = "prova:status:"
# Com --scale worker=N, cada container tem hostname diferente (bom nos logs)
WORKER_NAME = os.environ.get("WORKER_NAME") or socket.gethostname()
ANALISE_SEGUNDOS = float(os.environ.get("ANALISE_SEGUNDOS", "3"))
# Chance de falha simulada (0.0 a 1.0) — útil nos testes de reprocessamento
TAXA_FALHA = float(os.environ.get("TAXA_FALHA", "0"))

rodando = True


def pedir_parada(signum, frame) -> None:  # noqa: ARG001
    global rodando
    print(f"[{WORKER_NAME}] sinal {signum} — vou parar após o job atual", flush=True)
    rodando = False


signal.signal(signal.SIGTERM, pedir_parada)
signal.signal(signal.SIGINT, pedir_parada)

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def status_key(submission_id: str) -> str:
    return f"{STATUS_PREFIX}{submission_id}"


def atualizar(submission_id: str, **campos) -> None:
    raw = r.get(status_key(submission_id))
    if raw is None:
        dados = {"submission_id": submission_id}
    else:
        dados = json.loads(raw)
    dados.update(campos)
    r.set(status_key(submission_id), json.dumps(dados, ensure_ascii=False))


def processar(mensagem: dict) -> None:
    submission_id = mensagem["submission_id"]
    print(f"[{WORKER_NAME}] processando {submission_id} ...", flush=True)
    atualizar(
        submission_id,
        status="processando",
        worker=WORKER_NAME,
    )

    # Simula análise pesada (extração de texto + similaridade)
    time.sleep(ANALISE_SEGUNDOS)

    if random.random() < TAXA_FALHA:
        atualizar(submission_id, status="erro", worker=WORKER_NAME, erro="falha simulada")
        print(f"[{WORKER_NAME}] FALHA em {submission_id}", flush=True)
        return

    similaridade = random.randint(5, 40)
    atualizar(
        submission_id,
        status="concluido",
        worker=WORKER_NAME,
        relatorio={
            "similaridade_pct": similaridade,
            "parecer": "ok para correção manual" if similaridade < 30 else "revisar trechos",
        },
    )
    print(f"[{WORKER_NAME}] concluído {submission_id}", flush=True)


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

    print(f"[{WORKER_NAME}] escutando fila '{QUEUE_KEY}'", flush=True)

    while rodando:
        # BRPOP bloqueia até 2s: permite checar a flag "rodando" com frequência
        item = r.brpop(QUEUE_KEY, timeout=2)
        if item is None:
            continue
        _fila, raw = item
        mensagem = json.loads(raw)
        processar(mensagem)

    print(f"[{WORKER_NAME}] encerrado", flush=True)


if __name__ == "__main__":
    main()

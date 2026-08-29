"""
Worker (consumidor): tira um comando da fila, chama o emissor, dá ack só no fim.

Contraste com o lab de filas (Redis BRPOP): lá a mensagem some NA PEGADA.
Aqui auto_ack=False — se este processo morrer no meio do HTTP, o RabbitMQ
devolve a mensagem para Ready (passo 5 do tutorial).
"""

from __future__ import annotations

import json
import os
import socket
import urllib.error
import urllib.request

import pika

import rabbit
import status_store

RABBIT_URL = os.environ.get("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
EMISSOR_URL = os.environ.get("EMISSOR_URL", "http://emissor:8000")
MAX_TENTATIVAS = int(os.environ.get("MAX_TENTATIVAS", "3"))
# Com --scale worker=2 cada container tem hostname diferente (aparece nos logs)
WORKER_NAME = os.environ.get("WORKER_NAME") or socket.gethostname()


def chamar_emissor(matricula_id: str, aluno: str) -> tuple[bool, dict]:
    """HTTP para o 'sistema de fora'. True = 2xx; False = 500/timeout/rede."""
    payload = json.dumps({"matricula_id": matricula_id, "aluno": aluno}).encode("utf-8")
    req = urllib.request.Request(
        f"{EMISSOR_URL}/carteirinhas",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return True, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        corpo = exc.read().decode("utf-8", errors="replace")
        try:
            dados = json.loads(corpo)
        except json.JSONDecodeError:
            dados = {"erro": corpo}
        dados["http"] = exc.code
        return False, dados
    except Exception as exc:  # noqa: BLE001
        return False, {"erro": str(exc)}


def publicar(channel: pika.channel.Channel, mensagem: dict) -> None:
    """Reenfileira o mesmo comando com tentativas+1 (retry)."""
    rabbit.publicar_comando(channel, mensagem)


def on_message(channel: pika.channel.Channel, method, _properties, body: bytes) -> None:
    """
    Um job. Enquanto esta função roda, a mensagem está Unacked no painel.
    Só basic_ack / basic_nack no final — nunca no começo.
    """
    mensagem = json.loads(body.decode("utf-8"))
    matricula_id = mensagem["matricula_id"]
    aluno = mensagem["aluno"]
    tentativas = int(mensagem.get("tentativas", 1))

    print(
        f"[{WORKER_NAME}] tentando {matricula_id} aluno={aluno} tentativa={tentativas}/{MAX_TENTATIVAS}",
        flush=True,
    )
    status_store.salvar(
        matricula_id,
        status="processando",
        worker=WORKER_NAME,
        tentativas=tentativas,
    )

    ok, resposta = chamar_emissor(matricula_id, aluno)

    if ok:
        status_store.salvar(
            matricula_id,
            status="concluido",
            protocolo=resposta.get("protocolo"),
            emissor=resposta,
            worker=WORKER_NAME,
        )
        # Agora sim: o broker pode esquecer a mensagem
        channel.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[{WORKER_NAME}] OK {matricula_id} protocolo={resposta.get('protocolo')}", flush=True)
        return

    print(f"[{WORKER_NAME}] FALHA {matricula_id} tentativa={tentativas} detalhe={resposta}", flush=True)

    if tentativas < MAX_TENTATIVAS:
        # 500 passageiro: publica de novo e ack a cópia antiga (senão ficam duas)
        mensagem["tentativas"] = tentativas + 1
        status_store.salvar(matricula_id, status="na_fila", tentativas=tentativas)
        publicar(channel, mensagem)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        print(
            f"[{WORKER_NAME}] reenfileirado {matricula_id} próxima tentativa={tentativas + 1}",
            flush=True,
        )
        return

    # Esgotou as tentativas: nack SEM requeue → a topologia manda para a DLQ
    status_store.salvar(
        matricula_id,
        status="na_dlq",
        tentativas=tentativas,
        erro=resposta,
        worker=WORKER_NAME,
    )
    channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    print(f"[{WORKER_NAME}] DLQ {matricula_id} após {tentativas} tentativas", flush=True)


def main() -> None:
    _conn, channel = rabbit.conectar(RABBIT_URL)
    # prefetch=1: não pegue o próximo job enquanto este não tiver ack (compete consumers justo)
    channel.basic_qos(prefetch_count=1)
    # auto_ack=False é o coração do passo 5 (kill): sem ack, a mensagem volta
    channel.basic_consume(queue=rabbit.FILA, on_message_callback=on_message, auto_ack=False)
    print(
        f"[{WORKER_NAME}] escutando '{rabbit.FILA}' prefetch=1 ack manual max_tentativas={MAX_TENTATIVAS}",
        flush=True,
    )
    channel.start_consuming()


if __name__ == "__main__":
    main()

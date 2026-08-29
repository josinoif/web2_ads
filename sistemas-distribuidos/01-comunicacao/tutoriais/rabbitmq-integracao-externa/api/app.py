"""
Portal de matrícula (produtor).

Responsabilidade: aceitar o pedido do aluno e colocar um COMANDO na fila.
A chamada lenta/instável ao emissor de carteirinha NÃO roda aqui —
exceto em POST /matriculas/sincrono, que existe só para você sentir a dor
de acoplar o portal ao sistema de fora.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pika

import rabbit
import status_store

PORT = int(os.environ.get("PORT", "8000"))
RABBIT_URL = os.environ.get("RABBIT_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
EMISSOR_URL = os.environ.get("EMISSOR_URL", "http://emissor:8000")

# pika não é thread-safe; o HTTP server atende várias requests em paralelo
_lock = threading.Lock()
_conn: pika.BlockingConnection | None = None
_channel: pika.channel.Channel | None = None


def _channel_ok() -> pika.channel.Channel:
    """Reabre o canal se a conexão com o broker caiu no meio do caminho."""
    global _conn, _channel
    assert _channel is not None
    if _conn is None or _conn.is_closed or _channel.is_closed:
        _conn, _channel = rabbit.conectar(RABBIT_URL)
    return _channel


def publicar(mensagem: dict) -> None:
    """Produtor: só entrega o JSON na fila. Não espera o emissor."""
    with _lock:
        ch = _channel_ok()
        rabbit.publicar_comando(ch, mensagem)


def contar_filas() -> dict:
    """Ready na fila principal e na DLQ — o mesmo que o painel Management mostra."""
    with _lock:
        ch = _channel_ok()
        # passive=True: só consulta, não recria a fila
        principal = ch.queue_declare(queue=rabbit.FILA, durable=True, passive=True)
        dlq = ch.queue_declare(queue=rabbit.FILA_DLQ, durable=True, passive=True)
    return {
        "fila": rabbit.FILA,
        "prontas": principal.method.message_count,
        "dlq": rabbit.FILA_DLQ,
        "prontas_dlq": dlq.method.message_count,
    }


def chamar_emissor_sincrono(matricula_id: str, aluno: str) -> tuple[int, dict]:
    """Anti-padrão do tutorial: o portal espera o HTTP externo terminar."""
    payload = json.dumps({"matricula_id": matricula_id, "aluno": aluno}).encode("utf-8")
    req = urllib.request.Request(
        f"{EMISSOR_URL}/carteirinhas",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        corpo = exc.read().decode("utf-8", errors="replace")
        try:
            dados = json.loads(corpo)
        except json.JSONDecodeError:
            dados = {"erro": corpo}
        return exc.code, dados
    except Exception as exc:  # noqa: BLE001
        return 503, {"erro": str(exc)}


def enfileirar(aluno: str, matricula_id: str | None = None) -> dict:
    """
    Caminho feliz: grava status na_fila e publica o comando.
    A resposta 202 pode ir embora ANTES de o worker nem ter acordado.
    """
    matricula_id = matricula_id or f"mat-{uuid.uuid4().hex[:8]}"
    agora = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    registro = status_store.salvar(
        matricula_id,
        aluno=aluno,
        status="na_fila",
        tentativas=0,
        protocolo=None,
        enqueued_at=agora,
    )
    publicar(
        {
            "matricula_id": matricula_id,
            "aluno": aluno,
            "tentativas": 1,
            "enqueued_at": agora,
        }
    )
    return registro


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/health":
            self._json(200, {"ok": True})
            return

        if path == "/fila":
            self._json(200, contar_filas())
            return

        # Painel do aluno / da secretaria: "já emitiram a carteirinha?"
        if path.startswith("/matriculas/"):
            matricula_id = path.split("/", 2)[2]
            dados = status_store.ler(matricula_id)
            if dados is None:
                self._json(404, {"erro": "matrícula não encontrada", "matricula_id": matricula_id})
                return
            self._json(200, dados)
            return

        self._json(
            200,
            {
                "servico": "portal-matricula",
                "endpoints": [
                    "POST /matriculas",
                    "POST /matriculas/sincrono",
                    "POST /matriculas/lote?n=8",
                    "GET /matriculas/{id}",
                    "GET /fila",
                ],
            },
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        # 202 Accepted = "aceitei o trabalho, a carteirinha ainda não existe"
        if path == "/matriculas":
            body = self._read_json()
            aluno = body.get("aluno", "aluno-desconhecido")
            registro = enfileirar(aluno, body.get("matricula_id"))
            self._json(202, registro)
            return

        # Mesma matrícula, mas o aluno PAGA os ~3 s (e o 500) do emissor
        if path == "/matriculas/sincrono":
            body = self._read_json()
            aluno = body.get("aluno", "aluno-desconhecido")
            matricula_id = body.get("matricula_id") or f"sync-{uuid.uuid4().hex[:8]}"
            inicio = time.perf_counter()
            status_store.salvar(matricula_id, aluno=aluno, status="processando", tentativas=1)
            http_code, resposta = chamar_emissor_sincrono(matricula_id, aluno)
            latencia = round(time.perf_counter() - inicio, 2)
            if http_code >= 400:
                registro = status_store.salvar(
                    matricula_id,
                    status="erro",
                    erro=resposta,
                    latencia_api_segundos=latencia,
                )
                self._json(502, registro)
                return
            registro = status_store.salvar(
                matricula_id,
                status="concluido",
                protocolo=resposta.get("protocolo"),
                emissor=resposta,
                latencia_api_segundos=latencia,
            )
            self._json(200, registro)
            return

        if path == "/matriculas/lote":
            n = int(query.get("n", ["8"])[0])
            n = max(1, min(n, 40))
            criadas = [enfileirar(f"aluno-{i + 1:02d}") for i in range(n)]
            self._json(202, {"enviadas": n, **contar_filas(), "matriculas": criadas})
            return

        self._json(404, {"erro": "rota não encontrada"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    _conn, _channel = rabbit.conectar(RABBIT_URL)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] ouvindo em 0.0.0.0:{PORT} fila={rabbit.FILA}", flush=True)
    server.serve_forever()

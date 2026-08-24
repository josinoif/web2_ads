"""
API produtora: publica eventos no tópico Kafka provas.enviadas.

Diferença em relação à fila Redis: o tópico é um log; vários
consumer groups podem ler o mesmo evento (fan-out).
"""

from __future__ import annotations

import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable

from status_store import ler as ler_status
from status_store import salvar as salvar_status

KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.environ.get("TOPIC_PROVAS", "provas.enviadas")
PORT = int(os.environ.get("PORT", "8000"))
NUM_PARTITIONS = int(os.environ.get("NUM_PARTITIONS", "3"))
NOTIFICACOES_FILE = os.environ.get("NOTIFICACOES_FILE", "/data/notificacoes.jsonl")

producer: KafkaProducer | None = None


def ler_notificacoes(limit: int = 20) -> list[dict]:
    path = Path(NOTIFICACOES_FILE)
    if not path.exists():
        return []
    linhas = path.read_text(encoding="utf-8").splitlines()
    escolhidas = linhas[-limit:] if limit > 0 else linhas
    out: list[dict] = []
    for linha in escolhidas:
        linha = linha.strip()
        if not linha:
            continue
        try:
            out.append(json.loads(linha))
        except json.JSONDecodeError:
            continue
    return out


def esperar_kafka(tentativas: int = 60) -> None:
    global producer
    ultimo_erro: Exception | None = None
    for _ in range(tentativas):
        try:
            admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP, request_timeout_ms=2000)
            try:
                admin.create_topics(
                    [NewTopic(name=TOPIC, num_partitions=NUM_PARTITIONS, replication_factor=1)],
                    validate_only=False,
                )
                print(f"[api] tópico '{TOPIC}' criado ({NUM_PARTITIONS} partições)", flush=True)
            except Exception as exc:  # noqa: BLE001 — já existe / race no boot
                print(f"[api] create_topics: {exc.__class__.__name__}: {exc}", flush=True)
            finally:
                admin.close()

            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
            )
            return
        except NoBrokersAvailable as exc:
            ultimo_erro = exc
            time.sleep(1)
        except Exception as exc:  # noqa: BLE001
            ultimo_erro = exc
            time.sleep(1)
    raise SystemExit(f"Kafka indisponível: {ultimo_erro}")


def publicar(aluno: str, arquivo: str, submission_id: str | None = None) -> dict:
    assert producer is not None
    sid = submission_id or f"prova-{uuid.uuid4().hex[:8]}"
    evento = {
        "event_type": "ProvaEnviada",
        "submission_id": sid,
        "aluno": aluno,
        "arquivo": arquivo,
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    # chave = submission_id → mesma prova cai sempre na mesma partição
    fut = producer.send(TOPIC, key=sid, value=evento)
    meta = fut.get(timeout=10)
    producer.flush()
    resultado = {
        **evento,
        "topic": meta.topic,
        "partition": meta.partition,
        "offset": meta.offset,
    }
    salvar_status(
        sid,
        aluno=evento["aluno"],
        arquivo=evento["arquivo"],
        status="na_fila",
        event_type=evento["event_type"],
        published_at=evento["published_at"],
        topic=meta.topic,
        partition=meta.partition,
        offset=meta.offset,
    )
    return resultado


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
        query = parse_qs(parsed.query)

        if path == "/health":
            self._json(200, {"ok": True, "topic": TOPIC})
            return

        if path == "/notificacoes":
            limit = max(1, min(int(query.get("n", ["20"])[0]), 100))
            itens = ler_notificacoes(limit)
            self._json(200, {"total": len(itens), "itens": itens})
            return

        if path.startswith("/provas/"):
            sid = path.removeprefix("/provas/").strip("/")
            if not sid:
                self._json(400, {"erro": "informe submission_id"})
                return
            dados = ler_status(sid)
            if dados is None:
                self._json(404, {"erro": "prova não encontrada", "submission_id": sid})
                return
            self._json(200, dados)
            return

        self._json(
            200,
            {
                "servico": "api-kafka-provas",
                "topic": TOPIC,
                "endpoints": [
                    "POST /provas",
                    "POST /provas/lote?n=10",
                    "GET /provas/{submission_id}",
                    "GET /notificacoes?n=20",
                    "GET /health",
                ],
            },
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        if path == "/provas":
            body = self._read_json()
            evento = publicar(
                body.get("aluno", "aluno-desconhecido"),
                body.get("arquivo", "prova.pdf"),
                body.get("submission_id"),
            )
            self._json(202, evento)
            return

        if path == "/provas/lote":
            n = max(1, min(int(query.get("n", ["10"])[0]), 50))
            eventos = [
                publicar(f"aluno-{i+1:02d}", f"lote-{i+1:02d}.pdf") for i in range(n)
            ]
            self._json(202, {"publicados": n, "eventos": eventos})
            return

        self._json(404, {"erro": "rota não encontrada"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_kafka()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] ouvindo 0.0.0.0:{PORT} → tópico {TOPIC}", flush=True)
    server.serve_forever()

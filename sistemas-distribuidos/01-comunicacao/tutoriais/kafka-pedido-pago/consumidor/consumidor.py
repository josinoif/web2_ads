"""
Um contexto de negócio (estoque, nota-fiscal ou e-mail).

Duas portas de entrada, o MESMO trabalho:

- HTTP POST /processar  → caminho SEM Kafka (o portal chama em cadeia)
- Consumer Kafka        → caminho COM Kafka (lê o fato PedidoPago)

GROUP_ID diferente em cada serviço = fan-out: os três leem o mesmo evento.
"""

from __future__ import annotations

import json
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

import rastro

PORT = int(os.environ.get("PORT", "8000"))
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.environ.get("TOPIC", "pedidos.pagos")
# papel no arquivo de rastro; group_id pode ser outro nome (aparece no Kafka UI)
PAPEL = os.environ.get("PAPEL", "estoque")
GROUP_ID = os.environ.get("GROUP_ID", PAPEL)
ROTULO = os.environ.get("ROTULO", PAPEL)
TRABALHO_SEGUNDOS = float(os.environ.get("TRABALHO_SEGUNDOS", "1"))
NAME = os.environ.get("WORKER_NAME") or socket.gethostname()


def executar(evento: dict, origem: str, partition: int | None = None, offset: int | None = None) -> dict:
    """Simula o trabalho deste contexto (baixa estoque, emite NF, envia e-mail)."""
    time.sleep(TRABALHO_SEGUNDOS)
    registro = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "papel": PAPEL,
        "rotulo": ROTULO,
        "origem": origem,  # "kafka" ou "http-cadeia" — o tutorial compara os dois
        "pedido_id": evento.get("pedido_id"),
        "cliente": evento.get("cliente"),
        "valor_centavos": evento.get("valor_centavos"),
        "partition": partition,
        "offset": offset,
        "host": NAME,
    }
    rastro.registrar(PAPEL, registro)
    print(
        f"[{PAPEL}] ok pedido={evento.get('pedido_id')} origem={origem} "
        f"part={partition} off={offset}",
        flush=True,
    )
    return registro


def loop_kafka() -> None:
    """Lê o tópico para sempre. Offset deste GROUP_ID é independente dos outros."""
    consumer = None
    for _ in range(60):
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP,
                group_id=GROUP_ID,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda b: json.loads(b.decode("utf-8")),
                key_deserializer=lambda b: b.decode("utf-8") if b else None,
                consumer_timeout_ms=1000,
            )
            break
        except NoBrokersAvailable:
            time.sleep(1)
    if consumer is None:
        print(f"[{PAPEL}] Kafka indisponível — só HTTP (cadeia) vai funcionar", flush=True)
        return

    print(f"[{PAPEL}] Kafka group={GROUP_ID} tópico={TOPIC}", flush=True)
    while True:
        for msg in consumer:
            executar(msg.value, origem="kafka", partition=msg.partition, offset=msg.offset)


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
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "papel": PAPEL, "group_id": GROUP_ID})
            return
        if path == "/registros":
            self._json(200, {"papel": PAPEL, "itens": rastro.ler(PAPEL)})
            return
        self._json(200, {"servico": ROTULO, "papel": PAPEL, "group_id": GROUP_ID})

    def do_POST(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        # O portal SEM Kafka chama isto em sequência (estoque → nota → e-mail)
        if path == "/processar":
            evento = self._read_json()
            registro = executar(evento, origem="http-cadeia")
            self._json(200, registro)
            return
        self._json(404, {"erro": "rota não encontrada"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{PAPEL}] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    threading.Thread(target=loop_kafka, name="kafka", daemon=True).start()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[{PAPEL}] HTTP 0.0.0.0:{PORT} + consumer group={GROUP_ID}", flush=True)
    server.serve_forever()

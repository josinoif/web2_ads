"""
Checkout (produtor).

Dois caminhos de propósito:

- POST /pedidos/cadeia  → SEM Kafka: HTTP estoque → nota → e-mail (a dor)
- POST /pedidos         → COM Kafka: publica PedidoPago e devolve 202

O portal, no segundo caminho, NÃO conhece os interessados. Quem quiser
o fato cria um consumer group — inclusive um time que só aparece no mês 6.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable

import rastro

PORT = int(os.environ.get("PORT", "8000"))
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.environ.get("TOPIC", "pedidos.pagos")
NUM_PARTITIONS = int(os.environ.get("NUM_PARTITIONS", "3"))
# Hostnames do Compose — o caminho cadeia fala HTTP com eles
ESTOQUE_URL = os.environ.get("ESTOQUE_URL", "http://estoque:8000")
NOTA_URL = os.environ.get("NOTA_URL", "http://nota:8000")
EMAIL_URL = os.environ.get("EMAIL_URL", "http://email:8000")

producer: KafkaProducer | None = None

CADEIA = [
    ("estoque", ESTOQUE_URL),
    ("nota-fiscal", NOTA_URL),
    ("email", EMAIL_URL),
]


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
            except Exception as exc:  # noqa: BLE001 — já existe
                print(f"[api] create_topics: {exc.__class__.__name__}: {exc}", flush=True)
            finally:
                admin.close()

            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v, ensure_ascii=False, indent=2).encode("utf-8"),
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


def _http_json(method: str, url: str, body: dict | None = None, timeout: float = 20) -> tuple[int, dict]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            dados = json.loads(raw) if raw else {"erro": raw}
        except json.JSONDecodeError:
            dados = {"erro": raw}
        return exc.code, dados
    except Exception as exc:  # noqa: BLE001
        return 503, {"erro": str(exc)}


def publicar(cliente: str, valor_centavos: int, pedido_id: str | None = None) -> dict:
    """Um fato: o pagamento aconteceu. Quem reage não está nesta função."""
    assert producer is not None
    pedido_id = pedido_id or f"ped-{uuid.uuid4().hex[:8]}"
    evento = {
        "event_type": "PedidoPago",
        "pedido_id": pedido_id,
        "cliente": cliente,
        "valor_centavos": valor_centavos,
        "published_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    # chave = pedido_id → o mesmo pedido cai sempre na mesma partição (ordem local)
    fut = producer.send(TOPIC, key=pedido_id, value=evento)
    meta = fut.get(timeout=10)
    producer.flush()
    return {
        **evento,
        "topic": meta.topic,
        "partition": meta.partition,
        "offset": meta.offset,
    }


def executar_cadeia(evento: dict) -> tuple[int, dict]:
    """
    Anti-padrão: o checkout ORQUESTRA os outros sistemas.
    Se o 2º cair, o 1º já rodou — estado partido, e o 3º nem foi chamado.
    """
    feitos: list[str] = []
    for nome, base in CADEIA:
        code, corpo = _http_json("POST", f"{base}/processar", evento)
        if code >= 400:
            pendentes = [n for n, _ in CADEIA if n not in feitos and n != nome]
            return 502, {
                "erro": f"cadeia HTTP quebrou em '{nome}'",
                "ja_executados": feitos,
                "falhou": nome,
                "nao_chamados": pendentes,
                "detalhe": corpo,
                "pedido_id": evento.get("pedido_id"),
                "aviso": "estoque/NF/e-mail ficaram inconsistentes — o Kafka evita este acoplamento",
            }
        feitos.append(nome)
    return 200, {"ok": True, "executados": feitos, "pedido_id": evento.get("pedido_id")}


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
        n = max(1, min(int(query.get("n", ["20"])[0]), 50))

        if path == "/health":
            self._json(200, {"ok": True, "topic": TOPIC})
            return

        if path == "/rastreio":
            self._json(
                200,
                {
                    "estoque": rastro.ler("estoque", n),
                    "nota": rastro.ler("nota", n),
                    "email": rastro.ler("email", n),
                },
            )
            return

        if path.startswith("/rastreio/"):
            papel = path.split("/", 2)[2]
            if papel not in {"estoque", "nota", "email"}:
                self._json(404, {"erro": "papel desconhecido", "papel": papel})
                return
            itens = rastro.ler(papel, n)
            self._json(200, {"papel": papel, "total": len(itens), "itens": itens})
            return

        self._json(
            200,
            {
                "servico": "checkout",
                "topic": TOPIC,
                "endpoints": [
                    "POST /pedidos",
                    "POST /pedidos/cadeia",
                    "POST /pedidos/lote?n=6",
                    "GET /rastreio",
                    "GET /rastreio/{estoque|nota|email}",
                    "GET /health",
                ],
            },
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        if path == "/pedidos":
            body = self._read_json()
            resultado = publicar(
                body.get("cliente", "cliente-desconhecido"),
                int(body.get("valor_centavos", 4990)),
                body.get("pedido_id"),
            )
            self._json(202, resultado)
            return

        if path == "/pedidos/cadeia":
            body = self._read_json()
            evento = {
                "event_type": "PedidoPago",
                "pedido_id": body.get("pedido_id") or f"cad-{uuid.uuid4().hex[:8]}",
                "cliente": body.get("cliente", "cliente-cadeia"),
                "valor_centavos": int(body.get("valor_centavos", 4990)),
            }
            inicio = time.perf_counter()
            code, resultado = executar_cadeia(evento)
            resultado["latencia_api_segundos"] = round(time.perf_counter() - inicio, 2)
            self._json(code, resultado)
            return

        if path == "/pedidos/lote":
            n = max(1, min(int(query.get("n", ["6"])[0]), 30))
            eventos = [publicar(f"cliente-{i + 1:02d}", 1000 + i * 10) for i in range(n)]
            self._json(202, {"publicados": n, "eventos": eventos})
            return

        self._json(404, {"erro": "rota não encontrada"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_kafka()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] checkout em 0.0.0.0:{PORT} tópico={TOPIC}", flush=True)
    server.serve_forever()

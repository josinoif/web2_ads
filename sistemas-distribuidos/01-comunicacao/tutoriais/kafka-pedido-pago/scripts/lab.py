"""
Cliente do tutorial Kafka (stdlib + kafka-python já na imagem da API).

    docker compose exec -T api python lab.py ajuda
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

API = os.environ.get("LAB_API_URL", "http://127.0.0.1:8000")
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.environ.get("TOPIC", "pedidos.pagos")

AJUDA = """
Comandos (Linux e Windows):  docker compose exec -T api python lab.py …

  health              checkout + tópico
  cadeia [cliente]    SEM Kafka: HTTP estoque → nota → e-mail (a dor)
  pagar [cliente] [pedido_id]   COM Kafka: publica PedidoPago (202)
  lote [n]            vários eventos no tópico
  rastreio            o que estoque / nota / e-mail já fizeram
  rastreio <papel>    estoque | nota | email
  replay [n]          NOVO consumer group lê o log desde o início

Painel gráfico (host): http://localhost:8085
""".strip()


def _print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _request(method: str, url: str, body: dict | None = None, timeout: float = 40) -> tuple[int, dict | list]:
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


def _mostrar(code: int, dados: dict | list) -> dict | list:
    print(f"HTTP {code}")
    _print_json(dados)
    return dados


def cmd_health(_args: list[str]) -> int:
    code, dados = _request("GET", f"{API}/health")
    _mostrar(code, dados)
    return 0 if code < 400 else 1


def cmd_cadeia(args: list[str]) -> int:
    """Passo 1: o checkout espera cada sistema — e quebra no meio se um cair."""
    cliente = args[0] if args else "ana-cadeia"
    print("(SEM Kafka: o portal chama estoque, depois NF, depois e-mail)")
    inicio = time.perf_counter()
    code, dados = _request("POST", f"{API}/pedidos/cadeia", {"cliente": cliente})
    print(f"tempo_total_s={round(time.perf_counter() - inicio, 2)}")
    _mostrar(code, dados)
    return 0 if code < 400 else 1


def cmd_pagar(args: list[str]) -> int:
    """Passo 3: um fato no log. Os consumers reagem sozinhos."""
    cliente = args[0] if args else "bruno-kafka"
    pedido_id = args[1] if len(args) > 1 else None
    body: dict = {"cliente": cliente}
    if pedido_id:
        body["pedido_id"] = pedido_id
    inicio = time.perf_counter()
    code, dados = _request("POST", f"{API}/pedidos", body)
    print(f"tempo_total_s={round(time.perf_counter() - inicio, 2)}")
    _mostrar(code, dados)
    if isinstance(dados, dict) and dados.get("pedido_id"):
        print(f"pedido_id={dados['pedido_id']}")
        print(f"partition={dados.get('partition')} offset={dados.get('offset')}")
    return 0 if code < 400 else 1


def cmd_lote(args: list[str]) -> int:
    n = int(args[0]) if args else 6
    inicio = time.perf_counter()
    code, dados = _request("POST", f"{API}/pedidos/lote?n={n}", {})
    print(f"tempo_total_s={round(time.perf_counter() - inicio, 2)}")
    _mostrar(code, dados)
    return 0 if code < 400 else 1


def cmd_rastreio(args: list[str]) -> int:
    if args and args[0] in {"estoque", "nota", "email"}:
        code, dados = _request("GET", f"{API}/rastreio/{args[0]}")
    else:
        code, dados = _request("GET", f"{API}/rastreio")
    _mostrar(code, dados)
    return 0 if code < 400 else 1


def cmd_replay(args: list[str]) -> int:
    """Passo 6: group novo com earliest — o passado ainda está no log."""
    max_msgs = int(args[0]) if args else 8
    group_id = f"metricas-replay-{uuid.uuid4().hex[:6]}"
    from kafka import KafkaConsumer
    from kafka.errors import NoBrokersAvailable

    consumer = None
    for _ in range(40):
        try:
            consumer = KafkaConsumer(
                TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP,
                group_id=group_id,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                consumer_timeout_ms=12000,
                value_deserializer=lambda b: json.loads(b.decode("utf-8")),
            )
            break
        except NoBrokersAvailable:
            time.sleep(1)
    if consumer is None:
        print("Kafka indisponível", file=sys.stderr)
        return 1

    print(f"replay group={group_id} topic={TOPIC} max={max_msgs}", flush=True)
    n = 0
    for msg in consumer:
        n += 1
        ev = msg.value if isinstance(msg.value, dict) else {}
        print(
            f"REPLAY pedido={ev.get('pedido_id')} part={msg.partition} off={msg.offset}",
            flush=True,
        )
        if n >= max_msgs:
            break
    print(f"total_lido={n}", flush=True)
    print("No Kafka UI → Consumers: este group_id aparece (e some se ninguém ficar escutando).")
    consumer.close()
    return 0 if n else 1


def cmd_ajuda(_args: list[str]) -> int:
    print(AJUDA)
    return 0


COMANDOS = {
    "ajuda": cmd_ajuda,
    "help": cmd_ajuda,
    "health": cmd_health,
    "cadeia": cmd_cadeia,
    "pagar": cmd_pagar,
    "lote": cmd_lote,
    "rastreio": cmd_rastreio,
    "replay": cmd_replay,
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        return cmd_ajuda([])
    fn = COMANDOS.get(sys.argv[1])
    if fn is None:
        print(f"comando desconhecido: {sys.argv[1]}", file=sys.stderr)
        cmd_ajuda([])
        return 2
    return fn(sys.argv[2:])


if __name__ == "__main__":
    raise SystemExit(main())

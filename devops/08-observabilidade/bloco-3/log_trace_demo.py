"""
log_trace_demo.py - demonstra logs estruturados correlacionados via trace_id.

Uso:
    python log_trace_demo.py --requests 5

Sem instalar Prometheus/Loki/Tempo: apenas produz, no stdout, o
tipo de saida estruturada que as ferramentas esperam consumir.
"""
from __future__ import annotations

import argparse
import contextvars
import json
import random
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field

_trace_ctx: contextvars.ContextVar[dict] = contextvars.ContextVar("trace_ctx", default={})


def log(level: str, msg: str, **kw) -> None:
    ctx = _trace_ctx.get()
    registro = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "service": "pedidos",
        "env": "dev",
        "msg": msg,
        **ctx,
        **kw,
    }
    print(json.dumps(registro))


@dataclass
class Span:
    name: str
    trace_id: str
    span_id: str
    parent_span_id: str | None = None
    start_ns: int = field(default_factory=time.monotonic_ns)
    end_ns: int = 0
    attrs: dict = field(default_factory=dict)
    status: str = "OK"

    @property
    def duration_ms(self) -> float:
        return (self.end_ns - self.start_ns) / 1_000_000

    def to_dict(self) -> dict:
        return {
            "kind": "span",
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "duration_ms": round(self.duration_ms, 2),
            "attrs": self.attrs,
            "status": self.status,
        }


@contextmanager
def span(name: str, **attrs):
    ctx = _trace_ctx.get()
    trace_id = ctx.get("trace_id") or uuid.uuid4().hex
    parent = ctx.get("span_id")
    s = Span(name=name, trace_id=trace_id, span_id=uuid.uuid4().hex[:16], parent_span_id=parent, attrs=attrs)
    token = _trace_ctx.set({"trace_id": trace_id, "span_id": s.span_id})
    try:
        yield s
        s.status = "OK"
    except Exception as exc:
        s.status = "ERROR"
        log("ERROR", "span exception", span=name, error=str(exc))
        raise
    finally:
        s.end_ns = time.monotonic_ns()
        _trace_ctx.reset(token)
        print(json.dumps(s.to_dict()))


def simular_request(req_i: int) -> None:
    with span("POST /orders", route="/orders", method="POST") as root:
        log("INFO", "recebido POST /orders", request_index=req_i)
        with span("validar_estoque"):
            time.sleep(random.uniform(0.01, 0.05))
            log("INFO", "estoque valido", sku="xyz")
        with span("persistir_pedido") as s:
            tempo = random.uniform(0.02, 0.30)
            time.sleep(tempo)
            s.attrs["db.query_ms"] = round(tempo * 1000, 1)
            log("INFO", "pedido persistido", order_id=f"o-{req_i}")
        if random.random() < 0.1:
            root.status = "ERROR"
            log("ERROR", "falha publicar evento", order_id=f"o-{req_i}", queue="notificacoes")
        else:
            log("INFO", "pedido criado com sucesso", order_id=f"o-{req_i}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Demo de logs+traces correlacionados")
    p.add_argument("--requests", type=int, default=5)
    args = p.parse_args(argv)
    for i in range(args.requests):
        simular_request(i)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

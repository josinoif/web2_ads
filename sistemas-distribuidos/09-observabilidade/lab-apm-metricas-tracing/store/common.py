"""Common — logs + métricas Prometheus + spans OTel (lab APM)."""

from __future__ import annotations

import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.propagate import extract, inject
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio
from opentelemetry.trace import Status, StatusCode
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

SERVICE = os.environ.get("SERVICE_NAME", "app")
LOG_FILE = os.environ.get("LOG_FILE", "")
PROPAGATE_TRACE = os.environ.get("PROPAGATE_TRACE", "1") == "1"
OTEL_ENDPOINT = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4318")
# 1.0 = 100% (lab padrão); 0.2 = 20% — ParentBased respeita decisão do span raiz
OTEL_SAMPLE_RATIO = float(os.environ.get("OTEL_SAMPLE_RATIO", "1.0"))

if LOG_FILE:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    open(LOG_FILE, "a", encoding="utf-8").close()

_resource = Resource.create({"service.name": SERVICE})
_provider = TracerProvider(
    resource=_resource,
    sampler=ParentBasedTraceIdRatio(max(0.0, min(1.0, OTEL_SAMPLE_RATIO))),
)
_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{OTEL_ENDPOINT}/v1/traces"))
)
trace.set_tracer_provider(_provider)
tracer = trace.get_tracer(SERVICE)

REQS = Counter(
    "http_requests_total",
    "Total de requests HTTP",
    ["service", "route", "method", "status"],
)
LATENCY = Histogram(
    "http_request_duration_seconds",
    "Duração de requests HTTP",
    ["service", "route", "method"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


def current_trace_id() -> str:
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx.is_valid:
        return format(ctx.trace_id, "032x")
    return uuid.uuid4().hex


def log(level: str, msg: str, **fields: Any) -> None:
    if "trace_id" not in fields:
        fields["trace_id"] = current_trace_id()
    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "level": level,
        "service": SERVICE,
        "msg": msg,
        **fields,
    }
    line = json.dumps(record, ensure_ascii=False)
    print(line, flush=True)
    if LOG_FILE:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError:
            pass


def http_json(
    method: str,
    url: str,
    payload: dict | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> tuple[int, dict]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    hdrs = {"Content-Type": "application/json"}
    if PROPAGATE_TRACE:
        inject(hdrs)
    if headers:
        hdrs.update(headers)
    req = Request(url, data=body, method=method)
    for k, v in hdrs.items():
        req.add_header(k, v)
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            data = json.loads(raw) if raw else {}
            return resp.status, data
    except HTTPError as exc:
        raw = exc.read().decode("utf-8")
        try:
            data = json.loads(raw) if raw else {"erro": str(exc)}
        except json.JSONDecodeError:
            data = {"erro": raw or str(exc)}
        return exc.code, data
    except URLError as exc:
        return 503, {"erro": f"upstream indisponível: {exc.reason}"}


class JsonHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        return

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

    def _metrics(self) -> None:
        body = generate_latest()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPE_LATEST)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def observe(self, route: str, method: str, status: int, start: float) -> None:
        REQS.labels(SERVICE, route, method, str(status)).inc()
        LATENCY.labels(SERVICE, route, method).observe(time.perf_counter() - start)

    def start_server_span(self, name: str):
        if PROPAGATE_TRACE:
            # Message.get é case-insensitive; dict(items()) perde isso e quebra o extract W3C.
            carrier: dict[str, str] = {}
            tp = self.headers.get("traceparent")
            ts = self.headers.get("tracestate")
            if tp:
                carrier["traceparent"] = tp
            if ts:
                carrier["tracestate"] = ts
            ctx = extract(carrier)
        else:
            ctx = None
        return tracer.start_as_current_span(name, context=ctx)

    def mark_error(self, span, msg: str) -> None:
        span.set_status(Status(StatusCode.ERROR, msg))
        span.record_exception(RuntimeError(msg))

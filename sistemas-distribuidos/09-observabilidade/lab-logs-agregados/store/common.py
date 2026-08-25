"""Utilitários compartilhados — logs estruturados + HTTP JSON (lab 09)."""

from __future__ import annotations

import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


SERVICE = os.environ.get("SERVICE_NAME", "app")
LOG_FILE = os.environ.get("LOG_FILE", "")
PROPAGATE_TRACE = os.environ.get("PROPAGATE_TRACE", "1") == "1"
UNSTRUCTURED_LOG = os.environ.get("UNSTRUCTURED_LOG", "0") == "1"

if LOG_FILE:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    open(LOG_FILE, "a", encoding="utf-8").close()


def new_trace_id() -> str:
    return uuid.uuid4().hex


def log(level: str, msg: str, **fields: Any) -> None:
    if UNSTRUCTURED_LOG:
        extras = " ".join(f"{k}={v}" for k, v in fields.items())
        line = f"{level} {SERVICE}: {msg}" + (f" {extras}" if extras else "")
    else:
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
    req = Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    for k, v in (headers or {}).items():
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

    def trace_id_from_request(self) -> str:
        incoming = self.headers.get("X-Trace-Id", "").strip()
        if incoming and PROPAGATE_TRACE:
            return incoming
        return new_trace_id()

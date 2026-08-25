"""HTTP JSON mínimo — lab notificacao-canais."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import urlparse


class JsonHandler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _path(self) -> str:
        return urlparse(self.path).path.rstrip("/") or "/"

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.__class__.__module__}] {self.address_string()} - {fmt % args}", flush=True)

"""HTTP JSON mínimo — lab A (encurtador)."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler
from typing import Any
from urllib.parse import parse_qs, urlparse


class JsonHandler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(
        self,
        code: int,
        location: str,
        extra_headers: dict[str, str] | None = None,
        head_only: bool = False,
    ) -> None:
        self.send_response(code)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        if not head_only:
            self.wfile.write(b"")

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _path(self) -> str:
        return urlparse(self.path).path.rstrip("/") or "/"

    def _query(self) -> dict[str, list[str]]:
        return parse_qs(urlparse(self.path).query)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{self.__class__.__module__}] {self.address_string()} - {fmt % args}", flush=True)

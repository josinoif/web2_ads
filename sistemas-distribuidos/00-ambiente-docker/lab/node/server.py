"""Nó HTTP mínimo para lab de sistemas distribuídos."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


NODE_NAME = os.environ.get("NODE_NAME", "unknown")
PORT = int(os.environ.get("PORT", "8000"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = {
            "node": NODE_NAME,
            "path": self.path,
            "message": f"olá do nó {NODE_NAME}",
        }
        payload = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{NODE_NAME}] {self.address_string()} - {fmt % args}")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[{NODE_NAME}] ouvindo em 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

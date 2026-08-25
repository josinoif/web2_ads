"""Store — persistência em memória."""

from __future__ import annotations

import os
import uuid
from http.server import ThreadingHTTPServer

from common import JsonHandler

PORT = int(os.environ.get("PORT", "8000"))
STORE: dict[str, dict] = {}


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "service": "store", "itens": len(STORE)})
            return
        if path.startswith("/provas/"):
            sid = path.split("/", 2)[2]
            if sid not in STORE:
                self._json(404, {"erro": "não encontrado"})
                return
            self._json(200, STORE[sid])
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path != "/persistir":
            self._json(404, {"erro": "não encontrado"})
            return
        data = self._read_json()
        submission_id = data.get("submission_id") or f"srv-{uuid.uuid4().hex[:8]}"
        registro = {
            "submission_id": submission_id,
            "aluno": data.get("aluno") or "anon",
            "arquivo": data.get("arquivo") or "prova.pdf",
            "similaridade_pct": data.get("similaridade_pct", 12),
            "store": "servicos",
        }
        STORE[submission_id] = registro
        self._json(201, registro)


if __name__ == "__main__":
    print(f"[store] ouvindo 0.0.0.0:{PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

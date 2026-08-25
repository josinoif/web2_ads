"""Store — persiste a prova em memória (lab)."""

from __future__ import annotations

import os
import uuid
from http.server import ThreadingHTTPServer

from common import JsonHandler, log

PORT = int(os.environ.get("PORT", "8000"))
STORE: dict[str, dict] = {}


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "service": "store", "n": len(STORE)})
            return
        if path == "/admin/config":
            self._json(200, {"service": "store", "n": len(STORE)})
            return
        if path.startswith("/provas/"):
            sid = path.split("/", 2)[2]
            item = STORE.get(sid)
            if item is None:
                self._json(404, {"erro": "não encontrado", "submission_id": sid})
                return
            self._json(200, item)
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path != "/persistir":
            self._json(404, {"erro": "não encontrado"})
            return

        trace_id = self.trace_id_from_request()
        data = self._read_json()
        submission_id = uuid.uuid4().hex[:12]
        registro = {
            "submission_id": submission_id,
            "trace_id": trace_id,
            "aluno": data.get("aluno"),
            "arquivo": data.get("arquivo"),
            "similaridade_pct": data.get("similaridade_pct", 0),
        }
        STORE[submission_id] = registro
        log("INFO", "prova persistida", trace_id=trace_id, submission_id=submission_id, aluno=registro["aluno"])
        self._json(201, registro)


if __name__ == "__main__":
    log("INFO", "store iniciando", port=PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

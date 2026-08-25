"""Store APM — persistência em memória + OTel + métricas."""

from __future__ import annotations

import os
import time
import uuid
from http.server import ThreadingHTTPServer

from common import JsonHandler, current_trace_id, log

PORT = int(os.environ.get("PORT", "8000"))
STORE: dict[str, dict] = {}


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/metrics":
            self._metrics()
            return
        if path == "/health":
            self._json(200, {"ok": True, "service": "store", "n": len(STORE)})
            return
        if path.startswith("/provas/"):
            sid = path.split("/", 2)[2]
            item = STORE.get(sid)
            if item is None:
                self._json(404, {"erro": "não encontrado"})
                return
            self._json(200, item)
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path != "/persistir":
            self._json(404, {"erro": "não encontrado"})
            return

        start = time.perf_counter()
        data = self._read_json()
        with self.start_server_span("persistir") as span:
            submission_id = uuid.uuid4().hex[:12]
            tid = current_trace_id()
            registro = {
                "submission_id": submission_id,
                "trace_id": tid,
                "aluno": data.get("aluno"),
                "arquivo": data.get("arquivo"),
                "similaridade_pct": data.get("similaridade_pct", 0),
            }
            STORE[submission_id] = registro
            span.set_attribute("submission_id", submission_id)
            log("INFO", "prova persistida", submission_id=submission_id, aluno=registro["aluno"])
            self.observe("/persistir", "POST", 201, start)
            self._json(201, registro)


if __name__ == "__main__":
    log("INFO", "store iniciando", port=PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

"""Gateway — recebe POST /provas e chama o serviço de análise."""

from __future__ import annotations

import os
from http.server import ThreadingHTTPServer

from common import JsonHandler, http_json, log

PORT = int(os.environ.get("PORT", "8000"))
ANALISE_URL = os.environ.get("ANALISE_URL", "http://analise:8000").rstrip("/")
PROPAGATE_TRACE = os.environ.get("PROPAGATE_TRACE", "1") == "1"


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "service": "gateway"})
            return
        if path == "/admin/config":
            self._json(
                200,
                {
                    "service": "gateway",
                    "analise_url": ANALISE_URL,
                    "propagate_trace": PROPAGATE_TRACE,
                },
            )
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path != "/provas":
            self._json(404, {"erro": "não encontrado"})
            return

        trace_id = self.trace_id_from_request()
        data = self._read_json()
        aluno = data.get("aluno") or "anon"
        arquivo = data.get("arquivo") or "prova.pdf"

        log("INFO", "recebido POST /provas", trace_id=trace_id, aluno=aluno, arquivo=arquivo)

        headers = {}
        if PROPAGATE_TRACE:
            headers["X-Trace-Id"] = trace_id

        status, resp = http_json(
            "POST",
            f"{ANALISE_URL}/analisar",
            {"aluno": aluno, "arquivo": arquivo},
            headers=headers,
        )

        if status >= 400:
            log(
                "ERROR",
                "análise falhou",
                trace_id=trace_id,
                upstream_status=status,
                upstream=resp,
            )
            self._json(
                status if status < 600 else 502,
                {
                    "erro": "falha na análise",
                    "trace_id": trace_id,
                    "upstream": resp,
                },
            )
            return

        log(
            "INFO",
            "prova aceita",
            trace_id=trace_id,
            submission_id=resp.get("submission_id"),
            aluno=aluno,
        )
        self._json(
            201,
            {
                "status": "aceito",
                "trace_id": trace_id,
                "submission_id": resp.get("submission_id"),
                "aluno": aluno,
                "arquivo": arquivo,
                "relatorio": resp.get("relatorio"),
            },
        )


if __name__ == "__main__":
    log("INFO", "gateway iniciando", port=PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

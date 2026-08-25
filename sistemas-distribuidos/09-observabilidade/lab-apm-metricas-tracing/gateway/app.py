"""Gateway APM — POST /provas + /metrics + OTel (+ retries didáticos, ponte 06)."""

from __future__ import annotations

import os
import time
from http.server import ThreadingHTTPServer

from common import JsonHandler, current_trace_id, http_json, log, tracer

PORT = int(os.environ.get("PORT", "8000"))
ANALISE_URL = os.environ.get("ANALISE_URL", "http://analise:8000").rstrip("/")
GATEWAY_RETRIES = int(os.environ.get("GATEWAY_RETRIES", "0"))


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/metrics":
            self._metrics()
            return
        if path == "/health":
            self._json(200, {"ok": True, "service": "gateway"})
            return
        if path == "/admin/config":
            self._json(
                200,
                {
                    "service": "gateway",
                    "analise_url": ANALISE_URL,
                    "gateway_retries": GATEWAY_RETRIES,
                },
            )
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        global GATEWAY_RETRIES
        path = self.path.rstrip("/") or "/"

        if path == "/admin/retries":
            body = self._read_json()
            if "retries" in body:
                GATEWAY_RETRIES = int(body["retries"])
            log("WARN", "gateway_retries atualizado", gateway_retries=GATEWAY_RETRIES)
            self._json(200, {"gateway_retries": GATEWAY_RETRIES})
            return

        if path != "/provas":
            self._json(404, {"erro": "não encontrado"})
            return

        start = time.perf_counter()
        data = self._read_json()
        aluno = data.get("aluno") or "anon"
        arquivo = data.get("arquivo") or "prova.pdf"

        with self.start_server_span("POST /provas") as span:
            span.set_attribute("aluno", aluno)
            span.set_attribute("gateway_retries", GATEWAY_RETRIES)
            log("INFO", "recebido POST /provas", aluno=aluno, arquivo=arquivo)

            attempts = 1 + max(0, GATEWAY_RETRIES)
            status, resp = 500, {}
            for attempt in range(1, attempts + 1):
                with tracer.start_as_current_span(f"chamar_analise_tentativa_{attempt}") as child:
                    child.set_attribute("attempt", attempt)
                    status, resp = http_json(
                        "POST",
                        f"{ANALISE_URL}/analisar",
                        {"aluno": aluno, "arquivo": arquivo},
                    )
                    child.set_attribute("upstream_status", status)
                    if status < 400:
                        break
                    self.mark_error(child, f"análise falhou tentativa {attempt}")
                    log(
                        "WARN",
                        "análise falhou; retry?" if attempt < attempts else "análise falhou",
                        attempt=attempt,
                        attempts=attempts,
                        upstream_status=status,
                    )

            if status >= 400:
                self.mark_error(span, "análise falhou")
                log("ERROR", "análise falhou após tentativas", attempts=attempts, upstream=resp)
                self.observe("/provas", "POST", status, start)
                self._json(
                    status if status < 600 else 502,
                    {
                        "erro": "falha na análise",
                        "trace_id": current_trace_id(),
                        "attempts": attempts,
                        "upstream": resp,
                    },
                )
                return

            tid = current_trace_id()
            log("INFO", "prova aceita", submission_id=resp.get("submission_id"), aluno=aluno, attempts=attempts)
            self.observe("/provas", "POST", 201, start)
            self._json(
                201,
                {
                    "status": "aceito",
                    "trace_id": tid,
                    "submission_id": resp.get("submission_id"),
                    "aluno": aluno,
                    "arquivo": arquivo,
                    "attempts": attempts,
                    "relatorio": resp.get("relatorio"),
                },
            )


if __name__ == "__main__":
    log("INFO", "gateway iniciando", port=PORT, gateway_retries=GATEWAY_RETRIES)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

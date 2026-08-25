"""Análise APM — delay/erro injetáveis + OTel + métricas."""

from __future__ import annotations

import os
import random
import time
from http.server import ThreadingHTTPServer

from common import JsonHandler, current_trace_id, http_json, log

PORT = int(os.environ.get("PORT", "8000"))
STORE_URL = os.environ.get("STORE_URL", "http://store:8000").rstrip("/")
INJECT_DELAY_MS = int(os.environ.get("INJECT_DELAY_MS", "0"))
INJECT_ERROR_RATE = float(os.environ.get("INJECT_ERROR_RATE", "0"))
ANALISE_BASE_MS = int(os.environ.get("ANALISE_BASE_MS", "50"))


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/metrics":
            self._metrics()
            return
        if path == "/health":
            self._json(200, {"ok": True, "service": "analise"})
            return
        if path == "/admin/config":
            self._json(
                200,
                {
                    "service": "analise",
                    "inject_delay_ms": INJECT_DELAY_MS,
                    "inject_error_rate": INJECT_ERROR_RATE,
                },
            )
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        global INJECT_DELAY_MS, INJECT_ERROR_RATE
        path = self.path.rstrip("/") or "/"

        if path == "/admin/inject":
            body = self._read_json()
            if "delay_ms" in body:
                INJECT_DELAY_MS = int(body["delay_ms"])
            if "error_rate" in body:
                INJECT_ERROR_RATE = float(body["error_rate"])
            log("WARN", "inject atualizado", delay_ms=INJECT_DELAY_MS, error_rate=INJECT_ERROR_RATE)
            self._json(200, {"inject_delay_ms": INJECT_DELAY_MS, "inject_error_rate": INJECT_ERROR_RATE})
            return

        if path != "/analisar":
            self._json(404, {"erro": "não encontrado"})
            return

        start = time.perf_counter()
        data = self._read_json()
        aluno = data.get("aluno") or "anon"
        arquivo = data.get("arquivo") or "prova.pdf"

        with self.start_server_span("analisar") as span:
            span.set_attribute("aluno", aluno)
            log("INFO", "iniciando análise", aluno=aluno)

            if INJECT_ERROR_RATE > 0 and random.random() < INJECT_ERROR_RATE:
                self.mark_error(span, "falha injetada")
                log("ERROR", "falha injetada na análise", aluno=aluno)
                self.observe("/analisar", "POST", 500, start)
                self._json(500, {"erro": "falha injetada na análise", "trace_id": current_trace_id()})
                return

            delay_s = (ANALISE_BASE_MS + INJECT_DELAY_MS) / 1000.0
            span.set_attribute("inject_delay_ms", INJECT_DELAY_MS)
            time.sleep(delay_s)

            status, resp = http_json(
                "POST",
                f"{STORE_URL}/persistir",
                {"aluno": aluno, "arquivo": arquivo, "similaridade_pct": 12},
            )
            if status >= 400:
                self.mark_error(span, "store falhou")
                log("ERROR", "store falhou", upstream_status=status)
                self.observe("/analisar", "POST", status, start)
                self._json(status if status < 600 else 502, {"erro": "store falhou", "trace_id": current_trace_id()})
                return

            tid = current_trace_id()
            log("INFO", "análise concluída", submission_id=resp.get("submission_id"), duration_ms=int(delay_s * 1000))
            self.observe("/analisar", "POST", 200, start)
            self._json(
                200,
                {
                    "submission_id": resp.get("submission_id"),
                    "trace_id": tid,
                    "relatorio": {
                        "similaridade_pct": 12,
                        "parecer": "ok (lab APM)",
                        "duration_ms": int(delay_s * 1000),
                    },
                },
            )


if __name__ == "__main__":
    log("INFO", "analise iniciando", port=PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

"""Serviço de análise — hop do meio (delay/erro injetáveis)."""

from __future__ import annotations

import os
import random
import time
from http.server import ThreadingHTTPServer

from common import JsonHandler, http_json, log

PORT = int(os.environ.get("PORT", "8000"))
STORE_URL = os.environ.get("STORE_URL", "http://store:8000").rstrip("/")
PROPAGATE_TRACE = os.environ.get("PROPAGATE_TRACE", "1") == "1"
INJECT_DELAY_MS = int(os.environ.get("INJECT_DELAY_MS", "0"))
INJECT_ERROR_RATE = float(os.environ.get("INJECT_ERROR_RATE", "0"))
ANALISE_BASE_MS = int(os.environ.get("ANALISE_BASE_MS", "50"))


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "service": "analise"})
            return
        if path == "/admin/config":
            self._json(
                200,
                {
                    "service": "analise",
                    "store_url": STORE_URL,
                    "propagate_trace": PROPAGATE_TRACE,
                    "inject_delay_ms": INJECT_DELAY_MS,
                    "inject_error_rate": INJECT_ERROR_RATE,
                },
            )
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path == "/admin/inject":
            global INJECT_DELAY_MS, INJECT_ERROR_RATE
            body = self._read_json()
            if "delay_ms" in body:
                INJECT_DELAY_MS = int(body["delay_ms"])
            if "error_rate" in body:
                INJECT_ERROR_RATE = float(body["error_rate"])
            log(
                "WARN",
                "inject atualizado",
                delay_ms=INJECT_DELAY_MS,
                error_rate=INJECT_ERROR_RATE,
            )
            self._json(
                200,
                {
                    "inject_delay_ms": INJECT_DELAY_MS,
                    "inject_error_rate": INJECT_ERROR_RATE,
                },
            )
            return

        if path != "/analisar":
            self._json(404, {"erro": "não encontrado"})
            return

        trace_id = self.trace_id_from_request()
        data = self._read_json()
        aluno = data.get("aluno") or "anon"
        arquivo = data.get("arquivo") or "prova.pdf"

        log("INFO", "iniciando análise", trace_id=trace_id, aluno=aluno)

        if INJECT_ERROR_RATE > 0 and random.random() < INJECT_ERROR_RATE:
            log("ERROR", "falha injetada na análise", trace_id=trace_id, aluno=aluno)
            self._json(500, {"erro": "falha injetada na análise", "trace_id": trace_id})
            return

        delay_s = (ANALISE_BASE_MS + INJECT_DELAY_MS) / 1000.0
        time.sleep(delay_s)

        headers = {}
        if PROPAGATE_TRACE:
            headers["X-Trace-Id"] = trace_id

        status, resp = http_json(
            "POST",
            f"{STORE_URL}/persistir",
            {"aluno": aluno, "arquivo": arquivo, "similaridade_pct": 12},
            headers=headers,
        )
        if status >= 400:
            log(
                "ERROR",
                "store falhou",
                trace_id=trace_id,
                upstream_status=status,
                upstream=resp,
            )
            self._json(status if status < 600 else 502, {"erro": "store falhou", "trace_id": trace_id, "upstream": resp})
            return

        log(
            "INFO",
            "análise concluída",
            trace_id=trace_id,
            submission_id=resp.get("submission_id"),
            duration_ms=int(delay_s * 1000),
        )
        self._json(
            200,
            {
                "submission_id": resp.get("submission_id"),
                "trace_id": trace_id,
                "relatorio": {
                    "similaridade_pct": 12,
                    "parecer": "ok (lab observabilidade)",
                    "duration_ms": int(delay_s * 1000),
                },
            },
        )


if __name__ == "__main__":
    log("INFO", "analise iniciando", port=PORT)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

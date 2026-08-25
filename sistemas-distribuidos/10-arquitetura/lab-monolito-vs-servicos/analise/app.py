"""Análise — hop do meio (delay injetável)."""

from __future__ import annotations

import os
import time
import uuid
from http.server import ThreadingHTTPServer

from common import JsonHandler, http_json

PORT = int(os.environ.get("PORT", "8000"))
STORE_URL = os.environ.get("STORE_URL", "http://store:8000").rstrip("/")
INJECT_DELAY_MS = int(os.environ.get("INJECT_DELAY_MS", "0"))
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
                    "inject_delay_ms": INJECT_DELAY_MS,
                    "analise_base_ms": ANALISE_BASE_MS,
                },
            )
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        global INJECT_DELAY_MS
        path = self.path.rstrip("/") or "/"

        if path == "/admin/inject":
            body = self._read_json()
            if "delay_ms" in body:
                INJECT_DELAY_MS = int(body["delay_ms"])
            self._json(200, {"inject_delay_ms": INJECT_DELAY_MS})
            return

        if path != "/analisar":
            self._json(404, {"erro": "não encontrado"})
            return

        data = self._read_json()
        aluno = data.get("aluno") or "anon"
        arquivo = data.get("arquivo") or "prova.pdf"

        time.sleep((ANALISE_BASE_MS + INJECT_DELAY_MS) / 1000.0)

        status, resp = http_json(
            "POST",
            f"{STORE_URL}/persistir",
            {"aluno": aluno, "arquivo": arquivo, "similaridade_pct": 12},
        )
        if status >= 400:
            self._json(status if status < 600 else 502, {"erro": "store falhou", "upstream": resp})
            return

        submission_id = resp.get("submission_id") or f"srv-{uuid.uuid4().hex[:8]}"
        self._json(
            200,
            {
                "submission_id": submission_id,
                "aluno": aluno,
                "arquivo": arquivo,
                "relatorio": {
                    "similaridade_pct": 12,
                    "parecer": "ok (serviços)",
                    "store": resp.get("store"),
                },
            },
        )


if __name__ == "__main__":
    print(f"[analise] ouvindo 0.0.0.0:{PORT} → {STORE_URL}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

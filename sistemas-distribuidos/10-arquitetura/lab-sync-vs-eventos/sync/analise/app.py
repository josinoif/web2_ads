"""Análise sync — sleep + chama store."""

from __future__ import annotations

import os
import time
import uuid
from http.server import ThreadingHTTPServer

from common import JsonHandler, http_json

PORT = int(os.environ.get("PORT", "8000"))
STORE_URL = os.environ.get("STORE_URL", "http://store-sync:8000").rstrip("/")
ANALISE_SEGUNDOS = float(os.environ.get("ANALISE_SEGUNDOS", "2"))


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "service": "analise-sync"})
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path != "/analisar":
            self._json(404, {"erro": "não encontrado"})
            return

        data = self._read_json()
        aluno = data.get("aluno") or "anon"
        arquivo = data.get("arquivo") or "prova.pdf"
        time.sleep(ANALISE_SEGUNDOS)

        status, resp = http_json(
            "POST",
            f"{STORE_URL}/persistir",
            {"aluno": aluno, "arquivo": arquivo, "similaridade_pct": 12},
        )
        if status >= 400:
            self._json(status if status < 600 else 502, {"erro": "store falhou", "upstream": resp})
            return

        self._json(
            200,
            {
                "submission_id": resp.get("submission_id") or f"sync-{uuid.uuid4().hex[:8]}",
                "aluno": aluno,
                "arquivo": arquivo,
                "relatorio": {"similaridade_pct": 12, "parecer": "ok (sync)"},
            },
        )


if __name__ == "__main__":
    print(f"[analise-sync] :{PORT} sleep={ANALISE_SEGUNDOS}s → {STORE_URL}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

"""Gateway — borda HTTP dos serviços (chama análise)."""

from __future__ import annotations

import os
import time
from http.server import ThreadingHTTPServer

from common import JsonHandler, http_json

PORT = int(os.environ.get("PORT", "8000"))
ANALISE_URL = os.environ.get("ANALISE_URL", "http://analise:8000").rstrip("/")
MODO = "servicos"


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "service": "gateway", "modo": MODO})
            return
        if path == "/admin/config":
            self._json(200, {"service": "gateway", "modo": MODO, "analise_url": ANALISE_URL})
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/") or "/"
        if path != "/provas":
            self._json(404, {"erro": "não encontrado"})
            return

        start = time.perf_counter()
        data = self._read_json()
        aluno = data.get("aluno") or "anon"
        arquivo = data.get("arquivo") or "prova.pdf"

        status, resp = http_json(
            "POST",
            f"{ANALISE_URL}/analisar",
            {"aluno": aluno, "arquivo": arquivo},
        )
        lat_ms = round((time.perf_counter() - start) * 1000, 1)

        if status >= 400:
            self._json(
                status if status < 600 else 502,
                {
                    "erro": "falha na análise",
                    "modo": MODO,
                    "latencia_ms": lat_ms,
                    "upstream": resp,
                },
            )
            return

        self._json(
            201,
            {
                "status": "aceito",
                "modo": MODO,
                "latencia_ms": lat_ms,
                "submission_id": resp.get("submission_id"),
                "aluno": aluno,
                "arquivo": arquivo,
                "relatorio": resp.get("relatorio"),
            },
        )


if __name__ == "__main__":
    print(f"[gateway] ouvindo 0.0.0.0:{PORT} → {ANALISE_URL}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

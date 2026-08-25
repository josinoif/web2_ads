"""Monólito modular — um deployável, três arquivos de módulo.

Fronteiras de código (não de processo):
  portal_mod (este arquivo / Handler) · analise_mod.py · store_mod.py
"""

from __future__ import annotations

import os
import time
from http.server import ThreadingHTTPServer

import analise_mod
import store_mod
from common import JsonHandler

PORT = int(os.environ.get("PORT", "8000"))
MODO = "monolito"

analise_mod.BASE_MS = int(os.environ.get("ANALISE_BASE_MS", "50"))
analise_mod.DELAY_MS = int(os.environ.get("INJECT_DELAY_MS", "0"))


class Handler(JsonHandler):
    """portal_mod — borda HTTP / recibo."""

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        if path == "/health":
            self._json(
                200,
                {
                    "ok": True,
                    "service": "monolito",
                    "modo": MODO,
                    "itens": store_mod.tamanho(),
                    "modulos": store_mod.MODULOS,
                },
            )
            return
        if path == "/admin/config":
            self._json(
                200,
                {
                    "service": "monolito",
                    "modo": MODO,
                    "inject_delay_ms": analise_mod.DELAY_MS,
                    "analise_base_ms": analise_mod.BASE_MS,
                    "modulos": store_mod.MODULOS,
                    "arquivos": ["app.py", "analise_mod.py", "store_mod.py"],
                },
            )
            return
        if path.startswith("/provas/"):
            sid = path.split("/", 2)[2]
            reg = store_mod.obter(sid)
            if reg is None:
                self._json(404, {"erro": "não encontrado"})
                return
            self._json(200, reg)
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self.path.rstrip("/") or "/"

        if path == "/admin/inject":
            body = self._read_json()
            if "delay_ms" in body:
                analise_mod.DELAY_MS = int(body["delay_ms"])
            self._json(200, {"inject_delay_ms": analise_mod.DELAY_MS})
            return

        if path != "/provas":
            self._json(404, {"erro": "não encontrado"})
            return

        start = time.perf_counter()
        data = self._read_json()
        aluno = data.get("aluno") or "anon"
        arquivo = data.get("arquivo") or "prova.pdf"
        relatorio = analise_mod.processar(aluno, arquivo)
        registro = store_mod.persistir(aluno, arquivo, relatorio)
        lat_ms = round((time.perf_counter() - start) * 1000, 1)
        self._json(
            201,
            {
                "status": "aceito",
                "modo": MODO,
                "latencia_ms": lat_ms,
                "submission_id": registro["submission_id"],
                "aluno": aluno,
                "arquivo": arquivo,
                "relatorio": registro["relatorio"],
                "modulos": registro["modulos"],
            },
        )


if __name__ == "__main__":
    print(
        f"[monolito] :{PORT} arquivos=app.py,analise_mod.py,store_mod.py (1 processo)",
        flush=True,
    )
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

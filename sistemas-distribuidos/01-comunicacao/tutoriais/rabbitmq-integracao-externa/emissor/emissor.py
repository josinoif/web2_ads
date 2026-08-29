"""
Emissor de carteirinha — o "sistema de fora" (MOCK).

É lento de propósito e falha com frequência. Não é um bug do lab:
é o comportamento que o portal da faculdade NÃO pode copiar para a tela
do aluno (por isso existe a fila + worker).

Regras de falha (para os experimentos ficarem previsíveis):

- aluno == "veneno"     → sempre 500 (vai para a DLQ)
- aluno estavel-* ou teste-kill → nunca falha (passos 3 e 5)
- qualquer outro        → ~35% de 500 (retry no lote)
"""

from __future__ import annotations

import json
import os
import random
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT = int(os.environ.get("PORT", "8000"))
LENTEZA_SEGUNDOS = float(os.environ.get("LENTEZA_SEGUNDOS", "3"))
TAXA_FALHA = float(os.environ.get("TAXA_FALHA", "0.35"))
VENENO = os.environ.get("VENENO_ALUNO", "veneno")

# "Base" deste processo. Some se o container reiniciar — ok para o lab.
_registros: list[dict] = []


def _deve_falhar(aluno: str) -> bool:
    if aluno == VENENO:
        return True
    if aluno.startswith("estavel") or aluno.startswith("teste-kill"):
        return False
    return random.random() < TAXA_FALHA


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "servico": "emissor-carteirinha"})
            return
        # Evidência do tutorial: o sistema de fora REALMENTE gravou (não só o status do portal)
        if path == "/registros":
            self._json(200, {"total": len(_registros), "itens": list(reversed(_registros[-20:]))})
            return
        self._json(
            200,
            {
                "servico": "emissor-carteirinha (MOCK)",
                "aviso": "API externa lenta e instável — não chame isto na request do aluno",
                "endpoints": ["POST /carteirinhas", "GET /registros", "GET /health"],
            },
        )

    def do_POST(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path != "/carteirinhas":
            self._json(404, {"erro": "rota não encontrada"})
            return

        dados = self._read_json()
        aluno = dados.get("aluno", "?")
        matricula_id = dados.get("matricula_id", "?")
        print(
            f"[emissor] pedido aluno={aluno} matricula={matricula_id} — processando {LENTEZA_SEGUNDOS}s …",
            flush=True,
        )
        # Simula rede + processamento deles. Enquanto isso o worker está Unacked.
        time.sleep(LENTEZA_SEGUNDOS)

        if _deve_falhar(aluno):
            print(f"[emissor] FALHA 500 aluno={aluno} matricula={matricula_id}", flush=True)
            self._json(500, {"erro": "emissor indisponível", "aluno": aluno, "matricula_id": matricula_id})
            return

        protocolo = f"CART-{matricula_id[-8:]}"
        registro = {
            "protocolo": protocolo,
            "aluno": aluno,
            "matricula_id": matricula_id,
            "emitido_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        _registros.append(registro)
        print(f"[emissor] OK protocolo={protocolo} aluno={aluno}", flush=True)
        self._json(201, registro)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[emissor] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(
        f"[emissor] mock em 0.0.0.0:{PORT} lenteza={LENTEZA_SEGUNDOS}s taxa_falha={TAXA_FALHA}",
        flush=True,
    )
    server.serve_forever()

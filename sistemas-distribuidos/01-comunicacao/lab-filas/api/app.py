"""
API do portal de correção de provas.

Responsabilidade: receber o upload (simulado), registrar a prova e
colocar um job na fila. A análise pesada NÃO roda aqui.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
PORT = int(os.environ.get("PORT", "8000"))
QUEUE_KEY = "prova:fila"
STATUS_PREFIX = "prova:status:"
# Tempo falso de "análise de plágio" (segundos) — usado só no endpoint síncrono
ANALISE_SEGUNDOS = float(os.environ.get("ANALISE_SEGUNDOS", "3"))

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def status_key(submission_id: str) -> str:
    return f"{STATUS_PREFIX}{submission_id}"


def salvar_status(submission_id: str, dados: dict) -> None:
    r.set(status_key(submission_id), json.dumps(dados, ensure_ascii=False))


def ler_status(submission_id: str) -> dict | None:
    raw = r.get(status_key(submission_id))
    if raw is None:
        return None
    return json.loads(raw)


def enfileirar(submission_id: str, aluno: str, arquivo: str) -> dict:
    agora = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    registro = {
        "submission_id": submission_id,
        "aluno": aluno,
        "arquivo": arquivo,
        "status": "na_fila",
        "enqueued_at": agora,
        "relatorio": None,
    }
    mensagem = {
        "submission_id": submission_id,
        "aluno": aluno,
        "arquivo": arquivo,
        "enqueued_at": agora,
    }
    salvar_status(submission_id, registro)
    r.lpush(QUEUE_KEY, json.dumps(mensagem, ensure_ascii=False))
    return registro


def analisar_agora(submission_id: str, aluno: str, arquivo: str) -> dict:
    """Versão síncrona: a API faz o trabalho pesado e só depois responde."""
    agora = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    registro = {
        "submission_id": submission_id,
        "aluno": aluno,
        "arquivo": arquivo,
        "status": "processando",
        "enqueued_at": agora,
        "relatorio": None,
    }
    salvar_status(submission_id, registro)
    time.sleep(ANALISE_SEGUNDOS)
    registro["status"] = "concluido"
    registro["relatorio"] = {
        "similaridade_pct": 12,
        "parecer": "análise síncrona (feita dentro da API)",
    }
    salvar_status(submission_id, registro)
    return registro


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
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/health":
            self._json(200, {"ok": True})
            return

        if path == "/fila":
            self._json(200, {"fila": QUEUE_KEY, "tamanho": r.llen(QUEUE_KEY)})
            return

        if path.startswith("/provas/"):
            submission_id = path.split("/", 2)[2]
            dados = ler_status(submission_id)
            if dados is None:
                self._json(404, {"erro": "prova não encontrada", "submission_id": submission_id})
                return
            self._json(200, dados)
            return

        self._json(
            200,
            {
                "servico": "api-correcao",
                "endpoints": [
                    "POST /provas",
                    "POST /provas/sincrono",
                    "POST /provas/lote?n=10",
                    "GET /provas/{id}",
                    "GET /fila",
                ],
            },
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        if path == "/provas":
            body = self._read_json()
            submission_id = body.get("submission_id") or f"prova-{uuid.uuid4().hex[:8]}"
            aluno = body.get("aluno", "aluno-desconhecido")
            arquivo = body.get("arquivo", f"{submission_id}.pdf")
            registro = enfileirar(submission_id, aluno, arquivo)
            # 202 Accepted = "aceitei o trabalho, ainda não terminei"
            self._json(202, registro)
            return

        if path == "/provas/sincrono":
            body = self._read_json()
            submission_id = body.get("submission_id") or f"sync-{uuid.uuid4().hex[:8]}"
            aluno = body.get("aluno", "aluno-desconhecido")
            arquivo = body.get("arquivo", f"{submission_id}.pdf")
            inicio = time.perf_counter()
            registro = analisar_agora(submission_id, aluno, arquivo)
            registro["latencia_api_segundos"] = round(time.perf_counter() - inicio, 2)
            self._json(200, registro)
            return

        if path == "/provas/lote":
            n = int(query.get("n", ["10"])[0])
            n = max(1, min(n, 50))
            criadas = []
            for i in range(n):
                submission_id = f"lote-{uuid.uuid4().hex[:8]}"
                criadas.append(
                    enfileirar(submission_id, f"aluno-{i+1:02d}", f"{submission_id}.pdf")
                )
            self._json(
                202,
                {
                    "enviadas": n,
                    "tamanho_fila": r.llen(QUEUE_KEY),
                    "provas": criadas,
                },
            )
            return

        self._json(404, {"erro": "rota não encontrada"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    # Espera o Redis ficar pronto (útil no Compose)
    for tentativa in range(30):
        try:
            r.ping()
            break
        except redis.exceptions.ConnectionError:
            time.sleep(0.5)
    else:
        raise SystemExit("Redis indisponível")

    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] ouvindo em 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

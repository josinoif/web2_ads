"""
Servidor gRPC de análise de provas.

Demonstra:
  - AnalisarSincrono     → RPC unário bloqueante (sync)
  - SubmeterAnalise      → aceita rápido; trabalho em thread (async)
  - ConsultarStatus      → polling unário
  - AcompanharStatus     → server streaming (async na observação)
"""

from __future__ import annotations

import os
import random
import threading
import time
import uuid
from concurrent import futures

import grpc

import provas_pb2
import provas_pb2_grpc

ANALISE_SEGUNDOS = float(os.environ.get("ANALISE_SEGUNDOS", "3"))
PORT = int(os.environ.get("PORT", "50051"))

# Estado em memória (lab single-node)
_lock = threading.Lock()
_store: dict[str, dict] = {}


def _novo_id() -> str:
    return f"prova-{uuid.uuid4().hex[:8]}"


def _salvar(sid: str, **campos) -> dict:
    with _lock:
        atual = _store.get(sid, {"submission_id": sid})
        atual.update(campos)
        _store[sid] = atual
        return dict(atual)


def _ler(sid: str) -> dict | None:
    with _lock:
        dados = _store.get(sid)
        return dict(dados) if dados else None


def _para_msg(dados: dict) -> provas_pb2.StatusProva:
    return provas_pb2.StatusProva(
        submission_id=dados.get("submission_id", ""),
        aluno=dados.get("aluno", ""),
        arquivo=dados.get("arquivo", ""),
        status=dados.get("status", ""),
        parecer=dados.get("parecer", ""),
        similaridade_pct=int(dados.get("similaridade_pct", 0)),
        worker=dados.get("worker", ""),
    )


def _analisar(sid: str) -> None:
    _salvar(sid, status="processando", worker="grpc-worker")
    time.sleep(ANALISE_SEGUNDOS)
    sim = random.randint(5, 40)
    _salvar(
        sid,
        status="concluido",
        similaridade_pct=sim,
        parecer="ok para correção manual" if sim < 30 else "revisar trechos",
        worker="grpc-worker",
    )


class AnaliseProvasServicer(provas_pb2_grpc.AnaliseProvasServicer):
    def AnalisarSincrono(self, request, context):
        sid = request.submission_id or _novo_id()
        print(f"[server] AnalisarSincrono {sid} (bloqueante)", flush=True)
        _salvar(
            sid,
            aluno=request.aluno or "aluno",
            arquivo=request.arquivo or f"{sid}.pdf",
            status="processando",
        )
        _analisar(sid)
        return _para_msg(_ler(sid) or {})

    def SubmeterAnalise(self, request, context):
        sid = request.submission_id or _novo_id()
        print(f"[server] SubmeterAnalise {sid} (aceite rápido)", flush=True)
        _salvar(
            sid,
            aluno=request.aluno or "aluno",
            arquivo=request.arquivo or f"{sid}.pdf",
            status="na_fila",
        )
        threading.Thread(target=_analisar, args=(sid,), daemon=True).start()
        return provas_pb2.Aceite(submission_id=sid, status="na_fila")

    def ConsultarStatus(self, request, context):
        dados = _ler(request.submission_id)
        if dados is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("prova não encontrada")
            return provas_pb2.StatusProva()
        return _para_msg(dados)

    def AcompanharStatus(self, request, context):
        sid = request.submission_id
        print(f"[server] AcompanharStatus stream {sid}", flush=True)
        ultimo = None
        # Empurra mudanças até estado terminal (ou ~60s)
        deadline = time.time() + 60
        while time.time() < deadline:
            if not context.is_active():
                return
            dados = _ler(sid)
            if dados is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("prova não encontrada")
                return
            assinatura = (dados.get("status"), dados.get("parecer"))
            if assinatura != ultimo:
                ultimo = assinatura
                yield _para_msg(dados)
                if dados.get("status") in ("concluido", "erro"):
                    return
            time.sleep(0.4)


def serve() -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    provas_pb2_grpc.add_AnaliseProvasServicer_to_server(AnaliseProvasServicer(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"[server] gRPC em 0.0.0.0:{PORT}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

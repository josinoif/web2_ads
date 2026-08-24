"""Cliente CLI para o lab gRPC.

Modos:
  sincrono    — AnalisarSincrono (bloqueia até o fim)
  async-poll  — SubmeterAnalise + ConsultarStatus em loop
  stream      — SubmeterAnalise + AcompanharStatus (server streaming)
  aceite      — só SubmeterAnalise (imprime o id e sai)
  status ID   — ConsultarStatus de um submission_id
"""

from __future__ import annotations

import os
import sys
import time

import grpc

import provas_pb2
import provas_pb2_grpc

TARGET = os.environ.get("GRPC_TARGET", "grpc-server:50051")


def stub():
    channel = grpc.insecure_channel(TARGET)
    for _ in range(30):
        try:
            grpc.channel_ready_future(channel).result(timeout=1)
            break
        except Exception:
            time.sleep(0.5)
    return provas_pb2_grpc.AnaliseProvasStub(channel)


def modo_sincrono() -> None:
    s = stub()
    print(f"== AnalisarSincrono (SYNC) → {TARGET}")
    t0 = time.perf_counter()
    resp = s.AnalisarSincrono(
        provas_pb2.PedidoProva(aluno="maria", arquivo="maria.pdf")
    )
    dt = time.perf_counter() - t0
    print(f"status={resp.status} parecer={resp.parecer!r} similaridade={resp.similaridade_pct}")
    print(f"latência do RPC: {dt:.2f}s (≈ tempo da análise)")


def modo_async_poll() -> None:
    s = stub()
    print(f"== SubmeterAnalise + ConsultarStatus (ASYNC poll) → {TARGET}")
    t0 = time.perf_counter()
    ace = s.SubmeterAnalise(
        provas_pb2.PedidoProva(aluno="joao", arquivo="joao.pdf")
    )
    print(f"aceite em {time.perf_counter()-t0:.2f}s → id={ace.submission_id} status={ace.status}")

    while True:
        st = s.ConsultarStatus(provas_pb2.ConsultaId(submission_id=ace.submission_id))
        print(f"  poll: status={st.status}")
        if st.status in ("concluido", "erro"):
            print(f"final: parecer={st.parecer!r} similaridade={st.similaridade_pct}")
            break
        time.sleep(0.8)


def modo_stream(submission_id: str | None = None) -> None:
    s = stub()
    print(f"== SubmeterAnalise + AcompanharStatus (ASYNC stream) → {TARGET}")
    if not submission_id:
        ace = s.SubmeterAnalise(
            provas_pb2.PedidoProva(aluno="ana", arquivo="ana.pdf")
        )
        submission_id = ace.submission_id
        print(f"submetido id={submission_id}")

    for st in s.AcompanharStatus(provas_pb2.ConsultaId(submission_id=submission_id)):
        print(f"  stream: status={st.status} parecer={st.parecer!r}")


def modo_aceite() -> None:
    s = stub()
    print(f"== SubmeterAnalise (só aceite) → {TARGET}")
    t0 = time.perf_counter()
    ace = s.SubmeterAnalise(
        provas_pb2.PedidoProva(aluno="teste-queda", arquivo="queda.pdf")
    )
    print(f"aceite em {time.perf_counter()-t0:.2f}s → id={ace.submission_id} status={ace.status}")
    print("Guarde o id para: ./scripts/cliente.sh status <id>")
    print(f"SUBMISSION_ID={ace.submission_id}")


def modo_status(submission_id: str) -> None:
    s = stub()
    print(f"== ConsultarStatus {submission_id} → {TARGET}")
    try:
        st = s.ConsultarStatus(provas_pb2.ConsultaId(submission_id=submission_id))
        print(
            f"status={st.status} parecer={st.parecer!r} similaridade={st.similaridade_pct}",
            flush=True,
        )
    except grpc.RpcError as exc:
        print(f"erro gRPC: {exc.code()} — {exc.details()}", flush=True)
        raise SystemExit(1) from exc


def main() -> None:
    modos = ("sincrono", "async-poll", "stream", "aceite", "status")
    if len(sys.argv) < 2 or sys.argv[1] not in modos:
        print("uso: run-client.py sincrono|async-poll|stream|aceite|status [submission_id]")
        sys.exit(1)
    modo = sys.argv[1]
    if modo == "sincrono":
        modo_sincrono()
    elif modo == "async-poll":
        modo_async_poll()
    elif modo == "stream":
        modo_stream(sys.argv[2] if len(sys.argv) > 2 else None)
    elif modo == "aceite":
        modo_aceite()
    else:
        if len(sys.argv) < 3:
            print("uso: run-client.py status <submission_id>")
            sys.exit(1)
        modo_status(sys.argv[2])


if __name__ == "__main__":
    main()

"""store_mod — persistência em memória (mesmo processo do monólito)."""

from __future__ import annotations

import uuid

_STORE: dict[str, dict] = {}

MODULOS = ["portal_mod", "analise_mod", "store_mod"]


def persistir(aluno: str, arquivo: str, relatorio: dict) -> dict:
    submission_id = f"mono-{uuid.uuid4().hex[:8]}"
    registro = {
        "submission_id": submission_id,
        "aluno": aluno,
        "arquivo": arquivo,
        "similaridade_pct": relatorio.get("similaridade_pct", 12),
        "store": "monolito",
        "relatorio": relatorio,
        "modulos": list(MODULOS),
    }
    _STORE[submission_id] = registro
    return registro


def obter(sid: str) -> dict | None:
    return _STORE.get(sid)


def tamanho() -> int:
    return len(_STORE)

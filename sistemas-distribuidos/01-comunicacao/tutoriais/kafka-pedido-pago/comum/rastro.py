"""
Rastro de cada contexto (estoque, nota, e-mail).

O tópico Kafka guarda o EVENTO. Cada sistema grava o que *fez* neste
arquivo (volume compartilhado) para o portal/lab.py consultar.
"""

from __future__ import annotations

import json
import os
import threading
from pathlib import Path

RASTRO_DIR = Path(os.environ.get("RASTRO_DIR", "/data/rastro"))
_lock = threading.Lock()


def _path(papel: str) -> Path:
    RASTRO_DIR.mkdir(parents=True, exist_ok=True)
    return RASTRO_DIR / f"{papel}.jsonl"


def registrar(papel: str, registro: dict) -> None:
    """Append-only: um JSON por linha (histórico simples para o lab)."""
    linha = json.dumps(registro, ensure_ascii=False) + "\n"
    with _lock:
        with _path(papel).open("a", encoding="utf-8") as fh:
            fh.write(linha)


def ler(papel: str, limit: int = 30) -> list[dict]:
    path = _path(papel)
    if not path.exists():
        return []
    linhas = path.read_text(encoding="utf-8").splitlines()
    escolhidas = linhas[-limit:] if limit > 0 else linhas
    out: list[dict] = []
    for linha in escolhidas:
        linha = linha.strip()
        if not linha:
            continue
        try:
            out.append(json.loads(linha))
        except json.JSONDecodeError:
            continue
    return out

"""Persistência de status da análise (compartilhada com o worker via volume)."""

from __future__ import annotations

import json
import os
from pathlib import Path

STATUS_DIR = Path(os.environ.get("STATUS_DIR", "/data/status"))


def salvar(submission_id: str, **campos) -> dict:
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    path = STATUS_DIR / f"{submission_id}.json"
    dados: dict
    if path.exists():
        dados = json.loads(path.read_text(encoding="utf-8"))
    else:
        dados = {"submission_id": submission_id}
    dados.update(campos)
    path.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return dados


def ler(submission_id: str) -> dict | None:
    path = STATUS_DIR / f"{submission_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

"""
Status da matrícula para o GET do portal.

O RabbitMQ guarda a MENSAGEM (o comando). O parecer/status para o aluno
fica aqui: um JSON por matrícula num volume Docker compartilhado entre
API e worker. Sem isso, o portal não saberia responder GET /matriculas/{id}.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

STATUS_DIR = Path(os.environ.get("STATUS_DIR", "/data/status"))


def salvar(matricula_id: str, **campos) -> dict:
    """Cria ou atualiza o arquivo da matrícula (mescla com o que já existia)."""
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    path = STATUS_DIR / f"{matricula_id}.json"
    if path.exists():
        dados = json.loads(path.read_text(encoding="utf-8"))
    else:
        dados = {"matricula_id": matricula_id}
    dados.update(campos)
    path.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")
    return dados


def ler(matricula_id: str) -> dict | None:
    """None = essa matrícula ainda não foi aceita por este portal."""
    path = STATUS_DIR / f"{matricula_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

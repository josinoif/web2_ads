"""analise_mod — trabalho “pesado” (sleep + relatório); mesmo processo do monólito."""

from __future__ import annotations

import time

# Preenchidos por app.py a partir do ambiente (um processo = um config).
BASE_MS = 50
DELAY_MS = 0


def processar(aluno: str, arquivo: str) -> dict:
    time.sleep((BASE_MS + DELAY_MS) / 1000.0)
    return {
        "similaridade_pct": 12,
        "parecer": "ok (monólito / analise_mod)",
        "aluno": aluno,
        "arquivo": arquivo,
    }

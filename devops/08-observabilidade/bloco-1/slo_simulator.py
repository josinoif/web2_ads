"""
slo_simulator.py - simulador didatico de SLO e error budget.

Uso:
    python slo_simulator.py --slo 0.995 --janela-dias 28 --rps 50

O simulador gera 1 dia de requisicoes. A probabilidade de erro pode ser
configurada para demonstrar budget saudavel (<< SLO) e queima acelerada.
"""
from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Resultado:
    total: int
    bons: int
    ruins: int
    slo: float
    budget_total: int
    budget_consumido: int

    @property
    def sli_atual(self) -> float:
        return self.bons / self.total if self.total else 0.0

    @property
    def budget_restante(self) -> int:
        return self.budget_total - self.budget_consumido

    @property
    def budget_queimado_pct(self) -> float:
        return self.budget_consumido / self.budget_total * 100 if self.budget_total else 0.0


def simular(slo: float, janela_dias: int, rps: float, prob_erro: float, seed: int = 42) -> Resultado:
    random.seed(seed)
    total_janela = int(rps * 60 * 60 * 24 * janela_dias)
    budget_total = max(1, int((1 - slo) * total_janela))

    total_dia = int(rps * 60 * 60 * 24)
    bons = 0
    ruins = 0
    for _ in range(total_dia):
        if random.random() < prob_erro:
            ruins += 1
        else:
            bons += 1
    return Resultado(
        total=total_dia,
        bons=bons,
        ruins=ruins,
        slo=slo,
        budget_total=budget_total,
        budget_consumido=ruins,
    )


def relatorio(r: Resultado) -> str:
    return (
        f"Requisicoes no dia        : {r.total:>10}\n"
        f"Bons                      : {r.bons:>10}\n"
        f"Ruins                     : {r.ruins:>10}\n"
        f"SLI atual (dia)           : {r.sli_atual*100:>9.3f} %\n"
        f"SLO alvo                  : {r.slo*100:>9.3f} %\n"
        f"Budget total (janela)     : {r.budget_total:>10} erros\n"
        f"Budget consumido (dia)    : {r.budget_consumido:>10} erros\n"
        f"Budget restante           : {r.budget_restante:>10} erros\n"
        f"Budget queimado           : {r.budget_queimado_pct:>9.2f} %\n"
    )


def classificar(pct_queimado: float) -> str:
    if pct_queimado <= 5:
        return "SAUDAVEL: queima dentro do esperado."
    if pct_queimado <= 20:
        return "ATENCAO: queima acima da media. Revisar ultimos deploys."
    if pct_queimado < 100:
        return "ALERTA: queima rapida. Considerar reduzir risco (freeze parcial)."
    return "CRITICO: budget estourado. Freeze de novas features ate estabilizar."


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Simulador de SLO e error budget")
    p.add_argument("--slo", type=float, default=0.995, help="Alvo SLO (0-1)")
    p.add_argument("--janela-dias", type=int, default=28)
    p.add_argument("--rps", type=float, default=50.0)
    p.add_argument("--prob-erro", type=float, default=0.003, help="Probabilidade de erro por request")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args(argv)

    if not 0 < args.slo < 1:
        print("ERRO: --slo deve estar entre 0 e 1 (exclusivo)", file=sys.stderr)
        return 2

    r = simular(args.slo, args.janela_dias, args.rps, args.prob_erro, args.seed)
    print(relatorio(r))
    print(classificar(r.budget_queimado_pct))
    return 0 if r.budget_queimado_pct < 100 else 1


if __name__ == "__main__":
    raise SystemExit(main())

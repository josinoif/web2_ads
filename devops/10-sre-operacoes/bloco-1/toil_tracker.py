"""
toil_tracker.py - rastreia e classifica toil a partir de CSV de logs diarios.

Formato CSV esperado (separador virgula):
    data,autor,categoria,atividade,minutos,automatizavel,risco_automacao
    2026-03-09,alice,rotacao-segredo,rotate secret PIX gateway,45,sim,baixo
    2026-03-10,bob,incidente,paging 3am LedgerErr,60,parcial,medio

Uso:
    python toil_tracker.py data/toil-log.csv --budget-horas 20 --semana-inicio 2026-03-09
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

from rich.console import Console
from rich.table import Table


@dataclass(frozen=True)
class Entrada:
    data: date
    autor: str
    categoria: str
    atividade: str
    minutos: int
    automatizavel: str
    risco_automacao: str


@dataclass
class Resumo:
    total_min: int = 0
    por_categoria: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    por_autor: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    facilmente_automatizavel_min: int = 0


def parse_data(s: str) -> date:
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()


def carregar(path: str) -> list[Entrada]:
    entradas: list[Entrada] = []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        leitor = csv.DictReader(fh)
        for row in leitor:
            try:
                entradas.append(Entrada(
                    data=parse_data(row["data"]),
                    autor=row["autor"].strip(),
                    categoria=row["categoria"].strip(),
                    atividade=row["atividade"].strip(),
                    minutos=int(row["minutos"]),
                    automatizavel=row.get("automatizavel", "").strip().lower(),
                    risco_automacao=row.get("risco_automacao", "").strip().lower(),
                ))
            except (KeyError, ValueError) as exc:
                print(f"AVISO: linha invalida ignorada: {row} ({exc})", file=sys.stderr)
    return entradas


def resumir(entradas: list[Entrada], semana_inicio: date) -> Resumo:
    limite = semana_inicio + timedelta(days=7)
    r = Resumo()
    for e in entradas:
        if not (semana_inicio <= e.data < limite):
            continue
        r.total_min += e.minutos
        r.por_categoria[e.categoria] += e.minutos
        r.por_autor[e.autor] += e.minutos
        if e.automatizavel == "sim" and e.risco_automacao in ("baixo", "medio"):
            r.facilmente_automatizavel_min += e.minutos
    return r


def classificar(min_total: int, budget_min: int) -> str:
    if budget_min <= 0:
        return "?"
    ratio = min_total / budget_min
    if ratio < 0.5:
        return "verde"
    if ratio < 1.0:
        return "amarelo"
    return "vermelho"


def relatorio(r: Resumo, budget_horas: int) -> int:
    console = Console()
    budget_min = budget_horas * 60

    tbl = Table(title=f"Toil (semana) - budget {budget_horas}h = {budget_min}min")
    for c in ("categoria", "minutos", "horas"):
        tbl.add_column(c)
    for cat, minutos in sorted(r.por_categoria.items(), key=lambda x: -x[1]):
        tbl.add_row(cat, str(minutos), f"{minutos/60:.1f}h")
    console.print(tbl)

    tbl2 = Table(title="Por autor")
    for c in ("autor", "minutos", "horas"):
        tbl2.add_column(c)
    for autor, minutos in sorted(r.por_autor.items(), key=lambda x: -x[1]):
        tbl2.add_row(autor, str(minutos), f"{minutos/60:.1f}h")
    console.print(tbl2)

    status = classificar(r.total_min, budget_min)
    console.print(f"\nTotal: {r.total_min} min ({r.total_min/60:.1f}h) | Budget: {budget_horas}h | Status: [bold]{status}[/bold]")
    console.print(f"Facilmente automatizavel: {r.facilmente_automatizavel_min} min "
                  f"({r.facilmente_automatizavel_min/60:.1f}h) - candidatos prioritarios")

    return 0 if status != "vermelho" else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--budget-horas", type=int, default=20,
                   help="Budget semanal de toil em horas (default 20, i.e. 50% de 40h)")
    p.add_argument("--semana-inicio", default=None,
                   help="Data inicial da semana YYYY-MM-DD. Default: ultima segunda-feira")
    args = p.parse_args(argv)

    try:
        entradas = carregar(args.csv)
    except OSError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    if args.semana_inicio:
        semana_inicio = parse_data(args.semana_inicio)
    else:
        hoje = date.today()
        semana_inicio = hoje - timedelta(days=hoje.weekday())

    resumo = resumir(entradas, semana_inicio)
    if resumo.total_min == 0:
        print("Sem entradas para a semana alvo.")
        return 0

    return relatorio(resumo, args.budget_horas)


if __name__ == "__main__":
    raise SystemExit(main())

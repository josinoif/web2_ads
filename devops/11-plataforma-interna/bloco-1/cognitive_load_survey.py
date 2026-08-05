"""
cognitive_load_survey.py - agrega survey de cognitive load dos squads.

Formato CSV:
    data,squad,respondente,q_sobrecarga,q_ferramentas,q_servicos_mantidos,comentario

q_sobrecarga: 1 (baixa) a 5 (muito alta).
q_ferramentas: numero de ferramentas distintas usadas por semana.
q_servicos_mantidos: numero de servicos operados por squad.

Uso:
    python cognitive_load_survey.py respostas.csv --threshold 3.5
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table


@dataclass
class RespostaSquad:
    scores: list[int] = field(default_factory=list)
    ferramentas: list[int] = field(default_factory=list)
    servicos: list[int] = field(default_factory=list)
    respondentes: int = 0
    comentarios: list[str] = field(default_factory=list)

    @property
    def media_sobrecarga(self) -> float:
        return statistics.mean(self.scores) if self.scores else 0.0

    @property
    def media_ferramentas(self) -> float:
        return statistics.mean(self.ferramentas) if self.ferramentas else 0.0

    @property
    def media_servicos(self) -> float:
        return statistics.mean(self.servicos) if self.servicos else 0.0


def parse_int(s: str, minimo: int = 0) -> int:
    v = int(s)
    if v < minimo:
        raise ValueError(f"valor {v} menor que minimo {minimo}")
    return v


def carregar(path: str) -> dict[str, RespostaSquad]:
    dados: dict[str, RespostaSquad] = defaultdict(RespostaSquad)
    with open(path, "r", encoding="utf-8", newline="") as fh:
        leitor = csv.DictReader(fh)
        for row in leitor:
            try:
                s = row["squad"].strip()
                r = dados[s]
                sobrecarga = parse_int(row["q_sobrecarga"])
                if not 1 <= sobrecarga <= 5:
                    raise ValueError(f"q_sobrecarga fora de 1-5: {sobrecarga}")
                r.scores.append(sobrecarga)
                r.ferramentas.append(parse_int(row["q_ferramentas"]))
                r.servicos.append(parse_int(row["q_servicos_mantidos"]))
                r.respondentes += 1
                comentario = row.get("comentario", "").strip()
                if comentario:
                    r.comentarios.append(comentario)
            except (KeyError, ValueError) as exc:
                print(f"AVISO: linha invalida ignorada: {exc}", file=sys.stderr)
    return dados


def relatorio(dados: dict[str, RespostaSquad], threshold: float) -> int:
    if not dados:
        print("Sem respostas.")
        return 0

    console = Console()
    tbl = Table(title="Cognitive load por squad")
    for c in ("squad", "respondentes", "sobrecarga(avg)", "ferramentas(avg)", "servicos(avg)", "status"):
        tbl.add_column(c)

    ordenado = sorted(dados.items(), key=lambda kv: -kv[1].media_sobrecarga)
    squads_acima = 0
    for squad, r in ordenado:
        acima = r.media_sobrecarga >= threshold
        status = "[bold red]ALTO[/]" if acima else "ok"
        if acima:
            squads_acima += 1
        tbl.add_row(
            squad,
            str(r.respondentes),
            f"{r.media_sobrecarga:.2f}",
            f"{r.media_ferramentas:.1f}",
            f"{r.media_servicos:.1f}",
            status,
        )
    console.print(tbl)

    total = len(dados)
    console.print(f"\n{squads_acima}/{total} squads acima do threshold {threshold}.")
    if squads_acima > 0:
        console.print("\nProxima acao: investigar squads [red]ALTO[/] com entrevista e priorizar "
                      "absorcao de complexidade pela plataforma.")
    return 0 if squads_acima == 0 else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    p.add_argument("--threshold", type=float, default=3.5,
                   help="Acima deste valor a sobrecarga e considerada alta (1-5).")
    args = p.parse_args(argv)

    try:
        dados = carregar(args.csv)
    except OSError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    return relatorio(dados, args.threshold)


if __name__ == "__main__":
    raise SystemExit(main())

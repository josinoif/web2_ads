"""
dr_simulator.py - simula cenarios de DR e calcula RPO/RTO esperados.

Entrada: YAML com definicoes de cenarios e parametros.
    cenarios:
      - nome: "cluster-perdido"
        rpo_fonte_min: 5           # ultimo snapshot/backup
        etapas:
          - { nome: "detectar", minutos: 5 }
          - { nome: "decidir-DR", minutos: 5 }
          - { nome: "provisionar-cluster", minutos: 10 }
          - { nome: "velero-restore", minutos: 15 }
          - { nome: "validar", minutos: 5 }

Uso:
    python dr_simulator.py cenarios.yaml --rto-alvo-min 30 --rpo-alvo-min 5
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

import yaml
from rich.console import Console
from rich.table import Table


@dataclass(frozen=True)
class Etapa:
    nome: str
    minutos: int


@dataclass(frozen=True)
class Cenario:
    nome: str
    rpo_fonte_min: int
    etapas: list[Etapa]

    @property
    def rto_total_min(self) -> int:
        return sum(e.minutos for e in self.etapas)


def carregar(path: str) -> list[Cenario]:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    cenarios: list[Cenario] = []
    for c in data.get("cenarios", []):
        etapas = [Etapa(nome=e["nome"], minutos=int(e["minutos"]))
                  for e in c.get("etapas", [])]
        cenarios.append(Cenario(
            nome=c["nome"],
            rpo_fonte_min=int(c.get("rpo_fonte_min", 0)),
            etapas=etapas,
        ))
    return cenarios


def avaliar(c: Cenario, rpo_alvo: int, rto_alvo: int) -> tuple[str, str]:
    rpo_ok = c.rpo_fonte_min <= rpo_alvo
    rto_ok = c.rto_total_min <= rto_alvo
    rpo_label = "OK" if rpo_ok else f"EXCEDE (+{c.rpo_fonte_min - rpo_alvo}min)"
    rto_label = "OK" if rto_ok else f"EXCEDE (+{c.rto_total_min - rto_alvo}min)"
    return rpo_label, rto_label


def relatorio(cenarios: list[Cenario], rpo_alvo: int, rto_alvo: int) -> int:
    console = Console()
    algum_excede = False
    for c in cenarios:
        tbl = Table(title=f"Cenario: {c.nome}")
        for col in ("etapa", "minutos"):
            tbl.add_column(col)
        for e in c.etapas:
            tbl.add_row(e.nome, str(e.minutos))
        tbl.add_row("[b]TOTAL RTO[/b]", f"[b]{c.rto_total_min}[/b]")
        console.print(tbl)

        rpo_l, rto_l = avaliar(c, rpo_alvo, rto_alvo)
        console.print(f"RPO esperado: {c.rpo_fonte_min}min (alvo {rpo_alvo}) -> {rpo_l}")
        console.print(f"RTO esperado: {c.rto_total_min}min (alvo {rto_alvo}) -> {rto_l}\n")

        if "EXCEDE" in rpo_l or "EXCEDE" in rto_l:
            algum_excede = True

    return 1 if algum_excede else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("cenarios_yaml")
    p.add_argument("--rpo-alvo-min", type=int, default=15)
    p.add_argument("--rto-alvo-min", type=int, default=60)
    args = p.parse_args(argv)

    try:
        cenarios = carregar(args.cenarios_yaml)
    except (OSError, yaml.YAMLError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    if not cenarios:
        print("Nenhum cenario encontrado.")
        return 0

    return relatorio(cenarios, args.rpo_alvo_min, args.rto_alvo_min)


if __name__ == "__main__":
    raise SystemExit(main())

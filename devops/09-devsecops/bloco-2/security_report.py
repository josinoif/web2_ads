"""
security_report.py - consolida achados de seguranca em uma tabela unica.

Entende:
  - SARIF (Bandit, Semgrep, Trivy em modo SARIF)
  - JSON do pip-audit (--format json)

Uso:
    python security_report.py bandit.sarif semgrep.sarif pip-audit.json --fail-on high
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

SEV_RANK = {"none": 0, "note": 1, "low": 1, "medium": 2,
            "warning": 2, "high": 3, "error": 3, "critical": 4}


@dataclass(frozen=True)
class Achado:
    ferramenta: str
    id: str
    severidade: str
    alvo: str
    descricao: str


def carregar_sarif(path: str) -> list[Achado]:
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    out: list[Achado] = []
    for run in doc.get("runs", []):
        tool = ((run.get("tool") or {}).get("driver") or {}).get("name", "sarif")
        for res in run.get("results", []):
            lvl = res.get("level", res.get("properties", {}).get("severity", "warning")).lower()
            rid = res.get("ruleId", "?")
            loc = (res.get("locations") or [{}])[0].get("physicalLocation", {}).get("artifactLocation", {}).get("uri", "?")
            msg = (res.get("message") or {}).get("text", "")
            out.append(Achado(tool, rid, lvl, loc, msg))
    return out


def carregar_pip_audit(path: str) -> list[Achado]:
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    out: list[Achado] = []
    for dep in doc.get("dependencies", []):
        nome = dep.get("name")
        versao = dep.get("version")
        for v in dep.get("vulns", []):
            out.append(Achado(
                ferramenta="pip-audit",
                id=v.get("id", "?"),
                severidade=(v.get("aliases") and "medium") or "high",
                alvo=f"{nome}=={versao}",
                descricao=v.get("description", "")[:120],
            ))
    return out


def carregar(path: str) -> list[Achado]:
    if path.endswith(".sarif"):
        return carregar_sarif(path)
    if path.endswith(".json"):
        return carregar_pip_audit(path)
    raise ValueError(f"Formato nao suportado: {path}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("arquivos", nargs="+")
    p.add_argument("--fail-on", default="high", choices=list(SEV_RANK.keys()))
    args = p.parse_args(argv)

    limite = SEV_RANK[args.fail_on]
    todos: list[Achado] = []
    for f in args.arquivos:
        try:
            todos.extend(carregar(f))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"AVISO: nao consegui ler {f}: {exc}", file=sys.stderr)

    if not todos:
        print("Nenhum achado. (Arquivos vazios ou sem vulnerabilidades.)")
        return 0

    console = Console()
    tabela = Table(title="Relatorio consolidado de seguranca")
    for col in ("ferramenta", "severidade", "id", "alvo", "descricao"):
        tabela.add_column(col)
    for a in sorted(todos, key=lambda x: -SEV_RANK.get(x.severidade, 0)):
        tabela.add_row(a.ferramenta, a.severidade, a.id, a.alvo, a.descricao)
    console.print(tabela)

    piores = [a for a in todos if SEV_RANK.get(a.severidade, 0) >= limite]
    console.print(f"\nTotal: {len(todos)} | >= {args.fail_on}: {len(piores)}")
    return 0 if not piores else 1


if __name__ == "__main__":
    raise SystemExit(main())

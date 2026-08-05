"""
threat_catalog.py - cataloga e prioriza ameacas STRIDE a partir de YAML.

Formato YAML esperado:
    components:
      - name: auth
        flows: [login, refresh_token]
        threats:
          - id: T-001
            category: S  # Spoofing
            description: Credencial roubada via phishing
            likelihood: M  # L/M/H
            impact: H
            mitigations:
              - "MFA obrigatorio para perfis medicos"
            status: accepted # accepted/in-progress/mitigated

Uso:
    python threat_catalog.py threats.yaml
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

import yaml
from rich.console import Console
from rich.table import Table

CATEGORIAS = {"S": "Spoofing", "T": "Tampering", "R": "Repudiation",
              "I": "Info Disclosure", "D": "DoS", "E": "Elevation"}
SCORE = {"L": 1, "M": 2, "H": 3}


@dataclass(frozen=True)
class Ameaca:
    id: str
    componente: str
    categoria: str
    descricao: str
    likelihood: str
    impact: str
    mitigacoes: tuple[str, ...]
    status: str

    @property
    def risco(self) -> int:
        return SCORE.get(self.likelihood, 0) * SCORE.get(self.impact, 0)


def carregar(path: str) -> list[Ameaca]:
    with open(path, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    ameacas: list[Ameaca] = []
    for comp in doc.get("components", []):
        nome = comp.get("name", "?")
        for t in comp.get("threats", []):
            ameacas.append(
                Ameaca(
                    id=t.get("id", "?"),
                    componente=nome,
                    categoria=t.get("category", "?"),
                    descricao=t.get("description", ""),
                    likelihood=t.get("likelihood", "L"),
                    impact=t.get("impact", "L"),
                    mitigacoes=tuple(t.get("mitigations", [])),
                    status=t.get("status", "accepted"),
                )
            )
    return ameacas


def relatar(ameacas: list[Ameaca]) -> int:
    console = Console()
    tabela = Table(title="Catalogo de Ameacas (STRIDE)")
    for col in ("id", "componente", "categoria", "likelihood", "impact", "risco", "status", "descricao"):
        tabela.add_column(col)
    for a in sorted(ameacas, key=lambda x: -x.risco):
        cat = f"{a.categoria} - {CATEGORIAS.get(a.categoria, '?')}"
        tabela.add_row(a.id, a.componente, cat, a.likelihood, a.impact, str(a.risco), a.status, a.descricao)
    console.print(tabela)

    aberto_alto = [a for a in ameacas if a.risco >= 6 and a.status != "mitigated"]
    console.print(f"\nTotal ameacas: {len(ameacas)}")
    console.print(f"Alto risco em aberto (>=6 e nao mitigada): {len(aberto_alto)}")
    for a in aberto_alto:
        console.print(f"  - {a.id} [{a.componente}] {a.descricao} (status: {a.status})")
    return 0 if not aberto_alto else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Catalogo de ameacas STRIDE")
    p.add_argument("arquivo", help="YAML de ameacas")
    args = p.parse_args(argv)
    try:
        ameacas = carregar(args.arquivo)
    except (OSError, yaml.YAMLError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    if not ameacas:
        print("ERRO: nenhuma ameaca carregada", file=sys.stderr)
        return 2
    return relatar(ameacas)


if __name__ == "__main__":
    raise SystemExit(main())

"""
catalog_validator.py - valida um diretorio com catalog-info.yaml's e groups.

Espera estrutura:
    catalog/
      groups.yaml                     # lista kind: Group
      services/
        svc-a.yaml                    # kind: Component
        svc-b.yaml
      resources/
        db-a.yaml                     # kind: Resource

Regras:
- Todo Component tem owner no formato group:default/<nome>.
- owner deve existir em groups.yaml.
- lifecycle em {experimental, production, deprecated}.
- Se lifecycle == production: tags tem exatamente uma tag tier-{bronze,silver,gold}.
- dependsOn referencia entidade existente (component:/resource:).

Uso:
    python catalog_validator.py catalog/
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

import yaml
from rich.console import Console
from rich.table import Table

LIFECYCLES_VALIDAS = {"experimental", "production", "deprecated"}
TIERS_VALIDAS = {"tier-bronze", "tier-silver", "tier-gold"}


@dataclass(frozen=True)
class Achado:
    severidade: str
    entidade: str
    regra: str
    mensagem: str


def carregar_arquivos(raiz: str) -> list[dict]:
    docs: list[dict] = []
    for dirpath, _, files in os.walk(raiz):
        for f in files:
            if not f.endswith((".yaml", ".yml")):
                continue
            full = os.path.join(dirpath, f)
            try:
                with open(full, "r", encoding="utf-8") as fh:
                    for d in yaml.safe_load_all(fh):
                        if d:
                            d["__file__"] = full
                            docs.append(d)
            except (OSError, yaml.YAMLError) as exc:
                print(f"AVISO: {full}: {exc}", file=sys.stderr)
    return docs


def key(ent: dict) -> str:
    return f"{ent.get('kind', '?').lower()}:{(ent.get('metadata') or {}).get('name', '?')}"


def validar(docs: list[dict]) -> list[Achado]:
    achados: list[Achado] = []
    grupos = {
        (d.get("metadata") or {}).get("name")
        for d in docs if d.get("kind") == "Group"
    }
    existentes = {key(d) for d in docs if d.get("kind")}

    for d in docs:
        kind = d.get("kind")
        meta = d.get("metadata") or {}
        spec = d.get("spec") or {}
        nome = meta.get("name", "?")
        ent_label = f"{kind}/{nome}"

        if kind == "Component":
            owner = spec.get("owner", "")
            if not owner.startswith("group:"):
                achados.append(Achado("high", ent_label, "OWNER-FMT",
                                      "owner deve comecar com 'group:'"))
            else:
                grp = owner.split("/")[-1]
                if grp not in grupos:
                    achados.append(Achado("high", ent_label, "OWNER-UNK",
                                          f"grupo '{grp}' referenciado mas nao definido"))

            lifecycle = spec.get("lifecycle", "")
            if lifecycle not in LIFECYCLES_VALIDAS:
                achados.append(Achado("high", ent_label, "LIFECYCLE",
                                      f"lifecycle invalido: {lifecycle}"))

            tags = set(meta.get("tags", []) or [])
            tiers = tags & TIERS_VALIDAS
            if lifecycle == "production":
                if len(tiers) != 1:
                    achados.append(Achado("high", ent_label, "TIER-PROD",
                                          "production exige exatamente uma tag tier-{bronze,silver,gold}"))

            for ref in spec.get("dependsOn", []) or []:
                ref_norm = ref.replace("default/", "")
                if ref_norm.lower() not in existentes:
                    achados.append(Achado("medium", ent_label, "DEP-UNK",
                                          f"dependsOn '{ref}' nao encontrado no catalogo"))

    return achados


def relatorio(achados: list[Achado]) -> int:
    console = Console()
    if not achados:
        console.print("[green]Catalogo valido.[/]")
        return 0

    tbl = Table(title="Validacao de catalogo")
    for c in ("severidade", "entidade", "regra", "mensagem"):
        tbl.add_column(c)
    ordem = {"high": 3, "medium": 2, "low": 1}
    for a in sorted(achados, key=lambda x: (-ordem[x.severidade], x.entidade)):
        tbl.add_row(a.severidade, a.entidade, a.regra, a.mensagem)
    console.print(tbl)
    return 1 if any(a.severidade == "high" for a in achados) else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("dir")
    args = p.parse_args(argv)

    if not os.path.isdir(args.dir):
        print(f"ERRO: diretorio nao existe: {args.dir}", file=sys.stderr)
        return 2

    docs = carregar_arquivos(args.dir)
    achados = validar(docs)
    return relatorio(achados)


if __name__ == "__main__":
    raise SystemExit(main())

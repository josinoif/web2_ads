"""
template_audit.py - audita um Software Template (Backstage Scaffolder) para boas praticas.

Regras:
- metadata.description != vazio.
- tags nao vazio.
- spec.owner declarado.
- parameters com ao menos "name" e "owner".
- steps contem publish + catalog:register.
- output.entityRef presente.
- skeleton/catalog-info.yaml existe no diretorio do template.

Uso:
    python template_audit.py templates/python-fastapi-service
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

import yaml
from rich.console import Console
from rich.table import Table


@dataclass(frozen=True)
class Achado:
    severidade: str
    regra: str
    mensagem: str


def carregar_template(path_dir: str) -> dict:
    fpath = os.path.join(path_dir, "template.yaml")
    if not os.path.isfile(fpath):
        raise FileNotFoundError(f"template.yaml nao encontrado em {path_dir}")
    with open(fpath, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def auditar(template: dict, path_dir: str) -> list[Achado]:
    achados: list[Achado] = []

    meta = template.get("metadata", {}) or {}
    if not meta.get("description"):
        achados.append(Achado("high", "META-DESC",
                              "metadata.description obrigatoria para exibicao no portal"))
    if not meta.get("tags"):
        achados.append(Achado("low", "META-TAGS",
                              "metadata.tags vazio; dificulta descoberta"))

    spec = template.get("spec", {}) or {}
    if not spec.get("owner"):
        achados.append(Achado("high", "SPEC-OWNER",
                              "spec.owner obrigatorio para accountability"))

    params = spec.get("parameters", []) or []
    props_planas: set[str] = set()
    for grupo in params:
        props = (grupo or {}).get("properties", {}) or {}
        props_planas.update(props.keys())
    for obrigatorio in ("name", "owner"):
        if obrigatorio not in props_planas:
            achados.append(Achado("high", f"PARAM-{obrigatorio.upper()}",
                                  f"parametros devem ter '{obrigatorio}'"))

    steps = spec.get("steps", []) or []
    actions = {s.get("action") for s in steps if s}
    if not any(a and a.startswith("publish:") for a in actions):
        achados.append(Achado("high", "STEP-PUBLISH",
                              "falta step publish:* (github, gitlab...)"))
    if "catalog:register" not in actions:
        achados.append(Achado("high", "STEP-CATALOG",
                              "falta step catalog:register para aparecer no Software Catalog"))

    out = spec.get("output", {}) or {}
    links = out.get("links", []) or []
    if not any(l.get("entityRef") for l in links) and "entityRef" not in out:
        achados.append(Achado("medium", "OUTPUT-ENTITYREF",
                              "output sem entityRef; usuario nao volta para o catalogo"))

    skeleton_catalog = os.path.join(path_dir, "skeleton", "catalog-info.yaml")
    if not os.path.isfile(skeleton_catalog):
        achados.append(Achado("high", "SKEL-CATALOG",
                              "skeleton/catalog-info.yaml ausente; repositorio gerado nao entra no catalogo"))

    skeleton_readme = os.path.join(path_dir, "skeleton", "README.md")
    if not os.path.isfile(skeleton_readme):
        achados.append(Achado("medium", "SKEL-README",
                              "skeleton/README.md ausente; repositorio nasce sem docs"))

    return achados


def relatorio(achados: list[Achado], dir_alvo: str) -> int:
    console = Console()
    if not achados:
        console.print(f"[green]Template em {dir_alvo} passou na auditoria.[/]")
        return 0

    tbl = Table(title=f"Auditoria de template em {dir_alvo}")
    for c in ("severidade", "regra", "mensagem"):
        tbl.add_column(c)
    ordem = {"high": 3, "medium": 2, "low": 1}
    for a in sorted(achados, key=lambda x: -ordem[x.severidade]):
        tbl.add_row(a.severidade, a.regra, a.mensagem)
    console.print(tbl)
    return 1 if any(a.severidade == "high" for a in achados) else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("dir", help="Diretorio do template (contem template.yaml + skeleton/)")
    args = p.parse_args(argv)
    try:
        tpl = carregar_template(args.dir)
    except (FileNotFoundError, yaml.YAMLError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    achados = auditar(tpl, args.dir)
    return relatorio(achados, args.dir)


if __name__ == "__main__":
    raise SystemExit(main())

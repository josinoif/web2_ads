"""
chaos_plan.py - valida definicao de experimento chaos antes de aplicar.

Espera um YAML com dois documentos:
  1) Metadados do experimento (nao-Kubernetes):
     apiVersion: chaos.pagora/v1
     kind: Plan
     spec:
       hipotese: "..."
       blastRadius: { componente: "...", escala: "1 replica", janela: "5m" }
       steadyState:
         - { sli: "taxa 2xx", alvo: ">= 99.5%" }
       abort:
         - "SLI < 98% por 30s"
       responsavel: "alice@pagora"
       dataAprovacao: "2026-04-20"
  2) O manifesto Chaos Mesh de verdade.

Uso:
    python chaos_plan.py chaos/pod-kill.yaml
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass

import yaml
from rich.console import Console
from rich.table import Table

OBRIGATORIOS_SPEC = ["hipotese", "blastRadius", "steadyState", "abort", "responsavel"]
OBRIGATORIOS_BLAST = ["componente", "escala", "janela"]
CHAOSMESH_KINDS = {"PodChaos", "NetworkChaos", "StressChaos", "IOChaos",
                   "TimeChaos", "HTTPChaos", "DNSChaos", "Schedule", "Workflow"}


@dataclass(frozen=True)
class Achado:
    severidade: str
    regra: str
    mensagem: str


def carregar_documentos(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        docs = [d for d in yaml.safe_load_all(fh) if d]
    return docs


def encontrar(docs: list[dict]) -> tuple[dict | None, dict | None]:
    plano = None
    manifesto = None
    for d in docs:
        kind = d.get("kind")
        if kind == "Plan":
            plano = d
        elif kind in CHAOSMESH_KINDS:
            manifesto = d
    return plano, manifesto


def validar(plano: dict | None, manifesto: dict | None) -> list[Achado]:
    ach: list[Achado] = []
    if plano is None:
        ach.append(Achado("high", "PLAN-MISSING",
                          "Sem documento 'kind: Plan' com hipotese/blast/abort/responsavel."))
    if manifesto is None:
        ach.append(Achado("high", "CHAOS-MISSING",
                          f"Sem manifesto Chaos Mesh. Esperado kind em {sorted(CHAOSMESH_KINDS)}."))
    if plano is None:
        return ach

    spec = plano.get("spec", {}) or {}
    for campo in OBRIGATORIOS_SPEC:
        if campo not in spec:
            ach.append(Achado("high", f"SPEC-{campo.upper()}",
                              f"Plan.spec precisa do campo '{campo}'"))

    blast = spec.get("blastRadius", {}) or {}
    for campo in OBRIGATORIOS_BLAST:
        if campo not in blast:
            ach.append(Achado("medium", f"BLAST-{campo.upper()}",
                              f"blastRadius precisa do campo '{campo}'"))

    ss = spec.get("steadyState", []) or []
    if not ss:
        ach.append(Achado("medium", "STEADY-EMPTY",
                          "steadyState vazio: nenhum SLI para verificar."))

    abort = spec.get("abort", []) or []
    if not abort:
        ach.append(Achado("high", "ABORT-EMPTY",
                          "abort: sem criterios de parada, experimento nao e seguro."))

    resp = spec.get("responsavel", "")
    if not isinstance(resp, str) or "@" not in resp:
        ach.append(Achado("low", "RESP-INVALID",
                          "responsavel deve ser um contato (email)."))

    if manifesto is not None:
        dur = (manifesto.get("spec") or {}).get("duration")
        if dur is None and manifesto.get("kind") != "Schedule":
            ach.append(Achado("medium", "CHAOS-DURATION",
                              "Chaos sem 'duration' pode ficar preso. Adicione."))

    return ach


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("arquivo")
    args = p.parse_args(argv)
    try:
        docs = carregar_documentos(args.arquivo)
    except (OSError, yaml.YAMLError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    plano, manifesto = encontrar(docs)
    ach = validar(plano, manifesto)

    console = Console()
    if not ach:
        console.print("Experimento aparenta estar bem definido. Proceda com cautela.")
        return 0

    tbl = Table(title=f"Validacao de {args.arquivo}")
    for c in ("severidade", "regra", "mensagem"):
        tbl.add_column(c)
    ordem = {"high": 3, "medium": 2, "low": 1}
    for a in sorted(ach, key=lambda x: -ordem[x.severidade]):
        tbl.add_row(a.severidade, a.regra, a.mensagem)
    console.print(tbl)

    return 1 if any(a.severidade == "high" for a in ach) else 0


if __name__ == "__main__":
    raise SystemExit(main())

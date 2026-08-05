"""
capstone_checklist.py - valida presenca de artefatos do Capstone.

A validacao e estatica (presenca de arquivos/diretorios e, quando possivel,
leitura de conteudo minimo). Nao substitui a banca humana, mas oferece
autoavaliacao consistente.

Uso:
    python capstone_checklist.py <caminho-raiz-do-repo>

Saida:
    Tabela com cada checkpoint (severidade, categoria, status, detalhe).
    Exit code 0 se todos os "obrigatorios" passaram; 1 caso contrario.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console
from rich.table import Table


@dataclass(frozen=True)
class Checkpoint:
    obrigatorio: bool
    categoria: str
    descricao: str
    ok: bool
    detalhe: str = ""


def tem_arquivo(raiz: Path, *candidatos: str) -> tuple[bool, str]:
    for c in candidatos:
        p = raiz / c
        if p.is_file():
            return True, str(p.relative_to(raiz))
    return False, f"nenhum dos: {', '.join(candidatos)}"


def tem_diretorio(raiz: Path, *candidatos: str) -> tuple[bool, str]:
    for c in candidatos:
        p = raiz / c
        if p.is_dir():
            return True, str(p.relative_to(raiz))
    return False, f"nenhum dos: {', '.join(candidatos)}"


def conta_arquivos(raiz: Path, diretorio: str, padrao: str = "*") -> int:
    d = raiz / diretorio
    if not d.is_dir():
        return 0
    return sum(1 for _ in d.glob(padrao) if _.is_file())


def conteudo_contem(raiz: Path, arquivo: str, *termos: str) -> tuple[bool, str]:
    p = raiz / arquivo
    if not p.is_file():
        return False, "arquivo ausente"
    try:
        t = p.read_text(encoding="utf-8", errors="replace").lower()
    except OSError as exc:
        return False, f"erro de leitura: {exc}"
    faltando = [termo for termo in termos if termo.lower() not in t]
    if faltando:
        return False, f"faltando termos: {', '.join(faltando)}"
    return True, "ok"


def checar(raiz: Path) -> list[Checkpoint]:
    items: list[Checkpoint] = []

    # ---------- Marco 1: Design ----------
    ok, det = tem_arquivo(raiz, "README.md", "README.markdown")
    items.append(Checkpoint(True, "marco1:design", "README raiz", ok, det))

    ok, det = tem_arquivo(raiz, "LICENSE", "LICENSE.md", "LICENSE.txt")
    items.append(Checkpoint(True, "marco1:design", "LICENSE", ok, det))

    ok, det = tem_arquivo(raiz, ".gitignore")
    items.append(Checkpoint(True, "marco1:design", ".gitignore", ok, det))

    ok, det = tem_diretorio(raiz, "docs/adr")
    adr_count = conta_arquivos(raiz, "docs/adr", "*.md")
    items.append(Checkpoint(True, "marco1:design",
                            "ADRs (>= 5 em docs/adr/)",
                            ok and adr_count >= 5,
                            f"{adr_count} arquivos em docs/adr/"))

    ok, det = tem_diretorio(raiz, "docs/rfc", "docs/rfcs")
    items.append(Checkpoint(True, "marco1:design", "RFCs em docs/rfc/", ok, det))

    ok, det = tem_arquivo(raiz, "docs/charter.md", "docs/team-charter.md")
    items.append(Checkpoint(False, "marco1:design", "charter do projeto", ok, det))

    ok, det = tem_arquivo(raiz, "docs/arquitetura.md", "docs/architecture.md")
    items.append(Checkpoint(True, "marco1:design", "docs/arquitetura.md", ok, det))

    ok, det = tem_arquivo(raiz, ".github/workflows/ci.yml",
                          ".github/workflows/ci.yaml")
    items.append(Checkpoint(True, "marco1:design", "GitHub Actions CI", ok, det))

    ok, det = tem_arquivo(raiz, "Makefile")
    items.append(Checkpoint(False, "marco1:design", "Makefile com alvos", ok, det))

    # ---------- Marco 2: Entrega ----------
    ok, det = tem_arquivo(raiz, "services/api/Dockerfile",
                          "apps/api/Dockerfile", "api/Dockerfile", "Dockerfile")
    items.append(Checkpoint(True, "marco2:entrega", "Dockerfile hardened", ok, det))

    if ok:
        # heuristica: distroless + nonroot
        for candidato in ("services/api/Dockerfile", "apps/api/Dockerfile",
                          "api/Dockerfile", "Dockerfile"):
            p = raiz / candidato
            if p.is_file():
                texto = p.read_text(errors="replace").lower()
                bom = "distroless" in texto and "nonroot" in texto
                items.append(Checkpoint(
                    True, "marco2:entrega",
                    "Dockerfile usa distroless + nonroot",
                    bom,
                    "distroless+nonroot ok" if bom else "ausente - verifique hardening"))
                break

    ok, _ = tem_arquivo(raiz, ".github/workflows/ci.yml",
                        ".github/workflows/ci.yaml",
                        ".github/workflows/ci-cd.yml")
    if ok:
        for candidato in (".github/workflows/ci.yml", ".github/workflows/ci.yaml",
                          ".github/workflows/ci-cd.yml"):
            p = raiz / candidato
            if p.is_file():
                texto = p.read_text(errors="replace").lower()
                tem_cosign = "cosign" in texto
                tem_trivy = "trivy" in texto or "grype" in texto
                tem_sbom = "sbom" in texto or "syft" in texto
                items.append(Checkpoint(True, "marco2:entrega",
                                        "CI inclui Cosign + Trivy/Grype + SBOM",
                                        tem_cosign and tem_trivy and tem_sbom,
                                        f"cosign={tem_cosign} trivy={tem_trivy} sbom={tem_sbom}"))
                break

    ok, det = tem_diretorio(raiz, "infra/kubernetes/base", "k8s/base",
                            "deploy/k8s/base", "manifests/base")
    items.append(Checkpoint(True, "marco2:entrega",
                            "Manifests K8s base (Kustomize)", ok, det))

    ok, det = tem_diretorio(raiz, "infra/opentofu", "infra/terraform",
                            "infra/pulumi")
    items.append(Checkpoint(True, "marco2:entrega",
                            "IaC (OpenTofu/Terraform/Pulumi)", ok, det))

    # ---------- Marco 3: Operacao ----------
    ok, det = tem_arquivo(raiz, "docs/slos.md", "docs/slo.md",
                          "docs/slos/README.md")
    items.append(Checkpoint(True, "marco3:operacao", "SLOs declarados", ok, det))

    ok, det = tem_arquivo(raiz, "docs/ebp.md", "docs/error-budget-policy.md",
                          "docs/slos/ebp.md")
    items.append(Checkpoint(True, "marco3:operacao",
                            "Error Budget Policy", ok, det))

    ok, det = tem_diretorio(raiz, "docs/runbooks")
    runbooks = conta_arquivos(raiz, "docs/runbooks", "*.md")
    items.append(Checkpoint(True, "marco3:operacao",
                            "Runbooks (>= 3)",
                            ok and runbooks >= 3,
                            f"{runbooks} runbooks"))

    ok, det = tem_arquivo(raiz, "docs/security/threat-model.md",
                          "docs/threat-model.md")
    items.append(Checkpoint(True, "marco3:operacao",
                            "Threat model STRIDE", ok, det))

    ok, det = tem_diretorio(raiz, "infra/kyverno", "k8s/kyverno",
                            "policies/kyverno", "infra/kubernetes/kyverno")
    items.append(Checkpoint(True, "marco3:operacao",
                            "Policies Kyverno", ok, det))

    ok, det = tem_diretorio(raiz, "chaos")
    chaos_count = conta_arquivos(raiz, "chaos", "*.md") + conta_arquivos(raiz, "chaos", "*.yaml")
    items.append(Checkpoint(True, "marco3:operacao",
                            "Experimento(s) de Chaos",
                            ok and chaos_count >= 1,
                            f"{chaos_count} arquivos em chaos/"))

    ok, det = tem_arquivo(raiz, "docs/runbooks/dr-cluster-perdido.md",
                          "docs/dr.md", "docs/runbooks/dr.md")
    items.append(Checkpoint(True, "marco3:operacao", "DR playbook", ok, det))

    ok, det = tem_arquivo(raiz, "docs/postmortems/_TEMPLATE.md",
                          "docs/postmortem-template.md",
                          "docs/postmortems/template.md")
    items.append(Checkpoint(True, "marco3:operacao",
                            "Template de postmortem", ok, det))

    postmortems = conta_arquivos(raiz, "docs/postmortems", "*.md")
    items.append(Checkpoint(True, "marco3:operacao",
                            "Postmortem (>= 1 real/simulado)",
                            postmortems >= 2,
                            f"{postmortems} arquivos em docs/postmortems/ (inclui template)"))

    ok, det = tem_arquivo(raiz, "docs/lgpd/inventario-dados.md",
                          "docs/lgpd.md")
    items.append(Checkpoint(True, "marco3:operacao",
                            "Inventario LGPD", ok, det))

    # ---------- Marco 4: Plataforma ----------
    ok, det = tem_diretorio(raiz, "platform/catalog", "idp/catalog",
                            "backstage/catalog", "catalog")
    items.append(Checkpoint(True, "marco4:plataforma", "Software Catalog", ok, det))

    ok, det = tem_diretorio(raiz, "platform/templates", "backstage/templates",
                            "templates")
    items.append(Checkpoint(True, "marco4:plataforma", "Golden path template", ok, det))

    ok, det = tem_arquivo(raiz, "docs/dora-report.md",
                          "docs/metrics.md", "docs/metrics-report.md")
    items.append(Checkpoint(True, "marco4:plataforma", "DORA report", ok, det))

    ok, det = tem_arquivo(raiz, "docs/survey-capstone.md",
                          "docs/nps.md", "docs/survey.md")
    items.append(Checkpoint(False, "marco4:plataforma", "Survey/NPS", ok, det))

    ok, det = tem_arquivo(raiz, "docs/roadmap-pos.md",
                          "docs/platform-roadmap.md", "docs/roadmap.md")
    items.append(Checkpoint(True, "marco4:plataforma",
                            "Roadmap pos-capstone", ok, det))

    # ---------- Marco 5: Banca ----------
    ok, det = tem_arquivo(raiz, "docs/apresentacao.md",
                          "docs/pitch.md", "docs/presentation.md")
    items.append(Checkpoint(False, "marco5:banca", "Roteiro de apresentacao", ok, det))

    ok, det = tem_arquivo(raiz, "docs/banca-cenarios.md",
                          "docs/defense-scenarios.md")
    items.append(Checkpoint(False, "marco5:banca", "Cenarios da banca", ok, det))

    ok, det = tem_diretorio(raiz, "docs/retro")
    retros = conta_arquivos(raiz, "docs/retro", "*.md")
    items.append(Checkpoint(False, "marco5:banca",
                            "Retrospectivas dos marcos",
                            ok and retros >= 3,
                            f"{retros} retros em docs/retro/"))

    return items


def imprimir(items: list[Checkpoint]) -> int:
    console = Console()
    tbl = Table(title="Capstone checklist (static)")
    for c in ("obrigatorio", "categoria", "descricao", "status", "detalhe"):
        tbl.add_column(c)

    for i in items:
        status = "[green]ok[/]" if i.ok else ("[red]FALTA[/]" if i.obrigatorio else "[yellow]pend[/]")
        tbl.add_row(
            "sim" if i.obrigatorio else "bonus",
            i.categoria,
            i.descricao,
            status,
            i.detalhe,
        )
    console.print(tbl)

    obrig_falhas = [i for i in items if i.obrigatorio and not i.ok]
    total_obrig = sum(1 for i in items if i.obrigatorio)
    passou = total_obrig - len(obrig_falhas)

    console.print(f"\n{passou}/{total_obrig} obrigatorios atendidos.")
    if obrig_falhas:
        console.print("\n[red]Itens obrigatorios pendentes:[/]")
        for i in obrig_falhas:
            console.print(f"  - [{i.categoria}] {i.descricao} ({i.detalhe})")
        return 1
    console.print("[green]Pronto para autoavaliar na banca.[/]")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("raiz", nargs="?", default=".",
                    help="Caminho raiz do repositorio do capstone (default: .)")
    args = ap.parse_args(argv)
    raiz = Path(args.raiz).resolve()
    if not raiz.is_dir():
        print(f"ERRO: diretorio nao existe: {raiz}", file=sys.stderr)
        return 2
    items = checar(raiz)
    return imprimir(items)


if __name__ == "__main__":
    raise SystemExit(main())

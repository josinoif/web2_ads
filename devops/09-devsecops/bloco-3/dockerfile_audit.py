"""
dockerfile_audit.py - audita Dockerfile para boas praticas de seguranca.

Checa (independente de Trivy/Checkov):
  DOCK-001: usa :latest na FROM
  DOCK-002: nao define USER
  DOCK-003: instala pacotes comuns de ataque (curl, wget, nc, ssh, vim)
  DOCK-004: COPY . . sem .dockerignore visivel
  DOCK-005: sem HEALTHCHECK
  DOCK-006: sem LABEL org.opencontainers.image.source
  DOCK-007: usa ADD para URL remota
  DOCK-008: USER 0/root

Uso:
    python dockerfile_audit.py Dockerfile [--fail-on medium]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

SEV_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3}
PKGS_RISCO = {"curl", "wget", "netcat", "nc", "ssh", "openssh", "vim", "nano", "git"}


@dataclass(frozen=True)
class Issue:
    id: str
    linha: int
    severidade: str
    mensagem: str


def _escanear(dockerfile: str, base_dir: str) -> list[Issue]:
    linhas = dockerfile.splitlines()
    issues: list[Issue] = []

    tem_user = False
    usuario_ultimo = None
    tem_healthcheck = False
    tem_label_source = False

    for i, raw in enumerate(linhas, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        up = line.upper()

        if up.startswith("FROM "):
            m = re.match(r"FROM\s+([^\s]+)", line, re.I)
            if m and ":" in m.group(1) and m.group(1).endswith(":latest"):
                issues.append(Issue("DOCK-001", i, "high", f"FROM usa :latest ({m.group(1)})"))

        if up.startswith("USER "):
            tem_user = True
            usuario_ultimo = line.split()[1]
            if usuario_ultimo in ("0", "root"):
                issues.append(Issue("DOCK-008", i, "high", "USER root/0"))

        if up.startswith("RUN ") and ("apt-get install" in line or "apk add" in line):
            for p in PKGS_RISCO:
                if re.search(rf"\b{p}\b", line):
                    issues.append(Issue("DOCK-003", i, "medium",
                                        f"Instala pacote util a atacante: {p}"))

        if up.startswith("COPY "):
            partes = line.split()
            if len(partes) >= 2 and partes[1] == ".":
                dockerignore = os.path.join(base_dir, ".dockerignore")
                if not os.path.exists(dockerignore):
                    issues.append(Issue("DOCK-004", i, "medium",
                                        "COPY . . sem .dockerignore ao lado"))

        if up.startswith("HEALTHCHECK "):
            tem_healthcheck = True

        if up.startswith("LABEL ") and "org.opencontainers.image.source" in line:
            tem_label_source = True

        if up.startswith("ADD ") and re.search(r"https?://", line):
            issues.append(Issue("DOCK-007", i, "medium",
                                "ADD de URL remota (preferir RUN curl + verificacao)"))

    if not tem_user:
        issues.append(Issue("DOCK-002", 0, "high", "Dockerfile nao define USER explicitamente"))
    if not tem_healthcheck:
        issues.append(Issue("DOCK-005", 0, "low", "Sem HEALTHCHECK"))
    if not tem_label_source:
        issues.append(Issue("DOCK-006", 0, "low", "Sem LABEL org.opencontainers.image.source"))
    return issues


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("dockerfile")
    p.add_argument("--fail-on", default="high", choices=list(SEV_ORDER.keys()))
    args = p.parse_args(argv)

    try:
        with open(args.dockerfile, "r", encoding="utf-8") as fh:
            conteudo = fh.read()
    except OSError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    issues = _escanear(conteudo, base_dir=os.path.dirname(os.path.abspath(args.dockerfile)))

    console = Console()
    if not issues:
        console.print("Dockerfile passou em todas as checagens.")
        return 0

    tabela = Table(title=f"Auditoria {args.dockerfile}")
    for c in ("id", "linha", "severidade", "mensagem"):
        tabela.add_column(c)
    for iss in sorted(issues, key=lambda x: -SEV_ORDER[x.severidade]):
        tabela.add_row(iss.id, str(iss.linha), iss.severidade, iss.mensagem)
    console.print(tabela)

    lim = SEV_ORDER[args.fail_on]
    piores = [x for x in issues if SEV_ORDER[x.severidade] >= lim]
    console.print(f"\nTotal: {len(issues)} | >= {args.fail_on}: {len(piores)}")
    return 0 if not piores else 1


if __name__ == "__main__":
    raise SystemExit(main())

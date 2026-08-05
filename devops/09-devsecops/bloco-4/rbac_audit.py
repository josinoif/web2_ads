"""
rbac_audit.py - audita RBAC de um cluster Kubernetes.

Chama kubectl e analisa:
  RBAC-001: ServiceAccount com cluster-admin
  RBAC-002: Role/ClusterRole com verbo "*"
  RBAC-003: Role/ClusterRole com resource "*"
  RBAC-004: default SA usada por workloads (indicacao)

Uso:
    python rbac_audit.py [--namespace NS]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table


@dataclass(frozen=True)
class Achado:
    id: str
    severidade: str
    alvo: str
    descricao: str


def _kubectl_json(args: list[str]) -> dict:
    try:
        out = subprocess.check_output(["kubectl", *args, "-o", "json"],
                                      stderr=subprocess.STDOUT, timeout=30)
    except subprocess.CalledProcessError as exc:
        print(f"ERRO kubectl: {exc.output.decode(errors='replace')}", file=sys.stderr)
        sys.exit(2)
    return json.loads(out)


def _roles_por_nome(items: list[dict]) -> dict[str, dict]:
    return {it["metadata"]["name"]: it for it in items}


def auditar(namespace: str | None) -> list[Achado]:
    ach: list[Achado] = []

    crb = _kubectl_json(["get", "clusterrolebindings"])
    cr = _roles_por_nome(_kubectl_json(["get", "clusterroles"])["items"])

    rb_args = ["get", "rolebindings"]
    role_args = ["get", "roles"]
    if namespace:
        rb_args += ["-n", namespace]
        role_args += ["-n", namespace]
    else:
        rb_args += ["-A"]
        role_args += ["-A"]
    _ = _kubectl_json(rb_args)  # carregado para futura extensao
    r = _roles_por_nome(_kubectl_json(role_args)["items"])

    for item in crb.get("items", []):
        role_ref = item.get("roleRef", {})
        if role_ref.get("name") == "cluster-admin":
            for sub in item.get("subjects", []) or []:
                if sub.get("kind") == "ServiceAccount":
                    ach.append(Achado(
                        "RBAC-001", "high",
                        f"{sub.get('namespace','?')}/{sub.get('name','?')}",
                        f"SA tem cluster-admin via {item['metadata']['name']}"
                    ))

    for nome, role in {**cr, **r}.items():
        for rule in role.get("rules", []) or []:
            if "*" in (rule.get("verbs") or []):
                ach.append(Achado("RBAC-002", "medium", nome,
                                  f"regra com verbs=['*']: {rule}"))
            if "*" in (rule.get("resources") or []):
                ach.append(Achado("RBAC-003", "medium", nome,
                                  f"regra com resources=['*']: {rule}"))

    dep_args = ["get", "deployments"]
    if namespace:
        dep_args += ["-n", namespace]
    else:
        dep_args += ["-A"]
    deps = _kubectl_json(dep_args)
    for d in deps.get("items", []):
        md = d.get("metadata", {})
        sa = ((d.get("spec") or {}).get("template") or {}).get("spec", {}).get("serviceAccountName")
        if sa in (None, "", "default"):
            ach.append(Achado(
                "RBAC-004", "medium",
                f"{md.get('namespace','?')}/{md.get('name','?')}",
                "Deployment usa default ServiceAccount"
            ))
    return ach


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--namespace", default=None)
    args = p.parse_args(argv)

    ach = auditar(args.namespace)
    console = Console()
    if not ach:
        console.print("RBAC sem alertas encontrados.")
        return 0
    tabela = Table(title="Auditoria RBAC")
    for c in ("id", "severidade", "alvo", "descricao"):
        tabela.add_column(c)
    ordem = {"high": 3, "medium": 2, "low": 1, "info": 0}
    for a in sorted(ach, key=lambda x: -ordem[x.severidade]):
        tabela.add_row(a.id, a.severidade, a.alvo, a.descricao)
    console.print(tabela)
    return 1 if any(a.severidade == "high" for a in ach) else 0


if __name__ == "__main__":
    raise SystemExit(main())

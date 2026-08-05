"""
alerts_sanity.py - sanity check de PrometheusRule para higiene de alertas.

Uso:
    python alerts_sanity.py k8s/prometheusrules/*.yaml

Retorna codigo de saida != 0 se qualquer violacao for encontrada.
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from dataclasses import dataclass
from typing import Iterable

import yaml

SEVERIDADES = {"critical", "warning", "info"}
CAMPOS_ANNOT_OBRIGATORIOS = {"summary", "description", "runbook_url"}
FOR_MIN_MIN = 1
FOR_MAX_H = 1


@dataclass(frozen=True)
class Achado:
    arquivo: str
    alerta: str
    severidade: str
    motivo: str


def _for_em_minutos(texto: str) -> int:
    if not texto:
        return 0
    m = re.match(r"^(\d+)([smhd])$", texto.strip())
    if not m:
        return 0
    n, u = int(m.group(1)), m.group(2)
    mult = {"s": 1 / 60, "m": 1, "h": 60, "d": 1440}[u]
    return int(n * mult)


def auditar_arquivo(path: str) -> Iterable[Achado]:
    with open(path, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    if not doc or doc.get("kind") != "PrometheusRule":
        return
    groups = (doc.get("spec") or {}).get("groups") or []
    for grp in groups:
        for rule in grp.get("rules", []):
            alerta = rule.get("alert")
            if not alerta:
                continue
            labels = rule.get("labels", {}) or {}
            annots = rule.get("annotations", {}) or {}
            sev = labels.get("severity", "") or ""
            if sev not in SEVERIDADES:
                yield Achado(path, alerta, sev, f"severidade invalida ou ausente ({sev!r})")
            faltando = CAMPOS_ANNOT_OBRIGATORIOS - set(annots)
            if faltando:
                yield Achado(path, alerta, sev, f"annotation(s) faltando: {sorted(faltando)}")
            for_min = _for_em_minutos(rule.get("for", ""))
            if for_min and (for_min < FOR_MIN_MIN or for_min > FOR_MAX_H * 60):
                yield Achado(path, alerta, sev, f"campo 'for' fora do intervalo razoavel: {rule.get('for')}")


def tem_watchdog(paths: list[str]) -> bool:
    for p in paths:
        with open(p, "r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        groups = (doc.get("spec") or {}).get("groups") or []
        for grp in groups:
            for rule in grp.get("rules", []):
                if rule.get("alert") == "Watchdog":
                    return True
    return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Sanity check de PrometheusRule")
    p.add_argument("paths", nargs="+", help="arquivos YAML (ou globs)")
    args = p.parse_args(argv)

    arquivos: list[str] = []
    for padrao in args.paths:
        arquivos.extend(glob.glob(padrao))
    if not arquivos:
        print("ERRO: nenhum arquivo encontrado", file=sys.stderr)
        return 2

    achados: list[Achado] = []
    for f in arquivos:
        achados.extend(auditar_arquivo(f))

    if not tem_watchdog(arquivos):
        achados.append(Achado("(global)", "Watchdog", "info", "nenhuma regra Watchdog encontrada"))

    for a in achados:
        print(f"[{a.severidade or '-'}] {a.arquivo}::{a.alerta} -> {a.motivo}")

    print(f"\nTotal achados: {len(achados)}")
    return 0 if not achados else 1


if __name__ == "__main__":
    raise SystemExit(main())

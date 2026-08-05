"""
platform_metrics.py - calcula DORA e NPS da plataforma.

Entrada:
  deployments.csv: data,squad,status  (status in {success,failed,rolled-back})
  leadtime.csv:    commit_at,deploy_at (ISO8601)
  incidents.csv:   detect_at,restore_at (ISO8601)
  survey.csv:      respondente,score_nps (0-10)

Uso:
  python platform_metrics.py --deployments d.csv --leadtime lt.csv \
      --incidents inc.csv --survey s.csv
"""
from __future__ import annotations

import argparse
import csv
import statistics
import sys
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table


def ler_csv(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def classificar_dora(df_per_week: float, lead_time_days: float, cfr: float, mttr_hours: float) -> str:
    if df_per_week >= 7 and lead_time_days < 1 and cfr < 0.15 and mttr_hours < 1:
        return "Elite"
    if df_per_week >= 1 and lead_time_days < 7 and cfr < 0.30 and mttr_hours < 24:
        return "High"
    if df_per_week >= 0.25 and lead_time_days < 30 and cfr < 0.30 and mttr_hours < 168:
        return "Medium"
    return "Low"


def calc_deploy_freq(deploys: list[dict]) -> tuple[float, dict[str, float]]:
    successes = [d for d in deploys if d["status"] == "success"]
    if not successes:
        return 0.0, {}
    datas = [datetime.fromisoformat(d["data"]) for d in successes]
    semanas = max((max(datas) - min(datas)).days / 7.0, 1.0)
    por_squad: dict[str, int] = {}
    for d in successes:
        por_squad[d["squad"]] = por_squad.get(d["squad"], 0) + 1
    return len(successes) / semanas, {k: v / semanas for k, v in por_squad.items()}


def calc_lead_time_days(rows: list[dict]) -> float:
    leads = []
    for r in rows:
        c = datetime.fromisoformat(r["commit_at"])
        d = datetime.fromisoformat(r["deploy_at"])
        leads.append((d - c).total_seconds() / 86400)
    return statistics.median(leads) if leads else 0.0


def calc_cfr(deploys: list[dict]) -> float:
    if not deploys:
        return 0.0
    fails = sum(1 for d in deploys if d["status"] in {"failed", "rolled-back"})
    return fails / len(deploys)


def calc_mttr_hours(rows: list[dict]) -> float:
    if not rows:
        return 0.0
    tempos = []
    for r in rows:
        a = datetime.fromisoformat(r["detect_at"])
        b = datetime.fromisoformat(r["restore_at"])
        tempos.append((b - a).total_seconds() / 3600)
    return statistics.median(tempos)


def calc_nps(rows: list[dict]) -> tuple[float, int, int, int]:
    scores = [int(r["score_nps"]) for r in rows]
    if not scores:
        return 0.0, 0, 0, 0
    promotores = sum(1 for s in scores if s >= 9)
    passivos = sum(1 for s in scores if 7 <= s <= 8)
    detratores = sum(1 for s in scores if s <= 6)
    total = len(scores)
    nps = 100 * (promotores / total - detratores / total)
    return nps, promotores, passivos, detratores


def relatorio(args) -> int:
    console = Console()

    deploys = ler_csv(args.deployments)
    df, por_squad = calc_deploy_freq(deploys)
    lead = calc_lead_time_days(ler_csv(args.leadtime))
    cfr = calc_cfr(deploys)
    mttr = calc_mttr_hours(ler_csv(args.incidents))
    classe = classificar_dora(df, lead, cfr, mttr)

    tbl = Table(title="DORA (agregado)")
    for c in ("metrica", "valor"):
        tbl.add_column(c)
    tbl.add_row("Deploy Frequency (deploys/semana)", f"{df:.2f}")
    tbl.add_row("Lead Time (dias, mediana)", f"{lead:.2f}")
    tbl.add_row("Change Failure Rate", f"{cfr*100:.1f}%")
    tbl.add_row("MTTR (horas, mediana)", f"{mttr:.2f}")
    tbl.add_row("Classe DORA", classe)
    console.print(tbl)

    if por_squad:
        t2 = Table(title="Deploy Frequency por squad")
        for c in ("squad", "deploys/semana"):
            t2.add_column(c)
        for squad, v in sorted(por_squad.items(), key=lambda kv: -kv[1]):
            t2.add_row(squad, f"{v:.2f}")
        console.print(t2)

    if args.survey and Path(args.survey).exists():
        nps, p, pa, d = calc_nps(ler_csv(args.survey))
        t3 = Table(title="NPS Interno")
        for c in ("faixa", "quantidade"):
            t3.add_column(c)
        t3.add_row("Promotores (9-10)", str(p))
        t3.add_row("Passivos (7-8)", str(pa))
        t3.add_row("Detratores (0-6)", str(d))
        t3.add_row("NPS", f"{nps:+.1f}")
        console.print(t3)

    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deployments", required=True)
    ap.add_argument("--leadtime", required=True)
    ap.add_argument("--incidents", required=True)
    ap.add_argument("--survey", default="")
    args = ap.parse_args(argv)
    try:
        return relatorio(args)
    except OSError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

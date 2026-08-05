"""
incident_timeline.py - constroi timeline de incidente e calcula MTTR + fases.

Entrada: CSV com colunas timestamp,ator,fase,evento
Fases esperadas (padrao): detect, ack, investigate, mitigate, resolve

    timestamp,ator,fase,evento
    2026-03-09T14:18:00,CI,detect,deploy iniciou
    2026-03-09T14:19:30,monitor,detect,alerta p99 dispara
    2026-03-09T14:21:00,bob,ack,on-call reconhece
    2026-03-09T14:38:00,alice,investigate,cto chama dev da migracao
    2026-03-09T14:55:00,bob,mitigate,pg_terminate_backend executado
    2026-03-09T15:00:00,monitor,resolve,SLI volta ao normal

Uso:
    python incident_timeline.py incident.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta

from rich.console import Console
from rich.table import Table


FASES_ORDEM = ["detect", "ack", "investigate", "mitigate", "resolve"]


@dataclass(frozen=True)
class Evento:
    ts: datetime
    ator: str
    fase: str
    descricao: str


def parse_ts(s: str) -> datetime:
    s = s.strip()
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")


def carregar(path: str) -> list[Evento]:
    eventos: list[Evento] = []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        leitor = csv.DictReader(fh)
        for row in leitor:
            try:
                eventos.append(Evento(
                    ts=parse_ts(row["timestamp"]),
                    ator=row["ator"].strip(),
                    fase=row["fase"].strip().lower(),
                    descricao=row["evento"].strip(),
                ))
            except (KeyError, ValueError) as exc:
                print(f"AVISO: linha invalida: {row} ({exc})", file=sys.stderr)
    eventos.sort(key=lambda e: e.ts)
    return eventos


def primeira_ocorrencia(eventos: list[Evento], fase: str) -> datetime | None:
    for e in eventos:
        if e.fase == fase:
            return e.ts
    return None


def fmt_delta(d: timedelta | None) -> str:
    if d is None:
        return "-"
    total = int(d.total_seconds())
    h, rest = divmod(total, 3600)
    m, s = divmod(rest, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def relatorio(eventos: list[Evento]) -> int:
    if not eventos:
        print("Sem eventos.")
        return 0

    console = Console()

    tbl = Table(title=f"Timeline do incidente ({len(eventos)} eventos)")
    for c in ("timestamp", "fase", "ator", "evento"):
        tbl.add_column(c)
    for e in eventos:
        tbl.add_row(e.ts.isoformat(), e.fase, e.ator, e.descricao)
    console.print(tbl)

    inicio = primeira_ocorrencia(eventos, "detect") or eventos[0].ts
    ack = primeira_ocorrencia(eventos, "ack")
    mitigate = primeira_ocorrencia(eventos, "mitigate")
    resolve = primeira_ocorrencia(eventos, "resolve")

    tbl2 = Table(title="Metricas de incidente")
    for c in ("metrica", "valor", "descricao"):
        tbl2.add_column(c)
    tbl2.add_row("MTTA (tempo ate ack)",
                 fmt_delta((ack - inicio) if ack else None),
                 "Velocidade de deteccao humana")
    tbl2.add_row("MTTM (tempo ate mitigacao)",
                 fmt_delta((mitigate - inicio) if mitigate else None),
                 "Ate primeira acao corretiva")
    tbl2.add_row("MTTR (tempo ate resolucao)",
                 fmt_delta((resolve - inicio) if resolve else None),
                 "Fim do incidente")
    console.print(tbl2)

    fases_presentes = {e.fase for e in eventos}
    faltantes = [f for f in FASES_ORDEM if f not in fases_presentes]
    if faltantes:
        console.print(f"\n[yellow]Fases ausentes na timeline: {', '.join(faltantes)}[/yellow]")
        console.print("Dica: toda timeline de Sev-1/2 deveria cobrir todas as fases.")
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("csv")
    args = p.parse_args(argv)
    try:
        eventos = carregar(args.csv)
    except OSError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    return relatorio(eventos)


if __name__ == "__main__":
    raise SystemExit(main())

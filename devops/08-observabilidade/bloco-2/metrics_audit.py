"""
metrics_audit.py - auditor de cardinalidade de um endpoint /metrics.

Uso:
    python metrics_audit.py --url http://localhost:8000/metrics --top 15

Lista as metricas com mais series e aponta candidatas a revisao.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from urllib.parse import urlparse

import requests
from rich.console import Console
from rich.table import Table

LIMITE_SAUDAVEL = 100
LIMITE_ATENCAO = 1000


def parse_metrics(texto: str) -> list[tuple[str, str]]:
    """Retorna lista de (nome_metrica, linha_labels)."""
    saida: list[tuple[str, str]] = []
    for raw in texto.splitlines():
        if not raw or raw.startswith("#"):
            continue
        linha = raw.split(" ", 1)[0]
        if "{" in linha:
            nome = linha.split("{", 1)[0]
            labels = linha[linha.index("{"):]
        else:
            nome = linha
            labels = "{}"
        saida.append((nome, labels))
    return saida


def classificar(qtde: int) -> str:
    if qtde <= LIMITE_SAUDAVEL:
        return "ok"
    if qtde <= LIMITE_ATENCAO:
        return "atencao"
    return "alerta"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Auditor de cardinalidade de metricas Prometheus")
    p.add_argument("--url", required=True, help="URL do /metrics")
    p.add_argument("--top", type=int, default=15)
    args = p.parse_args(argv)

    parsed = urlparse(args.url)
    if parsed.scheme not in ("http", "https"):
        print("ERRO: URL deve comecar com http:// ou https://", file=sys.stderr)
        return 2

    try:
        resp = requests.get(args.url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"ERRO ao buscar {args.url}: {exc}", file=sys.stderr)
        return 2

    pares = parse_metrics(resp.text)
    contagem: Counter[str] = Counter()
    for nome, _ in pares:
        contagem[nome] += 1

    console = Console()
    tabela = Table(title=f"Cardinalidade por metrica (top {args.top})")
    tabela.add_column("Metrica")
    tabela.add_column("Series", justify="right")
    tabela.add_column("Status")
    for nome, qtde in contagem.most_common(args.top):
        tabela.add_row(nome, str(qtde), classificar(qtde))

    console.print(tabela)
    total = sum(contagem.values())
    console.print(f"[bold]Total de series:[/bold] {total}")
    alerta = sum(1 for n, q in contagem.items() if q > LIMITE_ATENCAO)
    if alerta:
        console.print(f"[red]{alerta} metrica(s) com cardinalidade > {LIMITE_ATENCAO}[/red]")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

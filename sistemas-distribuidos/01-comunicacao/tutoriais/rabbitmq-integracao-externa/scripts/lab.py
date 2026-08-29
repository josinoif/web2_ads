"""
Cliente HTTP do tutorial (só biblioteca padrão).

Rode DENTRO do container da API — assim o comando é igual no Windows e no Linux:

    docker compose exec -T api python lab.py ajuda

O -T evita o erro de TTY no PowerShell. Isto NÃO é o portal: é só um atalho
para não depender de curl/aspas de JSON no host.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request

# Dentro do container a API é localhost:8000; o emissor é o hostname do Compose
API = os.environ.get("LAB_API_URL", "http://127.0.0.1:8000")
EMISSOR = os.environ.get("LAB_EMISSOR_URL", "http://emissor:8000")

AJUDA = """
Comandos (Linux e Windows — sempre com: docker compose exec -T api python lab.py …)

  health                         API + emissor
  sincrono <aluno>               POST /matriculas/sincrono (a dor)
  enviar <aluno>                 POST /matriculas (202 + fila)
  lote [n]                       várias matrículas (padrão 8)
  status <matricula_id>          GET /matriculas/{id}
  fila                           GET /fila
  registros                      GET no emissor (o sistema de fora)
  acompanhar <matricula_id>      poll até concluido / na_dlq / erro
  veneno                         aluno que sempre toma 500 → DLQ
  esperar-processando <id>       poll até processando (antes do kill)

Kill do worker (também igual nos dois SOs):

  docker compose kill worker
  docker compose up -d worker
""".strip()


def _print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _request(method: str, url: str, body: dict | None = None, timeout: float = 30) -> tuple[int, dict | list]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            dados: dict | list = json.loads(raw) if raw else {}
            return resp.status, dados
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            dados = json.loads(raw) if raw else {"erro": raw}
        except json.JSONDecodeError:
            dados = {"erro": raw}
        return exc.code, dados


def _mostrar(code: int, dados: dict | list) -> dict | list:
    print(f"HTTP {code}")
    _print_json(dados)
    return dados


def cmd_health(_args: list[str]) -> int:
    print("--- api ---")
    _mostrar(*_request("GET", f"{API}/health"))
    print("--- emissor ---")
    _mostrar(*_request("GET", f"{EMISSOR}/health"))
    return 0


def cmd_sincrono(args: list[str]) -> int:
    """Passo 1: o aluno espera o emissor. tempo_total_s deve ser ~3."""
    aluno = args[0] if args else "estavel-maria"
    print(f"(demora ~3s — o portal espera o emissor; aluno={aluno})")
    inicio = time.perf_counter()
    code, dados = _request("POST", f"{API}/matriculas/sincrono", {"aluno": aluno}, timeout=40)
    print(f"tempo_total_s={round(time.perf_counter() - inicio, 2)}")
    _mostrar(code, dados)
    return 0 if code < 400 else 1


def cmd_enviar(args: list[str]) -> int:
    """Passo 2: 202 rápido; a carteirinha ainda não existe."""
    aluno = args[0] if args else "estavel-ana"
    inicio = time.perf_counter()
    code, dados = _request("POST", f"{API}/matriculas", {"aluno": aluno})
    print(f"tempo_total_s={round(time.perf_counter() - inicio, 2)}")
    _mostrar(code, dados)
    if isinstance(dados, dict) and dados.get("matricula_id"):
        print(f"matricula_id={dados['matricula_id']}")
    return 0 if code < 400 else 1


def cmd_lote(args: list[str]) -> int:
    n = int(args[0]) if args else 8
    inicio = time.perf_counter()
    code, dados = _request("POST", f"{API}/matriculas/lote?n={n}", {})
    print(f"tempo_total_s={round(time.perf_counter() - inicio, 2)}")
    _mostrar(code, dados)
    return 0 if code < 400 else 1


def cmd_status(args: list[str]) -> int:
    if not args:
        print("informe o matricula_id", file=sys.stderr)
        return 2
    code, dados = _request("GET", f"{API}/matriculas/{args[0]}")
    _mostrar(code, dados)
    return 0 if code < 400 else 1


def cmd_fila(_args: list[str]) -> int:
    code, dados = _request("GET", f"{API}/fila")
    _mostrar(code, dados)
    return 0 if code < 400 else 1


def cmd_registros(_args: list[str]) -> int:
    """Lista o que o MOCK do emissor gravou (evidência do sistema de fora)."""
    code, dados = _request("GET", f"{EMISSOR}/registros")
    _mostrar(code, dados)
    return 0 if code < 400 else 1


def cmd_acompanhar(args: list[str]) -> int:
    """Consulta o status a cada 1 s até terminar (ou 50 s)."""
    if not args:
        print("informe o matricula_id", file=sys.stderr)
        return 2
    mid = args[0]
    ultimo: dict | list = {}
    for i in range(1, 51):
        code, dados = _request("GET", f"{API}/matriculas/{mid}")
        status = dados.get("status", "?") if isinstance(dados, dict) else "?"
        print(f"[{i}] HTTP {code} status={status}")
        ultimo = dados
        if status in {"concluido", "na_dlq", "erro"}:
            _print_json(dados)
            return 0
        time.sleep(1)
    print("timeout")
    _print_json(ultimo)
    return 1


def cmd_veneno(_args: list[str]) -> int:
    """Passo 6: aluno que o emissor recusa sempre → DLQ após 3 tentativas."""
    rc = cmd_enviar(["veneno"])
    print("Acompanhe até na_dlq (~9s: 3 tentativas × 3s):")
    print("  docker compose exec -T api python lab.py acompanhar <matricula_id>")
    return rc


def cmd_esperar_processando(args: list[str]) -> int:
    """Passo 5: espera o worker entrar no HTTP de 3 s; aí você mata o container."""
    if not args:
        print("informe o matricula_id", file=sys.stderr)
        return 2
    mid = args[0]
    for i in range(1, 41):
        code, dados = _request("GET", f"{API}/matriculas/{mid}")
        status = dados.get("status", "?") if isinstance(dados, dict) else "?"
        print(f"[{i}] status={status}")
        if status == "processando":
            _print_json(dados)
            print("Agora, no mesmo terminal (Linux ou Windows):")
            print("  docker compose kill worker")
            return 0
        if status in {"concluido", "na_dlq", "erro"}:
            print("já terminou — envie de novo: python lab.py enviar teste-kill")
            return 1
        time.sleep(0.4)
    print("timeout esperando processando")
    return 1


def cmd_ajuda(_args: list[str]) -> int:
    print(AJUDA)
    return 0


COMANDOS = {
    "ajuda": cmd_ajuda,
    "help": cmd_ajuda,
    "health": cmd_health,
    "sincrono": cmd_sincrono,
    "enviar": cmd_enviar,
    "lote": cmd_lote,
    "status": cmd_status,
    "fila": cmd_fila,
    "registros": cmd_registros,
    "acompanhar": cmd_acompanhar,
    "veneno": cmd_veneno,
    "esperar-processando": cmd_esperar_processando,
}


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        return cmd_ajuda([])
    nome = sys.argv[1]
    fn = COMANDOS.get(nome)
    if fn is None:
        print(f"comando desconhecido: {nome}", file=sys.stderr)
        cmd_ajuda([])
        return 2
    return fn(sys.argv[2:])


if __name__ == "__main__":
    raise SystemExit(main())

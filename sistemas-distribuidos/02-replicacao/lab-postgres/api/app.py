"""
API do portal de notas — demonstra escrita no primary e leitura no primary ou na réplica.

Endpoints pensados para os experimentos do tutorial-postgres.md.
"""

from __future__ import annotations

import json
import os
import time
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import psycopg2
import psycopg2.extras

PORT = int(os.environ.get("PORT", "8000"))
PRIMARY_DSN = os.environ.get(
    "PRIMARY_DSN",
    "host=postgres-primary port=5432 dbname=portal user=portal password=portal",
)
REPLICA_DSN = os.environ.get(
    "REPLICA_DSN",
    "host=postgres-replica port=5432 dbname=portal user=portal password=portal",
)


def esperar_banco(dsn: str, rotulo: str, tentativas: int = 90) -> None:
    ultimo: Exception | None = None
    for _ in range(tentativas):
        try:
            with conectar(dsn) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            print(f"[api] {rotulo} ok", flush=True)
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            time.sleep(2)
    raise SystemExit(f"{rotulo} indisponível: {ultimo}")


@contextmanager
def conectar(dsn: str):
    conn = psycopg2.connect(dsn)
    try:
        yield conn
    finally:
        conn.close()


def dsn_destino(dest: str) -> tuple[str, str]:
    if dest == "replica":
        return REPLICA_DSN, "replica"
    return PRIMARY_DSN, "primary"


def upsert_nota(aluno_id: str, disciplina: str, valor: float) -> dict:
    sql = """
        INSERT INTO notas (aluno_id, disciplina, valor, atualizado_em)
        VALUES (%s, %s, %s, NOW())
        ON CONFLICT (aluno_id, disciplina)
        DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = NOW()
        RETURNING id, aluno_id, disciplina, valor, atualizado_em
    """
    with conectar(PRIMARY_DSN) as conn:
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (aluno_id, disciplina, valor))
            row = cur.fetchone()
    out = dict(row)
    out["valor"] = float(out["valor"])
    out["atualizado_em"] = out["atualizado_em"].isoformat()
    out["destino_escrita"] = "primary"
    return out


def listar_notas(aluno_id: str, dest: str) -> dict:
    dsn, rotulo = dsn_destino(dest)
    sql = """
        SELECT id, aluno_id, disciplina, valor, atualizado_em
        FROM notas
        WHERE aluno_id = %s
        ORDER BY disciplina
    """
    with conectar(dsn) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if dest == "replica":
                cur.execute("SELECT pg_is_in_recovery() AS em_recovery")
                recovery = bool(cur.fetchone()["em_recovery"])
            else:
                recovery = False
            cur.execute(sql, (aluno_id,))
            rows = cur.fetchall()
    notas = []
    for row in rows:
        item = dict(row)
        item["valor"] = float(item["valor"])
        item["atualizado_em"] = item["atualizado_em"].isoformat()
        notas.append(item)
    return {
        "aluno_id": aluno_id,
        "destino_leitura": rotulo,
        "em_recovery": recovery,
        "total": len(notas),
        "notas": notas,
    }


def lag_replicacao() -> dict:
    sql = """
        SELECT
            application_name,
            state,
            sync_state,
            pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes,
            EXTRACT(EPOCH FROM (NOW() - reply_time)) AS reply_lag_s
        FROM pg_stat_replication
    """
    with conectar(PRIMARY_DSN) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            replicas = [dict(r) for r in cur.fetchall()]
    for r in replicas:
        if r.get("lag_bytes") is not None:
            r["lag_bytes"] = int(r["lag_bytes"])
        if r.get("reply_lag_s") is not None:
            r["reply_lag_s"] = float(r["reply_lag_s"])
    return {"replicas": replicas}


def status_replicacao() -> dict:
    primary = {"role": "primary", "em_recovery": False}
    replica = {"role": "replica", "em_recovery": None, "ok": False}
    with conectar(PRIMARY_DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT pg_is_in_recovery()")
            primary["em_recovery"] = bool(cur.fetchone()[0])
    try:
        with conectar(REPLICA_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_is_in_recovery()")
                replica["em_recovery"] = bool(cur.fetchone()[0])
                replica["ok"] = True
    except Exception as exc:  # noqa: BLE001
        replica["erro"] = str(exc)
    return {"primary": primary, "replica": replica}


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)

        if path == "/health":
            self._json(200, {"ok": True, "servico": "api-notas-postgres"})
            return

        if path == "/replicacao/lag":
            self._json(200, lag_replicacao())
            return

        if path == "/replicacao/status":
            self._json(200, status_replicacao())
            return

        if path.startswith("/notas/"):
            aluno_id = path.removeprefix("/notas/").strip("/")
            dest = query.get("dest", ["primary"])[0]
            if dest not in ("primary", "replica"):
                self._json(400, {"erro": "dest deve ser primary ou replica"})
                return
            try:
                self._json(200, listar_notas(aluno_id, dest))
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc), "destino_leitura": dest})
            return

        self._json(
            200,
            {
                "endpoints": [
                    "POST /notas",
                    "GET /notas/{aluno_id}?dest=primary|replica",
                    "GET /replicacao/lag",
                    "GET /replicacao/status",
                    "GET /health",
                ]
            },
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") != "/notas":
            self._json(404, {"erro": "rota não encontrada"})
            return
        body = self._read_json()
        try:
            aluno_id = body["aluno_id"]
            disciplina = body["disciplina"]
            valor = float(body["valor"])
        except (KeyError, TypeError, ValueError):
            self._json(400, {"erro": "corpo esperado: aluno_id, disciplina, valor"})
            return
        try:
            self._json(201, upsert_nota(aluno_id, disciplina, valor))
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc)})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_banco(PRIMARY_DSN, "primary")
    # réplica pode demorar no primeiro boot
    for i in range(60):
        try:
            esperar_banco(REPLICA_DSN, "replica", tentativas=1)
            break
        except SystemExit:
            if i == 59:
                print("[api] aviso: réplica ainda não pronta — API sobe mesmo assim", flush=True)
            time.sleep(2)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

"""
API — compara escrita com replicação async vs sync (Postgres).

Mede latência do commit e expõe sync_state de pg_stat_replication.
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
MODO_LAB = os.environ.get("MODO_LAB", "async")


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
def conectar(dsn: str, connect_timeout: int = 30):
    conn = psycopg2.connect(dsn, connect_timeout=connect_timeout)
    try:
        yield conn
    finally:
        conn.close()


def upsert_nota(aluno_id: str, disciplina: str, valor: float) -> dict:
    sql = """
        INSERT INTO notas (aluno_id, disciplina, valor, atualizado_em)
        VALUES (%s, %s, %s, NOW())
        ON CONFLICT (aluno_id, disciplina)
        DO UPDATE SET valor = EXCLUDED.valor, atualizado_em = NOW()
        RETURNING id, aluno_id, disciplina, valor, atualizado_em
    """
    inicio = time.perf_counter()
    with conectar(PRIMARY_DSN, connect_timeout=120) as conn:
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (aluno_id, disciplina, valor))
            row = cur.fetchone()
    duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
    out = dict(row)
    out["valor"] = float(out["valor"])
    out["atualizado_em"] = out["atualizado_em"].isoformat()
    out["duracao_commit_ms"] = duracao_ms
    out["modo_lab"] = MODO_LAB
    return out


def ler_nota_replica(aluno_id: str, disciplina: str) -> dict | None:
    sql = """
        SELECT valor, atualizado_em
        FROM notas
        WHERE aluno_id = %s AND disciplina = %s
    """
    with conectar(REPLICA_DSN) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (aluno_id, disciplina))
            row = cur.fetchone()
    if not row:
        return None
    return {
        "valor": float(row["valor"]),
        "atualizado_em": row["atualizado_em"].isoformat(),
    }


def status_replicacao() -> dict:
    sql_lag = """
        SELECT
            application_name,
            state,
            sync_state,
            pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
        FROM pg_stat_replication
    """
    sql_settings = """
        SELECT name, setting
        FROM pg_settings
        WHERE name IN (
            'synchronous_commit',
            'synchronous_standby_names',
            'synchronous_replication'
        )
    """
    with conectar(PRIMARY_DSN) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql_lag)
            replicas = [dict(r) for r in cur.fetchall()]
            cur.execute(sql_settings)
            settings = {r["name"]: r["setting"] for r in cur.fetchall()}
    for r in replicas:
        if r.get("lag_bytes") is not None:
            r["lag_bytes"] = int(r["lag_bytes"])
    replica_ok = False
    try:
        with conectar(REPLICA_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_is_in_recovery()")
                replica_ok = bool(cur.fetchone()[0])
    except Exception as exc:  # noqa: BLE001
        return {
            "modo_lab": MODO_LAB,
            "replicas": replicas,
            "settings": settings,
            "replica_acessivel": False,
            "replica_erro": str(exc),
        }
    return {
        "modo_lab": MODO_LAB,
        "replicas": replicas,
        "settings": settings,
        "replica_acessivel": replica_ok,
    }


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
            self._json(200, {"ok": True, "servico": "api-sync-async", "modo_lab": MODO_LAB})
            return

        if path == "/replicacao/status":
            try:
                self._json(200, status_replicacao())
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        if path.startswith("/notas/"):
            aluno_id = path.removeprefix("/notas/").strip("/")
            disciplina = query.get("disciplina", ["SD"])[0]
            dest = query.get("dest", ["replica"])[0]
            try:
                if dest == "replica":
                    row = ler_nota_replica(aluno_id, disciplina)
                    if row is None:
                        self._json(404, {"erro": "nota não encontrada na réplica"})
                        return
                    self._json(200, {"aluno_id": aluno_id, "disciplina": disciplina, **row})
                else:
                    self._json(400, {"erro": "use dest=replica neste lab"})
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        self._json(
            200,
            {
                "modo_lab": MODO_LAB,
                "endpoints": [
                    "POST /notas",
                    "GET /notas/{aluno_id}?disciplina=SD&dest=replica",
                    "GET /replicacao/status",
                    "GET /health",
                ],
            },
        )

    def do_POST(self) -> None:
        if urlparse(self.path).path.rstrip("/") != "/notas":
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
            resultado = upsert_nota(aluno_id, disciplina, valor)
            try:
                resultado["replica_apos_commit"] = ler_nota_replica(aluno_id, disciplina)
            except Exception as exc:  # noqa: BLE001
                resultado["replica_apos_commit"] = {"erro": str(exc)}
            self._json(201, resultado)
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc), "modo_lab": MODO_LAB})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_banco(PRIMARY_DSN, "primary")
    for i in range(60):
        try:
            esperar_banco(REPLICA_DSN, "replica", tentativas=1)
            break
        except SystemExit:
            if i == 59:
                print("[api] aviso: réplica ainda não pronta", flush=True)
            time.sleep(2)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] modo_lab={MODO_LAB} ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

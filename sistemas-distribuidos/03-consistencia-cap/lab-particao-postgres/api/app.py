"""
API — matrícula com vagas limitadas sob replicação síncrona (tendência CP).

Partição: sem réplica sync em pg_stat_replication a API recusa a escrita (503).
Não usamos conn.cancel() no meio do SyncRep — no driver isso pode concluir o
COMMIT sem ACK da réplica (falso “sucesso”).
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
import psycopg2.errors

PORT = int(os.environ.get("PORT", "8000"))
PRIMARY_DSN = os.environ.get(
    "PRIMARY_DSN",
    "host=postgres-primary port=5432 dbname=portal user=portal password=portal",
)
REPLICA_DSN = os.environ.get(
    "REPLICA_DSN",
    "host=postgres-replica port=5432 dbname=portal user=portal password=portal",
)
STATEMENT_TIMEOUT_MS = int(os.environ.get("STATEMENT_TIMEOUT_MS", "45000"))


class SyncReplicaIndisponivel(RuntimeError):
    """Nenhuma réplica em sync/quorum — recusa de escrita (política CP)."""


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
def conectar(dsn: str, connect_timeout: int = 10):
    conn = psycopg2.connect(dsn, connect_timeout=connect_timeout)
    try:
        yield conn
    finally:
        conn.close()


def _contar_replicas_sync(cur) -> int:
    cur.execute(
        """
        SELECT count(*)::int AS n
        FROM pg_stat_replication
        WHERE sync_state IN ('sync', 'quorum')
        """
    )
    return int(cur.fetchone()["n"])


def matricular(disciplina_id: str, aluno_id: str) -> dict:
    sql = """
        WITH locked AS (
            SELECT id, vagas_restantes
            FROM disciplinas
            WHERE id = %s
            FOR UPDATE
        ),
        inserted AS (
            INSERT INTO matriculas (disciplina_id, aluno_id)
            SELECT %s, %s
            FROM locked
            WHERE vagas_restantes > 0
            ON CONFLICT (disciplina_id, aluno_id) DO NOTHING
            RETURNING disciplina_id, aluno_id, matriculado_em
        ),
        updated AS (
            UPDATE disciplinas d
            SET vagas_restantes = d.vagas_restantes - 1
            FROM inserted i
            WHERE d.id = i.disciplina_id
            RETURNING d.id, d.vagas_restantes
        )
        SELECT
            (SELECT COUNT(*) FROM inserted) AS inseriu,
            (SELECT vagas_restantes FROM locked) AS vagas_antes,
            (SELECT vagas_restantes FROM updated) AS vagas_depois,
            (SELECT matriculado_em FROM inserted) AS matriculado_em
    """
    inicio = time.perf_counter()
    with conectar(PRIMARY_DSN, connect_timeout=10) as conn:
        conn.autocommit = False
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SET LOCAL statement_timeout = {STATEMENT_TIMEOUT_MS}")
            # Fail-fast CP: sem standby sync o COMMIT ficaria em SyncRep para sempre
            # (statement_timeout NÃO cancela essa espera). Recusar é a política CP.
            if _contar_replicas_sync(cur) < 1:
                conn.rollback()
                raise SyncReplicaIndisponivel(
                    "nenhuma réplica sync/quorum — escrita recusada (CP); "
                    "confira /consistencia/status ou ./scripts/curar-particao.sh"
                )
            cur.execute(sql, (disciplina_id, disciplina_id, aluno_id))
            row = cur.fetchone()
            conn.commit()
    duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
    inseriu = int(row["inseriu"] or 0)
    if inseriu == 0:
        if row["vagas_antes"] is None:
            raise LookupError("disciplina não encontrada")
        if int(row["vagas_antes"]) <= 0:
            raise ValueError("sem vagas")
        raise ValueError("já matriculado")
    return {
        "disciplina_id": disciplina_id,
        "aluno_id": aluno_id,
        "vagas_restantes": int(row["vagas_depois"]),
        "matriculado_em": row["matriculado_em"].isoformat(),
        "duracao_commit_ms": duracao_ms,
        "modo": "sync_cp",
    }


def ler_disciplina(disciplina_id: str, dest: str) -> dict:
    dsn = REPLICA_DSN if dest == "replica" else PRIMARY_DSN
    sql = """
        SELECT d.id, d.nome, d.vagas_restantes,
               (SELECT COUNT(*) FROM matriculas m WHERE m.disciplina_id = d.id) AS matriculados
        FROM disciplinas d
        WHERE d.id = %s
    """
    with conectar(dsn) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (disciplina_id,))
            row = cur.fetchone()
    if not row:
        raise LookupError("disciplina não encontrada")
    out = dict(row)
    out["destino_leitura"] = dest
    out["matriculados"] = int(out["matriculados"])
    out["vagas_restantes"] = int(out["vagas_restantes"])
    return out


def status_consistencia() -> dict:
    sql_lag = """
        SELECT application_name, state, sync_state,
               pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
        FROM pg_stat_replication
    """
    sql_settings = """
        SELECT name, setting
        FROM pg_settings
        WHERE name IN ('synchronous_commit', 'synchronous_standby_names')
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
    replica_erro: str | None = None
    try:
        with conectar(REPLICA_DSN) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT pg_is_in_recovery()")
                replica_ok = bool(cur.fetchone()[0])
    except Exception as exc:  # noqa: BLE001
        replica_erro = str(exc)
    sync_ativo = any(r.get("sync_state") in ("sync", "quorum") for r in replicas)
    return {
        "modo_lab": "sync_cp",
        "replicas": replicas,
        "settings": settings,
        "replica_acessivel": replica_ok,
        "replica_erro": replica_erro,
        "sync_ativo": sync_ativo,
        "interpretacao": (
            "CP na escrita: commit sync exige réplica; API recusa (503) se sync_ativo=false"
            if sync_ativo
            else "sem réplica sync/quorum — POST /matricular retorna 503 (CP); "
            "se não for partição de propósito, rode ./scripts/curar-particao.sh e ativar-sync.sh"
        ),
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
            self._json(200, {"ok": True, "servico": "api-particao-postgres", "modo": "sync_cp"})
            return

        if path == "/consistencia/status":
            try:
                self._json(200, status_consistencia())
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        if path.startswith("/disciplinas/"):
            disciplina_id = path.removeprefix("/disciplinas/").strip("/")
            dest = query.get("dest", ["primary"])[0]
            if dest not in ("primary", "replica"):
                self._json(400, {"erro": "dest deve ser primary ou replica"})
                return
            try:
                self._json(200, ler_disciplina(disciplina_id, dest))
            except LookupError as exc:
                self._json(404, {"erro": str(exc)})
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc), "destino_leitura": dest})
            return

        self._json(
            200,
            {
                "modo": "sync_cp",
                "endpoints": [
                    "POST /matricular",
                    "GET /disciplinas/{id}?dest=primary|replica",
                    "GET /consistencia/status",
                    "GET /health",
                ],
            },
        )

    def do_POST(self) -> None:
        if urlparse(self.path).path.rstrip("/") != "/matricular":
            self._json(404, {"erro": "rota não encontrada"})
            return
        body = self._read_json()
        try:
            disciplina_id = body["disciplina_id"]
            aluno_id = body["aluno_id"]
        except KeyError:
            self._json(400, {"erro": "corpo esperado: disciplina_id, aluno_id"})
            return
        try:
            self._json(201, matricular(disciplina_id, aluno_id))
        except ValueError as exc:
            self._json(409, {"erro": str(exc), "modo": "sync_cp"})
        except LookupError as exc:
            self._json(404, {"erro": str(exc)})
        except SyncReplicaIndisponivel as exc:
            self._json(
                503,
                {
                    "erro": str(exc),
                    "modo": "sync_cp",
                    "dica": "GET /consistencia/status — sync_ativo deve ser true para matricular",
                },
            )
        except psycopg2.errors.QueryCanceled:
            self._json(
                503,
                {
                    "erro": "statement_timeout — operação cancelada",
                    "modo": "sync_cp",
                    "dica": "curl /consistencia/status ou ./scripts/curar-particao.sh",
                },
            )
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc), "modo": "sync_cp"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_banco(PRIMARY_DSN, "primary")
    # Não bloqueia a API por minutos se a réplica estiver particionada / DNS ausente.
    try:
        esperar_banco(REPLICA_DSN, "replica", tentativas=5)
    except SystemExit as exc:
        print(f"[api] aviso: {exc} — subindo mesmo assim (leitura dest=replica pode falhar)", flush=True)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] sync_cp ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

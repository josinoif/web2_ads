"""
API — matrícula com N instâncias e modos de coordenação.

Modos:
  broken      — read-modify-write sem exclusão (lost update)
  transaction — FOR UPDATE (padrão correto no mesmo Postgres)
  advisory    — pg_advisory_xact_lock por disciplina
  optimistic  — UPDATE com coluna version
"""

from __future__ import annotations

import hashlib
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
    "host=postgres port=5432 dbname=portal user=portal password=portal",
)
INSTANCE_ID = os.environ.get("INSTANCE_ID", os.environ.get("HOSTNAME", "api-local"))
RACE_DELAY_MS = int(os.environ.get("RACE_DELAY_MS", "150"))
MODOS = ("broken", "transaction", "advisory", "optimistic")


def esperar_banco(tentativas: int = 90) -> None:
    ultimo: Exception | None = None
    for _ in range(tentativas):
        try:
            with conectar() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            print(f"[{INSTANCE_ID}] postgres ok", flush=True)
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            time.sleep(2)
    raise SystemExit(f"Postgres indisponível: {ultimo}")


@contextmanager
def conectar(connect_timeout: int = 10):
    conn = psycopg2.connect(PRIMARY_DSN, connect_timeout=connect_timeout)
    try:
        yield conn
    finally:
        conn.close()


def advisory_key(disciplina_id: str) -> int:
    digest = hashlib.sha256(disciplina_id.encode()).digest()
    return int.from_bytes(digest[:8], "big", signed=True)


def _base_response(
    disciplina_id: str,
    aluno_id: str,
    modo: str,
    duracao_ms: float,
    **extra,
) -> dict:
    return {
        "disciplina_id": disciplina_id,
        "aluno_id": aluno_id,
        "modo": modo,
        "api_instance": INSTANCE_ID,
        "duracao_ms": round(duracao_ms, 2),
        **extra,
    }


def matricular_broken(disciplina_id: str, aluno_id: str) -> dict:
    inicio = time.perf_counter()
    with conectar() as conn:
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT vagas_restantes FROM disciplinas WHERE id = %s",
                (disciplina_id,),
            )
            row = cur.fetchone()
            if not row:
                raise LookupError("disciplina não encontrada")
            vagas_lidas = int(row["vagas_restantes"])
            if vagas_lidas <= 0:
                raise ValueError("sem vagas")

    time.sleep(RACE_DELAY_MS / 1000.0)

    with conectar() as conn:
        conn.autocommit = False
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT 1 FROM matriculas
                WHERE disciplina_id = %s AND aluno_id = %s
                """,
                (disciplina_id, aluno_id),
            )
            if cur.fetchone():
                raise ValueError("já matriculado")
            if vagas_lidas <= 0:
                raise ValueError("sem vagas")
            cur.execute(
                """
                INSERT INTO matriculas (disciplina_id, aluno_id, api_instance, modo)
                VALUES (%s, %s, %s, 'broken')
                """,
                (disciplina_id, aluno_id, INSTANCE_ID),
            )
            # Escrita absoluta do valor stale: ambos os writers leram 1 e
            # gravam 0 — duas matrículas, CHECK (>= 0) não impede overbooking.
            cur.execute(
                """
                UPDATE disciplinas
                SET vagas_restantes = %s
                WHERE id = %s
                """,
                (vagas_lidas - 1, disciplina_id),
            )
            cur.execute(
                "SELECT vagas_restantes FROM disciplinas WHERE id = %s",
                (disciplina_id,),
            )
            vagas_depois = int(cur.fetchone()["vagas_restantes"])
            conn.commit()

    return _base_response(
        disciplina_id,
        aluno_id,
        "broken",
        (time.perf_counter() - inicio) * 1000,
        vagas_restantes=vagas_depois,
        aviso="RMW sem lock — pode overbook sob concorrência",
    )


def matricular_transaction(disciplina_id: str, aluno_id: str) -> dict:
    inicio = time.perf_counter()
    sql = """
        WITH locked AS (
            SELECT id, vagas_restantes
            FROM disciplinas
            WHERE id = %s
            FOR UPDATE
        ),
        inserted AS (
            INSERT INTO matriculas (disciplina_id, aluno_id, api_instance, modo)
            SELECT %s, %s, %s, 'transaction'
            FROM locked
            WHERE vagas_restantes > 0
            ON CONFLICT (disciplina_id, aluno_id) DO NOTHING
            RETURNING disciplina_id
        ),
        updated AS (
            UPDATE disciplinas d
            SET vagas_restantes = d.vagas_restantes - 1,
                version = d.version + 1
            FROM inserted i
            WHERE d.id = i.disciplina_id
            RETURNING d.vagas_restantes, d.version
        )
        SELECT
            (SELECT COUNT(*) FROM inserted) AS inseriu,
            (SELECT vagas_restantes FROM locked) AS vagas_antes,
            (SELECT vagas_restantes FROM updated) AS vagas_depois,
            (SELECT version FROM updated) AS version
    """
    with conectar() as conn:
        conn.autocommit = False
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (disciplina_id, disciplina_id, aluno_id, INSTANCE_ID))
            row = cur.fetchone()
            conn.commit()

    inseriu = int(row["inseriu"] or 0)
    if inseriu == 0:
        if row["vagas_antes"] is None:
            raise LookupError("disciplina não encontrada")
        if int(row["vagas_antes"]) <= 0:
            raise ValueError("sem vagas")
        raise ValueError("já matriculado")

    return _base_response(
        disciplina_id,
        aluno_id,
        "transaction",
        (time.perf_counter() - inicio) * 1000,
        vagas_restantes=int(row["vagas_depois"]),
        version=int(row["version"]),
    )


def matricular_advisory(disciplina_id: str, aluno_id: str) -> dict:
    inicio = time.perf_counter()
    lock_id = advisory_key(disciplina_id)
    with conectar() as conn:
        conn.autocommit = False
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT pg_advisory_xact_lock(%s)", (lock_id,))
            cur.execute(
                "SELECT vagas_restantes FROM disciplinas WHERE id = %s FOR UPDATE",
                (disciplina_id,),
            )
            row = cur.fetchone()
            if not row:
                raise LookupError("disciplina não encontrada")
            if int(row["vagas_restantes"]) <= 0:
                raise ValueError("sem vagas")
            cur.execute(
                """
                INSERT INTO matriculas (disciplina_id, aluno_id, api_instance, modo)
                VALUES (%s, %s, %s, 'advisory')
                ON CONFLICT (disciplina_id, aluno_id) DO NOTHING
                RETURNING disciplina_id
                """,
                (disciplina_id, aluno_id, INSTANCE_ID),
            )
            inserted = cur.fetchone()
            if not inserted:
                raise ValueError("já matriculado")
            cur.execute(
                """
                UPDATE disciplinas
                SET vagas_restantes = vagas_restantes - 1,
                    version = version + 1
                WHERE id = %s
                RETURNING vagas_restantes, version
                """,
                (disciplina_id,),
            )
            updated = cur.fetchone()
            conn.commit()

    return _base_response(
        disciplina_id,
        aluno_id,
        "advisory",
        (time.perf_counter() - inicio) * 1000,
        vagas_restantes=int(updated["vagas_restantes"]),
        version=int(updated["version"]),
        advisory_lock_id=lock_id,
    )


def matricular_optimistic(disciplina_id: str, aluno_id: str) -> dict:
    inicio = time.perf_counter()
    with conectar() as conn:
        conn.autocommit = True
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT vagas_restantes, version FROM disciplinas WHERE id = %s",
                (disciplina_id,),
            )
            row = cur.fetchone()
            if not row:
                raise LookupError("disciplina não encontrada")
            if int(row["vagas_restantes"]) <= 0:
                raise ValueError("sem vagas")
            vagas_lidas = int(row["vagas_restantes"])
            version_lida = int(row["version"])

    time.sleep(RACE_DELAY_MS / 1000.0)

    with conectar() as conn:
        conn.autocommit = False
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO matriculas (disciplina_id, aluno_id, api_instance, modo)
                SELECT %s, %s, %s, 'optimistic'
                WHERE EXISTS (
                    SELECT 1 FROM disciplinas
                    WHERE id = %s AND vagas_restantes > 0 AND version = %s
                )
                ON CONFLICT (disciplina_id, aluno_id) DO NOTHING
                RETURNING disciplina_id
                """,
                (disciplina_id, aluno_id, INSTANCE_ID, disciplina_id, version_lida),
            )
            inserted = cur.fetchone()
            if not inserted:
                cur.execute(
                    "SELECT 1 FROM matriculas WHERE disciplina_id = %s AND aluno_id = %s",
                    (disciplina_id, aluno_id),
                )
                if cur.fetchone():
                    raise ValueError("já matriculado")
                raise ValueError("conflito de versão — tente novamente")

            cur.execute(
                """
                UPDATE disciplinas
                SET vagas_restantes = vagas_restantes - 1,
                    version = version + 1
                WHERE id = %s AND version = %s AND vagas_restantes > 0
                RETURNING vagas_restantes, version
                """,
                (disciplina_id, version_lida),
            )
            updated = cur.fetchone()
            if not updated:
                conn.rollback()
                raise ValueError("conflito de versão — tente novamente")
            conn.commit()

    return _base_response(
        disciplina_id,
        aluno_id,
        "optimistic",
        (time.perf_counter() - inicio) * 1000,
        vagas_restantes=int(updated["vagas_restantes"]),
        version=int(updated["version"]),
        version_lida=version_lida,
        vagas_lidas=vagas_lidas,
    )


def matricular(disciplina_id: str, aluno_id: str, modo: str) -> dict:
    if modo == "broken":
        return matricular_broken(disciplina_id, aluno_id)
    if modo == "transaction":
        return matricular_transaction(disciplina_id, aluno_id)
    if modo == "advisory":
        return matricular_advisory(disciplina_id, aluno_id)
    if modo == "optimistic":
        return matricular_optimistic(disciplina_id, aluno_id)
    raise ValueError(f"modo inválido: {modo}")


def ler_disciplina(disciplina_id: str) -> dict:
    sql = """
        SELECT d.id, d.nome, d.vagas_restantes, d.version,
               (SELECT COUNT(*) FROM matriculas m WHERE m.disciplina_id = d.id) AS matriculados,
               (SELECT json_agg(json_build_object(
                    'aluno_id', m.aluno_id,
                    'api_instance', m.api_instance,
                    'modo', m.modo,
                    'matriculado_em', m.matriculado_em
                ) ORDER BY m.matriculado_em)
                FROM matriculas m WHERE m.disciplina_id = d.id) AS matriculas
        FROM disciplinas d
        WHERE d.id = %s
    """
    with conectar() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, (disciplina_id,))
            row = cur.fetchone()
    if not row:
        raise LookupError("disciplina não encontrada")
    out = dict(row)
    out["matriculados"] = int(out["matriculados"])
    out["vagas_restantes"] = int(out["vagas_restantes"])
    out["version"] = int(out["version"])
    return out


def status_coordenacao() -> dict:
    sql = """
        SELECT d.id, d.vagas_restantes, d.version,
               (SELECT COUNT(*) FROM matriculas m WHERE m.disciplina_id = d.id) AS matriculados
        FROM disciplinas d
        ORDER BY d.id
    """
    with conectar() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)
            disciplinas = [dict(r) for r in cur.fetchall()]
    for d in disciplinas:
        d["matriculados"] = int(d["matriculados"])
        d["vagas_restantes"] = int(d["vagas_restantes"])
        d["version"] = int(d["version"])
    sd101 = next((d for d in disciplinas if d["id"] == "SD-101"), None)
    alerta_overbooking = False
    if sd101:
        alerta_overbooking = sd101["matriculados"] > 1 or sd101["vagas_restantes"] < 0
    return {
        "modo_lab": "concorrencia_postgres",
        "api_instance": INSTANCE_ID,
        "race_delay_ms": RACE_DELAY_MS,
        "modos_validos": list(MODOS),
        "disciplinas": disciplinas,
        "alerta_overbooking_sd101": alerta_overbooking,
        "interpretacao": (
            "Overbooking detectado em SD-101 — compare modo broken vs transaction"
            if alerta_overbooking
            else "Estado consistente com vagas — use broken + --paralelo para provocar corrida"
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

        if path == "/health":
            self._json(
                200,
                {
                    "ok": True,
                    "servico": "api-concorrencia-postgres",
                    "api_instance": INSTANCE_ID,
                },
            )
            return

        if path == "/coordenacao/status":
            try:
                self._json(200, status_coordenacao())
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        if path.startswith("/disciplinas/"):
            disciplina_id = path.removeprefix("/disciplinas/").strip("/")
            try:
                self._json(200, ler_disciplina(disciplina_id))
            except LookupError as exc:
                self._json(404, {"erro": str(exc)})
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        self._json(
            200,
            {
                "modo_lab": "concorrencia_postgres",
                "api_instance": INSTANCE_ID,
                "endpoints": [
                    "POST /matricular?mode=broken|transaction|advisory|optimistic",
                    "GET /disciplinas/{id}",
                    "GET /coordenacao/status",
                    "GET /health",
                ],
            },
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") != "/matricular":
            self._json(404, {"erro": "rota não encontrada"})
            return
        query = parse_qs(parsed.query)
        modo = query.get("mode", ["transaction"])[0]
        if modo not in MODOS:
            self._json(400, {"erro": f"mode deve ser um de: {', '.join(MODOS)}"})
            return
        body = self._read_json()
        try:
            disciplina_id = body["disciplina_id"]
            aluno_id = body["aluno_id"]
        except KeyError:
            self._json(400, {"erro": "corpo esperado: disciplina_id, aluno_id"})
            return
        try:
            self._json(201, matricular(disciplina_id, aluno_id, modo))
        except ValueError as exc:
            code = 409 if "conflito" in str(exc) else 409
            self._json(code, {"erro": str(exc), "modo": modo, "api_instance": INSTANCE_ID})
        except LookupError as exc:
            self._json(404, {"erro": str(exc)})
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc), "modo": modo, "api_instance": INSTANCE_ID})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{INSTANCE_ID}] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_banco()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[{INSTANCE_ID}] ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

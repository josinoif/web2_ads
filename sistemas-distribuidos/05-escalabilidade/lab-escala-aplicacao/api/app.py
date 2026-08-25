"""
API — boletim (leitura) para lab de escala na camada de aplicação.

N instâncias atrás do nginx; um Postgres compartilhado.
EXTRA_DELAY_MS / POST /admin/delay simula worker lento.
WORK_MS = CPU sintética por request (torna o ganho com N APIs visível).
DB_SLOTS = teto didático de acessos concorrentes ao store (Exp. aproximar teto).
"""

from __future__ import annotations

import json
import os
import threading
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
INSTANCE_ID = os.environ.get("INSTANCE_ID", "api-local")
# Mutáveis em runtime via /admin/*
work_ms = int(os.environ.get("WORK_MS", "15"))
extra_delay_ms = int(os.environ.get("EXTRA_DELAY_MS", "0"))
db_slots = int(os.environ.get("DB_SLOTS", "0"))  # 0 = ilimitado
store_hold_ms = int(os.environ.get("STORE_HOLD_MS", "0"))  # latência didática sob o slot
request_count = 0
_db_gate: threading.Semaphore | None = None
_db_gate_lock = threading.Lock()


def _rebuild_db_gate(slots: int) -> None:
    global _db_gate, db_slots
    db_slots = max(0, slots)
    with _db_gate_lock:
        _db_gate = threading.Semaphore(db_slots) if db_slots > 0 else None


_rebuild_db_gate(db_slots)


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


@contextmanager
def acesso_store():
    """Limita concorrência ao Postgres (simula pool/conexões escassas + hold)."""
    gate = _db_gate
    if gate is None:
        yield
        return
    gate.acquire()
    try:
        if store_hold_ms > 0:
            time.sleep(store_hold_ms / 1000.0)
        yield
    finally:
        gate.release()


def busy_work_ms(ms: int) -> None:
    """CPU sintética (busy-wait). sleep() liberaria o GIL e 1 API não saturaria."""
    if ms <= 0:
        return
    fim = time.perf_counter() + ms / 1000.0
    while time.perf_counter() < fim:
        pass


def boletim(aluno_id: str) -> dict:
    global request_count
    inicio = time.perf_counter()
    busy_work_ms(work_ms)
    if extra_delay_ms > 0:
        time.sleep(extra_delay_ms / 1000.0)

    sql_aluno = "SELECT id, nome FROM alunos WHERE id = %s"
    sql_notas = """
        SELECT disciplina_id, nota
        FROM notas
        WHERE aluno_id = %s
        ORDER BY disciplina_id
    """
    with acesso_store():
        with conectar() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql_aluno, (aluno_id,))
                aluno = cur.fetchone()
                if not aluno:
                    raise LookupError("aluno não encontrado")
                cur.execute(sql_notas, (aluno_id,))
                notas = [dict(r) for r in cur.fetchall()]
                for n in notas:
                    n["nota"] = float(n["nota"])

    request_count += 1
    duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
    return {
        "aluno_id": aluno["id"],
        "nome": aluno["nome"],
        "notas": notas,
        "api_instance": INSTANCE_ID,
        "duracao_ms": duracao_ms,
        "extra_delay_ms": extra_delay_ms,
        "work_ms": work_ms,
        "db_slots": db_slots,
    }


def status_escala() -> dict:
    with acesso_store():
        with conectar() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM alunos")
                n_alunos = int(cur.fetchone()[0])
                cur.execute("SELECT COUNT(*) FROM notas")
                n_notas = int(cur.fetchone()[0])
                cur.execute(
                    "SELECT count(*) FROM pg_stat_activity WHERE datname = current_database()"
                )
                conexoes = int(cur.fetchone()[0])
    return {
        "modo_lab": "escala_aplicacao",
        "camada": "aplicacao",
        "api_instance": INSTANCE_ID,
        "request_count_esta_instancia": request_count,
        "extra_delay_ms": extra_delay_ms,
        "work_ms": work_ms,
        "db_slots": db_slots,
        "store_hold_ms": store_hold_ms,
        "alunos": n_alunos,
        "notas": n_notas,
        "conexoes_postgres_visiveis": conexoes,
        "interpretacao": (
            "Escala de APP: N instâncias atrás do LB. "
            "WORK_MS = CPU sintética (busy-wait). "
            "DB_SLOTS+STORE_HOLD_MS = teto didático do store. "
            "Se RPS cai com o store limitado, o gargalo 'migrou' para dados."
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
            self._json(200, {"ok": True, "servico": "api-escala-aplicacao", "api_instance": INSTANCE_ID})
            return

        if path == "/escala/status":
            try:
                self._json(200, status_escala())
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        if path == "/boletim":
            aluno_id = query.get("aluno_id", ["aluno-1"])[0]
            try:
                self._json(200, boletim(aluno_id))
            except LookupError as exc:
                self._json(404, {"erro": str(exc)})
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc), "api_instance": INSTANCE_ID})
            return

        self._json(
            200,
            {
                "modo_lab": "escala_aplicacao",
                "camada": "aplicacao",
                "endpoints": [
                    "GET /boletim?aluno_id=aluno-1",
                    "GET /escala/status",
                    "POST /admin/delay  {\"ms\": 50}",
                    "POST /admin/work_ms {\"ms\": 5}",
                    "POST /admin/db_slots {\"slots\": 2}",
                    "GET /health",
                ],
            },
        )

    def do_POST(self) -> None:
        global extra_delay_ms, work_ms
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/admin/delay":
            body = self._read_json()
            try:
                ms = int(body.get("ms", 0))
            except (TypeError, ValueError):
                self._json(400, {"erro": "corpo esperado: {\"ms\": <int>}"})
                return
            if ms < 0 or ms > 5000:
                self._json(400, {"erro": "ms deve estar entre 0 e 5000"})
                return
            extra_delay_ms = ms
            self._json(
                200,
                {
                    "api_instance": INSTANCE_ID,
                    "extra_delay_ms": extra_delay_ms,
                    "aviso": "Delay só nesta instância — use para Exp. worker lento",
                },
            )
            return

        if path == "/admin/work_ms":
            body = self._read_json()
            try:
                ms = int(body.get("ms", 0))
            except (TypeError, ValueError):
                self._json(400, {"erro": "corpo esperado: {\"ms\": <int>}"})
                return
            if ms < 0 or ms > 500:
                self._json(400, {"erro": "ms deve estar entre 0 e 500"})
                return
            work_ms = ms
            self._json(200, {"api_instance": INSTANCE_ID, "work_ms": work_ms})
            return

        if path == "/admin/db_slots":
            body = self._read_json()
            try:
                slots = int(body.get("slots", 0))
            except (TypeError, ValueError):
                self._json(400, {"erro": "corpo esperado: {\"slots\": <int>}"})
                return
            if slots < 0 or slots > 64:
                self._json(400, {"erro": "slots deve estar entre 0 e 64 (0=ilimitado)"})
                return
            _rebuild_db_gate(slots)
            self._json(
                200,
                {
                    "api_instance": INSTANCE_ID,
                    "db_slots": db_slots,
                    "aviso": "0=ilimitado; >0 simula teto de acesso ao store nesta instância",
                },
            )
            return

        if path == "/admin/store_hold_ms":
            global store_hold_ms
            body = self._read_json()
            try:
                ms = int(body.get("ms", 0))
            except (TypeError, ValueError):
                self._json(400, {"erro": "corpo esperado: {\"ms\": <int>}"})
                return
            if ms < 0 or ms > 2000:
                self._json(400, {"erro": "ms deve estar entre 0 e 2000"})
                return
            store_hold_ms = ms
            self._json(200, {"api_instance": INSTANCE_ID, "store_hold_ms": store_hold_ms})
            return

        self._json(404, {"erro": "rota não encontrada"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{INSTANCE_ID}] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_banco()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[{INSTANCE_ID}] ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

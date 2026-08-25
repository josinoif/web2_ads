"""
API — matrícula com delay/falha injetáveis, idempotência e circuit breaker mínimo.

STORE_HOLD_MS: atraso sintético durante a escrita (simula store lento).
FAIL_RATE: 0–100, chance de 503 antes do commit (erro transiente).
CB_*: abre o circuito após N falhas na janela CB_WINDOW_SEC; falha rápido até CB_OPEN_SEC.
X-Deadline-Ms: deadline propagation didática — se hold > deadline, aborta rápido (504).
"""

from __future__ import annotations

import json
import os
import random
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

store_hold_ms = int(os.environ.get("STORE_HOLD_MS", "0"))
fail_rate = int(os.environ.get("FAIL_RATE", "0"))
cb_threshold = int(os.environ.get("CB_THRESHOLD", "5"))
cb_open_sec = float(os.environ.get("CB_OPEN_SEC", "8"))
cb_window_sec = float(os.environ.get("CB_WINDOW_SEC", "60"))
idem_ttl_sec = int(os.environ.get("IDEM_TTL_SEC", "3600"))

_cb_lock = threading.Lock()
_cb_fail_times: list[float] = []
_cb_opened_at: float | None = None
_cb_probe_in_flight = False
_stats = {
    "ok": 0,
    "fail": 0,
    "cb_reject": 0,
    "idem_hit": 0,
    "idem_expired": 0,
    "deadline_abort": 0,
    "requests": 0,
}
_lat_lock = threading.Lock()
_latencias_ms: list[float] = []
_LAT_MAX = 200


def esperar_banco(tentativas: int = 90) -> None:
    ultimo: Exception | None = None
    for _ in range(tentativas):
        try:
            with conectar() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            print("[api] postgres ok", flush=True)
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


def _lat_registrar(ms: float) -> None:
    with _lat_lock:
        _latencias_ms.append(float(ms))
        overflow = len(_latencias_ms) - _LAT_MAX
        if overflow > 0:
            del _latencias_ms[:overflow]


def _lat_resumo() -> dict:
    with _lat_lock:
        amostra = list(_latencias_ms)
    if not amostra:
        return {"n": 0, "p50_ms": None, "p95_ms": None, "max_ms": None}
    ordenada = sorted(amostra)

    def pct(p: float) -> float:
        idx = min(len(ordenada) - 1, max(0, int(round((p / 100.0) * (len(ordenada) - 1)))))
        return round(ordenada[idx], 2)

    return {
        "n": len(ordenada),
        "p50_ms": pct(50),
        "p95_ms": pct(95),
        "max_ms": round(ordenada[-1], 2),
        "janela": _LAT_MAX,
    }


def _cb_prune_locked(now: float) -> int:
    cutoff = now - cb_window_sec
    _cb_fail_times[:] = [t for t in _cb_fail_times if t >= cutoff]
    return len(_cb_fail_times)


def _cb_estado() -> str:
    with _cb_lock:
        if _cb_opened_at is None:
            return "fechado"
        if time.monotonic() - _cb_opened_at >= cb_open_sec:
            return "meio-aberto"
        return "aberto"


def _cb_permitir() -> bool:
    global _cb_opened_at, _cb_probe_in_flight
    with _cb_lock:
        if _cb_opened_at is None:
            return True
        elapsed = time.monotonic() - _cb_opened_at
        if elapsed >= cb_open_sec:
            if _cb_probe_in_flight:
                _stats["cb_reject"] += 1
                return False
            _cb_probe_in_flight = True
            return True
        _stats["cb_reject"] += 1
        return False


def _cb_registrar(sucesso: bool) -> None:
    global _cb_opened_at, _cb_probe_in_flight
    with _cb_lock:
        _cb_probe_in_flight = False
        now = time.monotonic()
        if sucesso:
            _cb_fail_times.clear()
            _cb_opened_at = None
            return
        _cb_fail_times.append(now)
        n = _cb_prune_locked(now)
        if n >= cb_threshold:
            _cb_opened_at = now


class CircuitOpen(RuntimeError):
    pass


class TransientFail(RuntimeError):
    pass


class DeadlineExceeded(RuntimeError):
    """Hold/trabalho não cabe no deadline propagado do cliente."""


class IdempotencyConflict(ValueError):
    """Mesma Idempotency-Key com corpo diferente — não é replay seguro."""


def _request_fingerprint(disciplina_id: str, aluno_id: str) -> str:
    return f"matricular|{disciplina_id}|{aluno_id}"


def matricular(
    disciplina_id: str,
    aluno_id: str,
    idem_key: str | None,
    deadline_ms: int | None = None,
) -> dict:
    if not _cb_permitir():
        with _cb_lock:
            n = _cb_prune_locked(time.monotonic())
        raise CircuitOpen(
            f"circuit breaker aberto — tente em ~{cb_open_sec:.0f}s "
            f"(falhas na janela {cb_window_sec:.0f}s: {n} ≥ {cb_threshold})"
        )

    inicio = time.perf_counter()
    fp = _request_fingerprint(disciplina_id, aluno_id)
    try:
        with conectar() as conn:
            conn.autocommit = False
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                if idem_key:
                    cur.execute(
                        "SELECT request_fingerprint, response_json, created_at "
                        "FROM idempotency_keys WHERE key = %s",
                        (idem_key,),
                    )
                    hit = cur.fetchone()
                    if hit:
                        age_sec = time.time() - hit["created_at"].timestamp()
                        if age_sec > idem_ttl_sec:
                            cur.execute(
                                "DELETE FROM idempotency_keys WHERE key = %s",
                                (idem_key,),
                            )
                            conn.commit()
                            _stats["idem_expired"] += 1
                        elif hit["request_fingerprint"] != fp:
                            conn.rollback()
                            raise IdempotencyConflict(
                                "Idempotency-Key já usada com outro corpo "
                                f"(fingerprint armazenado diverge de {fp!r})"
                            )
                        else:
                            conn.commit()
                            _stats["idem_hit"] += 1
                            _cb_registrar(True)
                            payload = json.loads(hit["response_json"])
                            payload["idempotent_replay"] = True
                            payload["duracao_ms"] = round(
                                (time.perf_counter() - inicio) * 1000, 2
                            )
                            return payload

                if fail_rate > 0 and random.randint(1, 100) <= fail_rate:
                    conn.rollback()
                    raise TransientFail(
                        f"falha injetada (FAIL_RATE={fail_rate}) — erro transiente"
                    )

                if (
                    deadline_ms is not None
                    and store_hold_ms > 0
                    and store_hold_ms > deadline_ms
                ):
                    conn.rollback()
                    _stats["deadline_abort"] += 1
                    raise DeadlineExceeded(
                        f"STORE_HOLD_MS={store_hold_ms} > X-Deadline-Ms={deadline_ms} "
                        "— abortado rápido (deadline propagation)"
                    )

                if store_hold_ms > 0:
                    time.sleep(store_hold_ms / 1000.0)

                with conectar() as conn_aud:
                    conn_aud.autocommit = True
                    with conn_aud.cursor() as cur_aud:
                        cur_aud.execute(
                            """
                            INSERT INTO auditoria_tentativas (disciplina_id, aluno_id)
                            VALUES (%s, %s)
                            """,
                            (disciplina_id, aluno_id),
                        )

                cur.execute(
                    """
                    SELECT vagas_restantes FROM disciplinas
                    WHERE id = %s FOR UPDATE
                    """,
                    (disciplina_id,),
                )
                row = cur.fetchone()
                if not row:
                    raise LookupError("disciplina não encontrada")
                if int(row["vagas_restantes"]) <= 0:
                    raise ValueError("sem vagas")

                cur.execute(
                    """
                    INSERT INTO matriculas (disciplina_id, aluno_id)
                    VALUES (%s, %s)
                    ON CONFLICT (disciplina_id, aluno_id) DO NOTHING
                    RETURNING matriculado_em
                    """,
                    (disciplina_id, aluno_id),
                )
                inserted = cur.fetchone()
                if not inserted:
                    raise ValueError("já matriculado")

                cur.execute(
                    """
                    UPDATE disciplinas
                    SET vagas_restantes = vagas_restantes - 1
                    WHERE id = %s
                    RETURNING vagas_restantes
                    """,
                    (disciplina_id,),
                )
                vagas = cur.fetchone()["vagas_restantes"]
                payload = {
                    "disciplina_id": disciplina_id,
                    "aluno_id": aluno_id,
                    "vagas_restantes": int(vagas),
                    "matriculado_em": inserted["matriculado_em"].isoformat(),
                    "idempotent_replay": False,
                    "store_hold_ms": store_hold_ms,
                    "deadline_ms": deadline_ms,
                }
                if idem_key:
                    cur.execute(
                        """
                        INSERT INTO idempotency_keys
                            (key, request_fingerprint, response_json)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (key) DO NOTHING
                        """,
                        (idem_key, fp, json.dumps(payload, ensure_ascii=False)),
                    )
                conn.commit()
        payload["duracao_ms"] = round((time.perf_counter() - inicio) * 1000, 2)
        _stats["ok"] += 1
        _cb_registrar(True)
        return payload
    except DeadlineExceeded:
        # Política do cliente — não conta como falha do store no CB.
        _cb_registrar(True)
        raise
    except (TransientFail, CircuitOpen):
        _stats["fail"] += 1
        _cb_registrar(False)
        raise
    except (ValueError, LookupError):
        _cb_registrar(True)
        raise
    except Exception:
        _stats["fail"] += 1
        _cb_registrar(False)
        raise


def contar_matriculas(
    disciplina_id: str | None = None, aluno_id: str | None = None
) -> dict:
    with conectar() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            where = []
            params: list = []
            if disciplina_id:
                where.append("disciplina_id = %s")
                params.append(disciplina_id)
            if aluno_id:
                where.append("aluno_id = %s")
                params.append(aluno_id)
            clause = (" WHERE " + " AND ".join(where)) if where else ""

            cur.execute(f"SELECT COUNT(*)::int AS n FROM matriculas{clause}", params)
            n = cur.fetchone()["n"]
            cur.execute(
                f"SELECT COUNT(*)::int AS n FROM auditoria_tentativas{clause}", params
            )
            aud = cur.fetchone()["n"]
            cur.execute(
                "SELECT disciplina_id, aluno_id, matriculado_em FROM matriculas "
                f"{clause} ORDER BY matriculado_em DESC LIMIT 20",
                params,
            )
            rows = [dict(r) for r in cur.fetchall()]
            for r in rows:
                r["matriculado_em"] = r["matriculado_em"].isoformat()
    out = {
        "matriculas": n,
        "auditoria_tentativas": aud,
        "recentes": rows,
        "filtro": {"disciplina_id": disciplina_id, "aluno_id": aluno_id},
    }
    if aluno_id:
        out["leitura"] = (
            "contagem DESTE aluno (Exp. 3: mat=1 e aud>1; Exp. 4: aud estável no replay)"
        )
    return out


def admin_config() -> dict:
    with _cb_lock:
        falhas_janela = _cb_prune_locked(time.monotonic())
    return {
        "store_hold_ms": store_hold_ms,
        "fail_rate": fail_rate,
        "cb_threshold": cb_threshold,
        "cb_open_sec": cb_open_sec,
        "cb_window_sec": cb_window_sec,
        "cb_falhas_na_janela": falhas_janela,
        "cb_estado": _cb_estado(),
        "idem_ttl_sec": idem_ttl_sec,
        "stats": dict(_stats),
        "latencia": _lat_resumo(),
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
        q = parse_qs(parsed.query)

        if path == "/health":
            self._json(200, {"ok": True, "servico": "api-timeout-postgres"})
            return
        if path == "/admin/config":
            self._json(200, admin_config())
            return
        if path == "/matriculas":
            disc = q.get("disciplina_id", [None])[0]
            aluno = q.get("aluno_id", [None])[0]
            self._json(200, contar_matriculas(disc, aluno))
            return
        self._json(
            200,
            {
                "endpoints": [
                    "POST /matricular",
                    "GET /matriculas",
                    "GET /admin/config",
                    "POST /admin/store_hold_ms",
                    "POST /admin/fail_rate",
                    "POST /admin/idem_ttl_sec",
                    "POST /admin/cb_reset",
                    "GET /health",
                ]
            },
        )

    def do_POST(self) -> None:
        global store_hold_ms, fail_rate, idem_ttl_sec
        path = urlparse(self.path).path.rstrip("/") or "/"
        body = self._read_json()

        if path == "/admin/store_hold_ms":
            store_hold_ms = int(body.get("ms", 0))
            self._json(200, admin_config())
            return
        if path == "/admin/fail_rate":
            fail_rate = max(0, min(100, int(body.get("rate", 0))))
            self._json(200, admin_config())
            return
        if path == "/admin/idem_ttl_sec":
            idem_ttl_sec = max(1, int(body.get("sec", 3600)))
            self._json(200, admin_config())
            return
        if path == "/admin/cb_reset":
            with _cb_lock:
                global _cb_opened_at, _cb_probe_in_flight
                _cb_fail_times.clear()
                _cb_opened_at = None
                _cb_probe_in_flight = False
            self._json(200, admin_config())
            return

        if path != "/matricular":
            self._json(404, {"erro": "rota não encontrada"})
            return

        try:
            disciplina_id = body["disciplina_id"]
            aluno_id = body["aluno_id"]
        except KeyError:
            self._json(400, {"erro": "corpo: disciplina_id, aluno_id"})
            return

        deadline_ms: int | None = None
        raw_dl = self.headers.get("X-Deadline-Ms") or body.get("deadline_ms")
        if raw_dl is not None and str(raw_dl).strip() != "":
            try:
                deadline_ms = max(1, int(raw_dl))
            except ValueError:
                self._json(400, {"erro": "X-Deadline-Ms inválido"})
                return

        _stats["requests"] += 1
        idem = self.headers.get("Idempotency-Key") or body.get("idempotency_key")
        t0 = time.perf_counter()
        try:
            self._json(201, matricular(disciplina_id, aluno_id, idem, deadline_ms))
        except CircuitOpen as exc:
            self._json(503, {"erro": str(exc), "circuit": "aberto"})
        except TransientFail as exc:
            self._json(503, {"erro": str(exc), "retryable": True})
        except DeadlineExceeded as exc:
            self._json(
                504,
                {
                    "erro": str(exc),
                    "code": "deadline_exceeded",
                    "retryable": True,
                },
            )
        except IdempotencyConflict as exc:
            self._json(
                422,
                {
                    "erro": str(exc),
                    "code": "idempotency_key_reuse_mismatch",
                    "retryable": False,
                },
            )
        except ValueError as exc:
            self._json(409, {"erro": str(exc)})
        except LookupError as exc:
            self._json(404, {"erro": str(exc)})
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc)})
        finally:
            _lat_registrar((time.perf_counter() - t0) * 1000.0)

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_banco()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] timeout-postgres ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

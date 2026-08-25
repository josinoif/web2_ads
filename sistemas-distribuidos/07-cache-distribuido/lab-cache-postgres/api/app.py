"""
API — boletim com cache-aside (Redis / local / off), invalidação e stampede lock.

STORE_HOLD_MS: atraso sintético na leitura da fonte (simula Postgres lento).
CACHE_BACKEND: redis | local | off
CACHE_TTL_SEC + TTL_JITTER_SEC: TTL efetivo = TTL ± jitter (se jitter > 0).
INVALIDATE_ON_WRITE: 1 → DEL da chave após PUT; 0 → deixa stale até TTL.
STAMPEDE_LOCK: 1 → só um miss busca na fonte (SET NX curto no Redis).
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
import redis

PORT = int(os.environ.get("PORT", "8000"))
PRIMARY_DSN = os.environ.get(
    "PRIMARY_DSN",
    "host=postgres port=5432 dbname=portal user=portal password=portal",
)
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

store_hold_ms = int(os.environ.get("STORE_HOLD_MS", "0"))
cache_backend = os.environ.get("CACHE_BACKEND", "redis").lower()
cache_ttl_sec = int(os.environ.get("CACHE_TTL_SEC", "60"))
invalidate_on_write = os.environ.get("INVALIDATE_ON_WRITE", "1") in (
    "1",
    "true",
    "True",
)
stampede_lock = os.environ.get("STAMPEDE_LOCK", "0") in ("1", "true", "True")
ttl_jitter_sec = int(os.environ.get("TTL_JITTER_SEC", "0"))

_redis: redis.Redis | None = None
_local_cache: dict[str, tuple[float, dict]] = {}
_local_lock = threading.Lock()

_stats = {
    "requests": 0,
    "hits": 0,
    "misses": 0,
    "store_reads": 0,
    "writes": 0,
    "invalidations": 0,
    "stampede_waits": 0,
    "stampede_fills": 0,
}
_lat_lock = threading.Lock()
_latencias_ms: list[float] = []
_LAT_MAX = 300


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
    return _redis


class CacheUnavailable(RuntimeError):
    """Redis indisponível — SPOF didático da camada de cache."""


def _redis_call(op):
    try:
        return op()
    except (redis.exceptions.RedisError, OSError) as exc:
        global _redis
        _redis = None  # força novo client após recovery
        raise CacheUnavailable(
            "cache Redis indisponível — camada de cache é SPOF neste lab"
        ) from exc


@contextmanager
def conectar(connect_timeout: int = 10):
    conn = psycopg2.connect(PRIMARY_DSN, connect_timeout=connect_timeout)
    try:
        yield conn
    finally:
        conn.close()


def esperar() -> None:
    ultimo: Exception | None = None
    for _ in range(90):
        try:
            with conectar() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            if cache_backend == "redis":
                get_redis().ping()
            print("[api] postgres + deps ok", flush=True)
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            time.sleep(2)
    raise SystemExit(f"dependências indisponíveis: {ultimo}")


def _cache_key(aluno_id: str) -> str:
    return f"boletim:{aluno_id}"


def _ttl_efetivo() -> int:
    base = max(1, cache_ttl_sec)
    if ttl_jitter_sec <= 0:
        return base
    delta = random.randint(-ttl_jitter_sec, ttl_jitter_sec)
    return max(1, base + delta)


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
        idx = min(
            len(ordenada) - 1,
            max(0, int(round((p / 100.0) * (len(ordenada) - 1)))),
        )
        return round(ordenada[idx], 2)

    return {
        "n": len(ordenada),
        "p50_ms": pct(50),
        "p95_ms": pct(95),
        "max_ms": round(ordenada[-1], 2),
        "janela": _LAT_MAX,
    }


def _hit_rate() -> float | None:
    total = _stats["hits"] + _stats["misses"]
    if total == 0:
        return None
    return round(_stats["hits"] / total, 4)


def _cache_get(key: str) -> dict | None:
    if cache_backend == "off":
        return None
    if cache_backend == "local":
        with _local_lock:
            item = _local_cache.get(key)
            if not item:
                return None
            exp, payload = item
            if time.time() >= exp:
                del _local_cache[key]
                return None
            return dict(payload)
    raw = _redis_call(lambda: get_redis().get(key))
    if raw is None:
        return None
    return json.loads(raw)


def _cache_set(key: str, payload: dict) -> int:
    ttl = _ttl_efetivo()
    if cache_backend == "off":
        return ttl
    if cache_backend == "local":
        with _local_lock:
            _local_cache[key] = (time.time() + ttl, dict(payload))
        return ttl
    blob = json.dumps(payload, ensure_ascii=False, default=str)
    _redis_call(lambda: get_redis().set(key, blob, ex=ttl))
    return ttl


def _cache_del(key: str) -> None:
    if cache_backend == "local":
        with _local_lock:
            _local_cache.pop(key, None)
        return
    if cache_backend == "redis":
        _redis_call(lambda: get_redis().delete(key))


def _cache_flush() -> None:
    if cache_backend == "local":
        with _local_lock:
            _local_cache.clear()
        return
    if cache_backend == "redis":

        def _flush() -> None:
            r = get_redis()
            for key in r.scan_iter("boletim:*"):
                r.delete(key)

        _redis_call(_flush)


def ler_fonte(aluno_id: str) -> dict:
    if store_hold_ms > 0:
        time.sleep(store_hold_ms / 1000.0)
    _stats["store_reads"] += 1
    with conectar() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT aluno_id, disciplina_id, nota, atualizado_em "
                "FROM boletim WHERE aluno_id = %s",
                (aluno_id,),
            )
            row = cur.fetchone()
            if not row:
                raise LookupError("aluno não encontrado")
            return {
                "aluno_id": row["aluno_id"],
                "disciplina_id": row["disciplina_id"],
                "nota": float(row["nota"]),
                "atualizado_em": row["atualizado_em"].isoformat(),
                # SoT — não confundir com de onde *esta* resposta foi servida
                "fonte_dados": "postgres",
            }


def _servido_de_cache() -> str:
    if cache_backend == "redis":
        return "redis"
    if cache_backend == "local":
        return "local"
    return "postgres"


def _embalar(
    payload: dict,
    *,
    cache: str,
    servido_de: str,
    inicio: float,
    ttl: int | None = None,
) -> dict:
    out = dict(payload)
    out["cache"] = cache
    out["servido_de"] = servido_de
    if ttl is not None:
        out["ttl_sec_aplicado"] = ttl
    out["duracao_ms"] = round((time.perf_counter() - inicio) * 1000, 2)
    return out


def _fill_apos_miss(aluno_id: str, key: str) -> tuple[dict, int]:
    payload = ler_fonte(aluno_id)
    # guarda só o dado (sem metadados de resposta)
    ttl = _cache_set(
        key,
        {
            "aluno_id": payload["aluno_id"],
            "disciplina_id": payload["disciplina_id"],
            "nota": payload["nota"],
            "atualizado_em": payload["atualizado_em"],
            "fonte_dados": payload["fonte_dados"],
        },
    )
    return payload, ttl


def _get_com_stampede_lock(aluno_id: str, key: str) -> tuple[dict, str, int | None]:
    """Single-flight didático: um miss preenche; outros esperam o SET."""
    lock_key = f"lock:{key}"
    token = f"{os.getpid()}-{threading.get_ident()}-{time.time_ns()}"
    got = _redis_call(lambda: get_redis().set(lock_key, token, nx=True, ex=5))
    if got:
        _stats["stampede_fills"] += 1
        try:
            cached = _cache_get(key)
            if cached is not None:
                _stats["hits"] += 1
                return cached, "hit", None
            _stats["misses"] += 1
            payload, ttl = _fill_apos_miss(aluno_id, key)
            return payload, "miss", ttl
        finally:
            # unlock seguro (só dono)
            def _unlock() -> None:
                r = get_redis()
                if r.get(lock_key) == token:
                    r.delete(lock_key)

            _redis_call(_unlock)
    # outro fill em andamento — espera o valor aparecer
    _stats["stampede_waits"] += 1
    deadline = time.time() + 4.0
    while time.time() < deadline:
        cached = _cache_get(key)
        if cached is not None:
            _stats["hits"] += 1
            return cached, "hit-wait", None
        time.sleep(0.05)
    _stats["misses"] += 1
    payload, ttl = _fill_apos_miss(aluno_id, key)
    return payload, "miss-timeout", ttl


def obter_boletim(aluno_id: str) -> dict:
    inicio = time.perf_counter()
    key = _cache_key(aluno_id)

    if cache_backend == "off":
        _stats["misses"] += 1
        payload = ler_fonte(aluno_id)
        return _embalar(payload, cache="off", servido_de="postgres", inicio=inicio)

    if (
        stampede_lock
        and cache_backend == "redis"
        and _cache_get(key) is None
    ):
        payload, origem, ttl = _get_com_stampede_lock(aluno_id, key)
        servido = (
            _servido_de_cache()
            if origem in ("hit", "hit-wait")
            else "postgres"
        )
        return _embalar(
            payload, cache=origem, servido_de=servido, inicio=inicio, ttl=ttl
        )

    cached = _cache_get(key)
    if cached is not None:
        _stats["hits"] += 1
        return _embalar(
            cached, cache="hit", servido_de=_servido_de_cache(), inicio=inicio
        )

    _stats["misses"] += 1
    payload, ttl = _fill_apos_miss(aluno_id, key)
    return _embalar(
        payload, cache="miss", servido_de="postgres", inicio=inicio, ttl=ttl
    )


def atualizar_nota(aluno_id: str, nota: float) -> dict:
    inicio = time.perf_counter()
    with conectar() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                UPDATE boletim
                SET nota = %s, atualizado_em = NOW()
                WHERE aluno_id = %s
                RETURNING aluno_id, disciplina_id, nota, atualizado_em
                """,
                (nota, aluno_id),
            )
            row = cur.fetchone()
            if not row:
                raise LookupError("aluno não encontrado")
            conn.commit()
            payload = {
                "aluno_id": row["aluno_id"],
                "disciplina_id": row["disciplina_id"],
                "nota": float(row["nota"]),
                "atualizado_em": row["atualizado_em"].isoformat(),
                "fonte_dados": "postgres",
            }

    key = _cache_key(aluno_id)
    invalidou = False
    if invalidate_on_write:
        _cache_del(key)
        invalidou = True
        _stats["invalidations"] += 1

    _stats["writes"] += 1
    return {
        **payload,
        "invalidou_cache": invalidou,
        "invalidate_on_write": invalidate_on_write,
        "duracao_ms": round((time.perf_counter() - inicio) * 1000, 2),
    }


def admin_config() -> dict:
    return {
        "store_hold_ms": store_hold_ms,
        "cache_backend": cache_backend,
        "cache_ttl_sec": cache_ttl_sec,
        "ttl_jitter_sec": ttl_jitter_sec,
        "invalidate_on_write": invalidate_on_write,
        "stampede_lock": stampede_lock,
        "stats": dict(_stats),
        "hit_rate": _hit_rate(),
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

        if path == "/health":
            self._json(200, {"ok": True, "servico": "api-cache-postgres"})
            return
        if path == "/admin/config":
            self._json(200, admin_config())
            return
        if path.startswith("/boletim/"):
            aluno_id = path.split("/", 2)[2]
            _stats["requests"] += 1
            t0 = time.perf_counter()
            try:
                self._json(200, obter_boletim(aluno_id))
            except LookupError as exc:
                self._json(404, {"erro": str(exc)})
            except CacheUnavailable as exc:
                self._json(
                    503,
                    {
                        "erro": str(exc),
                        "code": "redis_indisponivel",
                        "dica": "Exp. 5c: cache compartilhado parado = SPOF",
                    },
                )
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            finally:
                _lat_registrar((time.perf_counter() - t0) * 1000.0)
            return

        self._json(
            200,
            {
                "endpoints": [
                    "GET /boletim/{aluno_id}",
                    "PUT /boletim/{aluno_id}",
                    "GET /admin/config",
                    "POST /admin/store_hold_ms",
                    "POST /admin/cache_backend",
                    "POST /admin/cache_ttl_sec",
                    "POST /admin/ttl_jitter_sec",
                    "POST /admin/invalidate_on_write",
                    "POST /admin/stampede_lock",
                    "POST /admin/flush_cache",
                    "POST /admin/stats_reset",
                    "GET /health",
                ]
            },
        )

    def do_PUT(self) -> None:
        path = urlparse(self.path).path.rstrip("/") or "/"
        if not path.startswith("/boletim/"):
            self._json(404, {"erro": "rota não encontrada"})
            return
        aluno_id = path.split("/", 2)[2]
        body = self._read_json()
        try:
            nota = float(body["nota"])
        except (KeyError, TypeError, ValueError):
            self._json(400, {"erro": "corpo: {\"nota\": number}"})
            return
        try:
            self._json(200, atualizar_nota(aluno_id, nota))
        except LookupError as exc:
            self._json(404, {"erro": str(exc)})
        except CacheUnavailable as exc:
            self._json(
                503,
                {
                    "erro": str(exc),
                    "code": "redis_indisponivel",
                    "dica": "Exp. 5c: cache compartilhado parado = SPOF",
                },
            )
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc)})

    def do_POST(self) -> None:
        global store_hold_ms, cache_backend, cache_ttl_sec
        global invalidate_on_write, stampede_lock, ttl_jitter_sec
        path = urlparse(self.path).path.rstrip("/") or "/"
        body = self._read_json()

        if path == "/admin/store_hold_ms":
            store_hold_ms = int(body.get("ms", 0))
            self._json(200, admin_config())
            return
        if path == "/admin/cache_backend":
            backend = str(body.get("backend", "redis")).lower()
            if backend not in ("redis", "local", "off"):
                self._json(400, {"erro": "backend: redis|local|off"})
                return
            cache_backend = backend
            self._json(200, admin_config())
            return
        if path == "/admin/cache_ttl_sec":
            cache_ttl_sec = max(1, int(body.get("sec", 60)))
            self._json(200, admin_config())
            return
        if path == "/admin/ttl_jitter_sec":
            ttl_jitter_sec = max(0, int(body.get("sec", 0)))
            self._json(200, admin_config())
            return
        if path == "/admin/invalidate_on_write":
            invalidate_on_write = bool(body.get("enabled", True))
            self._json(200, admin_config())
            return
        if path == "/admin/stampede_lock":
            stampede_lock = bool(body.get("enabled", True))
            self._json(200, admin_config())
            return
        if path == "/admin/flush_cache":
            _cache_flush()
            self._json(200, {"ok": True, **admin_config()})
            return
        if path == "/admin/stats_reset":
            for k in _stats:
                _stats[k] = 0
            with _lat_lock:
                _latencias_ms.clear()
            self._json(200, admin_config())
            return

        self._json(404, {"erro": "rota não encontrada"})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] cache-postgres ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

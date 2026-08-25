"""
API — feed de avisos com cache-aside (Redis / local / off).

Domínio tolerante a stale: TTL generoso; invalidação opcional (padrão OFF).
INSTANCE_ID: identifica a réplica (api1 / api2) para o Exp. local vs compartilhado.
"""

from __future__ import annotations

import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import redis
from pymongo import MongoClient, DESCENDING

PORT = int(os.environ.get("PORT", "8000"))
INSTANCE_ID = os.environ.get("INSTANCE_ID", "api")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.environ.get("MONGO_DB", "portal")
COLL = "avisos"
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

store_hold_ms = int(os.environ.get("STORE_HOLD_MS", "0"))
cache_backend = os.environ.get("CACHE_BACKEND", "redis").lower()
cache_ttl_sec = int(os.environ.get("CACHE_TTL_SEC", "30"))
invalidate_on_write = os.environ.get("INVALIDATE_ON_WRITE", "0") in (
    "1",
    "true",
    "True",
)

client: MongoClient | None = None
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
}
_lat_lock = threading.Lock()
_latencias_ms: list[float] = []
_LAT_MAX = 300

FEED_KEY = "avisos:feed"


def get_mongo():
    global client
    if client is None:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client[DB_NAME][COLL]


def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis


def esperar() -> None:
    ultimo: Exception | None = None
    for _ in range(60):
        try:
            get_mongo().database.client.admin.command("ping")
            if cache_backend == "redis":
                get_redis().ping()
            print(f"[{INSTANCE_ID}] mongo + deps ok", flush=True)
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            time.sleep(2)
    raise SystemExit(f"dependências indisponíveis: {ultimo}")


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
    raw = get_redis().get(key)
    if raw is None:
        return None
    return json.loads(raw)


def _cache_set(key: str, payload: dict) -> int:
    ttl = max(1, cache_ttl_sec)
    if cache_backend == "off":
        return ttl
    if cache_backend == "local":
        with _local_lock:
            _local_cache[key] = (time.time() + ttl, dict(payload))
        return ttl
    get_redis().set(key, json.dumps(payload, ensure_ascii=False, default=str), ex=ttl)
    return ttl


def _cache_del(key: str) -> None:
    if cache_backend == "local":
        with _local_lock:
            _local_cache.pop(key, None)
        return
    if cache_backend == "redis":
        get_redis().delete(key)


def _cache_flush() -> None:
    if cache_backend == "local":
        with _local_lock:
            _local_cache.clear()
        return
    if cache_backend == "redis":
        get_redis().delete(FEED_KEY)


def ler_fonte(limite: int = 20) -> dict:
    if store_hold_ms > 0:
        time.sleep(store_hold_ms / 1000.0)
    _stats["store_reads"] += 1
    coll = get_mongo()
    docs = list(
        coll.find({}, {"_id": 0}).sort("publicado_em", DESCENDING).limit(limite)
    )
    return {
        "total": coll.count_documents({}),
        "avisos": docs,
        "fonte_dados": "mongodb",
    }


def _servido_de_cache() -> str:
    if cache_backend == "redis":
        return "redis"
    if cache_backend == "local":
        return "local"
    return "mongodb"


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
    out["servido_por"] = INSTANCE_ID  # qual réplica de API atendeu
    if ttl is not None:
        out["ttl_sec_aplicado"] = ttl
    out["duracao_ms"] = round((time.perf_counter() - inicio) * 1000, 2)
    return out


def listar_feed(limite: int = 20) -> dict:
    inicio = time.perf_counter()
    key = FEED_KEY

    if cache_backend == "off":
        _stats["misses"] += 1
        payload = ler_fonte(limite)
        return _embalar(payload, cache="off", servido_de="mongodb", inicio=inicio)

    cached = _cache_get(key)
    if cached is not None:
        _stats["hits"] += 1
        return _embalar(
            cached, cache="hit", servido_de=_servido_de_cache(), inicio=inicio
        )

    _stats["misses"] += 1
    payload = ler_fonte(limite)
    # guarda só o feed (sem metadados de resposta)
    ttl = _cache_set(
        key,
        {
            "total": payload["total"],
            "avisos": payload["avisos"],
            "fonte_dados": payload["fonte_dados"],
        },
    )
    return _embalar(
        payload, cache="miss", servido_de="mongodb", inicio=inicio, ttl=ttl
    )


def _now_iso() -> str:
    # milissegundos: ordenação estável quando vários avisos saem no mesmo segundo
    ms = int(time.time() * 1000)
    return (
        time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ms / 1000.0))
        + f".{ms % 1000:03d}Z"
    )


def publicar(titulo: str, corpo: str, campus_id: str) -> dict:
    inicio = time.perf_counter()
    doc = {
        "titulo": titulo,
        "corpo": corpo,
        "campus_id": campus_id,
        "publicado_em": _now_iso(),
        "publicado_via": INSTANCE_ID,
    }
    get_mongo().insert_one(dict(doc))
    doc.pop("_id", None)

    invalidou = False
    if invalidate_on_write:
        _cache_del(FEED_KEY)
        invalidou = True
        _stats["invalidations"] += 1

    _stats["writes"] += 1
    return {
        **doc,
        "invalidou_cache": invalidou,
        "invalidate_on_write": invalidate_on_write,
        "duracao_ms": round((time.perf_counter() - inicio) * 1000, 2),
    }


def admin_config() -> dict:
    return {
        "instance_id": INSTANCE_ID,
        "store_hold_ms": store_hold_ms,
        "cache_backend": cache_backend,
        "cache_ttl_sec": cache_ttl_sec,
        "invalidate_on_write": invalidate_on_write,
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
        q = parse_qs(parsed.query)

        if path == "/health":
            self._json(
                200,
                {"ok": True, "servico": "api-cache-mongodb", "instance_id": INSTANCE_ID},
            )
            return
        if path == "/admin/config":
            self._json(200, admin_config())
            return
        if path == "/avisos":
            limite = int(q.get("limite", ["20"])[0])
            _stats["requests"] += 1
            t0 = time.perf_counter()
            try:
                self._json(200, listar_feed(limite))
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            finally:
                _lat_registrar((time.perf_counter() - t0) * 1000.0)
            return

        self._json(
            200,
            {
                "instance_id": INSTANCE_ID,
                "endpoints": [
                    "GET /avisos",
                    "POST /avisos",
                    "GET /admin/config",
                    "POST /admin/store_hold_ms",
                    "POST /admin/cache_backend",
                    "POST /admin/cache_ttl_sec",
                    "POST /admin/invalidate_on_write",
                    "POST /admin/flush_cache",
                    "POST /admin/stats_reset",
                    "GET /health",
                ],
            },
        )

    def do_POST(self) -> None:
        global store_hold_ms, cache_backend, cache_ttl_sec, invalidate_on_write
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
            cache_ttl_sec = max(1, int(body.get("sec", 30)))
            self._json(200, admin_config())
            return
        if path == "/admin/invalidate_on_write":
            invalidate_on_write = bool(body.get("enabled", True))
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

        if path != "/avisos":
            self._json(404, {"erro": "rota não encontrada"})
            return

        try:
            titulo = body["titulo"]
            corpo = body.get("corpo", "")
            campus_id = body.get("campus_id", "REC")
        except KeyError:
            self._json(400, {"erro": "corpo: titulo (obrigatório), corpo, campus_id"})
            return

        try:
            self._json(201, publicar(titulo, corpo, campus_id))
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc)})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{INSTANCE_ID}] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar()
    # seed mínimo se vazio
    if get_mongo().count_documents({}) == 0:
        get_mongo().insert_one(
            {
                "titulo": "Bem-vindos",
                "corpo": "Aviso inicial do lab de cache",
                "campus_id": "REC",
                "publicado_em": _now_iso(),
                "publicado_via": "seed",
            }
        )
        print(f"[{INSTANCE_ID}] seed avisos ok", flush=True)

    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[{INSTANCE_ID}] cache-mongodb ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

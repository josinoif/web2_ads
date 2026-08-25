"""Encurtador didático: contador (base62) vs hash truncado + cache Redis.

Store = dict no processo com delay injetável (não é Postgres).
Redis = cache do GET + sequenciador no modo contador.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
from http.server import ThreadingHTTPServer

import redis

from common import JsonHandler

PORT = int(os.environ.get("PORT", "8000"))
MODO = os.environ.get("MODO", "contador")  # contador | hash
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
ALPH = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

r = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=0.5,
    socket_timeout=0.5,
)

state = {
    "store_hold_ms": int(os.environ.get("STORE_HOLD_MS", "20")),
    "cache_ttl_sec": int(os.environ.get("CACHE_TTL_SEC", "60")),
    "cache_enabled": os.environ.get("CACHE_ENABLED", "1") not in ("0", "false", "False"),
    "redirect_code": int(os.environ.get("REDIRECT_CODE", "302")),
    "hash_chars": int(os.environ.get("HASH_CHARS", "4")),
    "colisoes": 0,
    "lookups": 0,
    "hits": 0,
    "misses": 0,
}

store: dict[str, str] = {}
url_index: dict[str, str] = {}  # url -> codigo (dedup)
idem_index: dict[str, str] = {}  # Idempotency-Key -> codigo
lock = threading.Lock()
PREFIX = "c" if MODO == "contador" else "h"


def b62(n: int) -> str:
    if n <= 0:
        return ALPH[0]
    s: list[str] = []
    while n:
        n, rem = divmod(n, 62)
        s.append(ALPH[rem])
    return "".join(reversed(s))


def cache_key(code: str) -> str:
    return f"{PREFIX}:url:{code}"


def next_counter_code() -> str:
    n = int(r.incr(f"{PREFIX}:seq"))
    return b62(n + 1000)


def redis_get(key: str) -> str | None:
    try:
        return r.get(key)
    except redis.RedisError:
        return None


def redis_setex(key: str, ttl: int, value: str) -> None:
    try:
        r.setex(key, ttl, value)
    except redis.RedisError:
        pass


def hash_code(url: str, salt: str = "") -> str:
    raw = hashlib.md5(f"{url}|{salt}".encode(), usedforsecurity=False).hexdigest()
    return raw[: state["hash_chars"]]


def allocate_code(url: str) -> tuple[str, bool]:
    """Retorna (codigo, houve_colisao_na_primeira_tentativa)."""
    if MODO == "contador":
        return next_counter_code(), False

    first = hash_code(url)
    with lock:
        existing = store.get(first)
        if existing is None:
            return first, False
        if existing == url:
            return first, False
        state["colisoes"] += 1
        n = 0
        while True:
            n += 1
            cand = hash_code(url, salt=str(n))
            got = store.get(cand)
            if got is None or got == url:
                return cand, True


def store_get(code: str) -> str | None:
    time.sleep(state["store_hold_ms"] / 1000.0)
    with lock:
        return store.get(code)


def store_put(code: str, url: str) -> None:
    time.sleep(state["store_hold_ms"] / 1000.0)
    with lock:
        store[code] = url
        url_index[url] = code


class Handler(JsonHandler):
    def do_HEAD(self) -> None:
        """curl -I usa HEAD — mesmo caminho do GET no redirect."""
        path = self._path()
        if path.startswith("/r/"):
            code = path.split("/", 2)[2]
            self._lookup(code, as_json=False, head_only=True)
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

    def do_GET(self) -> None:
        path = self._path()
        if path == "/health":
            with lock:
                n = len(store)
                col = state["colisoes"]
            self._json(
                200,
                {
                    "ok": True,
                    "service": "encurtador",
                    "modo": MODO,
                    "urls": n,
                    "colisoes": col,
                    "cache_enabled": state["cache_enabled"],
                    "store_hold_ms": state["store_hold_ms"],
                    "redirect_code": state["redirect_code"],
                    "hash_chars": state["hash_chars"],
                    "lookups": state["lookups"],
                    "cache_hits": state["hits"],
                    "cache_misses": state["misses"],
                },
            )
            return
        if path == "/admin/config":
            self._json(200, {**{k: state[k] for k in (
                "store_hold_ms",
                "cache_ttl_sec",
                "cache_enabled",
                "redirect_code",
                "hash_chars",
                "colisoes",
                "lookups",
                "hits",
                "misses",
            )}, "modo": MODO, "urls": len(store)})
            return
        if path.startswith("/lookup/"):
            code = path.split("/", 2)[2]
            self._lookup(code, as_json=True)
            return
        if path.startswith("/r/"):
            code = path.split("/", 2)[2]
            self._lookup(code, as_json=False)
            return
        self._json(404, {"erro": "não encontrado"})

    def _lookup(self, code: str, as_json: bool, head_only: bool = False) -> None:
        state["lookups"] += 1
        t0 = time.perf_counter()
        fonte = "store"
        url = None
        if state["cache_enabled"]:
            cached = redis_get(cache_key(code))
            if cached:
                state["hits"] += 1
                url = cached
                fonte = "cache"
        if url is None:
            state["misses"] += 1
            url = store_get(code)
            if url is not None and state["cache_enabled"]:
                redis_setex(cache_key(code), state["cache_ttl_sec"], url)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        if url is None:
            if head_only:
                self.send_response(404)
                self.end_headers()
                return
            self._json(404, {"erro": "código desconhecido", "codigo": code, "tempo_ms": ms})
            return
        if as_json:
            self._json(
                200,
                {"codigo": code, "url": url, "fonte": fonte, "tempo_ms": ms, "modo": MODO},
            )
            return
        extra = {}
        if state["redirect_code"] == 301:
            extra["Cache-Control"] = "public, max-age=86400"
        elif state["redirect_code"] == 302:
            extra["Cache-Control"] = "no-store"
        extra["X-Fonte"] = fonte
        extra["X-Tempo-Ms"] = str(ms)
        self._redirect(state["redirect_code"], url, extra, head_only=head_only)

    def do_POST(self) -> None:
        path = self._path()
        if path == "/admin/config":
            body = self._read_json()
            if "store_hold_ms" in body:
                state["store_hold_ms"] = int(body["store_hold_ms"])
            if "cache_ttl_sec" in body:
                state["cache_ttl_sec"] = int(body["cache_ttl_sec"])
            if "cache_enabled" in body:
                v = body["cache_enabled"]
                state["cache_enabled"] = v not in (0, False, "0", "false", "False")
            if "redirect_code" in body:
                rc = int(body["redirect_code"])
                if rc not in (301, 302):
                    self._json(400, {"erro": "redirect_code deve ser 301 ou 302"})
                    return
                state["redirect_code"] = rc
            if "hash_chars" in body:
                state["hash_chars"] = max(2, min(8, int(body["hash_chars"])))
            if body.get("flush_cache"):
                for k in r.scan_iter(f"{PREFIX}:url:*"):
                    r.delete(k)
            if body.get("reset_store"):
                with lock:
                    store.clear()
                    url_index.clear()
                    idem_index.clear()
                    state["colisoes"] = 0
                    state["lookups"] = 0
                    state["hits"] = 0
                    state["misses"] = 0
            self._json(200, {"ok": True, "config": {
                "store_hold_ms": state["store_hold_ms"],
                "cache_enabled": state["cache_enabled"],
                "redirect_code": state["redirect_code"],
                "hash_chars": state["hash_chars"],
            }})
            return

        if path != "/encurtar":
            self._json(404, {"erro": "não encontrado"})
            return

        body = self._read_json()
        url = (body.get("url") or "").strip()
        if not url:
            self._json(400, {"erro": "url obrigatória"})
            return
        idem = (self.headers.get("Idempotency-Key") or body.get("idempotency_key") or "").strip()

        with lock:
            if idem and idem in idem_index:
                code = idem_index[idem]
                existing = store.get(code)
                hit = ("idempotency_key", code, existing)
            elif url in url_index:
                code = url_index[url]
                hit = ("url_dedup", code, store.get(code))
            else:
                hit = None

        if hit is not None:
            via, code, existing = hit
            if via == "idempotency_key" and existing is not None and existing != url:
                self._json(409, {"erro": "Idempotency-Key reutilizada com URL diferente", "codigo": code})
                return
            if via == "url_dedup" and idem:
                with lock:
                    idem_index[idem] = code
            self._json(
                200,
                {
                    "codigo": code,
                    "url": url,
                    "modo": MODO,
                    "colisao": False,
                    "idempotente": True,
                    "via": via,
                    "tempo_ms": 0,
                    "lookup": f"/lookup/{code}",
                    "redirect": f"/r/{code}",
                },
            )
            return

        t0 = time.perf_counter()
        try:
            code, colidiu = allocate_code(url)
        except redis.RedisError as e:
            self._json(
                503,
                {
                    "erro": "redis indisponível",
                    "modo": MODO,
                    "detalhe": str(e),
                    "dica": "contador precisa de INCR; hash usa só o store local no POST",
                },
            )
            return
        store_put(code, url)
        if idem:
            with lock:
                idem_index[idem] = code
        if state["cache_enabled"]:
            redis_setex(cache_key(code), state["cache_ttl_sec"], url)
        ms = round((time.perf_counter() - t0) * 1000, 1)
        self._json(
            201,
            {
                "codigo": code,
                "url": url,
                "modo": MODO,
                "colisao": colidiu,
                "idempotente": False,
                "tempo_ms": ms,
                "lookup": f"/lookup/{code}",
                "redirect": f"/r/{code}",
            },
        )


def main() -> None:
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"encurtador modo={MODO} port={PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()

"""API com rate limit em janela fixa (fixed window) via Redis.

Implementação: INCR + EXPIRE na janela. Não é token bucket nem sliding window.

FAIL_MODE=closed → Redis down = 503 (não atende)
FAIL_MODE=open   → Redis down = deixa passar (fail-open)
"""

from __future__ import annotations

import os
import time
from http.server import ThreadingHTTPServer

import redis

from common import JsonHandler

PORT = int(os.environ.get("PORT", "8000"))
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
FAIL_MODE = os.environ.get("FAIL_MODE", "closed")  # closed | open
LIMIT = int(os.environ.get("RATE_LIMIT", "5"))
WINDOW_SEC = int(os.environ.get("RATE_WINDOW_SEC", "10"))

r = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=0.5,
    socket_timeout=0.5,
)

stats = {"ok": 0, "limited": 0, "fail_open": 0, "fail_closed": 0}


def check_limit(key: str) -> tuple[bool, str, int]:
    """Retorna (allowed, motivo, remaining)."""
    bucket = f"rl:{key}"
    try:
        n = int(r.incr(bucket))
        if n == 1:
            r.expire(bucket, WINDOW_SEC)
        ttl = int(r.ttl(bucket) or WINDOW_SEC)
        if n > LIMIT:
            return False, "rate_limited", 0
        return True, "ok", max(0, LIMIT - n)
    except redis.RedisError as e:
        if FAIL_MODE == "open":
            return True, f"fail_open:{e}", -1
        return False, f"fail_closed:{e}", 0


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self._path()
        if path == "/health":
            redis_ok = False
            try:
                redis_ok = r.ping() is True
            except redis.RedisError:
                pass
            self._json(
                200,
                {
                    "ok": True,
                    "service": "rate-limiter",
                    "fail_mode": FAIL_MODE,
                    "limit": LIMIT,
                    "window_sec": WINDOW_SEC,
                    "redis_ok": redis_ok,
                    "stats": stats,
                },
            )
            return
        if path == "/admin/config":
            self._json(200, {"fail_mode": FAIL_MODE, "limit": LIMIT, "window_sec": WINDOW_SEC, "stats": stats})
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self._path()
        if path == "/admin/reset":
            try:
                for k in r.scan_iter("rl:*"):
                    r.delete(k)
            except redis.RedisError:
                pass
            stats["ok"] = stats["limited"] = stats["fail_open"] = stats["fail_closed"] = 0
            self._json(200, {"ok": True, "stats": stats})
            return

        if path != "/api":
            self._json(404, {"erro": "não encontrado"})
            return

        body = self._read_json()
        key = (body.get("key") or self.headers.get("X-Api-Key") or "anon").strip() or "anon"
        t0 = time.perf_counter()
        allowed, motivo, remaining = check_limit(key)
        ms = round((time.perf_counter() - t0) * 1000, 1)

        if not allowed:
            if motivo.startswith("fail_closed"):
                stats["fail_closed"] += 1
                self._json(
                    503,
                    {
                        "erro": "rate limiter indisponível (fail-closed)",
                        "motivo": motivo,
                        "fail_mode": FAIL_MODE,
                        "tempo_ms": ms,
                    },
                )
                return
            stats["limited"] += 1
            self._json(
                429,
                {
                    "erro": "too many requests",
                    "key": key,
                    "limit": LIMIT,
                    "window_sec": WINDOW_SEC,
                    "remaining": remaining,
                    "tempo_ms": ms,
                },
            )
            return

        if motivo.startswith("fail_open"):
            stats["fail_open"] += 1
        else:
            stats["ok"] += 1
        self._json(
            200,
            {
                "ok": True,
                "key": key,
                "remaining": remaining,
                "motivo": motivo,
                "fail_mode": FAIL_MODE,
                "echo": body.get("echo", "pong"),
                "tempo_ms": ms,
            },
        )


def main() -> None:
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"rate-limiter fail_mode={FAIL_MODE} limit={LIMIT}/{WINDOW_SEC}s port={PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()

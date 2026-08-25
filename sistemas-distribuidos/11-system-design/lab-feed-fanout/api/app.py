"""Feed didático: fan-out on write vs fan-out on read.

MODO=write → POST preenche inbox (inline ou via worker).
MODO=read  → POST só grava; GET junta os posts de quem o usuário segue.
"""

from __future__ import annotations

import json
import os
import time
from http.server import ThreadingHTTPServer

import redis

from common import JsonHandler

PORT = int(os.environ.get("PORT", "8000"))
MODO = os.environ.get("MODO", "write")  # write | read
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

state = {
    "fanout_mode": os.environ.get("FANOUT_MODE", "inline"),  # inline | worker
    "fanout_ms_per_follower": int(os.environ.get("FANOUT_MS_PER_FOLLOWER", "5")),
}


def fanout_to_followers(author: str, post_id: str) -> int:
    followers = list(r.smembers(f"user:{author}:followers"))
    delay = state["fanout_ms_per_follower"] / 1000.0
    for f in followers:
        r.lpush(f"inbox:{f}", post_id)
        if delay:
            time.sleep(delay)
    r.lpush(f"inbox:{author}", post_id)
    return len(followers)


def hydrate(ids: list[str]) -> list[dict]:
    out = []
    for pid in ids:
        data = r.hgetall(f"post:{pid}")
        if data:
            out.append(data)
    return out


def merge_read_feed(user: str, limit: int = 20) -> list[dict]:
    followees = list(r.smembers(f"user:{user}:following"))
    followees.append(user)
    posts: list[dict] = []
    delay = state["fanout_ms_per_follower"] / 1000.0
    for uid in followees:
        ids = r.lrange(f"posts_by:{uid}", 0, 19)
        if delay:
            time.sleep(delay)
        posts.extend(hydrate(ids))
    posts.sort(key=lambda p: float(p.get("ts", 0)), reverse=True)
    return posts[:limit]


class Handler(JsonHandler):
    def do_GET(self) -> None:
        path = self._path()
        if path == "/health":
            self._json(
                200,
                {
                    "ok": True,
                    "service": "feed",
                    "modo": MODO,
                    "fanout_mode": state["fanout_mode"] if MODO == "write" else "n/a",
                    "fanout_ms_per_follower": state["fanout_ms_per_follower"],
                    "users": r.scard("users"),
                    "posts": int(r.get("post:seq") or 0),
                    "fila_fanout": r.llen("fanout_q") if MODO == "write" else 0,
                },
            )
            return
        if path == "/admin/config":
            self._json(200, {"modo": MODO, **state})
            return
        if path.startswith("/users/") and path.count("/") == 2:
            uid = path.split("/")[2]
            if not r.sismember("users", uid):
                self._json(404, {"erro": "usuário desconhecido"})
                return
            self._json(
                200,
                {
                    "id": uid,
                    "followers": r.scard(f"user:{uid}:followers"),
                    "following": r.scard(f"user:{uid}:following"),
                    "inbox_len": r.llen(f"inbox:{uid}"),
                    "posts_len": r.llen(f"posts_by:{uid}"),
                },
            )
            return
        if path.startswith("/feed/"):
            uid = path.split("/")[2]
            t0 = time.perf_counter()
            if MODO == "write":
                ids = r.lrange(f"inbox:{uid}", 0, 19)
                items = hydrate(ids)
                origem = "inbox"
            else:
                items = merge_read_feed(uid)
                origem = "merge"
            ms = round((time.perf_counter() - t0) * 1000, 1)
            self._json(200, {"user": uid, "origem": origem, "tempo_ms": ms, "n": len(items), "items": items})
            return
        self._json(404, {"erro": "não encontrado"})

    def do_POST(self) -> None:
        path = self._path()
        if path == "/admin/config":
            body = self._read_json()
            if "fanout_mode" in body:
                mode = body["fanout_mode"]
                if mode not in ("inline", "worker"):
                    self._json(400, {"erro": "fanout_mode: inline|worker"})
                    return
                state["fanout_mode"] = mode
            if "fanout_ms_per_follower" in body:
                state["fanout_ms_per_follower"] = max(0, int(body["fanout_ms_per_follower"]))
            if body.get("reset"):
                r.flushdb()
            self._json(200, {"ok": True, **state})
            return

        if path == "/admin/seed":
            body = self._read_json()
            n = max(1, min(200, int(body.get("n", 40))))
            r.flushdb()
            r.sadd("users", "celeb", "leitor")
            for i in range(1, n + 1):
                uid = f"u{i}"
                r.sadd("users", uid)
                r.sadd("user:celeb:followers", uid)
                r.sadd(f"user:{uid}:following", "celeb")
                r.sadd(f"user:{uid}:followers", "leitor")  # inverted: leitor follows uid
                r.sadd("user:leitor:following", uid)
            for i in (2, 3, 4):
                if i <= n:
                    r.sadd("user:u1:followers", f"u{i}")
                    r.sadd(f"user:u{i}:following", "u1")
            # leitor also follows u1 → counted in u1 followers
            self._json(
                200,
                {
                    "ok": True,
                    "n": n,
                    "celeb_followers": r.scard("user:celeb:followers"),
                    "u1_followers": r.scard("user:u1:followers"),
                    "leitor_following": r.scard("user:leitor:following"),
                },
            )
            return

        if path == "/users":
            body = self._read_json()
            uid = (body.get("id") or "").strip()
            if not uid:
                self._json(400, {"erro": "id obrigatório"})
                return
            r.sadd("users", uid)
            self._json(201, {"id": uid})
            return

        if path == "/follow":
            body = self._read_json()
            follower = body.get("follower") or ""
            followee = body.get("followee") or ""
            if not follower or not followee:
                self._json(400, {"erro": "follower e followee"})
                return
            r.sadd("users", follower, followee)
            r.sadd(f"user:{followee}:followers", follower)
            r.sadd(f"user:{follower}:following", followee)
            self._json(200, {"ok": True, "follower": follower, "followee": followee})
            return

        if path != "/posts":
            self._json(404, {"erro": "não encontrado"})
            return

        body = self._read_json()
        author = (body.get("author") or "").strip()
        text = (body.get("text") or "").strip() or "(vazio)"
        if not author:
            self._json(400, {"erro": "author obrigatório"})
            return
        r.sadd("users", author)
        t0 = time.perf_counter()
        post_id = str(r.incr("post:seq"))
        ts = str(time.time())
        r.hset(f"post:{post_id}", mapping={"id": post_id, "author": author, "text": text, "ts": ts})
        r.lpush(f"posts_by:{author}", post_id)

        seguidores = int(r.scard(f"user:{author}:followers"))
        fanout = "none"
        if MODO == "write":
            if state["fanout_mode"] == "worker":
                r.lpush("fanout_q", json.dumps({"post_id": post_id, "author": author}))
                fanout = "enfileirado"
            else:
                fanout_to_followers(author, post_id)
                fanout = "inline"
        ms = round((time.perf_counter() - t0) * 1000, 1)
        code = 202 if fanout == "enfileirado" else 201
        self._json(
            code,
            {
                "id": post_id,
                "author": author,
                "modo": MODO,
                "fanout": fanout,
                "seguidores": seguidores,
                "tempo_ms": ms,
            },
        )


def main() -> None:
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"feed modo={MODO} port={PORT}", flush=True)
    httpd.serve_forever()


if __name__ == "__main__":
    main()

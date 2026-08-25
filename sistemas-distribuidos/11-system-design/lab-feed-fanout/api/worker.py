"""Consome fanout_q e preenche inboxes (só topologia write)."""

from __future__ import annotations

import json
import os
import time

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
MS = int(os.environ.get("FANOUT_MS_PER_FOLLOWER", "5"))

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def fanout(author: str, post_id: str) -> int:
    followers = list(r.smembers(f"user:{author}:followers"))
    delay = MS / 1000.0
    for f in followers:
        r.lpush(f"inbox:{f}", post_id)
        if delay:
            time.sleep(delay)
    r.lpush(f"inbox:{author}", post_id)
    return len(followers)


def main() -> None:
    print(f"worker fanout redis={REDIS_URL} ms/follower={MS}", flush=True)
    while True:
        item = r.brpop("fanout_q", timeout=5)
        if not item:
            continue
        _key, raw = item
        data = json.loads(raw)
        n = fanout(data["author"], data["post_id"])
        print(f"fanout post={data['post_id']} author={data['author']} followers={n}", flush=True)


if __name__ == "__main__":
    main()

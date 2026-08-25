"""
API — publicação de avisos com delay/falha, retry e dedup opcional (MongoDB).

REQUIRE_UNIQUE=0 → insert sempre (retry duplica documentos).
REQUIRE_UNIQUE=1 → upsert por aviso_id / Idempotency-Key (efeito único).
WRITE_CONCERN: 1 | majority (didático; single-node majority ≈ local).
"""

from __future__ import annotations

import json
import os
import random
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from pymongo import MongoClient, WriteConcern
from pymongo.errors import DuplicateKeyError

PORT = int(os.environ.get("PORT", "8000"))
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017")
DB_NAME = os.environ.get("MONGO_DB", "portal")
COLL = "avisos"

store_hold_ms = int(os.environ.get("STORE_HOLD_MS", "0"))
fail_rate = int(os.environ.get("FAIL_RATE", "0"))
require_unique = os.environ.get("REQUIRE_UNIQUE", "0") in ("1", "true", "True")
write_concern = os.environ.get("WRITE_CONCERN", "1")

client: MongoClient | None = None
_stats = {"ok": 0, "fail": 0, "dup_blocked": 0}


def get_coll():
    global client
    if client is None:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    wc = WriteConcern(w="majority" if write_concern == "majority" else int(write_concern))
    return client[DB_NAME].get_collection(COLL, write_concern=wc)


def esperar(tentativas: int = 60) -> None:
    ultimo: Exception | None = None
    for _ in range(tentativas):
        try:
            get_coll().database.client.admin.command("ping")
            print("[api] mongo ok", flush=True)
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            time.sleep(2)
    raise SystemExit(f"Mongo indisponível: {ultimo}")


def garantir_indice() -> None:
    coll = get_coll()
    try:
        coll.drop_index("aviso_id_unique")
    except Exception:  # noqa: BLE001
        pass
    if require_unique:
        # Lab: limpa avisos para o índice unique poder ser criado após Exp. duplicata.
        coll.delete_many({})
        coll.create_index("aviso_id", unique=True, name="aviso_id_unique")
        print("[api] índice unique aviso_id ATIVO (coleção limpa)", flush=True)
    else:
        print("[api] índice unique OFF (retry pode duplicar)", flush=True)


def publicar(titulo: str, corpo: str, aviso_id: str | None, campus_id: str) -> dict:
    inicio = time.perf_counter()
    if fail_rate > 0 and random.randint(1, 100) <= fail_rate:
        _stats["fail"] += 1
        raise RuntimeError(f"falha injetada (FAIL_RATE={fail_rate})")

    if store_hold_ms > 0:
        time.sleep(store_hold_ms / 1000.0)

    aid = aviso_id or str(uuid.uuid4())
    doc = {
        "aviso_id": aid,
        "campus_id": campus_id,
        "titulo": titulo,
        "corpo": corpo,
        "publicado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "store_hold_ms": store_hold_ms,
        "require_unique": require_unique,
        "write_concern": write_concern,
    }
    coll = get_coll()

    if require_unique:
        result = coll.update_one(
            {"aviso_id": aid},
            {"$setOnInsert": doc},
            upsert=True,
        )
        replay = result.matched_count > 0 and result.upserted_id is None
        if replay:
            existing = coll.find_one({"aviso_id": aid}, {"_id": 0})
            existing = existing or doc
            existing["idempotent_replay"] = True
            existing["duracao_ms"] = round((time.perf_counter() - inicio) * 1000, 2)
            _stats["ok"] += 1
            return existing
    else:
        # sempre insert — mesmo aviso_id pode repetir (sem unique)
        coll.insert_one(dict(doc))
        doc.pop("_id", None)

    doc["idempotent_replay"] = False
    doc["duracao_ms"] = round((time.perf_counter() - inicio) * 1000, 2)
    _stats["ok"] += 1
    return doc


def listar(limite: int = 50) -> dict:
    coll = get_coll()
    docs = list(coll.find({}, {"_id": 0}).sort("publicado_em", -1).limit(limite))
    return {"total": coll.count_documents({}), "avisos": docs}


def admin_config() -> dict:
    return {
        "store_hold_ms": store_hold_ms,
        "fail_rate": fail_rate,
        "require_unique": require_unique,
        "write_concern": write_concern,
        "stats": dict(_stats),
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
        path = urlparse(self.path).path.rstrip("/") or "/"
        if path == "/health":
            self._json(200, {"ok": True, "servico": "api-timeout-mongodb"})
            return
        if path == "/admin/config":
            self._json(200, admin_config())
            return
        if path == "/avisos":
            q = parse_qs(urlparse(self.path).query)
            limite = int(q.get("limite", ["50"])[0])
            self._json(200, listar(limite))
            return
        self._json(
            200,
            {
                "endpoints": [
                    "POST /avisos",
                    "GET /avisos",
                    "GET /admin/config",
                    "POST /admin/store_hold_ms",
                    "POST /admin/fail_rate",
                    "POST /admin/require_unique",
                    "GET /health",
                ]
            },
        )

    def do_POST(self) -> None:
        global store_hold_ms, fail_rate, require_unique, write_concern
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
        if path == "/admin/require_unique":
            require_unique = bool(body.get("enabled", True))
            garantir_indice()
            self._json(200, admin_config())
            return
        if path == "/admin/write_concern":
            write_concern = str(body.get("w", "1"))
            self._json(200, admin_config())
            return

        if path != "/avisos":
            self._json(404, {"erro": "rota não encontrada"})
            return

        titulo = body.get("titulo")
        if not titulo:
            self._json(400, {"erro": "titulo obrigatório"})
            return
        corpo = body.get("corpo", "")
        campus_id = body.get("campus_id", "A")
        aviso_id = (
            self.headers.get("Idempotency-Key")
            or body.get("aviso_id")
            or body.get("idempotency_key")
        )
        try:
            self._json(201, publicar(titulo, corpo, aviso_id, campus_id))
        except DuplicateKeyError:
            _stats["dup_blocked"] += 1
            self._json(409, {"erro": "aviso_id duplicado", "aviso_id": aviso_id})
        except Exception as exc:  # noqa: BLE001
            _stats["fail"] += 1
            self._json(503, {"erro": str(exc), "retryable": True})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar()
    garantir_indice()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] timeout-mongodb ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

"""
API do portal de notas — MongoDB replica set.

Escrita no primary; leitura com read preference primary ou secondary.
"""

from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from pymongo import MongoClient, ReadPreference, errors

PORT = int(os.environ.get("PORT", "8000"))
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0",
)
DB_NAME = os.environ.get("MONGO_DB", "portal")
COLL = "notas"

client: MongoClient | None = None


def get_client() -> MongoClient:
    global client
    if client is None:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    return client


def esperar_cluster(tentativas: int = 90) -> None:
    ultimo: Exception | None = None
    for _ in range(tentativas):
        try:
            c = get_client()
            c.admin.command("ping")
            info = c.admin.command("replSetGetStatus")
            if info.get("myState") in (1, 2):  # primary or secondary
                print(f"[api] replica set ok (state={info.get('myState')})", flush=True)
                return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
        time.sleep(2)
    raise SystemExit(f"MongoDB replica set indisponível: {ultimo}")


def coll_com_dest(dest: str):
    c = get_client()
    db = c[DB_NAME]
    if dest == "secondary":
        return db.get_collection(COLL, read_preference=ReadPreference.SECONDARY_PREFERRED)
    return db[COLL]


def upsert_nota(aluno_id: str, disciplina: str, valor: float) -> dict:
    doc = {
        "aluno_id": aluno_id,
        "disciplina": disciplina,
        "valor": valor,
        "atualizado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    coll = coll_com_dest("primary")
    coll.update_one(
        {"aluno_id": aluno_id, "disciplina": disciplina},
        {"$set": doc},
        upsert=True,
    )
    out = dict(doc)
    out["destino_escrita"] = "primary"
    return out


def listar_notas(aluno_id: str, dest: str) -> dict:
    coll = coll_com_dest(dest)
    rows = list(coll.find({"aluno_id": aluno_id}, {"_id": 0}).sort("disciplina", 1))
    return {
        "aluno_id": aluno_id,
        "destino_leitura": dest,
        "total": len(rows),
        "notas": rows,
    }


def status_replica_set() -> dict:
    c = get_client()
    status = c.admin.command("replSetGetStatus")
    membros = []
    for m in status.get("members", []):
        membros.append(
            {
                "name": m.get("name"),
                "stateStr": m.get("stateStr"),
                "health": m.get("health"),
                "optimeDate": str(m.get("optimeDate")),
            }
        )
    return {
        "set": status.get("set"),
        "myState": status.get("myState"),
        "membros": membros,
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
            self._json(200, {"ok": True, "servico": "api-notas-mongodb"})
            return

        if path == "/replicacao/status":
            try:
                self._json(200, status_replica_set())
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        if path.startswith("/notas/"):
            aluno_id = path.removeprefix("/notas/").strip("/")
            dest = query.get("dest", ["primary"])[0]
            if dest not in ("primary", "secondary"):
                self._json(400, {"erro": "dest deve ser primary ou secondary"})
                return
            try:
                self._json(200, listar_notas(aluno_id, dest))
            except errors.AutoReconnect as exc:
                self._json(503, {"erro": str(exc), "dica": "cluster pode estar elegendo primary"})
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc), "destino_leitura": dest})
            return

        self._json(
            200,
            {
                "endpoints": [
                    "POST /notas",
                    "GET /notas/{aluno_id}?dest=primary|secondary",
                    "GET /replicacao/status",
                    "GET /health",
                ]
            },
        )

    def do_POST(self) -> None:
        if urlparse(self.path).path.rstrip("/") != "/notas":
            self._json(404, {"erro": "rota não encontrada"})
            return
        body = self._read_json()
        try:
            aluno_id = body["aluno_id"]
            disciplina = body["disciplina"]
            valor = float(body["valor"])
        except (KeyError, TypeError, ValueError):
            self._json(400, {"erro": "corpo esperado: aluno_id, disciplina, valor"})
            return
        try:
            self._json(201, upsert_nota(aluno_id, disciplina, valor))
        except errors.AutoReconnect as exc:
            self._json(503, {"erro": str(exc), "dica": "primary indisponível — failover?"})
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc)})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_cluster()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

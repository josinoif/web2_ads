"""
API — feed de avisos com readConcern / writeConcern configuráveis.

Domínio tolerante (AP-ish): publicar e ler avisos com níveis de consistência diferentes.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from pymongo import MongoClient, ReadPreference, errors
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

PORT = int(os.environ.get("PORT", "8000"))
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0",
)
DB_NAME = os.environ.get("MONGO_DB", "portal")
COLL = "avisos"

client: MongoClient | None = None


def get_client() -> MongoClient:
    global client
    if client is None:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
    return client


def esperar_cluster(tentativas: int = 90) -> None:
    ultimo: Exception | None = None
    for _ in range(tentativas):
        try:
            c = get_client()
            c.admin.command("ping")
            info = c.admin.command("replSetGetStatus")
            if info.get("myState") in (1, 2):
                print(f"[api] replica set ok (state={info.get('myState')})", flush=True)
                return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
        time.sleep(2)
    raise SystemExit(f"MongoDB replica set indisponível: {ultimo}")


def write_concern_de(nivel: str) -> WriteConcern:
    if nivel == "majority":
        return WriteConcern(w="majority", wtimeout=8000)
    if nivel in ("w1", "local", "1"):
        return WriteConcern(w=1, wtimeout=8000)
    raise ValueError("writeConcern deve ser majority ou w1")


def read_concern_de(nivel: str) -> ReadConcern:
    if nivel == "majority":
        return ReadConcern(level="majority")
    if nivel == "local":
        return ReadConcern(level="local")
    raise ValueError("readConcern deve ser majority ou local")


def coll_leitura(dest: str, read_concern: str):
    c = get_client()
    db = c.get_database(
        DB_NAME,
        read_concern=read_concern_de(read_concern),
        read_preference=(
            ReadPreference.SECONDARY_PREFERRED if dest == "secondary" else ReadPreference.PRIMARY_PREFERRED
        ),
    )
    return db[COLL]


def publicar_aviso(titulo: str, corpo: str, write_concern: str) -> dict:
    doc = {
        "id": str(uuid.uuid4()),
        "titulo": titulo,
        "corpo": corpo,
        "publicado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    inicio = time.perf_counter()
    c = get_client()
    db = c.get_database(DB_NAME, write_concern=write_concern_de(write_concern))
    db[COLL].insert_one(doc)
    duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
    out = dict(doc)
    out.pop("_id", None)
    out["write_concern"] = write_concern
    out["duracao_ms"] = duracao_ms
    return out


def listar_avisos(dest: str, read_concern: str, limite: int = 20) -> dict:
    inicio = time.perf_counter()
    coll = coll_leitura(dest, read_concern)
    rows = list(
        coll.find({}, {"_id": 0})
        .sort("publicado_em", -1)
        .limit(limite)
    )
    duracao_ms = round((time.perf_counter() - inicio) * 1000, 2)
    return {
        "destino_leitura": dest,
        "read_concern": read_concern,
        "total": len(rows),
        "duracao_ms": duracao_ms,
        "avisos": rows,
        "aviso_ui": "Feed pode estar desatualizado sob partição — compare majority vs local",
    }


def status_consistencia() -> dict:
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
    primaries = [m for m in membros if m.get("stateStr") == "PRIMARY"]
    return {
        "set": status.get("set"),
        "myState": status.get("myState"),
        "membros": membros,
        "primary": primaries[0]["name"] if primaries else None,
        "interpretacao": "majority exige quórum; local/secondary pode ler valor antigo (AP-ish)",
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
            self._json(200, {"ok": True, "servico": "api-consistencia-mongodb"})
            return

        if path == "/consistencia/status":
            try:
                self._json(200, status_consistencia())
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        if path == "/avisos":
            dest = query.get("dest", ["primary"])[0]
            rc = query.get("readConcern", ["majority"])[0]
            limite = int(query.get("limit", ["20"])[0])
            if dest not in ("primary", "secondary"):
                self._json(400, {"erro": "dest deve ser primary ou secondary"})
                return
            try:
                self._json(200, listar_avisos(dest, rc, limite))
            except ValueError as exc:
                self._json(400, {"erro": str(exc)})
            except errors.OperationFailure as exc:
                self._json(503, {"erro": str(exc), "readConcern": rc})
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        self._json(
            200,
            {
                "endpoints": [
                    "POST /avisos?writeConcern=majority|w1",
                    "GET /avisos?dest=primary|secondary&readConcern=majority|local",
                    "GET /consistencia/status",
                    "GET /health",
                ]
            },
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") != "/avisos":
            self._json(404, {"erro": "rota não encontrada"})
            return
        query = parse_qs(parsed.query)
        wc = query.get("writeConcern", ["majority"])[0]
        body = self._read_json()
        try:
            titulo = body["titulo"]
            corpo = body.get("corpo", "")
        except KeyError:
            self._json(400, {"erro": "corpo esperado: titulo, corpo (opcional)"})
            return
        try:
            self._json(201, publicar_aviso(titulo, corpo, wc))
        except ValueError as exc:
            self._json(400, {"erro": str(exc)})
        except errors.WriteConcernError as exc:
            self._json(
                503,
                {
                    "erro": str(exc),
                    "write_concern": wc,
                    "dica": "majority falha se quórum indisponível — tente w1 ou cure partição",
                },
            )
        except errors.WTimeoutError as exc:
            self._json(503, {"erro": str(exc), "write_concern": wc})
        except errors.AutoReconnect as exc:
            self._json(503, {"erro": str(exc), "dica": "cluster elegendo primary?"})
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc)})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[api] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_cluster()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

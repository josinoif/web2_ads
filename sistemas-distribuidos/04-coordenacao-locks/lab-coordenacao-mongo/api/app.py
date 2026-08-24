"""
API — fila de reserva com Mongo (RMW vs atômico) e lock Redis.

Modos:
  rmw         — read-modify-write no documento (corrida)
  atomic      — findOneAndUpdate condicional
  redis-lock  — SET NX + operação + unlock seguro
"""

from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import redis
from pymongo import MongoClient, ReturnDocument
PORT = int(os.environ.get("PORT", "8000"))
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
DB_NAME = os.environ.get("MONGO_DB", "portal")
INSTANCE_ID = os.environ.get("INSTANCE_ID", "api-coordenacao")
RACE_DELAY_MS = int(os.environ.get("RACE_DELAY_MS", "150"))
LOCK_TTL_SEC = int(os.environ.get("LOCK_TTL_SEC", "10"))
MODOS = ("rmw", "atomic", "redis-lock")

mongo_client: MongoClient | None = None
redis_client: redis.Redis | None = None

UNLOCK_LUA = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


def get_mongo() -> MongoClient:
    global mongo_client
    if mongo_client is None:
        mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
    return mongo_client


def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client


def filas():
    return get_mongo()[DB_NAME]["filas_reserva"]


def esperar_servicos(tentativas: int = 60) -> None:
    ultimo: Exception | None = None
    for _ in range(tentativas):
        try:
            get_mongo().admin.command("ping")
            get_redis().ping()
            seed_inicial()
            print(f"[{INSTANCE_ID}] mongo + redis ok", flush=True)
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            time.sleep(2)
    raise SystemExit(f"Serviços indisponíveis: {ultimo}")


def seed_inicial() -> None:
    coll = filas()
    coll.create_index("disciplina_id", unique=True)
    coll.update_one(
        {"disciplina_id": "SD-101"},
        {
            "$setOnInsert": {
                "disciplina_id": "SD-101",
                "nome": "Sistemas Distribuídos",
                "vagas_restantes": 1,
                "reservas": [],
                "fencing_token": 0,
            }
        },
        upsert=True,
    )
    coll.update_one(
        {"disciplina_id": "BD-201"},
        {
            "$setOnInsert": {
                "disciplina_id": "BD-201",
                "nome": "Banco de Dados",
                "vagas_restantes": 30,
                "reservas": [],
                "fencing_token": 0,
            }
        },
        upsert=True,
    )


@contextmanager
def redis_lock(disciplina_id: str, hold_seconds: int = 0):
    r = get_redis()
    key = f"lock:reserva:{disciplina_id}"
    token = str(uuid.uuid4())
    # TTL fixo: hold > TTL simula lock órfão (não estender o TTL no hold).
    acquired = r.set(key, token, nx=True, ex=LOCK_TTL_SEC)
    if not acquired:
        raise ValueError("lock indisponível — outro processo reservando")
    fencing = int(r.incr(f"fencing:{disciplina_id}"))
    try:
        if hold_seconds > 0:
            time.sleep(hold_seconds)
        yield fencing
    finally:
        r.eval(UNLOCK_LUA, 1, key, token)


def reservar_rmw(disciplina_id: str, aluno_id: str) -> dict:
    inicio = time.perf_counter()
    coll = filas()
    doc = coll.find_one({"disciplina_id": disciplina_id})
    if not doc:
        raise LookupError("disciplina não encontrada")
    if int(doc.get("vagas_restantes", 0)) <= 0:
        raise ValueError("sem vagas")
    if any(r.get("aluno_id") == aluno_id for r in doc.get("reservas", [])):
        raise ValueError("já reservado")

    vagas_lidas = int(doc["vagas_restantes"])
    time.sleep(RACE_DELAY_MS / 1000.0)

    reserva = {
        "aluno_id": aluno_id,
        "api_instance": INSTANCE_ID,
        "modo": "rmw",
        "reservado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    coll.update_one(
        {"disciplina_id": disciplina_id},
        {
            "$inc": {"vagas_restantes": -1},
            "$push": {"reservas": reserva},
        },
    )
    atual = coll.find_one({"disciplina_id": disciplina_id}, {"_id": 0})
    return {
        "disciplina_id": disciplina_id,
        "aluno_id": aluno_id,
        "modo": "rmw",
        "api_instance": INSTANCE_ID,
        "vagas_lidas": vagas_lidas,
        "vagas_restantes": int(atual["vagas_restantes"]),
        "total_reservas": len(atual.get("reservas", [])),
        "duracao_ms": round((time.perf_counter() - inicio) * 1000, 2),
        "aviso": "RMW sem operação atômica — pode reservar além das vagas",
    }


def reservar_atomic(disciplina_id: str, aluno_id: str) -> dict:
    inicio = time.perf_counter()
    coll = filas()
    reserva = {
        "aluno_id": aluno_id,
        "api_instance": INSTANCE_ID,
        "modo": "atomic",
        "reservado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    doc = coll.find_one_and_update(
        {
            "disciplina_id": disciplina_id,
            "vagas_restantes": {"$gt": 0},
            "reservas.aluno_id": {"$ne": aluno_id},
        },
        {
            "$inc": {"vagas_restantes": -1},
            "$push": {"reservas": reserva},
        },
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0},
    )
    if not doc:
        existente = coll.find_one({"disciplina_id": disciplina_id})
        if not existente:
            raise LookupError("disciplina não encontrada")
        if any(r.get("aluno_id") == aluno_id for r in existente.get("reservas", [])):
            raise ValueError("já reservado")
        raise ValueError("sem vagas")
    return {
        "disciplina_id": disciplina_id,
        "aluno_id": aluno_id,
        "modo": "atomic",
        "api_instance": INSTANCE_ID,
        "vagas_restantes": int(doc["vagas_restantes"]),
        "total_reservas": len(doc.get("reservas", [])),
        "duracao_ms": round((time.perf_counter() - inicio) * 1000, 2),
    }


def reservar_redis_lock(
    disciplina_id: str,
    aluno_id: str,
    hold_seconds: int = 0,
) -> dict:
    inicio = time.perf_counter()
    with redis_lock(disciplina_id, hold_seconds=hold_seconds) as fencing_token:
        coll = filas()
        doc = coll.find_one({"disciplina_id": disciplina_id})
        if not doc:
            raise LookupError("disciplina não encontrada")
        stored = int(doc.get("fencing_token", 0))
        if fencing_token <= stored:
            raise ValueError("fencing token rejeitado — lock órfão ou escrita tardia")
        result = reservar_atomic(disciplina_id, aluno_id)
        coll.update_one(
            {"disciplina_id": disciplina_id, "fencing_token": {"$lt": fencing_token}},
            {"$set": {"fencing_token": fencing_token}},
        )
        result["fencing_token"] = fencing_token
        result["modo"] = "redis-lock"
        result["duracao_ms"] = round((time.perf_counter() - inicio) * 1000, 2)
        if hold_seconds > 0:
            result["hold_seconds"] = hold_seconds
        return result


def reservar(
    disciplina_id: str,
    aluno_id: str,
    modo: str,
    hold_seconds: int = 0,
) -> dict:
    if modo == "rmw":
        return reservar_rmw(disciplina_id, aluno_id)
    if modo == "atomic":
        return reservar_atomic(disciplina_id, aluno_id)
    if modo == "redis-lock":
        return reservar_redis_lock(disciplina_id, aluno_id, hold_seconds)
    raise ValueError(f"modo inválido: {modo}")


def ler_fila(disciplina_id: str) -> dict:
    doc = filas().find_one({"disciplina_id": disciplina_id}, {"_id": 0})
    if not doc:
        raise LookupError("disciplina não encontrada")
    doc["total_reservas"] = len(doc.get("reservas", []))
    doc["vagas_restantes"] = int(doc.get("vagas_restantes", 0))
    return doc


def status_coordenacao() -> dict:
    docs = list(filas().find({}, {"_id": 0}).sort("disciplina_id", 1))
    r = get_redis()
    locks = []
    for key in r.scan_iter("lock:reserva:*"):
        ttl = r.ttl(key)
        locks.append({"chave": key, "valor": r.get(key), "ttl_seg": ttl})
    sd101 = next((d for d in docs if d.get("disciplina_id") == "SD-101"), None)
    alerta = False
    if sd101:
        alerta = len(sd101.get("reservas", [])) > 1 or int(sd101.get("vagas_restantes", 0)) < 0
    return {
        "modo_lab": "coordenacao_mongo_redis",
        "api_instance": INSTANCE_ID,
        "modos_validos": list(MODOS),
        "filas": docs,
        "locks_ativos": locks,
        "alerta_overbooking_sd101": alerta,
        "interpretacao": (
            "Overbooking em SD-101 — compare rmw vs atomic/redis-lock"
            if alerta
            else "Estado consistente — provoque corrida com rmw + --paralelo"
        ),
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
            self._json(200, {"ok": True, "servico": "api-coordenacao-mongo", "api_instance": INSTANCE_ID})
            return

        if path == "/coordenacao/status":
            try:
                self._json(200, status_coordenacao())
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        if path.startswith("/filas/"):
            disciplina_id = path.removeprefix("/filas/").strip("/")
            try:
                self._json(200, ler_fila(disciplina_id))
            except LookupError as exc:
                self._json(404, {"erro": str(exc)})
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        self._json(
            200,
            {
                "modo_lab": "coordenacao_mongo_redis",
                "endpoints": [
                    "POST /reservar?mode=rmw|atomic|redis-lock&hold_seconds=0",
                    "GET /filas/{disciplina_id}",
                    "GET /coordenacao/status",
                    "GET /health",
                ],
            },
        )

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.rstrip("/") != "/reservar":
            self._json(404, {"erro": "rota não encontrada"})
            return
        query = parse_qs(parsed.query)
        modo = query.get("mode", ["atomic"])[0]
        hold_seconds = int(query.get("hold_seconds", ["0"])[0])
        if modo not in MODOS:
            self._json(400, {"erro": f"mode deve ser um de: {', '.join(MODOS)}"})
            return
        body = self._read_json()
        try:
            disciplina_id = body["disciplina_id"]
            aluno_id = body["aluno_id"]
        except KeyError:
            self._json(400, {"erro": "corpo esperado: disciplina_id, aluno_id"})
            return
        try:
            self._json(201, reservar(disciplina_id, aluno_id, modo, hold_seconds))
        except ValueError as exc:
            self._json(409, {"erro": str(exc), "modo": modo, "api_instance": INSTANCE_ID})
        except LookupError as exc:
            self._json(404, {"erro": str(exc)})
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc), "modo": modo})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{INSTANCE_ID}] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar_servicos()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[{INSTANCE_ID}] ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

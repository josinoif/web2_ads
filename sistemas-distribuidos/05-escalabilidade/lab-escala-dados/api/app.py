"""
API router — escala na camada de dados por partição (campus_id → mongo-a | mongo-b).

Não é Mongo Shard Cluster oficial: dois stores + roteamento na aplicação.
Demonstra hot key vs carga espalhada e custo de fan-out (leitura global).

WRITE_MS / READ_SHARD_MS = custos sintéticos para o ganho spread e o fan-out
ficarem mensuráveis no notebook (não são latência real de produção).
"""

from __future__ import annotations

import json
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from pymongo import MongoClient

PORT = int(os.environ.get("PORT", "8000"))
MONGO_A_URI = os.environ.get("MONGO_A_URI", "mongodb://mongo-a:27017")
MONGO_B_URI = os.environ.get("MONGO_B_URI", "mongodb://mongo-b:27017")
DB_NAME = os.environ.get("MONGO_DB", "portal")
INSTANCE_ID = os.environ.get("INSTANCE_ID", "api-router-dados")
COLL = "avisos"
WRITE_MS = int(os.environ.get("WRITE_MS", "8"))
READ_SHARD_MS = int(os.environ.get("READ_SHARD_MS", "20"))

client_a: MongoClient | None = None
client_b: MongoClient | None = None


def get_clients() -> tuple[MongoClient, MongoClient]:
    global client_a, client_b
    if client_a is None:
        client_a = MongoClient(MONGO_A_URI, serverSelectionTimeoutMS=5000)
    if client_b is None:
        client_b = MongoClient(MONGO_B_URI, serverSelectionTimeoutMS=5000)
    return client_a, client_b


def shard_de(campus_id: str) -> str:
    """Regra didática: campus A → mongo-a; demais → mongo-b (ou hash)."""
    c = (campus_id or "").strip().upper()
    if c in ("A", "CAMPUS-A", "RECIFE"):
        return "A"
    if c in ("B", "CAMPUS-B", "CARUARU"):
        return "B"
    return "A" if sum(ord(ch) for ch in c) % 2 == 0 else "B"


def coll_para(campus_id: str):
    a, b = get_clients()
    shard = shard_de(campus_id)
    client = a if shard == "A" else b
    return client[DB_NAME][COLL], shard


def esperar(tentativas: int = 60) -> None:
    ultimo: Exception | None = None
    for _ in range(tentativas):
        try:
            a, b = get_clients()
            a.admin.command("ping")
            b.admin.command("ping")
            print(f"[{INSTANCE_ID}] mongo-a + mongo-b ok", flush=True)
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            time.sleep(2)
    raise SystemExit(f"Mongo indisponível: {ultimo}")


def publicar(campus_id: str, titulo: str, corpo: str = "") -> dict:
    inicio = time.perf_counter()
    if WRITE_MS > 0:
        time.sleep(WRITE_MS / 1000.0)
    coll, shard = coll_para(campus_id)
    doc = {
        "id": str(uuid.uuid4()),
        "campus_id": campus_id,
        "titulo": titulo,
        "corpo": corpo,
        "shard": shard,
        "publicado_em": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    coll.insert_one(doc)
    doc.pop("_id", None)
    doc["duracao_ms"] = round((time.perf_counter() - inicio) * 1000, 2)
    doc["api_instance"] = INSTANCE_ID
    doc["write_ms"] = WRITE_MS
    return doc


def listar(campus_id: str | None, limite: int = 50) -> dict:
    inicio = time.perf_counter()
    if campus_id:
        if READ_SHARD_MS > 0:
            time.sleep(READ_SHARD_MS / 1000.0)
        coll, shard = coll_para(campus_id)
        rows = list(coll.find({"campus_id": campus_id}, {"_id": 0}).sort("publicado_em", -1).limit(limite))
        return {
            "modo": "single_shard",
            "campus_id": campus_id,
            "shard": shard,
            "total": len(rows),
            "duracao_ms": round((time.perf_counter() - inicio) * 1000, 2),
            "read_shard_ms": READ_SHARD_MS,
            "avisos": rows,
        }

    # Fan-out: custo por shard (paralelo) — wall clock ≈ max(custo_A, custo_B) + merge
    a, b = get_clients()

    def ler(client: MongoClient, rotulo: str):
        if READ_SHARD_MS > 0:
            time.sleep(READ_SHARD_MS / 1000.0)
        rows = list(
            client[DB_NAME][COLL]
            .find({}, {"_id": 0})
            .sort("publicado_em", -1)
            .limit(limite)
        )
        return rotulo, rows

    avisos: list[dict] = []
    with ThreadPoolExecutor(max_workers=2) as pool:
        futs = [pool.submit(ler, a, "A"), pool.submit(ler, b, "B")]
        por_shard = {}
        for fut in as_completed(futs):
            rotulo, rows = fut.result()
            por_shard[rotulo] = len(rows)
            avisos.extend(rows)
    avisos.sort(key=lambda x: x.get("publicado_em", ""), reverse=True)
    # Custo didático de agregar N shards (merge/sort) — em rede real o gap cresce com N e RTT
    if READ_SHARD_MS > 0:
        time.sleep(READ_SHARD_MS / 1000.0)
    return {
        "modo": "fanout_todos_shards",
        "total": len(avisos[:limite]),
        "por_shard": por_shard,
        "duracao_ms": round((time.perf_counter() - inicio) * 1000, 2),
        "read_shard_ms": READ_SHARD_MS,
        "avisos": avisos[:limite],
        "aviso_didatico": (
            "Fan-out: leituras em paralelo (~1× READ_SHARD_MS) + agregação (~+1×). "
            "Single ≈ 1×. Em produção o gap cresce com N shards e latência de rede."
        ),
    }


def status_escala() -> dict:
    a, b = get_clients()
    ca = a[DB_NAME][COLL].count_documents({})
    cb = b[DB_NAME][COLL].count_documents({})
    return {
        "modo_lab": "escala_dados",
        "camada": "dados",
        "api_instance": INSTANCE_ID,
        "write_ms": WRITE_MS,
        "read_shard_ms": READ_SHARD_MS,
        "shards": {
            "A": {"host": "mongo-a", "avisos": ca},
            "B": {"host": "mongo-b", "avisos": cb},
        },
        "regra": "campus A/RECIFE → shard A; B/CARUARU → shard B; outros por hash",
        "interpretacao": (
            "Evidência principal: distribuição hot vs spread nos shards. "
            "WRITE_MS torna o tempo de lote spread tipicamente menor que hot "
            "(dois stores em paralelo). Fan-out encarece leitura global. "
            "Réplica de leitura (02) é outra técnica da mesma camada."
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
        query = parse_qs(parsed.query)

        if path == "/health":
            self._json(200, {"ok": True, "servico": "api-escala-dados", "api_instance": INSTANCE_ID})
            return

        if path == "/escala/status":
            try:
                self._json(200, status_escala())
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        if path == "/avisos":
            campus = query.get("campus_id", [None])[0]
            limite = int(query.get("limit", ["50"])[0])
            try:
                self._json(200, listar(campus, limite))
            except Exception as exc:  # noqa: BLE001
                self._json(503, {"erro": str(exc)})
            return

        self._json(
            200,
            {
                "modo_lab": "escala_dados",
                "camada": "dados",
                "endpoints": [
                    "POST /avisos",
                    "GET /avisos?campus_id=A",
                    "GET /avisos  (fan-out)",
                    "GET /escala/status",
                    "GET /health",
                ],
            },
        )

    def do_POST(self) -> None:
        if urlparse(self.path).path.rstrip("/") != "/avisos":
            self._json(404, {"erro": "rota não encontrada"})
            return
        body = self._read_json()
        try:
            campus_id = body["campus_id"]
            titulo = body["titulo"]
        except KeyError:
            self._json(400, {"erro": "corpo esperado: campus_id, titulo, corpo?"})
            return
        try:
            self._json(201, publicar(campus_id, titulo, body.get("corpo", "")))
        except Exception as exc:  # noqa: BLE001
            self._json(503, {"erro": str(exc)})

    def log_message(self, fmt: str, *args) -> None:
        print(f"[{INSTANCE_ID}] {self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    esperar()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[{INSTANCE_ID}] ouvindo 0.0.0.0:{PORT}", flush=True)
    server.serve_forever()

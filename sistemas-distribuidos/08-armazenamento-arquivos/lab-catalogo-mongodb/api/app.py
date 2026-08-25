"""
API — catálogo de entregas com deduplicação content-addressable (SHA-256 → key MinIO).

Coleções:
  entregas  — registro lógico por aluno
  blobs     — { _id: sha256, object_key, n_referencias, tamanho_bytes }

READ_FROM_SECONDARY_SIM=1 → listagem lê um cache local atrasado (didático: catálogo stale).
REJECT_ON_INTEGRITY_FAIL: 1 → GET com hash divergente responde 409;
  0 (padrão) → 200 + X-Integridade: falha + body (soft verify didático).
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import boto3
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError
from bson import ObjectId
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError

PORT = int(os.environ.get("PORT", "8000"))
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017")
MONGO_DB = os.environ.get("MONGO_DB", "portal")
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "trabalhos")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "0") in ("1", "true", "True")

read_secondary_sim = os.environ.get("READ_FROM_SECONDARY_SIM", "0") in (
    "1",
    "true",
    "True",
)
reject_on_integrity_fail = os.environ.get("REJECT_ON_INTEGRITY_FAIL", "0") in (
    "1",
    "true",
    "True",
)
_config_lock = threading.Lock()
_stale_cache: list[dict] | None = None
_stale_lock = threading.Lock()

_client: MongoClient | None = None
_stats = {
    "uploads": 0,
    "dedup_hits": 0,
    "uploads_novos_blobs": 0,
    "deletes": 0,
    "integridade_falhas": 0,
}


def db():
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    return _client[MONGO_DB]


def _cfg_get_stale() -> bool:
    with _config_lock:
        return read_secondary_sim


def _cfg_set_stale(value: bool) -> None:
    global read_secondary_sim, _stale_cache
    with _config_lock:
        read_secondary_sim = value
    if not value:
        with _stale_lock:
            _stale_cache = None


def _cfg_get_reject_integrity() -> bool:
    with _config_lock:
        return reject_on_integrity_fail


def _cfg_set_reject_integrity(value: bool) -> None:
    global reject_on_integrity_fail
    with _config_lock:
        reject_on_integrity_fail = value


def _snapshot_entregas() -> int:
    global _stale_cache
    docs = list(db().entregas.find().sort("created_at", 1))
    rows = [serialize_entrega(d) for d in docs]
    with _stale_lock:
        _stale_cache = rows
    return len(rows)


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=("https://" if MINIO_SECURE else "http://") + MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def esperar() -> None:
    ultimo: Exception | None = None
    for _ in range(30):
        try:
            db().command("ping")
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            time.sleep(1)
    raise RuntimeError(f"Mongo indisponível: {ultimo}")


def put_if_absent(object_key: str, data: bytes, content_type: str) -> bool:
    """PutObject; retorna True se gravou, False se já existia."""
    client = s3_client()
    try:
        client.head_object(Bucket=MINIO_BUCKET, Key=object_key)
        return False
    except ClientError as exc:
        status = int(exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0))
        code = str(exc.response.get("Error", {}).get("Code", ""))
        if status not in (404,) and code not in ("404", "NoSuchKey", "NotFound"):
            raise RuntimeError(f"HeadObject: {exc}") from exc
    try:
        client.put_object(
            Bucket=MINIO_BUCKET,
            Key=object_key,
            Body=data,
            ContentType=content_type,
        )
        return True
    except (BotoCoreError, ClientError, OSError) as exc:
        raise RuntimeError(f"PutObject falhou: {exc}") from exc


def get_object(object_key: str) -> bytes:
    try:
        resp = s3_client().get_object(Bucket=MINIO_BUCKET, Key=object_key)
        return resp["Body"].read()
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in ("NoSuchKey", "404", "NotFound") or int(
            exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0)
        ) == 404:
            raise FileNotFoundError(object_key) from exc
        raise RuntimeError(str(exc)) from exc


def delete_object(object_key: str) -> None:
    try:
        s3_client().delete_object(Bucket=MINIO_BUCKET, Key=object_key)
    except (BotoCoreError, ClientError, OSError) as exc:
        raise RuntimeError(str(exc)) from exc


def list_keys() -> list[str]:
    client = s3_client()
    keys: list[str] = []
    token = None
    while True:
        kwargs = {"Bucket": MINIO_BUCKET}
        if token:
            kwargs["ContinuationToken"] = token
        resp = client.list_objects_v2(**kwargs)
        for item in resp.get("Contents") or []:
            keys.append(item["Key"])
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
    return keys


def serialize_entrega(doc: dict) -> dict:
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    if isinstance(out.get("created_at"), datetime):
        out["created_at"] = out["created_at"].isoformat()
    return out


def json_response(handler: BaseHTTPRequestHandler, code: int, body: dict) -> None:
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(raw)))
    handler.end_headers()
    handler.wfile.write(raw)


def read_body(handler: BaseHTTPRequestHandler) -> bytes:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    return handler.rfile.read(length) if length else b""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        print(f"[api] {self.address_string()} {fmt % args}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/health":
            try:
                db().command("ping")
                ok = True
                err = None
                try:
                    s3_client().head_bucket(Bucket=MINIO_BUCKET)
                except Exception as exc:  # noqa: BLE001
                    ok = False
                    err = str(exc)
                json_response(
                    self,
                    200 if ok else 503,
                    {"ok": ok, "storage_ok": ok, "storage_error": err},
                )
            except Exception as exc:  # noqa: BLE001
                json_response(self, 503, {"ok": False, "error": str(exc)})
            return

        if path == "/admin/config":
            json_response(
                self,
                200,
                {
                    "read_from_secondary_sim": _cfg_get_stale(),
                    "reject_on_integrity_fail": _cfg_get_reject_integrity(),
                    "bucket": MINIO_BUCKET,
                    "stats": _stats,
                },
            )
            return

        if path == "/admin/objetos":
            try:
                keys = list_keys()
                blobs = list(db().blobs.find())
                for b in blobs:
                    b["sha256"] = b.pop("_id")
                json_response(
                    self,
                    200,
                    {
                        "n_objetos_minio": len(keys),
                        "keys": keys,
                        "blobs": blobs,
                    },
                )
            except Exception as exc:  # noqa: BLE001
                json_response(self, 503, {"error": str(exc)})
            return

        if path == "/entregas":
            try:
                if _cfg_get_stale():
                    with _stale_lock:
                        cached = _stale_cache
                    if cached is not None:
                        json_response(
                            self,
                            200,
                            {
                                "entregas": cached,
                                "leitura": "stale_sim",
                                "aviso": "listagem de cache local (simula secondary atrasado)",
                            },
                        )
                        return
                docs = list(db().entregas.find().sort("created_at", 1))
                rows = [serialize_entrega(d) for d in docs]
                json_response(
                    self,
                    200,
                    {"entregas": rows, "leitura": "primary", "n": len(rows)},
                )
            except Exception as exc:  # noqa: BLE001
                json_response(self, 503, {"error": str(exc)})
            return

        if path.startswith("/entregas/") and path.endswith("/arquivo"):
            mid = path[len("/entregas/") : -len("/arquivo")]
            try:
                doc = db().entregas.find_one({"_id": ObjectId(mid)})
            except Exception:  # noqa: BLE001
                json_response(self, 400, {"error": "id inválido"})
                return
            if not doc:
                json_response(self, 404, {"error": "entrega não encontrada"})
                return
            try:
                data = get_object(doc["object_key"])
                digest = hashlib.sha256(data).hexdigest()
                integridade = "ok" if digest == doc["sha256"] else "falha"
                if integridade == "falha":
                    _stats["integridade_falhas"] += 1
                    if _cfg_get_reject_integrity():
                        json_response(
                            self,
                            409,
                            {
                                "error": "integridade falhou — bytes ≠ sha256 do metadado",
                                "code": "integridade_falha",
                                "integridade": "falha",
                                "sha256_metadado": doc["sha256"],
                                "sha256_bytes": digest,
                                "dica": "lab: REJECT_ON_INTEGRITY_FAIL=1 simula rejeição de produção",
                            },
                        )
                        return
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="{doc["nome_arquivo"]}"',
                )
                self.send_header("Content-Length", str(len(data)))
                self.send_header("X-Sha256", digest)
                self.send_header("X-Integridade", integridade)
                self.end_headers()
                self.wfile.write(data)
            except FileNotFoundError:
                json_response(
                    self,
                    404,
                    {
                        "error": "blob ausente no MinIO (metadado órfão?)",
                        "object_key": doc["object_key"],
                    },
                )
            except Exception as exc:  # noqa: BLE001
                json_response(self, 503, {"error": str(exc)})
            return

        json_response(self, 404, {"error": "não encontrado"})

    def do_PUT(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        body = read_body(self)
        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            json_response(self, 400, {"error": "JSON inválido"})
            return

        if path == "/admin/config":
            if "read_from_secondary_sim" in payload:
                raw = payload["read_from_secondary_sim"]
                if isinstance(raw, str):
                    enable = raw.lower() in ("1", "true", "yes")
                else:
                    enable = bool(raw)
                if enable:
                    _snapshot_entregas()
                _cfg_set_stale(enable)
            if "reject_on_integrity_fail" in payload:
                raw = payload["reject_on_integrity_fail"]
                if isinstance(raw, str):
                    _cfg_set_reject_integrity(raw.lower() in ("1", "true", "yes"))
                else:
                    _cfg_set_reject_integrity(bool(raw))
            json_response(
                self,
                200,
                {
                    "ok": True,
                    "read_from_secondary_sim": _cfg_get_stale(),
                    "reject_on_integrity_fail": _cfg_get_reject_integrity(),
                },
            )
            return

        json_response(self, 404, {"error": "não encontrado"})

    def do_DELETE(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        if not path.startswith("/entregas/"):
            json_response(self, 404, {"error": "não encontrado"})
            return
        mid = path[len("/entregas/") :]
        try:
            oid = ObjectId(mid)
        except Exception:  # noqa: BLE001
            json_response(self, 400, {"error": "id inválido"})
            return

        try:
            doc = db().entregas.find_one_and_delete({"_id": oid})
            if not doc:
                json_response(self, 404, {"error": "entrega não encontrada"})
                return
            sha = doc["sha256"]
            blob = db().blobs.find_one_and_update(
                {"_id": sha},
                {"$inc": {"n_referencias": -1}},
                return_document=ReturnDocument.AFTER,
            )
            removed_object = False
            if blob and blob.get("n_referencias", 0) <= 0:
                delete_object(blob["object_key"])
                db().blobs.delete_one({"_id": sha})
                removed_object = True
            _stats["deletes"] += 1
            json_response(
                self,
                200,
                {
                    "apagou_entrega": True,
                    "sha256": sha,
                    "n_referencias": (blob or {}).get("n_referencias", 0),
                    "removeu_objeto_minio": removed_object,
                },
            )
        except Exception as exc:  # noqa: BLE001
            json_response(self, 503, {"error": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/admin/snapshot-stale":
            n = _snapshot_entregas()
            json_response(self, 200, {"ok": True, "n": n})
            return

        if path != "/entregas":
            json_response(self, 404, {"error": "não encontrado"})
            return

        aluno_id = self.headers.get("X-Aluno-Id", "aluno-01")
        disciplina = self.headers.get("X-Disciplina", "SD")
        nome_arquivo = self.headers.get("X-Nome-Arquivo", "trabalho.bin")
        content_type = self.headers.get("Content-Type", "application/octet-stream")
        data = read_body(self)
        if not data:
            json_response(self, 400, {"error": "corpo vazio"})
            return

        sha = hashlib.sha256(data).hexdigest()
        object_key = f"sha256/{sha}"

        try:
            existing = db().blobs.find_one({"_id": sha})
            if existing:
                dedup = True
                updated = db().blobs.find_one_and_update(
                    {"_id": sha},
                    {"$inc": {"n_referencias": 1}},
                    return_document=ReturnDocument.AFTER,
                )
                _stats["dedup_hits"] += 1
                n_ref = updated.get("n_referencias", 1)
            else:
                wrote = put_if_absent(object_key, data, content_type)
                db().blobs.insert_one(
                    {
                        "_id": sha,
                        "object_key": object_key,
                        "n_referencias": 1,
                        "tamanho_bytes": len(data),
                    }
                )
                if wrote:
                    _stats["uploads_novos_blobs"] += 1
                    dedup = False
                else:
                    _stats["dedup_hits"] += 1
                    dedup = True
                n_ref = 1

            now = datetime.now(timezone.utc)
            doc = {
                "aluno_id": aluno_id,
                "disciplina": disciplina,
                "nome_arquivo": nome_arquivo,
                "object_key": object_key,
                "sha256": sha,
                "tamanho_bytes": len(data),
                "status": "entregue",
                "created_at": now,
            }
            res = db().entregas.insert_one(doc)
            doc["_id"] = res.inserted_id
            _stats["uploads"] += 1

            json_response(
                self,
                201,
                {
                    "entrega": serialize_entrega(doc),
                    "deduplicado": dedup,
                    "n_referencias": n_ref,
                },
            )
        except RuntimeError as exc:
            json_response(
                self,
                503,
                {"error": str(exc), "code": "storage_indisponivel", "status": "falha"},
            )
        except PyMongoError as exc:
            json_response(
                self,
                503,
                {"error": str(exc), "code": "meta_falhou", "status": "falha"},
            )


def main() -> None:
    esperar()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[api] catalogo-mongodb na porta {PORT} bucket={MINIO_BUCKET}")
    server.serve_forever()


if __name__ == "__main__":
    main()

"""
API — entrega de trabalhos (bytes em MinIO ou disco local + metadado no Postgres).

STORAGE_BACKEND: minio | local
FAIL_AFTER_BLOB: 1 → PutObject ok, mas não grava metadado (órfão didático)
REJECT_ON_INTEGRITY_FAIL: 1 → GET com hash divergente responde 409 (modo “produção”);
  0 (padrão) → 200 + X-Integridade: falha + body (soft verify didático)
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import uuid
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import boto3
import psycopg2
import psycopg2.extras
from botocore.client import Config
from botocore.exceptions import BotoCoreError, ClientError

PORT = int(os.environ.get("PORT", "8000"))
INSTANCE_ID = os.environ.get("INSTANCE_ID", "api")
PRIMARY_DSN = os.environ.get(
    "PRIMARY_DSN",
    "host=postgres port=5432 dbname=portal user=portal password=portal",
)
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.environ.get("MINIO_BUCKET", "trabalhos")
MINIO_SECURE = os.environ.get("MINIO_SECURE", "0") in ("1", "true", "True")
LOCAL_UPLOAD_DIR = Path(os.environ.get("LOCAL_UPLOAD_DIR", "/data/uploads"))

storage_backend = os.environ.get("STORAGE_BACKEND", "minio").lower()
fail_after_blob = os.environ.get("FAIL_AFTER_BLOB", "0") in ("1", "true", "True")
reject_on_integrity_fail = os.environ.get("REJECT_ON_INTEGRITY_FAIL", "0") in (
    "1",
    "true",
    "True",
)
_config_lock = threading.Lock()

_stats = {
    "uploads": 0,
    "downloads": 0,
    "uploads_falhos": 0,
    "orfaos_simulados": 0,
    "integridade_falhas": 0,
}


def _cfg_get_backend() -> str:
    with _config_lock:
        return storage_backend


def _cfg_set_backend(value: str) -> None:
    global storage_backend
    with _config_lock:
        storage_backend = value.lower()


def _cfg_get_fail() -> bool:
    with _config_lock:
        return fail_after_blob


def _cfg_set_fail(value: bool) -> None:
    global fail_after_blob
    with _config_lock:
        fail_after_blob = value


def _cfg_get_reject_integrity() -> bool:
    with _config_lock:
        return reject_on_integrity_fail


def _cfg_set_reject_integrity(value: bool) -> None:
    global reject_on_integrity_fail
    with _config_lock:
        reject_on_integrity_fail = value


@contextmanager
def conectar(connect_timeout: int = 10):
    conn = psycopg2.connect(PRIMARY_DSN, connect_timeout=connect_timeout)
    try:
        yield conn
    finally:
        conn.close()


def esperar() -> None:
    ultimo: Exception | None = None
    for _ in range(30):
        try:
            with conectar(connect_timeout=3) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            return
        except Exception as exc:  # noqa: BLE001
            ultimo = exc
            import time

            time.sleep(1)
    raise RuntimeError(f"Postgres indisponível: {ultimo}")


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=("https://" if MINIO_SECURE else "http://") + MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_local_dir() -> None:
    LOCAL_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def put_bytes(object_key: str, data: bytes, content_type: str) -> str:
    backend = _cfg_get_backend()
    if backend == "local":
        ensure_local_dir()
        path = LOCAL_UPLOAD_DIR / object_key.replace("/", "_")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return "local"
    try:
        s3_client().put_object(
            Bucket=MINIO_BUCKET,
            Key=object_key,
            Body=data,
            ContentType=content_type,
        )
    except (BotoCoreError, ClientError, OSError) as exc:
        raise RuntimeError(f"MinIO PutObject falhou: {exc}") from exc
    return "minio"


def get_bytes(object_key: str, storage: str) -> bytes:
    if storage == "local":
        path = LOCAL_UPLOAD_DIR / object_key.replace("/", "_")
        if not path.is_file():
            raise FileNotFoundError(object_key)
        return path.read_bytes()
    try:
        resp = s3_client().get_object(Bucket=MINIO_BUCKET, Key=object_key)
        return resp["Body"].read()
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code", "")
        if code in ("NoSuchKey", "404", "NotFound"):
            raise FileNotFoundError(object_key) from exc
        raise RuntimeError(f"MinIO GetObject falhou: {exc}") from exc
    except (BotoCoreError, OSError) as exc:
        raise RuntimeError(f"MinIO GetObject falhou: {exc}") from exc


def list_object_keys() -> list[str]:
    try:
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
    except (BotoCoreError, ClientError, OSError) as exc:
        raise RuntimeError(f"MinIO ListObjects falhou: {exc}") from exc


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
        print(f"[{INSTANCE_ID}] {self.address_string()} {fmt % args}")

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/health":
            try:
                with conectar(connect_timeout=2) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                storage_ok = True
                storage_err = None
                if _cfg_get_backend() == "minio":
                    try:
                        s3_client().head_bucket(Bucket=MINIO_BUCKET)
                    except Exception as exc:  # noqa: BLE001
                        storage_ok = False
                        storage_err = str(exc)
                json_response(
                    self,
                    200 if storage_ok else 503,
                    {
                        "ok": storage_ok,
                        "instance": INSTANCE_ID,
                        "storage_backend": _cfg_get_backend(),
                        "storage_ok": storage_ok,
                        "storage_error": storage_err,
                    },
                )
            except Exception as exc:  # noqa: BLE001
                json_response(self, 503, {"ok": False, "error": str(exc)})
            return

        if path == "/admin/config":
            json_response(
                self,
                200,
                {
                    "instance": INSTANCE_ID,
                    "storage_backend": _cfg_get_backend(),
                    "fail_after_blob": _cfg_get_fail(),
                    "reject_on_integrity_fail": _cfg_get_reject_integrity(),
                    "bucket": MINIO_BUCKET,
                    "stats": _stats,
                },
            )
            return

        if path == "/admin/orfaos":
            try:
                keys = set(list_object_keys())
                with conectar() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT object_key FROM entregas WHERE storage = 'minio'"
                        )
                        refs = {row[0] for row in cur.fetchall()}
                orfaos = sorted(keys - refs)
                json_response(
                    self,
                    200,
                    {
                        "objetos_minio": len(keys),
                        "referenciados": len(refs & keys),
                        "orfaos": orfaos,
                        "n_orfaos": len(orfaos),
                    },
                )
            except Exception as exc:  # noqa: BLE001
                json_response(self, 503, {"error": str(exc)})
            return

        if path == "/entregas":
            qs = parse_qs(parsed.query)
            aluno = (qs.get("aluno_id") or [None])[0]
            try:
                with conectar() as conn:
                    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        if aluno:
                            cur.execute(
                                "SELECT * FROM entregas WHERE aluno_id = %s ORDER BY id",
                                (aluno,),
                            )
                        else:
                            cur.execute("SELECT * FROM entregas ORDER BY id")
                        rows = [dict(r) for r in cur.fetchall()]
                        for r in rows:
                            if r.get("created_at") is not None:
                                r["created_at"] = r["created_at"].isoformat()
                json_response(
                    self,
                    200,
                    {"entregas": rows, "servido_por": INSTANCE_ID},
                )
            except Exception as exc:  # noqa: BLE001
                json_response(self, 503, {"error": str(exc)})
            return

        if path.startswith("/entregas/") and path.endswith("/arquivo"):
            mid = path[len("/entregas/") : -len("/arquivo")]
            try:
                eid = int(mid)
            except ValueError:
                json_response(self, 400, {"error": "id inválido"})
                return
            try:
                with conectar() as conn:
                    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                        cur.execute("SELECT * FROM entregas WHERE id = %s", (eid,))
                        row = cur.fetchone()
                if not row:
                    json_response(self, 404, {"error": "entrega não encontrada"})
                    return
                data = get_bytes(row["object_key"], row["storage"])
                digest = hashlib.sha256(data).hexdigest()
                integridade = "ok" if digest == row["sha256"] else "falha"
                _stats["downloads"] += 1
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
                                "sha256_metadado": row["sha256"],
                                "sha256_bytes": digest,
                                "servido_por": INSTANCE_ID,
                                "dica": "lab: REJECT_ON_INTEGRITY_FAIL=1 simula rejeição de produção",
                            },
                        )
                        return
                self.send_response(200)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header(
                    "Content-Disposition",
                    f'attachment; filename="{row["nome_arquivo"]}"',
                )
                self.send_header("Content-Length", str(len(data)))
                self.send_header("X-Servido-Por", INSTANCE_ID)
                self.send_header("X-Storage", row["storage"])
                self.send_header("X-Sha256", digest)
                self.send_header("X-Integridade", integridade)
                self.end_headers()
                self.wfile.write(data)
            except FileNotFoundError:
                json_response(
                    self,
                    404,
                    {
                        "error": "arquivo não encontrado neste nó/storage",
                        "servido_por": INSTANCE_ID,
                        "dica": "com STORAGE_BACKEND=local cada API tem seu disco",
                    },
                )
            except Exception as exc:  # noqa: BLE001
                json_response(self, 503, {"error": str(exc), "servido_por": INSTANCE_ID})
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
            if "storage_backend" in payload:
                val = str(payload["storage_backend"]).lower()
                if val not in ("minio", "local"):
                    json_response(self, 400, {"error": "storage_backend: minio|local"})
                    return
                _cfg_set_backend(val)
            if "fail_after_blob" in payload:
                raw = payload["fail_after_blob"]
                if isinstance(raw, str):
                    _cfg_set_fail(raw.lower() in ("1", "true", "yes"))
                else:
                    _cfg_set_fail(bool(raw))
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
                    "instance": INSTANCE_ID,
                    "storage_backend": _cfg_get_backend(),
                    "fail_after_blob": _cfg_get_fail(),
                    "reject_on_integrity_fail": _cfg_get_reject_integrity(),
                },
            )
            return

        json_response(self, 404, {"error": "não encontrado"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/admin/reconciliar-orfaos":
            try:
                keys = set(list_object_keys())
                with conectar() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT object_key FROM entregas WHERE storage = 'minio'"
                        )
                        refs = {row[0] for row in cur.fetchall()}
                orfaos = sorted(keys - refs)
                removed = []
                client = s3_client()
                for key in orfaos:
                    client.delete_object(Bucket=MINIO_BUCKET, Key=key)
                    removed.append(key)
                json_response(
                    self,
                    200,
                    {"removidos": removed, "n": len(removed), "servido_por": INSTANCE_ID},
                )
            except Exception as exc:  # noqa: BLE001
                json_response(self, 503, {"error": str(exc)})
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
        object_key = f"{disciplina}/{aluno_id}/{uuid.uuid4().hex}_{nome_arquivo}"
        backend = _cfg_get_backend()

        try:
            storage = put_bytes(object_key, data, content_type)
        except RuntimeError as exc:
            _stats["uploads_falhos"] += 1
            json_response(
                self,
                503,
                {
                    "error": str(exc),
                    "code": "storage_indisponivel",
                    "status": "falha",
                    "servido_por": INSTANCE_ID,
                },
            )
            return

        if _cfg_get_fail():
            _stats["orfaos_simulados"] += 1
            json_response(
                self,
                503,
                {
                    "error": "falha simulada após PutObject — metadado NÃO gravado",
                    "code": "fail_after_blob",
                    "object_key": object_key,
                    "sha256": sha,
                    "status": "falha",
                    "blob_orfao": True,
                    "servido_por": INSTANCE_ID,
                    "storage": storage,
                },
            )
            return

        try:
            with conectar() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(
                        """
                        INSERT INTO entregas
                          (aluno_id, disciplina, nome_arquivo, object_key, sha256,
                           tamanho_bytes, storage, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, 'entregue')
                        RETURNING *
                        """,
                        (
                            aluno_id,
                            disciplina,
                            nome_arquivo,
                            object_key,
                            sha,
                            len(data),
                            storage,
                        ),
                    )
                    row = dict(cur.fetchone())
                    conn.commit()
                    row["created_at"] = row["created_at"].isoformat()
            _stats["uploads"] += 1
            json_response(
                self,
                201,
                {
                    "entrega": row,
                    "servido_por": INSTANCE_ID,
                    "storage_backend": backend,
                },
            )
        except Exception as exc:  # noqa: BLE001
            _stats["uploads_falhos"] += 1
            json_response(
                self,
                503,
                {
                    "error": f"metadado falhou após blob: {exc}",
                    "code": "meta_falhou",
                    "object_key": object_key,
                    "blob_orfao": True,
                    "status": "falha",
                    "servido_por": INSTANCE_ID,
                },
            )


def main() -> None:
    esperar()
    ensure_local_dir()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(
        f"[{INSTANCE_ID}] entrega-postgres na porta {PORT} "
        f"backend={_cfg_get_backend()} bucket={MINIO_BUCKET}"
    )
    server.serve_forever()


if __name__ == "__main__":
    main()

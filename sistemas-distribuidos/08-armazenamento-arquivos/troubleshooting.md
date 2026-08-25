# Troubleshooting — Labs do módulo 08

Faça **um lab por vez**. Ao trocar:

```bash
docker compose down -v
```

Encerre labs 02–07 se as portas conflitarem.

---

## Portas deste módulo

> Use **só um** lab deste módulo por vez. Se a porta estiver ocupada: `docker ps` e `down -v` no outro lab (ou em 02–07).

| Serviço | Host |
|---------|------|
| API Postgres api1 / api2 | **8090** / **8091** |
| Postgres | **5442** |
| MinIO (lab PG) API / console | **9010** / **9011** |
| API Mongo | **8092** |
| Mongo | **27123** |
| MinIO (lab Mongo) API / console | **9020** / **9021** |

---

## Geral

| Sintoma | O que tentar |
|---------|----------------|
| `Cannot connect to Docker daemon` | Docker Desktop **ou** Podman: `export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock` |
| Porta em uso | `docker ps`; `down -v` no outro lab |
| API 503 no boot | Postgres/Mongo/MinIO subindo — espere; `./scripts/up.sh` |
| `COMPOSE_FILE` / projeto errado | `unset COMPOSE_FILE COMPOSE_PROJECT_NAME` |
| Scripts `compose: command not found` | Use `_compose.sh` via `./scripts/up.sh` |
| MinIO AccessDenied / bucket inexistente | Rode de novo `./scripts/up.sh` (o serviço `minio-init` cria o bucket `trabalhos`) |
| Credenciais MinIO | Labs usam `minioadmin` / `minioadmin` (só didático) |
| O que é `mc`? | Cliente CLI do MinIO. Scripts usam `compose run … minio-init` — **não** precisa instalar `mc` no host |
| `compose run` / `mc pipe` falha | Rode na pasta do lab; MinIO up; serviço `minio-init` existe no Compose |
| “Precisa de cluster / pre-signed no lab?” | Não — conceito em [teoria §9](teoria.md); labs usam Put via API + MinIO single-node |

---

## Lab Postgres (`lab-entrega-postgres`, :8090/:8091)

| Sintoma | O que tentar |
|---------|----------------|
| Download ok numa API e 404 na outra | Confirme `STORAGE_BACKEND=local` — é o Exp. didático; volte com `set-backend.sh minio` |
| Upload 503 “storage” | MinIO parado — `compose ps`; `compose start minio`; se bucket sumiu, `compose run --rm minio-init` |
| Órfão não aparece | `./scripts/provar-orfao.sh` (liga falha após blob); depois `reconciliar-orfaos.sh` |
| Metadado sem arquivo | Não é o caminho feliz — rode reconciliar; ou `down -v` + `up` limpo |
| api2 não sobe | `./scripts/up.sh` espera as duas; `compose ps` |
| `X-Integridade: falha` | Soft verify (padrão). Para 409: `set-reject-integrity.sh 1` ou `./scripts/provar-integridade-falha.sh` |
| Conteúdo “fantasma” de run antigo | `docker compose down -v` e `./scripts/up.sh` |

---

## Lab Mongo (`lab-catalogo-mongodb`, :8092)

| Sintoma | O que tentar |
|---------|----------------|
| Dois uploads = dois objetos | Confirme que o **conteúdo** é idêntico; veja `sha256` na resposta |
| Apagar removeu o blob cedo demais | Refcount: só remove se `n_referencias=0` — `./scripts/status-objetos.sh` |
| Listagem sem o upload novo | Se `read_from_secondary_sim` estiver on, é o Exp. stale (catálogo atrasado) — desligue no script |
| Volume MinIO apagado | Metadados órfãos — esperado no Exp. RPO; restore com `provar-backup-restore.sh` ou `down -v` + `up` |
| Backup/restore falha no `mc` | Confirme MinIO up; `compose run` na pasta do lab; disco em `/tmp/sd08-catalogo-minio-backup` |

---

## Ponte com outros módulos

| Sintoma “parece 08” | Na verdade… |
|---------------------|-------------|
| Lag de **nota** em réplica PG | [02](../02-replicacao/) / [03](../03-consistencia-cap/) |
| Timeout genérico na API | [06](../06-falhas-timeout/) |
| Como criar bucket MinIO no dia a dia | [`infra/storage`](../../infra/storage/) |

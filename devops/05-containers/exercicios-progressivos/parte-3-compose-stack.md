# Parte 3 — Stack Local com Docker Compose

**Duração:** 90 a 120 minutos
**Pré-requisitos:** Partes 1 e 2 concluídas, Bloco 3 ([Compose](../bloco-3/03-compose-multi-servico.md)) estudado.

---

## Contexto

O runner Python está containerizado (Parte 2). Agora é hora de **subir o stack inteiro** com um comando — permitindo que uma estagiária rode toda a CodeLab localmente em minutos.

---

## Tarefas

### 1. FastAPI mínima em `src/codelab/api.py`

```python
"""API da CodeLab — recebe submissões e consulta vereditos (esqueleto)."""
from __future__ import annotations

import os
import uuid
from datetime import datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)

app = FastAPI(title="CodeLab API", version="0.1.0")


class Submissao(BaseModel):
    linguagem: Literal["python", "javascript", "c"]
    codigo: str
    entrada: str = ""


class Resposta(BaseModel):
    id: str
    status: str
    criado_em: datetime


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    try:
        r.ping()
        return {"status": "ok"}
    except redis.exceptions.RedisError as e:
        raise HTTPException(503, detail=f"redis indisponivel: {e}")


@app.post("/submissoes", response_model=Resposta)
def criar(sub: Submissao) -> Resposta:
    sid = str(uuid.uuid4())
    agora = datetime.utcnow().isoformat()
    r.hset(f"sub:{sid}", mapping={
        "linguagem": sub.linguagem,
        "codigo": sub.codigo,
        "entrada": sub.entrada,
        "status": "PENDENTE",
        "criado_em": agora,
    })
    r.lpush("fila", sid)
    return Resposta(id=sid, status="PENDENTE", criado_em=datetime.fromisoformat(agora))


@app.get("/submissoes/{sid}", response_model=Resposta)
def consultar(sid: str) -> Resposta:
    dados = r.hgetall(f"sub:{sid}")
    if not dados:
        raise HTTPException(404, detail="submissao nao encontrada")
    return Resposta(id=sid, status=dados["status"], criado_em=datetime.fromisoformat(dados["criado_em"]))
```

### 2. Worker mínimo em `src/codelab/worker.py`

```python
"""Worker da CodeLab — puxa submissões da fila (esqueleto).

Em produção, aqui é onde o worker invoca o Docker para lançar o runner. Neste
exercício, apenas marca a submissão como processada após pequena espera.
"""
from __future__ import annotations

import os
import time
import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True)


def main() -> int:
    print("[worker] iniciado", flush=True)
    while True:
        item = r.brpop("fila", timeout=5)
        if item is None:
            continue
        _, sid = item
        r.hset(f"sub:{sid}", "status", "PROCESSANDO")
        time.sleep(0.5)  # simular execução
        r.hset(f"sub:{sid}", "status", "AC")
        print(f"[worker] processada {sid}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
```

### 3. Dockerfiles da API e do Worker

Crie `docker/api.Dockerfile` e `docker/worker.Dockerfile` — multi-stage, usuário não-root, labels OCI.

Dica: ambos podem **compartilhar builder stage** se o projeto for um único `pyproject.toml` / `requirements.txt`. Assim, cache é reaproveitado.

Exemplo esboçado (adapte):

```dockerfile
# syntax=docker/dockerfile:1.6
ARG PYVER=3.12.7

FROM python:${PYVER}-slim-bookworm AS builder
ENV PIP_NO_CACHE_DIR=1
WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

FROM python:${PYVER}-slim-bookworm
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app app
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY --from=builder /install /usr/local
COPY --chown=app:app src/codelab /app/src/codelab
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s CMD python -c "import urllib.request,sys; \
  sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"
ENTRYPOINT ["uvicorn", "codelab.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Worker é similar, sem `HEALTHCHECK` HTTP (pode usar `exit 0` simples ou omitir).

### 4. `docker-compose.yml` base

Escreva o `docker-compose.yml` que sobe: **postgres**, **redis**, **api**, **worker**. Para o **runner**, trate como **serviço opcional** (`profiles: ["runners"]`) — normalmente é lançado sob demanda pelo worker.

Requisitos:

- `healthcheck` em postgres, redis, api.
- `depends_on: { condition: service_healthy }` no que faz sentido.
- Volumes nomeados para postgres.
- Redes separadas `backend` (db/redis/worker) e `frontend` (api).
- `deploy.resources.limits` em todos os serviços.
- `.env.example` com as variáveis.

### 5. Override para dev

Crie `docker-compose.override.yml`:

- Bind mount de `src/` na API e worker para hot-reload.
- `command` da API com `--reload` do uvicorn.
- Porta 5432 exposta para DBeaver/psql do host (dev only).
- `LOG_LEVEL: DEBUG`.

### 6. Compose de testes

Crie `docker-compose.test.yml` para CI:

- `tmpfs` em `/var/lib/postgresql/data` (teste rápido).
- Portas não expostas.
- Env de teste.

### 7. Makefile

```makefile
.PHONY: up down logs shell test rebuild ps

up:
	docker compose up -d --build

up-prod:
	docker compose -f docker-compose.yml up -d --build

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

shell:
	docker compose exec api bash

ps:
	docker compose ps

rebuild:
	docker compose build --no-cache
	docker compose up -d

test:
	docker compose -f docker-compose.yml -f docker-compose.test.yml up -d --build
	docker compose -f docker-compose.yml -f docker-compose.test.yml exec -T api pytest tests/ -v || true
	docker compose -f docker-compose.yml -f docker-compose.test.yml down --volumes
```

### 8. README operacional

No `README.md` do repositório, adicione seção "Rodando localmente":

```markdown
## Rodando localmente

Pré-requisitos: Docker Engine 24+, Docker Compose V2.

```bash
cp .env.example .env
make up
curl http://localhost:8000/health
```

Diagrama (Mermaid) do stack rodando.

### 9. Teste manual

```bash
make up

# Esperar todos saudáveis
docker compose ps

# Submeter
curl -X POST http://localhost:8000/submissoes \
  -H "Content-Type: application/json" \
  -d '{"linguagem":"python","codigo":"print(1+1)","entrada":""}'

# Exemplo de resposta: {"id":"<uuid>","status":"PENDENTE",...}

# Consultar (esperar o worker processar)
sleep 2
curl http://localhost:8000/submissoes/<uuid>
# status deve virar "AC"
```

---

## O que entregar

1. **Código:**
   - `src/codelab/api.py`, `src/codelab/worker.py`
   - `docker/api.Dockerfile`, `docker/worker.Dockerfile`
   - `docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.test.yml`
   - `Makefile`, `.env.example`, `.dockerignore`
2. **Evidências:**
   - Saída de `docker compose ps` mostrando **todos** os serviços `Up` e `healthy`.
   - Captura da submissão + consulta bem-sucedidas.
   - Tempo do `make up` do zero (idealmente < 2 min em cold build, < 20s em warm).
3. **Documentação:**
   - `docs/arquitetura.md` com diagrama Mermaid do stack + mapa serviço→imagem→responsabilidade.

## Critérios de aceitação

- `make up` funciona num clone fresco do repositório em **≤ 5 min**.
- `docker compose ps` mostra **status healthy** em api, postgres e redis.
- Submissão fim-a-fim funciona (POST + GET retornam AC após worker processar).
- `docker-compose.yml` **sozinho** (sem override) funciona — produção-like.
- Healthchecks **não** dependem de `curl` externo ou comandos indisponíveis na imagem.

---

## Dicas

- Se `redis` no hostname não resolver dentro do container, verifique se os serviços estão **na mesma rede**.
- Erros de permissão no volume do Postgres: o Postgres oficial cria usuário `postgres` com UID específico; não mude `USER` dessa imagem.
- `healthcheck` da API dependente de `/ready` com redis pode oscilar — use `/health` leve no container e `/ready` apenas para K8s readiness (Mod 7).

---

## Próximo passo

Avance para a **[Parte 4 — Pipeline de imagens](parte-4-pipeline-imagens.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — Dockerfile do Runner Python](parte-2-dockerfile-runner.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](../README.md) | **Próximo →**<br>[Parte 4 — Pipeline de Imagens (CI com scan, SBOM, assinatura)](parte-4-pipeline-imagens.md) |

<!-- nav:end -->

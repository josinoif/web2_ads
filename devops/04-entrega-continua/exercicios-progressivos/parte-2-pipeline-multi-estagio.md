# Parte 2 — Pipeline Multi-estágio com Artefato Único

> **Duração:** 1h30 a 2h.
> **Objetivo:** construir o **deployment pipeline** funcional para o serviço Tracking API da LogiTrack, respeitando **build once, deploy many**.

---

## Contexto

Com o diagnóstico pronto (Parte 1), agora você constrói o **pipeline-alvo**. Este é o **coração** do módulo — o que vai ser referenciado nas Partes 3, 4 e 5.

---

## O que você vai entregar

Um repositório GitHub com:

- Aplicação **Tracking API** mínima em FastAPI (fornecida como esqueleto abaixo).
- **Pipeline CI** (`.github/workflows/ci.yml`) — constrói UM artefato.
- **Pipeline CD** (`.github/workflows/cd.yml`) — promove o MESMO artefato por 3 estágios.
- **GitHub Environments** configurados: `dev`, `staging`, `production`.
- **Evidências**: screenshots / links de runs passando e de tag criada.

---

## Esqueleto da aplicação Tracking API

Crie a seguinte estrutura. Esta é **referência mínima** — você pode expandir à vontade.

### `pyproject.toml`

```toml
[project]
name = "logitrack-tracking"
version = "0.0.0"      # sobrescrita pelo pipeline
description = "LogiTrack — Tracking API"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.110",
    "uvicorn>=0.29",
    "pydantic>=2.6",
    "pydantic-settings>=2.2",
]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
```

### `src/tracking/__init__.py`

```python
__version__ = "0.0.0"
```

### `src/tracking/config.py`

```python
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="LOGITRACK_",
        case_sensitive=False,
    )

    environment: str = Field(default="dev")
    log_level: str = "INFO"
    version: str = "0.0.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### `src/tracking/api.py`

```python
from fastapi import FastAPI
from tracking.config import get_settings

app = FastAPI(title="LogiTrack — Tracking API")


@app.get("/health/live")
def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness():
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.environment,
        "version": settings.version,
    }


@app.get("/rastreio/{codigo}")
def rastrear(codigo: str):
    return {
        "codigo": codigo,
        "status": "EM_ROTA",
        "ultima_atualizacao": "2026-04-21T12:00:00Z",
    }
```

### `tests/unit/test_api.py`

```python
from fastapi.testclient import TestClient
from tracking.api import app


def test_liveness():
    resp = TestClient(app).get("/health/live")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_readiness():
    resp = TestClient(app).get("/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "environment" in body


def test_rastreio_retorna_estrutura_esperada():
    resp = TestClient(app).get("/rastreio/ABC123")
    assert resp.status_code == 200
    body = resp.json()
    assert body["codigo"] == "ABC123"
    assert "status" in body
```

### `tests/smoke/test_smoke.py`

```python
"""Smoke tests — rodam contra o ambiente real após deploy."""
import os
import httpx
import pytest


@pytest.fixture(scope="session")
def base_url():
    url = os.environ.get("TARGET_URL")
    if not url:
        pytest.skip("TARGET_URL não configurado.")
    return url.rstrip("/")


def test_liveness_respondendo(base_url):
    r = httpx.get(f"{base_url}/health/live", timeout=5)
    assert r.status_code == 200


def test_readiness_respondendo(base_url):
    r = httpx.get(f"{base_url}/health/ready", timeout=5)
    assert r.status_code == 200
    assert r.json().get("environment")


def test_rastreio_publico(base_url):
    r = httpx.get(f"{base_url}/rastreio/TEST123", timeout=5)
    assert r.status_code == 200
```

### `scripts/deploy.sh`

```bash
#!/usr/bin/env bash
# Placeholder "deploy" — em ambiente real, substitua por ansible/terraform/k8s.
# Aqui: baixa o artefato, instala em venv efêmero e roda com systemd/supervisord.
set -euo pipefail

ENV="${1:?uso: deploy.sh <env> <artifact.whl>}"
ARTIFACT="${2:?artifact.whl obrigatório}"

echo "[deploy] alvo: ${ENV}"
echo "[deploy] artefato: ${ARTIFACT}"

# Em sala de aula: simulamos o deploy.
# Real: scp/rsync + restart de serviço remoto.
test -f "$ARTIFACT" || { echo "artefato não existe"; exit 1; }
echo "[deploy] OK (simulado)."
```

Torne executável: `chmod +x scripts/deploy.sh`.

---

## Tarefas

### 1. Inicializar o repositório

```bash
# Dentro do diretório logitrack-tracking criado na Parte 1
git add .
git commit -m "chore: inicializa esqueleto do serviço Tracking"
```

Suba para o GitHub:

```bash
gh repo create logitrack-tracking --public --source=. --push
# ou via web UI + git remote add origin ...
```

### 2. Criar `.github/workflows/ci.yml`

Use como **base** o [ci.yml do Bloco 2](../bloco-2/02-deployment-pipeline.md#51-githubworkflowsciyml--commit-stage). Adapte para o seu projeto.

**Requisitos obrigatórios:**

- Roda em **push e pull_request**.
- Executa: lint (ruff), format check (ruff), testes unitários com cobertura (>= 70%).
- Gera o `.whl` com `python -m build`.
- Publica o artefato via `actions/upload-artifact` com nome **único** (ex.: `logitrack-tracking-${{ github.sha }}`).
- Output `version` para o próximo workflow.

### 3. Criar `.github/workflows/cd.yml`

Base: o [cd.yml do Bloco 2](../bloco-2/02-deployment-pipeline.md#52-githubworkflowscdyml--deployment-pipeline). Adapte.

**Requisitos obrigatórios:**

- Dispara **após CI passar** em `main` (via `workflow_run`) — e **sempre** se tiver `workflow_dispatch` para testes manuais.
- **3 jobs** encadeados: `deploy-dev`, `deploy-staging`, `deploy-production`.
- Cada job **baixa** o artefato via `actions/download-artifact` — **não recompila**.
- `deploy-production` usa `environment: production` com **aprovação manual** (via GitHub Environments).
- Job de **smoke** pós-deploy em staging (executa `tests/smoke` com `TARGET_URL` apontando para staging).
- Na aprovação e sucesso do `deploy-production`, **criar tag** semver (pode ser manual por agora — Parte 5 automatiza).

### 4. Configurar GitHub Environments

Na UI do GitHub (`Settings → Environments`), crie:

- **dev** — sem regras.
- **staging** — sem regras, mas com secret `STAGING_URL` (pode ser `https://staging.example.com` falso).
- **production** — com `Required reviewers` = você mesmo; secret `PROD_URL`.

### 5. Rodar o pipeline e colher evidências

- Abra um PR com mudança trivial (ex.: ajustar um texto). Veja o CI rodar.
- Merge na `main`. Veja o CD rodar até staging.
- Aprove manualmente a ida para `production`.
- Capture screenshots OU links dos runs.

### 6. Rodar o analisador de pipeline do Bloco 2

```bash
pip install pyyaml
python scripts/analisa_pipeline.py .github/workflows/cd.yml
```

*(Copie o script do [Bloco 2, seção 6](../bloco-2/02-deployment-pipeline.md#6-script-python-analisador-de-pipeline) para `scripts/analisa_pipeline.py`.)*

**Espera-se:** violações **zero**. Se houver, **ajuste o pipeline** e documente o que mudou.

---

## Entregáveis

```
logitrack-tracking/
├── src/tracking/...
├── tests/unit/...
├── tests/smoke/...
├── scripts/
│   ├── deploy.sh
│   └── analisa_pipeline.py       # copiado do Bloco 2
├── .github/workflows/
│   ├── ci.yml
│   └── cd.yml
├── pyproject.toml
├── requirements.txt
├── README.md                     # instruções + diagrama do pipeline
└── docs/
    └── evidencias-parte-2.md     # links dos runs + screenshots
```

No `docs/evidencias-parte-2.md`:

- Link para um run de CI **verde**.
- Link para um run de CD **até staging**.
- Link para o run de CD **aprovado para production** (com tag criada).
- Saída do `analisa_pipeline.py` copiada no final.

---

## Critérios de sucesso

- [ ] CI e CD separados, no mesmo repositório.
- [ ] Artefato **único** no CI, baixado no CD (`build once`).
- [ ] 3 environments distintos com deploy encadeado.
- [ ] `production` exige aprovação manual e tem secret próprio.
- [ ] Smoke test pós-deploy em pelo menos staging.
- [ ] `analisa_pipeline.py` retorna **OK**.
- [ ] Pelo menos **1 run completo** documentado.

---

## Dicas e armadilhas

- **Workflow de CD disparado por `workflow_run`** tem pegadinhas com `github.event.workflow_run.id` para baixar artefato entre workflows. Alternativa mais simples: **unir tudo em `ci.yml`** com jobs encadeados — é aceito.
- **Secrets em PRs de forks** não são expostos. Se estiver em repositório aberto, PRs de terceiros **falharão** os jobs que precisam de secrets. Isso é o comportamento correto.
- **Deploy "simulado"**: não se preocupe em ter infraestrutura real. O `deploy.sh` pode apenas **imprimir** que faria o deploy. O importante é que o **artefato é o mesmo**.
- **Tag SemVer** pode ser colocada manualmente nesta parte (ex.: `git tag v0.1.0`). A automatização é tópico da Parte 5.

---

## Próximo passo

[Parte 3 — Feature Flags e estratégia de release](parte-3-feature-flags.md). Agora o pipeline existe; vamos ensinar o sistema a **liberar features**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — Diagnóstico do Pipeline da LogiTrack](parte-1-diagnostico-pipeline.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](../README.md) | **Próximo →**<br>[Parte 3 — Feature Flags e Estratégia de Release](parte-3-feature-flags.md) |

<!-- nav:end -->

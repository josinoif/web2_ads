# Bloco 2 — Deployment Pipeline e Promoção de Artefatos

> **Duração estimada:** 70 a 80 minutos. Inclui construção de um pipeline completo em GitHub Actions.

Este é o bloco técnico central do módulo. Vamos **construir** o deployment pipeline que falta à LogiTrack.

---

## 1. O que é um Deployment Pipeline

**Definição (Humble & Farley, 2014, cap. 5):**

> *"O deployment pipeline é a automação do processo de release de software, desde o commit até a produção. É o caminho pelo qual qualquer mudança no código fonte percorre até chegar ao usuário final."*

Estrutura canônica:

```mermaid
flowchart LR
    Dev[Commit] --> Build[Commit Stage<br/>build + unit tests]
    Build -->|artefato| Int[Acceptance Stage<br/>testes de integração/E2E]
    Int -->|mesmo artefato| Staging[Staging<br/>ambiente prod-like]
    Staging -->|mesmo artefato| Prod[(Production)]

    Build -.->|falhou?| Reject1[❌]
    Int -.->|falhou?| Reject2[❌]
    Staging -.->|falhou?| Reject3[❌]

    style Build fill:#c8e6c9
    style Int fill:#fff9c4
    style Staging fill:#ffe0b2
    style Prod fill:#ffcdd2
```

**Propriedades essenciais:**

1. **Todo commit entra no pipeline.** Sem exceção.
2. **Cada estágio é mais caro** que o anterior (mais recursos, mais tempo, mais risco).
3. **Cada estágio é mais estrito** em sua validação.
4. **O artefato é o mesmo** em todos os estágios (princípio "build once").
5. **Falha em qualquer estágio para o pipeline** para aquele artefato.

---

## 2. Os dois princípios invioláveis

### 2.1 Build Once, Deploy Many

**Regra:** **construa o artefato exatamente uma vez**, no primeiro estágio. Todos os estágios seguintes **reutilizam** esse artefato imutável.

```mermaid
flowchart TD
    subgraph "❌ ERRADO — o que a LogiTrack faz hoje"
        E1[commit] --> EB1[build 1<br/>→ artefato A]
        EB1 --> EBQ1[testes]
        EBQ1 --> EB2[build 2<br/>→ artefato B]
        EB2 --> ES[staging]
        ES --> EB3[build 3<br/>→ artefato C]
        EB3 --> EP[produção]
    end

    subgraph "✅ CERTO"
        C1[commit] --> CB[build ÚNICO<br/>→ artefato imutável]
        CB --> CT[testes sobre o<br/>MESMO artefato]
        CT --> CS[staging: usa<br/>MESMO artefato]
        CS --> CP[produção: usa<br/>MESMO artefato]
    end

    style EB1 fill:#ffcdd2
    style EB2 fill:#ffcdd2
    style EB3 fill:#ffcdd2
    style CB fill:#c8e6c9
```

**Por que isso importa?**

- **Reproduzibilidade:** se o teste passou no artefato X e o artefato X vai para prod, o teste continua válido.
- **Depuração:** quando um bug aparece em prod, você sabe **exatamente** qual binário está rodando.
- **Segurança:** não há chance de que uma dependência muda entre staging e prod (ex.: `latest` virou outra versão).
- **Velocidade:** compilar 1 vez é mais rápido que compilar 3.

**Como garantir?**

- Artefato **imutável** (arquivo `.whl`, imagem Docker com tag única, `.zip`, etc.).
- **Tag única** que identifica o artefato (ex.: `sha-abc1234` ou `v1.2.3`).
- **Registry** que armazena artefatos (GitHub Packages, Docker Hub, artifactory, S3, GitHub Releases).
- **Promoção** move uma **referência**, não reconstrói.

### 2.2 Promote-Don't-Rebuild

Mover entre ambientes é um ato de **referência**: "este artefato X que estava em staging agora vai para prod".

Nenhum deploy pode **reconstruir**. Nenhum deploy pode **modificar** o artefato (adicionar configuração embutida, por exemplo).

**Consequência importante:** **configuração** **não** pode ser embutida no artefato. O mesmo binário precisa rodar em dev, staging e prod — diferença é configuração externa (variáveis de ambiente, arquivos montados, secrets).

---

## 3. Configuração por ambiente

Se o artefato é único, **a diferença entre ambientes está na configuração**. Três princípios:

### 3.1 12-Factor App (Adam Wiggins, Heroku, 2012)

A Config Factor III diz:

> *"A configuração de uma aplicação é tudo o que provavelmente varia entre deploys (staging, production, development). Isso inclui: credenciais de serviços externos, handles por ambiente, valores de deploy (ex.: hostname), e qualquer outra coisa que muda entre ambientes."*

**Regra canônica:** config via **variáveis de ambiente**.

### 3.2 Secrets nunca no artefato

Credenciais **não** podem estar no binário/imagem. Devem vir de:

- **Variáveis de ambiente** injetadas pelo orquestrador.
- **Secret manager** (HashiCorp Vault, AWS Secrets Manager, GitHub Encrypted Secrets).
- **Arquivo montado** em tempo de execução.

Razão adicional: se estão no artefato, ficam no Git (histórico) e no registry (público potencial).

### 3.3 Exemplo Python — `config.py` com `pydantic-settings`

```python
"""config.py — configuração por ambiente, validada."""
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,           # nunca use .env em produção
        env_prefix="LOGITRACK_",
        case_sensitive=False,
    )

    environment: str = Field(..., description="dev | staging | production")
    database_url: str
    log_level: str = "INFO"
    enable_debug_endpoints: bool = False
    max_request_size_kb: int = 512

    # Feature flags (ver Bloco 3)
    flag_estimativa_ml: bool = False
    flag_circuit_breaker_billing: bool = True  # kill switch operacional


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**Uso:**

```bash
# Staging
export LOGITRACK_ENVIRONMENT=staging
export LOGITRACK_DATABASE_URL=postgresql://staging-db:5432/tracking
export LOGITRACK_LOG_LEVEL=DEBUG

# Produção (secrets via secret manager)
export LOGITRACK_ENVIRONMENT=production
export LOGITRACK_DATABASE_URL=${SECRET_DATABASE_URL}  # injetado pelo orquestrador
export LOGITRACK_LOG_LEVEL=INFO
```

O **mesmo** artefato roda em ambos.

---

## 4. Os estágios de um pipeline completo

### 4.1 Commit Stage (2 a 5 min)

**Objetivo:** detectar problemas **baratos** o mais rápido possível.

| Passo | O que faz |
|-------|-----------|
| Checkout | Clona o repositório |
| Lint / Format check | Ruff, Black (ou `ruff format --check`) |
| Análise estática | Ruff, mypy, Bandit (segurança) |
| Testes unitários | Pytest com cobertura |
| Build do artefato | `python -m build` → `.whl` |
| Publicação do artefato | Upload para registry (GitHub Packages, S3, etc.) |

**Saída:** artefato **identificável por tag única** (ex.: `logitrack-tracking-1.0.0+sha-abc1234.whl`).

### 4.2 Acceptance Stage (10 a 30 min)

**Objetivo:** rodar testes **mais caros** contra o artefato.

| Passo | O que faz |
|-------|-----------|
| Baixa o artefato do registry | `pip install logitrack-tracking==$VERSION` |
| Sobe dependências reais | Testcontainers (Postgres, Redis) |
| Testes de integração | Módulo 3, Bloco 4 |
| Smoke tests E2E | Pequeno subconjunto de E2E crítico |
| Testes de contrato | Pact (opcional) |

**Saída:** artefato **aprovado para staging**.

### 4.3 Staging

**Objetivo:** ambiente **prod-like** onde o artefato é instalado **de verdade**. Feedback final antes de produção.

| Passo | O que faz |
|-------|-----------|
| Deploy do artefato | Instala o mesmo `.whl`/imagem |
| Migrations aplicadas | Banco de staging recebe migrations |
| Smoke tests pós-deploy | Health check, login, rota crítica |
| Testes manuais exploratórios | Opcional, mas útil |

**Staging "que mente" (anti-padrão do Bloco 1):** se staging usa dados diferentes, tráfego diferente, versão diferente de Python → feedback é falso. **Staging deve ser idêntico a produção**, exceto:

- Tamanho (menos réplicas).
- Dados (sintéticos ou anonimizados).

### 4.4 Production

**Objetivo:** deploy real, com **estratégia de release** que permite rollback rápido.

| Passo | O que faz |
|-------|-----------|
| Gate de aprovação | Manual (CDelivery) ou automático (CDeployment) |
| Migrations expand (Bloco 4) | Aplicadas **antes** do novo código |
| Deploy progressivo | Blue-Green, Canary ou Rolling (Bloco 3) |
| Smoke tests pós-deploy | Automático — se falha, rollback |
| Monitoramento ativo | 5xx, latência, erros — por 15-30 min |
| Migrations contract | **Depois** de confirmar estabilidade |

---

## 5. Pipeline completo em GitHub Actions

Este é um **workflow funcional** que a LogiTrack pode começar a usar. Arquivos em `.github/workflows/`.

### 5.1 `.github/workflows/ci.yml` — Commit Stage

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    name: Commit Stage
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # necessário para semver a partir de tags

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install
        run: |
          python -m pip install --upgrade pip build
          pip install -r requirements.txt

      - name: Lint
        run: ruff check .

      - name: Format check
        run: ruff format --check .

      - name: Unit tests + coverage
        run: |
          pytest tests/unit \
            --cov=src --cov-branch \
            --cov-report=xml --cov-report=term-missing \
            --cov-fail-under=75

      - name: Compute version
        id: version
        run: |
          # versão = tag mais recente + sha curto
          BASE=$(git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0")
          SHA=$(git rev-parse --short HEAD)
          VERSION="${BASE#v}+sha.${SHA}"
          echo "version=${VERSION}" >> "$GITHUB_OUTPUT"
          echo "Versão calculada: ${VERSION}"

      - name: Build artifact
        run: |
          # Ajusta a versão no pyproject e constrói o wheel
          python -m build --wheel

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: logitrack-tracking-${{ steps.version.outputs.version }}
          path: dist/*.whl
          retention-days: 30
```

### 5.2 `.github/workflows/cd.yml` — Deployment Pipeline

```yaml
name: CD

on:
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: [main]
  workflow_dispatch:          # permite disparo manual

jobs:
  acceptance:
    name: Acceptance Stage
    if: ${{ github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.resolve.outputs.version }}

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: tracking
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Download artifact from CI
        uses: actions/download-artifact@v4
        with:
          pattern: logitrack-tracking-*
          path: dist
          run-id: ${{ github.event.workflow_run.id }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          merge-multiple: true

      - name: Resolve version
        id: resolve
        run: |
          WHEEL=$(ls dist/*.whl | head -n1)
          VERSION=$(basename "$WHEEL" | sed -E 's/logitrack_tracking-([^-]+)-.*/\1/')
          echo "version=${VERSION}" >> "$GITHUB_OUTPUT"
          echo "Artefato: $WHEEL — versão: $VERSION"

      - name: Install artifact
        run: |
          pip install dist/*.whl
          pip install -r requirements-test.txt

      - name: Integration tests
        env:
          LOGITRACK_ENVIRONMENT: test
          LOGITRACK_DATABASE_URL: postgresql://postgres:test@localhost:5432/tracking
        run: pytest tests/integration -v

  deploy-staging:
    name: Deploy → Staging
    needs: acceptance
    runs-on: ubuntu-latest
    environment: staging        # GitHub Environment com secrets próprios

    steps:
      - uses: actions/checkout@v4

      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          pattern: logitrack-tracking-*
          path: dist
          run-id: ${{ github.event.workflow_run.id }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          merge-multiple: true

      - name: Apply migrations (expand phase)
        env:
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: ./scripts/migrate.sh --phase=expand

      - name: Deploy artifact to staging
        env:
          DEPLOY_TARGET: ${{ secrets.STAGING_HOST }}
          DEPLOY_KEY: ${{ secrets.STAGING_DEPLOY_KEY }}
        run: ./scripts/deploy.sh --env=staging --artifact=dist/*.whl

      - name: Smoke tests
        env:
          TARGET_URL: ${{ secrets.STAGING_URL }}
        run: pytest tests/smoke --base-url="$TARGET_URL"

      - name: Apply migrations (contract phase)
        if: success()
        env:
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: ./scripts/migrate.sh --phase=contract

  deploy-production:
    name: Deploy → Production
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production     # exige aprovação manual no GitHub Environments

    steps:
      - uses: actions/checkout@v4

      - name: Download artifact
        uses: actions/download-artifact@v4
        with:
          pattern: logitrack-tracking-*
          path: dist
          run-id: ${{ github.event.workflow_run.id }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          merge-multiple: true

      - name: Apply migrations (expand phase)
        env:
          DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
        run: ./scripts/migrate.sh --phase=expand

      - name: Deploy artifact (canary 10%)
        env:
          DEPLOY_TARGET: ${{ secrets.PROD_HOST }}
          DEPLOY_KEY: ${{ secrets.PROD_DEPLOY_KEY }}
        run: ./scripts/deploy.sh --env=production --canary-percent=10 --artifact=dist/*.whl

      - name: Monitor canary for 10 minutes
        run: ./scripts/monitor.sh --duration=600 --error-threshold=0.02

      - name: Promote to 100%
        if: success()
        run: ./scripts/deploy.sh --env=production --promote-full

      - name: Smoke tests (full)
        env:
          TARGET_URL: ${{ secrets.PROD_URL }}
        run: pytest tests/smoke --base-url="$TARGET_URL"

      - name: Apply migrations (contract phase)
        if: success()
        env:
          DATABASE_URL: ${{ secrets.PROD_DATABASE_URL }}
        run: ./scripts/migrate.sh --phase=contract

      - name: Tag release
        if: success()
        run: |
          git tag "v${{ needs.acceptance.outputs.version }}"
          git push origin "v${{ needs.acceptance.outputs.version }}"
```

### 5.3 GitHub Environments — o que fazem

GitHub oferece o conceito de **Environment** (staging, production) com:

- **Secrets específicos** do ambiente (ex.: `STAGING_DATABASE_URL` só visível em jobs `environment: staging`).
- **Protection rules**:
  - *Required reviewers* — 1+ aprovadores antes do job rodar.
  - *Wait timer* — atrasa X minutos antes de começar.
  - *Deployment branches* — só `main` pode deployar para production.
- **Deployment history** visível na UI.

**Configuração sugerida para a LogiTrack:**

- `staging`: sem aprovação, deploy automático.
- `production`: 1 reviewer obrigatório (começo da jornada CDelivery); depois do amadurecimento, remover e usar **smoke tests automáticos** como gate.

---

## 6. Script Python: analisador de pipeline

Para os exercícios, vamos ter um script que **analisa** um pipeline.yml e **aponta violações** dos princípios do bloco.

### `analisa_pipeline.py`

```python
"""Analisa um workflow YAML de CI/CD e aponta violações dos princípios CDelivery.

Verifica:
  1) Build único: existe exatamente 1 passo que gera o artefato.
  2) Promote-don't-rebuild: estágios posteriores ao build NÃO reconstroem.
  3) Artefato compartilhado: download-artifact referenciando mesmo run.
  4) Gate manual ou automático em production.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.stderr.write("Este script requer PyYAML: pip install pyyaml\n")
    sys.exit(2)


PALAVRAS_DE_BUILD = (
    "python -m build",
    "pip wheel",
    "docker build",
    "setup.py bdist",
    "setup.py sdist",
    "poetry build",
)


@dataclass
class Analise:
    violacoes: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    pontos_positivos: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.violacoes


def _extrair_runs(workflow: dict) -> list[tuple[str, str]]:
    """Retorna lista de (job_name, run_command)."""
    runs: list[tuple[str, str]] = []
    for job_name, job in (workflow.get("jobs") or {}).items():
        for step in job.get("steps", []):
            cmd = step.get("run") or ""
            if cmd:
                runs.append((job_name, cmd))
    return runs


def analisar(workflow: dict) -> Analise:
    a = Analise()

    runs = _extrair_runs(workflow)
    jobs = workflow.get("jobs") or {}

    # 1) Build único
    jobs_com_build = set()
    for job, cmd in runs:
        if any(p in cmd for p in PALAVRAS_DE_BUILD):
            jobs_com_build.add(job)

    if len(jobs_com_build) == 0:
        a.avisos.append("Nenhum passo de build detectado; certifique-se de que o artefato é produzido.")
    elif len(jobs_com_build) == 1:
        a.pontos_positivos.append(
            f"Build único detectado no job '{list(jobs_com_build)[0]}' — princípio 'build once' respeitado."
        )
    else:
        a.violacoes.append(
            f"Violação 'build once': {len(jobs_com_build)} jobs constroem artefato: {sorted(jobs_com_build)}"
        )

    # 2) Upload do artefato no build stage
    upload_ok = False
    for job in jobs_com_build:
        for step in jobs[job].get("steps", []):
            uses = step.get("uses", "") or ""
            if "actions/upload-artifact" in uses:
                upload_ok = True
    if jobs_com_build and not upload_ok:
        a.violacoes.append(
            "Build não publica artefato (falta actions/upload-artifact). Estágios seguintes terão de reconstruir."
        )
    elif upload_ok:
        a.pontos_positivos.append("Artefato publicado via upload-artifact — pode ser promovido.")

    # 3) Download do artefato em estágios posteriores
    downloads = 0
    for job_name, job in jobs.items():
        if job_name in jobs_com_build:
            continue
        for step in job.get("steps", []):
            uses = step.get("uses", "") or ""
            if "actions/download-artifact" in uses:
                downloads += 1
    if upload_ok and downloads == 0:
        a.violacoes.append(
            "Artefato foi publicado mas nenhum estágio posterior o consome. Os estágios devem reutilizar o artefato."
        )
    if downloads > 0:
        a.pontos_positivos.append(
            f"{downloads} job(s) consome(m) artefato via download-artifact — promoção real."
        )

    # 4) Gate em production
    prod_jobs = [
        name for name, job in jobs.items()
        if (job.get("environment") == "production"
            or (isinstance(job.get("environment"), dict)
                and job["environment"].get("name") == "production"))
    ]
    if not prod_jobs:
        a.avisos.append("Nenhum job referencia environment 'production'. Sem GitHub Environment, não há gates formais.")
    else:
        a.pontos_positivos.append(
            f"Job(s) com environment 'production' encontrado(s): {prod_jobs}. "
            "Configure protection rules (reviewers, deployment branches)."
        )

    return a


def imprimir(a: Analise) -> None:
    if a.pontos_positivos:
        print("✅ Pontos positivos:")
        for p in a.pontos_positivos:
            print(f"  • {p}")
    if a.avisos:
        print("\n⚠️  Avisos:")
        for w in a.avisos:
            print(f"  • {w}")
    if a.violacoes:
        print("\n❌ Violações:")
        for v in a.violacoes:
            print(f"  • {v}")
    print(f"\n>> Resultado: {'OK' if a.ok else 'FALHA'}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("workflow_yaml", help="Caminho para um arquivo .yml de workflow.")
    args = p.parse_args(argv)

    with Path(args.workflow_yaml).open() as f:
        workflow = yaml.safe_load(f)

    analise = analisar(workflow)
    imprimir(analise)
    return 0 if analise.ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

Uso:

```bash
pip install pyyaml
python analisa_pipeline.py .github/workflows/cd.yml
```

Exemplo de saída para o workflow bom (seção 5.2):

```
✅ Pontos positivos:
  • Artefato publicado via upload-artifact — pode ser promovido.
  • 3 job(s) consome(m) artefato via download-artifact — promoção real.
  • Job(s) com environment 'production' encontrado(s): ['deploy-production']. ...

⚠️  Avisos:
  • Nenhum passo de build detectado; certifique-se de que o artefato é produzido.

>> Resultado: OK
```

*(O aviso de "nenhum build detectado" aparece porque o `cd.yml` **não** constrói — o build está no `ci.yml`. Isso é o comportamento correto.)*

---

## 7. Aplicação ao cenário da LogiTrack

| Sintoma | Como o Bloco 2 endereça |
|---------|-------------------------|
| 3 — Artefatos recompilados em cada estágio | Commit Stage constrói uma vez e publica; CD só consome. |
| 4 — Ambientes divergentes / config copiada à mão | `config.py` com pydantic-settings + secrets por GitHub Environment. |
| 2 — Deploy manual de 87 passos | Substituído por `deploy.sh` idempotente invocado pelo workflow. |
| 7 — Release train (2 a 4 semanas de fila) | Cada commit verde vira uma execução do pipeline — sem fila. |

---

## 8. Cuidados e trade-offs

### 8.1 Pipeline lento mata CDelivery

Pipeline que demora **45 minutos** para completar desencoraja mergear com frequência. Meta: **Commit Stage < 10 min**, **Acceptance Stage < 30 min**.

Técnicas para acelerar:

- **Paralelizar** jobs (lint e testes em paralelo).
- **Cache** de dependências (actions/cache ou setup-python cache).
- **Testes de integração em paralelo** (pytest-xdist).
- **Quebrar** suítes (unit rápido sempre; integração em job separado).

### 8.2 Flaky tests sabotam o pipeline

Testes intermitentes fazem o time **normalizar red builds** ("é só re-rodar"). Isso corrói a disciplina.

- **Quarentena** para flaky (testes marcados, fora do gate).
- **Investigação obrigatória** antes de voltar.

### 8.3 Custo de registry

Registry não é grátis:

- GitHub Packages: free tier limitado.
- Imagens Docker acumulam espaço.
- Política de retenção: manter 30 a 90 dias de artefatos.

### 8.4 Secrets em PRs

PRs de forks **não recebem secrets** por padrão (segurança). Isso pode quebrar o pipeline acceptance em PRs externos. Solução: **separar** workflows — CI público sem secrets, CD restrito a `main`.

---

## Resumo do bloco

- **Deployment pipeline** é a automação do caminho "commit → produção".
- Dois princípios invioláveis: **build once, deploy many** e **promote-don't-rebuild**.
- Configuração é **externa** ao artefato (12-Factor III).
- Estágios: **Commit Stage** (2-5 min), **Acceptance Stage** (10-30 min), **Staging**, **Production**.
- **GitHub Environments** oferece gates, secrets segregados e protection rules gratuitos.
- Pipeline lento e flaky sabotam CDelivery.
- O script `analisa_pipeline.py` detecta as violações mais comuns.

---

## Próximo passo

- Faça os **[exercícios resolvidos do Bloco 2](02-exercicios-resolvidos.md)**.
- Siga para o **[Bloco 3 — Estratégias de Release](../bloco-3/03-estrategias-release.md)**.

---

## Referências deste bloco

- **Humble, J.; Farley, D.** *Entrega Contínua*, cap. 5 e 13.
- **Wiggins, A.** *The Twelve-Factor App.* [12factor.net](https://12factor.net/).
- **GitHub Actions — Environments:** [docs.github.com/en/actions/deployment/targeting-different-environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment).
- **GitHub Actions — Artifacts:** [docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts).
- **pydantic-settings:** [docs.pydantic.dev/latest/concepts/pydantic_settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Resolvidos — Bloco 1](../bloco-1/01-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](../README.md) | **Próximo →**<br>[Exercícios Resolvidos — Bloco 2](02-exercicios-resolvidos.md) |

<!-- nav:end -->

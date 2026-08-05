# Parte 3 — Golden paths: dois templates funcionais

**Objetivo.** Publicar dois Software Templates que um dev possa usar via Scaffolder. Cada um gera repositório **pronto para deploy**, com CI verde no primeiro push.

**Pré-requisitos.** Parte 2 concluída. GitHub account com permissão de criar repo.

**Entregáveis em `orbita-idp/templates/`:**

1. `python-fastapi-service/` — template completo com skeleton.
2. `<outro>/` — à sua escolha: Postgres DB, Kafka topic, Worker Python, Go service.
3. Cada template passa em `template_audit.py` (exit 0).
4. Execução comprovada: screenshot ou video de `Create service → Commit → CI verde`.
5. `docs/templates.md` — documentação dos 2 templates.

---

## 3.1 Template 1 — `python-fastapi-service`

Estrutura:

```
templates/python-fastapi-service/
├── template.yaml                           # Backstage Scaffolder
└── skeleton/
    ├── catalog-info.yaml                   # entra no catalogo
    ├── README.md
    ├── pyproject.toml
    ├── src/app/__init__.py
    ├── src/app/main.py                     # FastAPI hello + /healthz /ready
    ├── tests/test_main.py                  # pytest basico
    ├── Dockerfile                          # multi-stage distroless nonroot
    ├── .github/workflows/ci.yml            # lint, test, bandit, pip-audit, build
    ├── .github/workflows/release.yml       # semver tag -> build+push+cosign
    ├── helm/Chart.yaml                     # chart minimo com SLOs default
    ├── helm/values.yaml
    ├── mkdocs.yml
    └── docs/
        ├── index.md
        ├── arquitetura.md
        ├── runbook.md
        └── onboarding.md
```

### 3.1.1 `template.yaml`

Exemplo no Bloco 2. Adaptar para OrbitaTech (catálogo, groups).

### 3.1.2 CI default (`.github/workflows/ci.yml`)

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -e '.[dev]'
      - run: ruff check .
      - run: pytest -q --cov=src --cov-fail-under=70
      - run: bandit -r src -ll
      - run: pip-audit --strict
  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          push: ${{ github.event_name == 'push' }}
          tags: ghcr.io/orbita/${{ github.event.repository.name }}:sha-${{ github.sha }}
```

### 3.1.3 Dockerfile

Multi-stage, distroless, nonroot. Modelo no Bloco 2.

### 3.1.4 Helm standard

`Chart.yaml` + `values.yaml` com:
- 2 replicas (tier silver default).
- Readiness/liveness probes.
- Resources (requests/limits).
- PodDisruptionBudget opcional.
- NetworkPolicy default-deny + allow para obs stack.

### 3.1.5 Validar

```bash
python ../bloco-2/template_audit.py templates/python-fastapi-service
# deve retornar exit 0
```

## 3.2 Template 2 — escolher um

Opções aceitas:

- **`postgres-db`** — gera `DatabaseClaim` CR + helm values.
- **`kafka-topic`** — gera `KafkaTopic` YAML + política.
- **`cronjob-worker`** — worker Python rodando em CronJob com observability.
- **`go-http-service`** — serviço Go similar ao FastAPI.

Estrutura análoga (`template.yaml` + `skeleton/`). Foco: o template gerar algo que **realmente funciona** (aplica no cluster ou cria o recurso concreto).

## 3.3 Executar o template

Fluxo de teste:

1. Abrir Backstage.
2. *Create → Novo servico Python FastAPI*.
3. Preencher: `demo-servico`, descrição, owner (um grupo válido).
4. Apontar para repo GitHub de teste.
5. Scaffolder cria repo.
6. Verificar: CI verde no primeiro push.
7. Catálogo mostra o novo componente.

Salvar prints em `docs/screenshots/`.

## 3.4 Documentação `docs/templates.md`

Para cada template:
- Quando usar.
- O que gera.
- Campos no Scaffolder.
- Decisões técnicas (ADR resumo).
- Como extender.
- Quem mantém (owner).

---

## Critérios de aceitação da Parte 3

- [ ] 2 templates versionados.
- [ ] `template_audit.py` exit 0 em ambos.
- [ ] Execução real do template 1 cria **repositório GitHub** com CI verde.
- [ ] CI contém lint, test, bandit, pip-audit, build.
- [ ] Dockerfile multi-stage, distroless, nonroot.
- [ ] Helm com probes + resources + PodDisruptionBudget.
- [ ] `docs/templates.md` documenta ambos.
- [ ] Screenshots em `docs/screenshots/`.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — Backstage e Software Catalog](parte-2-backstage-catalogo.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Parte 4 — Capabilities, tiers e contratos](parte-4-contratos.md) |

<!-- nav:end -->

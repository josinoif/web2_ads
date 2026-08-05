# Entrega Avaliativa do Módulo 5

**Módulo:** Containers (5h)
**Cenário:** CodeLab — ver [00-cenario-pbl.md](00-cenario-pbl.md)

---

## Objetivo da entrega

Construir a **CodeLab containerizada**: o serviço mínimo viável de um juiz online usando imagens OCI, com runners isolados, ambiente local reproduzível, imagens publicadas, escaneadas e documentadas.

---

## O que entregar

### 1. Repositório GitHub com aplicação + Dockerfiles

Estrutura mínima:

```
codelab-judge/
├── src/codelab/
│   ├── api.py                  # FastAPI — recebe submissões
│   ├── worker.py               # worker que puxa da fila
│   └── runners/
│       ├── python/run.sh       # executa 1 submissão Python
│       ├── javascript/run.sh   # executa 1 submissão JS
│       └── c/run.sh            # executa 1 submissão C
├── docker/
│   ├── api.Dockerfile
│   ├── worker.Dockerfile
│   ├── runner-python.Dockerfile
│   ├── runner-javascript.Dockerfile
│   └── runner-c.Dockerfile
├── docker-compose.yml
├── docker-compose.override.yml # dev
├── tests/
│   ├── unit/
│   └── integration/
├── .github/workflows/
│   └── images.yml              # build + push + scan
├── scripts/
│   └── adicionar-linguagem.md  # runbook para nova linguagem
├── docs/
│   ├── arquitetura.md          # diagrama + decisões
│   ├── runbook-imagens.md
│   └── adr/                    # ao menos 2 ADRs
├── requirements.txt
├── pyproject.toml
├── .dockerignore
├── .hadolint.yaml
└── README.md
```

### 2. Três runners de linguagem com imagens próprias

Obrigatórios **no mínimo 3 runners distintos**: Python, JavaScript e C (ou equivalentes).

Requisitos de cada imagem runner:

- **Base mínima** (distroless, alpine ou slim, justificada).
- **Multi-stage** quando aplicável (compilados).
- **`USER` não-root**.
- **`HEALTHCHECK`** (quando o runner for serviço persistente) **ou** documentação de por que não há.
- **Nenhum segredo** embutido (verificável).
- **Tamanho**: imagem final **< 300 MB** (Python/JS) e **< 100 MB** (C compilado estaticamente).

### 3. Ambiente local com Docker Compose

Um único `docker compose up` deve subir:

- API (porta 8000 local)
- Worker
- Redis
- Postgres
- Runners (imagens prontas — podem ser lazy / on-demand)

Requisitos:

- **`healthcheck`** em Postgres e Redis; `depends_on` com `condition: service_healthy`.
- **Volumes** nomeados para persistência de Postgres.
- **Arquivo de override** para dev (hot reload).
- **Variáveis de ambiente** documentadas em `.env.example`.
- **Makefile** ou README com comandos convenientes.

### 4. Pipeline CI/CD de imagens

Workflow `.github/workflows/images.yml` que:

- Dispara em push de `main` ou tag semver.
- **Lint** dos Dockerfiles (Hadolint).
- **Build** das 3+ imagens (matriz).
- **Scan** com Trivy — falha se achar **CRITICAL** ou **HIGH** não ignorada.
- Gera **SBOM** (Syft) como artefato.
- **Push** ao **GHCR** com tags `:sha-<7>` e `:vX.Y.Z` (quando tag semver).
- Labels OCI obrigatórias (`org.opencontainers.image.*`).

### 5. Documento de arquitetura

`docs/arquitetura.md` (2 a 4 páginas):

- Diagrama Mermaid da arquitetura containerizada.
- Mapa **serviço → imagem → responsabilidade**.
- **O que é isolamento de cada runner** (namespaces usados, limites aplicados) e o que **não** é isolamento (ex.: `--network=none` não resolve tudo).
- **Limites de recursos** por runner (CPU, memória, PIDs, tempo).
- **O que fica para Módulo 7** — reconhecer fronteiras (ex.: "em produção real, orquestrador K8s com PSP/PSA").

### 6. Dois ADRs

Em `docs/adr/`:

- **ADR 001 — Imagem base** (distroless vs alpine vs slim).
- **ADR 002 — Estratégia de isolamento do runner** (user namespace, seccomp, read-only FS, --network=none).

### 7. Runbook "adicionar linguagem"

`scripts/adicionar-linguagem.md` — passo a passo para **1 engenheiro** adicionar uma nova linguagem em **menos de 1 dia**:

1. Criar `docker/runner-<lang>.Dockerfile` seguindo o template.
2. Criar `src/codelab/runners/<lang>/run.sh`.
3. Adicionar testes básicos.
4. Adicionar ao CI matrix.
5. Publicar PR; pipeline cuida do push da imagem.

Demonstre isso adicionando uma **quarta linguagem** (ex.: Go) seguindo o próprio runbook.

### 8. Evidências

No README do repositório, links para:

- Run verde do workflow de imagens.
- Imagem do **GHCR** publicada (mostre URL e digest).
- Saída de `docker images` mostrando tamanhos.
- Saída de `trivy image` (fragmento representativo).
- Arquivo SBOM (syft/SPDX JSON) no registry ou como artefato.

---

## Critérios de avaliação

| Critério | Peso | O que se espera |
|----------|------|------------------|
| **Dockerfiles idiomáticos** | 20% | Multi-stage onde aplicável; USER não-root; cache bem ordenado; `.dockerignore`; `HEALTHCHECK` ou justificativa. |
| **Tamanho e reprodutibilidade das imagens** | 10% | Dentro das metas de tamanho; `docker build` idempotente. |
| **Compose multi-serviço** | 15% | 5+ serviços; healthchecks; `depends_on` com condição; volumes corretos. |
| **Pipeline de imagens** | 15% | Build + scan + SBOM + push funcional; tags corretas; matriz. |
| **Segurança do runner** | 15% | --network=none; FS read-only; limites CPU/mem/PIDs; sem segredos; discussão de trade-offs. |
| **Documentação (arquitetura + ADR)** | 10% | Diagramas claros, ADRs defensíveis. |
| **Runbook e 4ª linguagem adicionada** | 10% | Processo rodável por outra pessoa em < 1 dia. |
| **Reconhece limites** | 5% | Admite que K8s (Módulo 7) resolve coisas que o Compose não resolve (autoscaling, self-heal, PSP). |

---

## Formato e prazo

- **Formato:** link do repositório GitHub.
- **README** deve conter:
  - Setup em 1 comando (`make up` ou equivalente).
  - Diagrama da arquitetura.
  - Links para evidências.
  - Limites reconhecidos.
- **Prazo:** conforme definido pelo professor. Sugestão: **1 semana após o encerramento do módulo**.

---

## Dicas

- **Não tente implementar o judge por inteiro** — submeter, executar, retornar veredito é muito. Foco: **imagens + compose + pipeline**. Execução real dos runners pode ser simulada (rodar um "hello world" da linguagem com limites).
- **Distroless em Python é chato** — `python:3.12-slim` é um bom padrão; distroless fica para imagens compiladas (Go, Rust).
- **`--network=none`** no runner é fundamental. Documente.
- **Não use `latest`** em NENHUMA imagem base. Pinne semver ou digest.
- **Admita** o que fica de fora — gVisor, Kata, user namespaces, PSP; mencione sem implementar.

---

## Referência rápida do módulo

- [Cenário PBL — CodeLab](00-cenario-pbl.md)
- [Bloco 1 — Fundamentos](bloco-1/01-fundamentos-containers.md)
- [Bloco 2 — Dockerfile](bloco-2/02-dockerfile-boas-praticas.md)
- [Bloco 3 — Compose](bloco-3/03-compose-multi-servico.md)
- [Bloco 4 — Produção e segurança](bloco-4/04-producao-seguranca.md)
- [Exercícios progressivos](exercicios-progressivos/)
- [Referências bibliográficas](referencias.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Plano de Adoção e Reconhecimento de Limites](exercicios-progressivos/parte-5-plano-e-limites.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](README.md) | **Próximo →**<br>[Referências Bibliográficas — Módulo 5](referencias.md) |

<!-- nav:end -->

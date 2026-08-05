# Exercícios Progressivos — Módulo 5

Cinco exercícios encadeados que **constroem**, passo a passo, a CodeLab containerizada. Cada parte produz artefatos usados na seguinte.

**Duração total estimada:** 6 a 10 horas.

---

## Panorama

| # | Entrega | Foco | Arquivo |
|---|---------|------|---------|
| 1 | Diagnóstico da CodeLab atual | Bloco 1 — fundamentos + gap analysis | [parte-1-diagnostico.md](parte-1-diagnostico.md) |
| 2 | Dockerfile do primeiro runner | Bloco 2 — imagem idiomática + multi-stage | [parte-2-dockerfile-runner.md](parte-2-dockerfile-runner.md) |
| 3 | Ambiente local com Compose | Bloco 3 — stack completa | [parte-3-compose-stack.md](parte-3-compose-stack.md) |
| 4 | Pipeline de imagens + segurança | Bloco 4 — CI com scan, SBOM, assinatura | [parte-4-pipeline-imagens.md](parte-4-pipeline-imagens.md) |
| 5 | Plano de adoção + reconhecimento de limites | Integração + ponte para Mod 6/7 | [parte-5-plano-e-limites.md](parte-5-plano-e-limites.md) |

---

## Pré-requisitos

- **Todos os blocos** do Módulo 5 estudados.
- Linux, macOS ou Windows com WSL2.
- **Docker** (ou Podman + `alias docker=podman`).
- Python 3.12+, `pip`, `git`.
- Conta no **GitHub** (para o pipeline da parte 4).
- Ferramentas recomendadas (instale durante o exercício conforme necessidade): `trivy`, `syft`, `hadolint`, `dive`, `cosign`.

## Estrutura sugerida do repositório final

```
codelab-judge/
├── src/codelab/
│   ├── api.py
│   ├── worker.py
│   └── runners/python/run.sh
├── docker/
│   ├── api.Dockerfile
│   ├── worker.Dockerfile
│   └── runner-python.Dockerfile
├── tests/
│   ├── unit/
│   └── smoke/
├── .github/workflows/images.yml
├── docs/
│   ├── diagnostico.md                # Parte 1
│   ├── arquitetura.md                # Parte 3
│   ├── adr/
│   │   ├── 001-imagem-base.md
│   │   └── 002-isolamento-runner.md
│   ├── plano-adocao.md               # Parte 5
│   └── limites-reconhecidos.md       # Parte 5
├── docker-compose.yml
├── docker-compose.override.yml
├── docker-compose.test.yml
├── requirements.txt
├── pyproject.toml
├── .dockerignore
├── .hadolint.yaml
├── Makefile
└── README.md
```

---

## Como entregar

Cada exercício contém seção **"O que entregar"**. Em todos:

- **Código/arquivo no repositório**.
- **Captura de execução** (saída de comando, screenshot) quando a saída for relevante.
- **Explicação curta** (markdown) do **porquê** — não só o que.

Entrega única ao final dos 5: **link do repositório** com tudo integrado. Critérios de aceitação estão em [`entrega-avaliativa.md`](../entrega-avaliativa.md).

---

## Boas práticas ao longo do percurso

1. **Commits pequenos** com mensagens claras (reaproveite Conventional Commits do Módulo 4).
2. **ADRs** são curtos (1 página). Documentem trade-offs, não narrem código.
3. Valide **cada imagem** com:
   - `hadolint` no Dockerfile.
   - `analyze_dockerfile.py` (Bloco 2) — se quiser variedade.
   - `docker build --progress=plain` — reveja logs.
   - `docker images` — confira tamanho.
4. **Teste localmente** antes do push: `docker compose up -d && docker compose ps`.
5. **Não pule diagnóstico** — o exercício 1 dá contexto crítico para os demais.

---

## Conexão com módulos anteriores

| De onde vem | O que usa aqui |
|-------------|----------------|
| **Módulo 2** — Git, CI básico | Workflow da parte 4 |
| **Módulo 3** — testes, Testcontainers | Testes unitários dentro de container; smoke test pós-build |
| **Módulo 4** — pipeline, feature flags | Pipeline de imagens é **continuação direta** do `cd.yml`; imagem substitui wheel como artefato |

---

## Próximo passo

Comece pela **[Parte 1 — Diagnóstico](parte-1-diagnostico.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Resolvidos — Bloco 4](../bloco-4/04-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](../README.md) | **Próximo →**<br>[Parte 1 — Diagnóstico da CodeLab](parte-1-diagnostico.md) |

<!-- nav:end -->

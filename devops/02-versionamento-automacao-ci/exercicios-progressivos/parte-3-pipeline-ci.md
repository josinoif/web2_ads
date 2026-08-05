# Parte 3 — Construção de Pipeline CI (2h)

**Objetivo:** Configurar um pipeline de CI real em um projeto simples (Node, Java ou Python), com build, testes automatizados, linter e geração de artefato.

---

## Referência de conteúdo

- [Bloco 2 — Integração Contínua](../bloco-2/02-integracao-continua.md)
- [Bloco 3 — Automação e toil](../bloco-3/03-automacao-toil.md)

---

## Setup do projeto

Escolha **uma** stack:

- **Node.js** — npm, Jest (ou outro test runner), ESLint
- **Java** — Maven, JUnit
- **Python** — pip, pytest, Ruff (ou flake8/black)

Crie um projeto **mínimo** (ou use um repositório existente de exercício) com:

- Pelo menos **um arquivo de código** e **um teste** que passa
- **Script de build** (ex.: `npm run build`, `mvn package`, ou equivalente)
- **Linter** configurado (ESLint, Checkstyle/Ruff, etc.)

---

## Requisitos do pipeline

O pipeline deve:

1. **Executar** em todo push/PR na branch principal (ex.: `main`)
2. **Checkout** do repositório
3. **Instalar dependências** de forma reprodutível (ex.: `npm ci`, `pip install -r requirements.txt`, `mvn` com cache)
4. **Rodar o linter**
5. **Executar o build**
6. **Executar os testes automatizados**
7. **Gerar artefato** (ex.: diretório `dist/`, JAR, ZIP) e publicá-lo como artefato do job (GitHub Actions: `upload-artifact`; GitLab CI: `artifacts`; CodeBuild: configuração de artefatos)

Se qualquer etapa falhar, o pipeline deve falhar.

---

## Ferramentas possíveis

| Ferramenta | Arquivo de configuração | Onde roda |
|------------|--------------------------|-----------|
| **GitHub Actions** | `.github/workflows/ci.yml` | GitHub |
| **GitLab CI** | `.gitlab-ci.yml` | GitLab |
| **AWS CodeBuild** | `buildspec.yml` (+ pipeline no console) | AWS |

Exemplos de pipeline para cada stack estão no [Bloco 2](../bloco-2/02-integracao-continua.md).

---

## Exemplo mínimo (Node + GitHub Actions)

Estrutura:

```text
projeto/
├── package.json
├── src/
│   └── index.js
├── test/
│   └── index.test.js
└── .github/
    └── workflows/
        └── ci.yml
```

**ci.yml** (esqueleto):

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint
      - run: npm run build
      - run: npm test
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

Adapte para seu projeto (nome do path do artefato, comandos de build/test).

---

## Checklist de conclusão

- [ ] Pipeline dispara em push e PR na branch principal
- [ ] Lint roda e falha se houver violação
- [ ] Build roda com sucesso
- [ ] Testes rodam e pipeline falha se algum teste falhar
- [ ] Artefato é gerado e disponibilizado (Actions/Artifacts ou equivalente)
- [ ] Documentação mínima: README ou comentário no YAML explicando as etapas

---

## Entrega (para a Parte 3)

- **Arquivo(.yml ou buildspec)** do pipeline no repositório
- (Opcional) **Link** do repositório ou do último run do pipeline bem-sucedido

Isso será parte da **entrega avaliativa do módulo** (ver [entrega-avaliativa.md](../entrega-avaliativa.md)).

---

## Próximo passo

Na **Parte 4 — Quebra controlada** ([parte-4-quebra-controlada.md](parte-4-quebra-controlada.md)) o professor (ou você, em dupla) introduz um erro proposital (teste falhando, lint falhando ou build falhando); você interpreta os logs, corrige e reflete sobre o impacto.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — Estratégia de Versionamento (1h)](parte-2-estrategia-versionamento.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Parte 4 — Quebra Controlada (1h)](parte-4-quebra-controlada.md) |

<!-- nav:end -->

# Parte 4 — Quality Gates no Pipeline CI

**Tempo:** ~1h
**Pré-requisitos:** Parte 2 e Parte 3 concluídas, **conta GitHub**, **Bloco 3**.
**Entregável:** `.github/workflows/ci.yml` + link para **1 run passando** e **1 run falhando** (do mesmo repositório).

---

## Objetivo

Automatizar **todos** os quality gates no pipeline CI do seu repositório no GitHub. Ao final:

- Cada push / PR dispara o workflow.
- Há pelo menos **5 gates** ativos: lint, format, unit + cobertura, integração, complexidade.
- Você **demonstra** que o gate funciona — cria um commit propositalmente ruim e vê o pipeline **vermelhar**.

---

## Passo 1 — Hospede no GitHub

Se ainda não está:

```bash
# (após criar um repositório vazio em github.com/seu-usuario/mediquick-agendamento)
git remote add origin git@github.com:SEU-USUARIO/mediquick-agendamento.git
git branch -M main
git push -u origin main
```

---

## Passo 2 — Crie o workflow

Arquivo `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  fast-lane:
    name: Fast (lint + format + unit)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pip install radon

      - name: Ruff (lint)
        run: ruff check .

      - name: Ruff (format check)
        run: ruff format --check .

      - name: Complexidade (radon)
        run: |
          # falha se qualquer função ficar grau D+ (CC > 20)
          ! radon cc src --min D --json | grep -q '"rank":'

      - name: Unit tests + coverage
        run: |
          pytest tests/unit \
            --cov=src --cov-branch \
            --cov-report=term-missing \
            --cov-report=xml \
            --cov-fail-under=70

      - name: Upload coverage xml
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-xml
          path: coverage.xml

  integration:
    name: Integration (Postgres via Testcontainers)
    runs-on: ubuntu-latest
    needs: fast-lane
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Integration tests
        run: pytest tests/integration -v
```

> **Nota:** o runner `ubuntu-latest` **já tem Docker instalado** — Testcontainers funciona direto.

**Commit:**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: adiciona pipeline com quality gates completos"
git push
```

Acesse: `github.com/SEU-USUARIO/mediquick-agendamento/actions`. Acompanhe o run verde.

---

## Passo 3 — Ajuste `--cov-fail-under` para a realidade do seu repo

Se seu projeto está em 55% de cobertura (realista para começo), `--cov-fail-under=70` trava a CI. Ajuste para o valor **atual** do seu repo (ou pouco acima). O ratchet sobe aos poucos.

---

## Passo 4 — **Demonstração**: crie um PR que FALHA e outro que PASSA

### PR que falha

Crie um branch:

```bash
git checkout -b exp/quebrar-gate
```

Faça **uma** alteração que **viola um gate**. Exemplos:

- Adicione `x = 1` não usado em uma função (quebra lint).
- Remova um assert de um teste unit (cobertura cai).
- Adicione uma função com CC 25 (quebra radon).

Commit e push:

```bash
git add -A
git commit -m "chore: violação proposital para testar gate"
git push -u origin exp/quebrar-gate
```

Abra um PR via `gh pr create` ou UI. Veja o CI **vermelhar**. **Tire screenshot** ou **capture o link** do run falho.

### PR que passa

Volte ao `main`, faça uma melhoria legítima (ex.: adicionar um teste), commit, PR. Veja o CI **verde**.

---

## Passo 5 — Documente no README

No `README.md`:

```markdown
## CI e Quality Gates

Pipeline: `.github/workflows/ci.yml`

### Gates ativos

- [x] **Lint** — `ruff check`
- [x] **Format** — `ruff format --check`
- [x] **Complexity** — `radon cc --min D` (falha em funções CC > 20)
- [x] **Unit tests + coverage** — `pytest --cov-fail-under=70`
- [x] **Integration tests** — `pytest tests/integration` (com Testcontainers Postgres)

### Evidência de funcionamento

- Run passando (main): https://github.com/SEU-USUARIO/mediquick-agendamento/actions/runs/XXXXX
- Run falhando (PR propositalmente quebrado): https://github.com/SEU-USUARIO/mediquick-agendamento/actions/runs/YYYYY
```

---

## Passo 6 — (Opcional) Pre-commit local

Para **encurtar ainda mais** o feedback, rode os gates leves **localmente antes** de commitar. Instale:

```bash
pip install pre-commit
```

Arquivo `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: pytest-unit
        name: pytest-unit
        entry: pytest tests/unit
        language: system
        pass_filenames: false
```

Ative:

```bash
pre-commit install
```

Daqui em diante, **cada `git commit`** roda lint + unit antes de permitir. Se alguma coisa falha, o commit é **bloqueado** — você conserta e tenta de novo. É o **shift-left no extremo**.

---

## Critérios de "pronto"

- [ ] `.github/workflows/ci.yml` com **≥5 gates** funcionando.
- [ ] **1 run verde** (link no README).
- [ ] **1 run vermelho** de um PR que quebrou um gate de propósito (link no README).
- [ ] README atualizado com instrução de setup + descrição dos gates.
- [ ] (Opcional) `.pre-commit-config.yaml` configurado.

---

## Dicas

- **Cache de pip** é essencial — `cache: "pip"` no setup-python reduz build de 90s para 20s.
- **Evite** `needs:` excessivo — se 2 jobs podem rodar em paralelo, deixe-os paralelos. Feedback é **mínimo dos jobs**.
- **Permissões mínimas**: não dê `contents: write` se você não precisa. Use o mínimo.
- **Se o Docker falhar** em testes de integração no runner, verifique versão e quota. `ubuntu-latest` costuma funcionar; `macos-latest` exige virtualização nested.
- **Secrets**: não commite em `.env`. Use **GitHub Secrets** se precisar de credenciais (aparece no Módulo 9).

---

## Próximo passo

Com o pipeline funcionando, siga para a **[Parte 5 — Reflexão e plano MediQuick](parte-5-reflexao-plano.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Integração com Testcontainers (Postgres real)](parte-3-integracao-testcontainers.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Parte 5 — Reflexão e Plano MediQuick](parte-5-reflexao-plano.md) |

<!-- nav:end -->

# Parte 2 — Pipeline de segurança no CI

**Entrega desta parte:**

- `.github/workflows/security-ci.yml` com jobs paralelos.
- `pre-commit` configurado.
- Exceções documentadas em `.trivyignore` e `SECURITY.md`.

---

## 1. Pre-commit local

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.2
    hooks:
      - id: gitleaks

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.10
    hooks:
      - id: bandit
        args: ["-q", "-lll"]
        exclude: ^tests/

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.3
    hooks:
      - id: ruff
        args: ["--fix"]
```

Instalar:

```bash
pip install pre-commit
pre-commit install
# Rodar uma vez para baixar hooks:
pre-commit run --all-files
```

---

## 2. `.gitleaks.toml` customizado

```toml
title = "MedVault gitleaks"

[extend]
useDefault = true

[[rules]]
id = "medvault-api-key"
description = "Chave de API MedVault"
regex = '''medvault_(sk|pk)_[A-Za-z0-9]{32,}'''
tags = ["key", "medvault"]

[allowlist]
paths = ['''tests/fixtures/.*''']
```

---

## 3. Workflow de CI

`.github/workflows/security-ci.yml`:

```yaml
name: security-ci

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  contents: read
  security-events: write

jobs:
  sast-bandit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install bandit[sarif]==1.7.10
      - run: bandit -r src/ -f sarif -o bandit.sarif || true
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: bandit.sarif }
      - run: bandit -r src/ -q -lll        # falha em HIGH

  sast-semgrep:
    runs-on: ubuntu-latest
    container:
      image: returntocorp/semgrep
    steps:
      - uses: actions/checkout@v4
      - run: semgrep --config auto --sarif --output semgrep.sarif src/ .semgrep/ || true
      - uses: github/codeql-action/upload-sarif@v3
        with: { sarif_file: semgrep.sarif }
      - run: semgrep --config auto --error src/

  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install pip-audit
      - run: pip-audit -r requirements.txt --strict

  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITLEAKS_CONFIG: ${{ github.workspace }}/.gitleaks.toml

  iac:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trivy config (Dockerfile, k8s yaml, helm)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: config
          severity: HIGH,CRITICAL
          exit-code: '1'

  image:
    runs-on: ubuntu-latest
    needs: [sast-bandit, sast-semgrep, sca, secrets, iac]
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t medvault/api:ci .
      - name: Trivy image
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: medvault/api:ci
          severity: HIGH,CRITICAL
          exit-code: '1'
          ignorefile: .trivyignore
```

---

## 4. Regra custom Semgrep

`.semgrep/medvault.yaml`:

```yaml
rules:
  - id: medvault-no-cpf-log
    pattern-either:
      - pattern: logger.$X($MSG, cpf=$Y, ...)
      - pattern: log.$X($MSG, cpf=$Y, ...)
      - pattern: print($MSG)
    message: "Nao logar/printar CPF (dado sensivel LGPD)."
    severity: ERROR
    languages: [python]

  - id: medvault-no-sql-concat
    message: "SQL concatenado com input. Use parametros."
    severity: ERROR
    languages: [python]
    patterns:
      - pattern-either:
          - pattern: f"SELECT ... {$X.query_params[$K]} ..."
          - pattern: "SELECT ..." + $X.query_params[$K] + ...
```

Insira isca em `src/` num branch e valide que Semgrep detecta na CI.

---

## 5. Exceções documentadas

`.trivyignore`:

```
# CVE-2024-12345
#   package: openssl 3.0.11
#   severity: HIGH
#   status: aceita ate 2026-07-01
#   justificativa: fluxo vulneravel (callback customizado de TLS) nao existe no produto
#   owner: AppSec@medvault | ticket: SEC-4321
CVE-2024-12345
```

`SECURITY.md`:

```markdown
# Security Policy

## Report
security@medvault.example

## CVE Exceptions

As excecoes aceitas estao em `.trivyignore` com data de revisao obrigatoria.
Revisao periodica a cada 90 dias.

## Supported versions
Suportamos as 2 ultimas versoes minor (atualmente 1.2.x e 1.3.x).
```

---

## 6. Branch protection

No GitHub, em *Settings → Branches → main*:

- Require pull request before merging (≥ 1 approval).
- Require status checks: `sast-bandit`, `sast-semgrep`, `sca`, `secrets`, `iac`, `image`.
- Require branches to be up to date.
- Include administrators.

---

## 7. Makefile

Adicionar:

```makefile
precommit:
	pre-commit run --all-files

sast:
	bandit -r src/ -q -lll
	semgrep --config auto --error src/

sca:
	pip-audit -r requirements.txt --strict

scan: sast sca
	gitleaks detect --source . --config .gitleaks.toml
	trivy config . --severity HIGH,CRITICAL
```

---

## Critérios de aceitação

- [ ] Workflow `security-ci` roda em toda PR e exibe ao menos 1 job em vermelho quando você insere uma isca.
- [ ] `.trivyignore` tem comentário com data, dono e justificativa em cada CVE.
- [ ] SARIF de Bandit e Semgrep aparecem em *Security → Code scanning*.
- [ ] `pre-commit run --all-files` passa localmente.
- [ ] Branch protection configurada em `main`.

Próxima: [Parte 3 — SBOM, assinatura e proveniência](./parte-3-sbom-assinatura.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — Threat model e Dockerfile endurecido](parte-1-threat-model.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](../README.md) | **Próximo →**<br>[Parte 3 — SBOM, assinatura e proveniência](parte-3-sbom-assinatura.md) |

<!-- nav:end -->

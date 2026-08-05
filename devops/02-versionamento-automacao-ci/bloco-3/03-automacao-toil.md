# Bloco 3 — Automação como Redução de Toil

No SRE (Site Reliability Engineering), **“Eliminating Toil”** (eliminar toil) é um princípio central. Automação não é luxo: é mecanismo de **redução de erro humano**, **padronização**, **escalabilidade** e **observabilidade**. Neste bloco você verá o que é toil, a diferença entre automação reativa e estruturante, e como pipelines de CI se encaixam nessa visão.

---

## 1. O que é toil (SRE)

**Toil** é trabalho manual, repetitivo, que:
- pode ser automatizado;
- não agrega valor de longo prazo (não escala com o crescimento do sistema);
- tende a crescer linearmente com o tamanho do sistema ou do time.

Exemplos: rodar testes manualmente antes de cada merge, fazer deploy copiando arquivos por SSH, reiniciar serviços à mão quando algo falha, preencher planilhas de release.

> **Referência:** *Site Reliability Engineering* (O'Reilly). Capítulo “Eliminating Toil”. O livro define toil e discute quando automatizar e como priorizar.

---

## 2. Automação não é luxo

A automação no contexto DevOps/SRE serve para:

| Objetivo | Descrição |
|----------|-----------|
| **Redução de erro humano** | Passos manuais falham (esquecer um comando, ordem errada); o pipeline executa sempre a mesma sequência. |
| **Padronização** | Todo mundo usa o mesmo build, mesmos testes, mesmo ambiente; menos “na minha máquina funciona”. |
| **Escalabilidade** | O mesmo pipeline atende 1 ou 100 desenvolvedores; não é preciso “uma pessoa que sabe fazer o deploy”. |
| **Observabilidade inicial** | Logs do pipeline, duração dos jobs, histórico de falhas — primeira camada de visibilidade sobre o processo. |

---

## 3. Automação reativa vs automação estruturante

| Tipo | Descrição | Exemplo |
|------|------------|---------|
| **Reativa** | Automatizar **depois** que um problema se repete; foca em “não fazer de novo à mão”. | Script que reinicia o serviço quando cai; runbook automatizado após um incidente. |
| **Estruturante** | Automação **desde o início** do fluxo; o processo já nasce automatizado. | Pipeline de CI desde o primeiro commit; deploy via pipeline, não manual. |

Para um time como a DevPay, **automação estruturante** significa: em vez de “alguém roda os testes antes do merge”, o **CI roda os testes** em todo PR. O processo é desenhado com automação no centro, reduzindo toil e variabilidade.

---

## 4. CI como automação estruturante

O pipeline de CI é um exemplo de automação estruturante:

- **Build** — automatizado a cada push/PR.
- **Testes** — executados sempre, sem depender de alguém “lembrar”.
- **Lint** — rodado no mesmo lugar, com as mesmas regras.

Ferramentas comuns:

- **GitHub Actions** — workflows em YAML no repositório; integrado ao GitHub.
- **GitLab CI** — `.gitlab-ci.yml`; integrado ao GitLab.
- **AWS CodeBuild** — build na nuvem AWS; integra com CodePipeline, CodeCommit, etc. (visão em *AWS Certified DevOps Engineer*).

Exemplo mínimo **GitLab CI** (`.gitlab-ci.yml`), equivalente conceitual ao GitHub Actions:

```yaml
stages:
  - lint
  - test
  - build

lint:
  stage: lint
  image: node:20
  script:
    - npm ci
    - npm run lint

test:
  stage: test
  image: node:20
  script:
    - npm ci
    - npm test

build:
  stage: build
  image: node:20
  script:
    - npm ci
    - npm run build
  artifacts:
    paths:
      - dist/
```

---

## 5. Comandos que viram etapas do pipeline

O que hoje é manual pode virar passo do pipeline:

| Ação manual | No pipeline |
|-------------|-------------|
| `npm test` antes de commitar | Job “test” no CI a cada push/PR. |
| `npm run lint` | Job “lint” no CI. |
| `mvn clean package` e enviar JAR por FTP | Job “build” + etapa de publicação de artefato ou deploy. |
| “Rodar script de migração no servidor” | Etapa de deploy que executa o script de forma padronizada. |

Exemplo de **comando único** que simula o que o CI faz (Node):

```bash
npm ci && npm run lint && npm run build && npm test
```

Se isso falhar localmente, o pipeline também falhará; usar isso antes de push ajuda a não “quebrar o CI”.

---

## 6. Observabilidade inicial

O próprio pipeline gera dados úteis:

- **Status** (sucesso/falha) por commit e branch.
- **Duração** dos jobs — identificar etapas lentas.
- **Logs** — motivo da falha (teste, lint, compilação).
- **Histórico** — tendência de falhas em determinada área.

Isso é uma forma inicial de **observabilidade do processo de entrega**, complementar à observabilidade da aplicação em produção (métricas, logs, traces).

---

## 7. Referência AWS (CodeBuild)

Para visão em nuvem (AWS), o material de certificação *AWS Certified DevOps Engineer* cobre:

- **CodeBuild** — serviço de build gerenciado; você define um `buildspec.yml` com fases (install, build, post_build).
- Integração com **CodePipeline** (orquestração), **CodeCommit** (repositório), **S3** (artefatos).

Exemplo mínimo de **buildspec.yml** (conceitual):

```yaml
version: 0.2
phases:
  install:
    runtime-versions:
      nodejs: 20
    commands:
      - npm ci
  build:
    commands:
      - npm run lint
      - npm run build
      - npm test
artifacts:
  files:
    - '**/*'
  base-directory: dist
```

Isso mantém a mesma ideia: install → lint → build → test → artefato.

---

## Resumo do bloco

- **Toil** = trabalho manual, repetitivo, automatizável; SRE prega sua eliminação.
- **Automação** reduz erro humano, padroniza, escala e gera observabilidade do processo.
- **Reativa** = automatizar após o problema se repetir; **estruturante** = processo já nasce automatizado (ex.: CI desde o início).
- **Pipeline de CI** é automação estruturante; GitHub Actions, GitLab CI e CodeBuild são ferramentas que implementam essa ideia.

**Próximo:** [Bloco 4 — Métricas e impacto](../bloco-4/04-metricas-impacto.md)  
**Exercícios deste bloco:** [03-exercicios-resolvidos.md](03-exercicios-resolvidos.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Exercícios Resolvidos (Integração Contínua)](../bloco-2/02-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Bloco 3 — Exercícios Resolvidos (Automação e Toil)](03-exercicios-resolvidos.md) |

<!-- nav:end -->

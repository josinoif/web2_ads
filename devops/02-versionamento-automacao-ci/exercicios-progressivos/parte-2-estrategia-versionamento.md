# Parte 2 — Estratégia de Versionamento (1h)

**Objetivo:** Definir estratégia de branching, política de PR, política de versionamento e critérios de merge para o cenário DevPay, e entregar um documento curto com justificativa técnica.

---

## Contexto

Com base no diagnóstico da Parte 1 e no conteúdo do [Bloco 1 — Versionamento](../bloco-1/01-versionamento.md), você vai propor como a DevPay deve organizar versionamento e integração.

---

## O que definir

### 1. Estratégia de branching

Escolha **uma** abordagem (ou uma variação) e descreva em 3–5 linhas como ela funcionará na DevPay:

- **Git Flow** — main + develop + feature/release/hotfix
- **GitHub Flow** — main sempre implantável + branches de feature curtas
- **Trunk-Based Development** — uma branch principal, branches muito curtas

Indique:

- Nome da branch principal (ex.: `main` ou `master`)
- Padrão de nome de branches (ex.: `feature/DEVPAY-42-descricao`, `fix/DEVPAY-55-bug`)
- Vida máxima desejada de uma branch (ex.: 1–3 dias)

---

### 2. Política de Pull Request

Defina regras para abertura e aprovação de PRs:

- **Revisão:** quantos aprovadores? Obrigatório para todo merge?
- **Tamanho:** há limite de tamanho (ex.: PRs pequenos, um conceito por PR)?
- **CI:** o pipeline deve passar antes de permitir merge? Branch atualizada com main?

Escreva em tópicos (ex.: “Todo PR exige 1 aprovação”; “CI deve estar verde”).

---

### 3. Política de versionamento

- **Esquema:** Semantic Versioning (MAJOR.MINOR.PATCH)? Outro?
- **Onde a versão vive:** no código (package.json, pom.xml, __version__), em tags Git, em ambos?
- **Quem decide o número:** desenvolvedor, tech lead, pipeline (ex.: gerar a partir da tag)?

Resposta em 5–8 linhas.

---

### 4. Critérios de merge

Liste os critérios que **devem** ser atendidos para um PR ser mergeado na branch principal. Exemplos:

- CI passando (build + testes + lint)
- Branch atualizada com main
- Pelo menos 1 aprovação de revisão
- Sem conflitos
- (Outros que o grupo definir)

---

## Entrega

**Documento curto** (1–2 páginas) contendo:

1. Estratégia de branching (com justificativa em 2–3 linhas: por que essa escolha para a DevPay?)
2. Política de PR (resumida)
3. Política de versionamento (resumida)
4. Critérios de merge (lista)
5. **Justificativa técnica:** como essas escolhas ajudam a **reduzir risco**, **aumentar integração frequente** e **melhorar previsibilidade**, em conexão com o que foi visto no Bloco 1 e no cenário PBL.

Use, se quiser, referências ao material (ex.: “conforme Humble & Farley, integração frequente reduz risco de integração tardia”).

---

## Próximo passo

Na **Parte 3 — Construção de Pipeline CI** ([parte-3-pipeline-ci.md](parte-3-pipeline-ci.md)) você vai implementar um pipeline real (build, testes, linter, artefato) em um projeto simples, usando GitHub Actions, GitLab CI ou CodeBuild.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — Diagnóstico (30 min)](parte-1-diagnostico.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Parte 3 — Construção de Pipeline CI (2h)](parte-3-pipeline-ci.md) |

<!-- nav:end -->

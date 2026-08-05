# Marco 1 — Design e fundação

**Tag alvo:** `v0.1.0-design-ready`.
**Tempo sugerido:** 2 semanas.
**Fase correspondente:** [Fase 1](../bloco-1/01-fase-design.md) + [armadilhas](../bloco-1/01-armadilhas-e-dicas.md).

---

## Objetivo

Fundar o repositório com **decisões explícitas**, **CI verde** e um **esqueleto de código** que prove o mínimo de ciclo (commit → test → feedback).

Não há produto rodando ainda — há **intenção organizada**.

---

## Entregáveis

### Estrutura e documentação
- [ ] Repositório criado com `.gitignore`, `LICENSE`, `CODEOWNERS`.
- [ ] `README.md` com pitch + diagrama Mermaid + como rodar (placeholder).
- [ ] `docs/charter.md` com missão, valores, papéis, política de on-call (mesmo simulada).
- [ ] `docs/arquitetura.md` com diagrama final-alvo.
- [ ] `docs/lgpd/inventario-dados.md` preliminar.

### Decisões
- [ ] ≥ 5 ADRs aceitos em `docs/adr/`.
- [ ] 1 RFC em `docs/rfc/` com alternativas reais.
- [ ] Numeração sequencial; formato consistente.

### CI + código
- [ ] `.github/workflows/ci.yml` rodando lint + test + SAST + SCA.
- [ ] `services/api/` com esqueleto FastAPI + 1 teste de smoke.
- [ ] `pyproject.toml` com deps mínimas e `[dev]` extras.
- [ ] `Makefile` com alvos declarados.

### Evidências
- [ ] ≥ 3 PRs mergeados (não tudo num commit).
- [ ] Retrospectiva em `docs/retro/marco1.md`.
- [ ] `CHANGELOG.md` com entrada para `v0.1.0`.
- [ ] Tag `v0.1.0-design-ready`.

---

## Critérios de avaliação deste marco

| Item | Peso local |
|------|------------|
| Qualidade dos ADRs (contexto + alternativas + consequências) | 30% |
| RFC com debate real | 15% |
| README raiz claro | 15% |
| CI verde com ferramentas corretas | 15% |
| LGPD preliminar + charter | 10% |
| Histórico de commits/PRs | 10% |
| Retrospectiva | 5% |

---

## Armadilhas que matam este marco

- ADRs genéricos, com "No contexto moderno de DevOps...".
- RFC que só descreve a solução sem discutir alternativas.
- 1 commit gigante com "initial project structure" — sem trilha de aprendizado.
- Nenhuma consideração LGPD.
- CI que **não roda**, só existe o arquivo.

---

## Antes de fechar o marco

Responda em voz alta (ou escrito em `docs/retro/marco1.md`):

1. *Qual ADR eu menos gosto? Por quê?*
2. *Qual decisão eu adiei porque ainda não sei? (Candidata a RFC futura.)*
3. *Se eu fosse contratado amanhã para continuar esse projeto, o README me bastaria?*
4. *Qual trade-off de LGPD eu ainda não encarei?*

Se responder essas perguntas com sinceridade, o marco 1 está pronto.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Marcos do Capstone — roteiro de 5 partes](README.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Marco 2 — Sistema entregando em staging](parte-2-entrega-end-to-end.md) |

<!-- nav:end -->

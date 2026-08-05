# Entrega Avaliativa do Módulo 2

**Módulo:** Versionamento, Automação e CI (5h)

---

## O que entregar

Os alunos devem entregar:

### 1. Arquivo do pipeline

- **Arquivo de configuração** do pipeline de CI (ex.: `.github/workflows/ci.yml`, `.gitlab-ci.yml` ou `buildspec.yml`).
- O pipeline deve incluir: **checkout**, **instalação de dependências**, **lint**, **build**, **testes** e **geração/publicação de artefato**.
- Pode ser o mesmo repositório e pipeline desenvolvidos na Parte 3 dos exercícios progressivos.

### 2. Estratégia de versionamento documentada

- **Documento curto** (1–2 páginas) com:
  - Estratégia de branching adotada (ou recomendada para o cenário)
  - Política de Pull Request (revisão, CI obrigatório, tamanho)
  - Política de versionamento (ex.: Semantic Versioning)
  - Critérios de merge

Pode ser o documento produzido na Parte 2 (estrategia de versionamento), revisado e ampliado se necessário.

### 3. Justificativa técnica

Texto (cerca de 1 página) explicando as escolhas com base em:

- **Redução de risco** — como versionamento e CI reduzem risco (integração frequente, feedback rápido, gates de qualidade).
- **Frequência de integração** — por que a estratégia de branching e os critérios de merge favorecem integração frequente.
- **Automatização** — como o pipeline elimina toil e padroniza build/teste.
- **Impacto organizacional** — em que medida as mudanças afetam a forma de trabalhar do time (ex.: responsabilidade compartilhada, confiança no processo).

Sugestão: usar referências ao material do módulo e às obras indicadas (Humble & Farley, SRE, AWS DevOps) quando aplicável. Ver [referencias.md](referencias.md).

---

## Critérios de avaliação (sugestão)

| Critério | Peso | O que se espera |
|----------|------|------------------|
| Pipeline funcional e completo | Alto | Pipeline roda em push/PR; lint, build, teste e artefato configurados; falha quando esperado. |
| Estratégia coerente e documentada | Médio | Branching, PR e versionamento descritos de forma clara e consistente. |
| Justificativa técnica | Alto | Argumentação baseada em redução de risco, integração frequente, automação e impacto organizacional. |
| Alinhamento ao cenário PBL | Médio | Respostas aplicáveis ao problema da DevPay (ou ao contexto escolhido). |

---

## Formato e prazo

- **Formato:** repositório (com pipeline e, se desejado, README) + documento em PDF ou Markdown (estratégia + justificativa).
- **Prazo:** conforme definido pelo professor.

---

## Referência rápida do módulo

- [Cenário PBL](00-cenario-pbl.md)
- [Bloco 1 — Versionamento](bloco-1/01-versionamento.md)
- [Bloco 2 — Integração Contínua](bloco-2/02-integracao-continua.md)
- [Bloco 3 — Automação e toil](bloco-3/03-automacao-toil.md)
- [Bloco 4 — Métricas e impacto](bloco-4/04-metricas-impacto.md)
- [Exercícios progressivos](exercicios-progressivos/)
- [Referências bibliográficas](referencias.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Reflexão Final (30 min)](exercicios-progressivos/parte-5-reflexao.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](README.md) | **Próximo →**<br>[Referências Bibliográficas](referencias.md) |

<!-- nav:end -->

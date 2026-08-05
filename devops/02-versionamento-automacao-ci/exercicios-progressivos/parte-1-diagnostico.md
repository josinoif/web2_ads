# Parte 1 — Diagnóstico (30 min)

**Objetivo:** Aplicar o cenário PBL da DevPay para identificar problemas estruturais, classificar riscos e mapear causas técnicas e organizacionais.

---

## Contexto

Releia o cenário da DevPay em [00-cenario-pbl.md](../00-cenario-pbl.md):

- Branches por semanas → conflitos enormes ao integrar
- Bugs só em homologação
- Deploy manual
- Medo em cada release

---

## Atividade em grupo (4–5 pessoas)

### 1. Identificar problemas estruturais

Liste **pelo menos 4 problemas** que você considera **estruturais** (não pontuais) no processo da DevPay. Para cada um, indique se é mais:

- **Técnico** (ferramenta, processo técnico)
- **Organizacional** (cultura, responsabilidade, fluxo de decisão)
- **Híbrido**

**Exemplo de preenchimento:**

| # | Problema estrutural | Técnico / Organizacional / Híbrido |
|---|----------------------|------------------------------------|
| 1 | Integração tardia (branches longas) | Híbrido |
| 2 | ... | ... |

---

### 2. Classificar riscos

Para cada problema listado, classifique o **risco** que ele gera:

- **Alto** — impacto direto em produção, clientes ou segurança
- **Médio** — atrasa entrega ou consome tempo do time de forma repetida
- **Baixo** — incômodo, mas contornável

**Exemplo:**

| Problema | Risco (Alto/Médio/Baixo) | Justificativa em uma linha |
|----------|---------------------------|----------------------------|
| Bugs só em homologação | Alto | Custo de correção alto; pode vazar para produção |

---

### 3. Mapear causas

Escolha **dois** problemas e para cada um faça um **mapeamento simples de causa**:

- **Causa técnica:** o que na ferramenta ou no processo técnico permite esse problema?
- **Causa organizacional:** o que na forma de trabalhar do time (papéis, prioridades, hábitos) contribui?

**Exemplo (problema: “conflitos enormes ao integrar”):**

- **Causa técnica:** branches longas e divergentes; falta de integração contínua com a main.
- **Causa organizacional:** priorização de “entregar feature inteira” antes de integrar; falta de política de branch curta.

---

## Entrega (em sala)

- Um **documento curto** (lista + tabelas) ou **poster** com:
  - Problemas estruturais identificados
  - Classificação de risco
  - Mapeamento de causas (técnicas e organizacionais) para pelo menos 2 problemas

- **Discussão em grupo maior:** cada grupo apresenta 1 problema e 1 causa que considera mais crítica.

---

## Próximo passo

Com o diagnóstico feito, siga para a **Parte 2 — Estratégia de versionamento** ([parte-2-estrategia-versionamento.md](parte-2-estrategia-versionamento.md)), onde você vai propor branching, política de PR e critérios de merge para a DevPay.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Progressivos — Módulo 2](README.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Parte 2 — Estratégia de Versionamento (1h)](parte-2-estrategia-versionamento.md) |

<!-- nav:end -->

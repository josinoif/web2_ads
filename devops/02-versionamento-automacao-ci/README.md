# Módulo 2 — Versionamento, Automação e CI

**Carga horária:** 5 horas  
**Nível:** Graduação (ensino superior)

---

## Objetivos de Aprendizagem

Ao final do módulo, você será capaz de:

- Explicar **por que a integração contínua reduz risco** (fundamentação Humble & Farley).
- **Modelar uma estratégia de versionamento** adequada ao contexto do projeto.
- **Criar e configurar um pipeline de CI** real (build, testes, linter, artefato).
- Entender o **impacto do CI na confiabilidade** (ligação com SRE).
- **Diferenciar** automação reativa de automação estruturante.
- **Relacionar** CI com redução de lead time e risco de deploy.

---

## Estrutura do Material

O conteúdo está organizado em **blocos teóricos** e **exercícios progressivos**, no modelo PBL (Problem-Based Learning).

| Ordem | Conteúdo | Arquivo(s) |
|-------|----------|------------|
| 0 | Cenário PBL (DevPay) | [00-cenario-pbl.md](00-cenario-pbl.md) |
| 1 | Versionamento como controle de complexidade | [bloco-1/01-versionamento.md](bloco-1/01-versionamento.md) · [exercícios](bloco-1/01-exercicios-resolvidos.md) |
| 2 | Integração Contínua (CI) | [bloco-2/02-integracao-continua.md](bloco-2/02-integracao-continua.md) · [exercícios](bloco-2/02-exercicios-resolvidos.md) |
| 3 | Automação como redução de toil | [bloco-3/03-automacao-toil.md](bloco-3/03-automacao-toil.md) · [exercícios](bloco-3/03-exercicios-resolvidos.md) |
| 4 | Métricas e impacto | [bloco-4/04-metricas-impacto.md](bloco-4/04-metricas-impacto.md) · [exercícios](bloco-4/04-exercicios-resolvidos.md) |
| 5 | Exercícios progressivos (5 partes) | [exercicios-progressivos/](exercicios-progressivos/) |
| 6 | Entrega avaliativa | [entrega-avaliativa.md](entrega-avaliativa.md) |
| — | Referências bibliográficas | [referencias.md](referencias.md) |

---

## Como Estudar

1. **Comece pelo cenário PBL** — leia o problema da DevPay e a pergunta norteadora.
2. **Siga a ordem dos blocos** — cada bloco aprofunda conceitos e traz exemplos e comandos.
3. **Faça os exercícios resolvidos** após cada bloco para fixar.
4. **Execute os exercícios progressivos** (diagnóstico → estratégia → pipeline → quebra controlada → reflexão).
5. **Consulte as referências** (Humble & Farley, SRE, AWS DevOps) quando indicado no texto.

---

## Ideia Central do Módulo

O módulo não é sobre ferramenta; é sobre **conceitos**:

| Conceito | Significado |
|----------|-------------|
| **Versionamento** | Controle de risco e complexidade |
| **CI** | Feedback rápido e integração frequente |
| **Automação** | Escalabilidade e redução de toil |
| **Pipeline** | Linha de produção de software |

Como Humble & Farley descrevem em *Entrega Contínua*, o pipeline é a **linha de produção de software**: cada commit pode ser construído, testado e potencialmente entregue de forma repetível e segura.

---

*Material alinhado a fundamentação em Entrega Contínua (Humble & Farley), SRE (O'Reilly) e práticas de mercado (GitHub, GitLab, AWS).*

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Referências Bibliográficas — Módulo 1](../01-fundamentos-cultura/referencias.md) | **↑ Índice**<br>Módulo 2 — Versionamento e integração contínua | **Próximo →**<br>[Cenário PBL — Problema Norteador do Módulo](00-cenario-pbl.md) |

<!-- nav:end -->

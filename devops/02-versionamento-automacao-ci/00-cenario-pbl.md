# Cenário PBL — Problema Norteador do Módulo

Este módulo é guiado por um **problema real** (PBL). O conteúdo teórico e os exercícios estão a serviço de responder à pergunta norteadora ao final.

---

## A empresa: DevPay

A **DevPay** é uma startup que desenvolve um **sistema de pagamentos**. O produto está no mercado, mas o processo de desenvolvimento e entrega está cheio de atritos.

---

## Problemas atuais

| Problema | Descrição |
|----------|------------|
| **Branches longas** | Cada desenvolvedor trabalha em sua própria branch por **semanas**. |
| **Conflitos enormes** | Na hora de integrar, os merges viram pesadelos: conflitos em dezenas de arquivos. |
| **Bugs tardios** | Defeitos só aparecem no **ambiente de homologação**, quando o custo de correção já é alto. |
| **Deploy manual** | Cada ida para produção depende de passos manuais e scripts “na cabeça” de uma pessoa. |
| **Medo em cada release** | Toda release gera **medo**: “Será que quebrou algo?”. |

---

## O que a empresa quer

- **Reduzir risco** — menos surpresas em produção.
- **Aumentar velocidade** — entregar valor com mais frequência.
- **Garantir qualidade mínima automática** — não depender só de “lembrar” de rodar testes.

---

## Pergunta norteadora

> **Como estruturar versionamento e CI para reduzir risco e aumentar previsibilidade?**

Durante o módulo, você vai:

1. **Diagnosticar** os problemas estruturais (técnicos e organizacionais).
2. **Definir** uma estratégia de versionamento e de PRs.
3. **Construir** um pipeline de CI real (build, testes, linter, artefato).
4. **Vivenciar** uma quebra controlada (teste/lint/build falhando) e corrigir.
5. **Refletir** sobre limites e trade-offs (velocidade vs burocracia, trunk-based, responsabilidade).

Ao final, a entrega avaliativa pede o **arquivo do pipeline**, a **estratégia documentada** e uma **justificativa técnica** alinhada a redução de risco, integração frequente e automação.

---

## Próximo passo

Leia o **[Bloco 1 — Versionamento como controle de complexidade](bloco-1/01-versionamento.md)** para começar a construir as bases que a DevPay (e qualquer time) precisa para reduzir risco e ganhar previsibilidade.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Módulo 2 — Versionamento, Automação e CI](README.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](README.md) | **Próximo →**<br>[Bloco 1 — Versionamento como Controle de Complexidade](bloco-1/01-versionamento.md) |

<!-- nav:end -->

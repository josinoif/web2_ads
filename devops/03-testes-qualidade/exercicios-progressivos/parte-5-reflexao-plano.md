# Parte 5 — Reflexão e Plano MediQuick

**Tempo:** ~30 minutos
**Pré-requisitos:** Partes 1–4 concluídas.
**Entregável:** documento `docs/estrategia-de-testes.md` no seu repositório (1 a 2 páginas).

---

## Objetivo

Consolidar tudo em um **documento curto** que junta:

- O **diagnóstico** (da Parte 1).
- As **decisões técnicas** (das Partes 2–4).
- Um **plano de 6 meses** para a MediQuick.
- **Limites e riscos** do plano.

Este documento é **peça central** da [entrega avaliativa](../entrega-avaliativa.md).

---

## Estrutura sugerida do documento

### Seção 1 — Diagnóstico (~1/2 página)

Recupere da **Parte 1**:

- Proporção atual da pirâmide da MediQuick (%).
- Anti-padrão identificado (Ice Cream Cone etc.).
- Diagrama Mermaid **atual** vs. **alvo**.

### Seção 2 — Decisões técnicas deste repositório (~1/2 página)

Explique **as escolhas** que você fez durante as Partes 2–4:

1. **Proporção de testes** escolhida (ex.: 20 unit + 5 integração + 1 E2E). Por quê?
2. **Threshold de cobertura**. Por quê esse valor e não outro?
3. **Estratégia de test doubles**. Onde usou mock/stub/fake? O que **evitou** mockar e por quê?
4. **Quais sintomas da MediQuick seu repo resolve**? (Ex.: sintoma 1, 5, 9.) Quais **ficam para outros módulos**?

### Seção 3 — Plano de 6 meses para a MediQuick (~1/2 página)

Matrize **meses x ações** (ou narrativa). Inclua:

- **Mês 1**: primeiros passos (pre-commit, pipeline mínimo, cobertura baseline).
- **Mês 2–3**: TDD em feature nova + caracterização do crítico.
- **Mês 4–5**: Testcontainers em integrações, aposentar E2E redundante.
- **Mês 6**: ratchet de cobertura, avaliação de mutation testing.

Diga explicitamente **o que NÃO tentar fazer** agora (ex.: não escrever Playwright ainda).

### Seção 4 — Riscos e limites (~1/4 de página)

Liste **pelo menos 3 riscos** concretos:

- O que pode **atrapalhar** a execução do plano?
- O que **cobertura + TDD NÃO resolvem** sozinhos (ex.: qualidade de requisito, design de produto)?
- Que **efeitos perversos** (Lei de Goodhart) podem surgir?

### Seção 5 — Referências (~1/4 de página)

Cite **mínimo 2 obras da pasta `books/`** + 1 referência externa (Fowler, Google, etc.). Use o formato do arquivo [referencias.md](../referencias.md).

---

## Roteiro de perguntas para guiar a reflexão

Responda mentalmente — as respostas compõem o documento:

### Sobre TDD

- Como foi fazer TDD? Foi mais lento ou mais rápido que escrever "normal"?
- Quando sentiu o ciclo curto funcionando? E quando **quis desistir**?
- O design do seu código é diferente de como você faria sem TDD? Em que ponto?

### Sobre cobertura

- Sua cobertura chegou a quantos %?
- Onde faltou cobertura e por quê? Vai atacar depois?
- Um teste seu dá 100% de cobertura mas tem assert fraco — você sabe qual?

### Sobre Testcontainers

- Alguma vez você colocou um teste que dava passa como unit mas falhava em integração? O que era?
- Subir contêiner é lento? Quanto? Vale?

### Sobre o pipeline

- Quanto tempo o pipeline leva no total? (em segundos/minutos)
- Qual gate barrou mais tentativas? Isso reflete um problema do código ou do gate?
- Se um dev da MediQuick usasse seu pipeline, ela reclamaria? De quê?

### Sobre a transformação da MediQuick

- Qual é o **primeiro passo** que você daria se chegasse lá segunda-feira?
- O que levaria **mais do que 6 meses**? (Ex.: cultura, redesenho arquitetural.)
- Se **só uma** das práticas pudesse ser adotada (TDD, BDD, Testcontainers, Quality Gates, etc.), qual teria **maior ROI** para a MediQuick? Por quê?

---

## Critérios de "pronto"

- [ ] Documento `docs/estrategia-de-testes.md` commitado no repositório.
- [ ] **5 seções** (diagnóstico, decisões, plano, riscos, referências).
- [ ] **2 diagramas Mermaid** (atual vs. alvo).
- [ ] **Mínimo 2 referências** de `books/` + 1 externa.
- [ ] Entre **600 e 1500 palavras**. Não mais.
- [ ] Você **se reconhece** no texto — é a sua opinião técnica, não regurgitação do material.

---

## Exemplo de abertura (apenas como calibre)

> # Estratégia de Testes — MediQuick
>
> ## 1. Diagnóstico
>
> A MediQuick apresenta o anti-padrão **Ice Cream Cone** em estado avançado. Com ~380 E2E (76%), 100 integração (20%) e apenas 20 unit (4%), a pirâmide está invertida e há ainda uma camada de teste manual que consome 3 dias por release. Cobertura unitária < 15% e 5 pessoas de QA em burnout são os sintomas mais graves.
>
> ## 2. Decisões deste repositório
>
> Este repositório foi construído com 20 testes unitários, 4 de integração (Postgres via Testcontainers) e 2 E2E HTTP — totalizando 26. A proporção (77%/15%/8%) reproduz deliberadamente a pirâmide saudável que a MediQuick deveria perseguir. Threshold de cobertura foi fixado em **75%** — realisticamente atingível para código novo com TDD, mas exigente o suficiente para bloquear omissões óbvias. Test doubles foram usados **apenas** para `notificador` (serviço externo de e-mail) via Mock; banco, tempo e lógica de negócio foram testados **sem mock** — optamos por Fake (in-memory) onde fazia sentido.
>
> Este repositório resolve os sintomas **1** (cobertura baixa), **5** (dev não roda local — pre-commit resolve), **9** (over-mocking — só 1 mock) e **10** (sem quality gates). Os sintomas 2 (pirâmide invertida global), 3 (flaky E2E) e 4 (QA gargalo) ficam para iniciativa organizacional da MediQuick, não para um repositório de exemplo.
>
> ## 3. Plano de 6 meses...

---

## Próximo passo

Com este documento, você tem **todos os artefatos** da entrega avaliativa:

- Repositório Git com domínio + testes unit + integração + E2E.
- Pipeline CI com quality gates (passando e falhando, demonstrado).
- Documento de estratégia.

**Siga para a** [entrega avaliativa](../entrega-avaliativa.md) **para conferir o checklist final e organizar o material.**

---

## Em uma frase

> *O objetivo do módulo não é "ter muitos testes"; é **ter a confiança para entregar rápido**. Teste é ferramenta; confiança é o resultado.*

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 4 — Quality Gates no Pipeline CI](parte-4-quality-gates-ci.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Entrega Avaliativa do Módulo 3](../entrega-avaliativa.md) |

<!-- nav:end -->

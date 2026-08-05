# Parte 1 — Diagnóstico da Pirâmide Atual da MediQuick

**Tempo:** ~30 minutos
**Pré-requisitos:** Bloco 1 — Pirâmide de testes e fundamentos.
**Entregável:** análise escrita + 1 diagrama (Mermaid ou desenho).

---

## Objetivo

Aplicar o conceito de **pirâmide de testes** ao estado atual da MediQuick e **identificar**:

- Qual anti-padrão se manifesta.
- Que investimento mudaria mais o resultado em 3 meses.
- Que trade-offs qualquer escolha implica.

---

## Contexto (resumo do cenário PBL)

Da [descrição da MediQuick](../00-cenario-pbl.md):

- ~500 testes: **~380 E2E**, **~100 integração**, **~20 unit**.
- Cobertura unitária **< 15%**.
- E2E **flaky** — 1 em 4 falha sem motivo real.
- QA manual revisa **3 dias** por release.
- Dev **não roda** teste localmente.

---

## Instruções

### Passo 1 — Calcule as proporções

Com base nos números acima (ou estime você mesmo):

| Nível | Quantidade | % do total |
|-------|------------|-----------|
| Unit | 20 | __% |
| Integração | 100 | __% |
| E2E | 380 | __% |
| **Total** | **500** | 100% |

**Complete os percentuais.**

### Passo 2 — Classifique o anti-padrão

Dos anti-padrões do Bloco 1, qual a MediQuick manifesta? Justifique em 2 a 3 frases.

- Ice Cream Cone
- Hourglass
- Test Diamond
- Pirâmide fraca (base pequena)

### Passo 3 — Crie um diagrama Mermaid do estado atual vs. alvo

Use o template abaixo. Substitua os números.

```markdown
**Atual (MediQuick):**

\```mermaid
flowchart TB
    M[Teste Manual<br/>não automatizado]
    E[E2E<br/>__%]
    I[Integração<br/>__%]
    U[Unit<br/>__%]
    style E fill:#ffcdd2
    style I fill:#fff9c4
    style U fill:#c8e6c9
    style M fill:#ef9a9a
\```

**Alvo (6 meses):**

\```mermaid
flowchart TB
    E2[E2E<br/>__%]
    I2[Integração<br/>__%]
    U2[Unit<br/>__%]
    style E2 fill:#ffcdd2
    style I2 fill:#fff9c4
    style U2 fill:#c8e6c9
\```
```

### Passo 4 — Priorize as intervenções

Liste **3 ações** por ordem de impacto/custo. Para cada uma:

- **Ação**: descrição
- **Impacto esperado** (por que mexe no problema)
- **Custo** (humano, infra, tempo)
- **Prazo razoável**

Exemplo de formato:

```
1. Aposentar 50% dos E2E redundantes, migrando para unit/integração.
   Impacto: reduz 40 min do tempo de pipeline; libera sinal útil.
   Custo: 2 devs x 3 semanas, reescrevendo testes no caminho.
   Prazo: mês 2-3.
```

### Passo 5 — Reconheça riscos da transformação

Em 3 a 5 linhas, responda: **o que pode dar errado** em uma transformação dessas? Dê exemplos concretos.

---

## Critérios de "pronto"

- [ ] Proporções percentuais calculadas.
- [ ] Anti-padrão nomeado e justificado.
- [ ] **2 diagramas** Mermaid (estado atual + alvo) funcionando.
- [ ] **3 ações priorizadas** com impacto + custo + prazo.
- [ ] Seção de **riscos** mencionando pelo menos 2 riscos concretos.

---

## Dicas

- **Não** escolha o alvo "80/15/5" mecânica-mente. Explique por que esse é o alvo **da MediQuick**, dado o domínio médico.
- **Não** proponha "reescrever tudo". A MediQuick **não pode parar** de entregar. Proponha transformação **incremental**.
- **Reconheça que 20% de unit pode ser impossível em 3 meses** — seja honesto sobre o ritmo.

---

## Exemplo de resposta (versão reduzida, para calibrar)

> **Classificação:** Ice Cream Cone. 76% do esforço está em E2E (380/500), contra apenas 4% em unit. Acrescente-se a camada de teste manual de 3 dias por release — a MediQuick está **além** do Ice Cream Cone, está "em pizza gigante invertida".
>
> **Prioridade 1:** introduzir TDD em **features novas** (não tocar no legado ainda). Custo: 0 pessoas adicionais, requer treinamento de 1 semana. Impacto: a partir do mês 2, todo código novo vem com teste. Prazo: mês 1.
>
> **Prioridade 2:** caracterizar os caminhos críticos do domínio (agendamento, prescrição) via **testes unit pós-hoc**. Custo: 2 devs, 3-4 semanas. Impacto: cobertura de 15% → 40% nos módulos críticos. Prazo: mês 2-3.
>
> **Prioridade 3:** aposentar gradualmente E2E redundantes; 450 → ~30 em 6 meses. Impacto: pipeline mais rápido, menos flaky. Custo: 1 dev, contínuo. Prazo: mês 2-6.
>
> **Riscos:** (1) time resistir a TDD sem ganhos visíveis antes de 2 meses; (2) legado crítico pode ter bugs latentes que só aparecem quando testado de verdade; (3) aposentar E2E pode pular cobertura real se migração for pressa demais.

> Este exemplo serve como **calibre** — sua resposta deve ser **sua**, adaptada ao que você acredita.

---

## Próximo passo

Com o diagnóstico pronto, avance para a **[Parte 2 — TDD do serviço de Agendamento](parte-2-tdd-agendamento.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Progressivos — Módulo 3](README.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Parte 2 — TDD do Serviço de Agendamento](parte-2-tdd-agendamento.md) |

<!-- nav:end -->

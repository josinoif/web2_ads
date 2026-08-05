# Bloco 4 — Exercícios Resolvidos (Métricas e Impacto)

---

## Exercício 1 — Relacionar CI e métricas

**Enunciado:** Explique em uma frase como a adoção de CI pode **reduzir o lead time** de uma mudança até produção.

**Solução:**

O CI automatiza build e testes a cada push/PR, eliminando espera por integração manual e por “rodar testes na máquina de alguém”, de modo que o código fica “pronto para deploy” mais rápido e o tempo total do commit até produção tende a diminuir.

---

## Exercício 2 — Change failure rate

**Enunciado:** Um time faz 20 deploys no mês; 3 resultaram em rollback ou hotfix. Qual a change failure rate? O que o CI pode fazer para melhorar esse número?

**Solução:**

- **Change failure rate** = 3/20 = **15%**.
- **CI** pode melhorar ao garantir que todo código mergeado (e deployado) passou em build e testes automatizados, reduzindo a quantidade de mudanças “quebradas” que chegam a produção; assim, a tendência é diminuir o numerador (menos deploys com falha) e, com o tempo, a taxa.

---

## Exercício 3 — MTTR e pipeline

**Enunciado:** Por que um pipeline de deploy automatizado pode **reduzir o MTTR** após um incidente causado por um deploy ruim?

**Solução:**

Com pipeline de deploy definido e automatizado, o time pode fazer **rollback** (reverter para a versão anterior) ou **hotfix** (correção + novo deploy) executando o mesmo processo, sem depender de passos manuais e frágeis. O tempo para “restaurar” o serviço (revertendo ou corrigindo) diminui, reduzindo o MTTR.

---

## Exercício 4 — Falso positivo no pipeline

**Enunciado:** O que é um “falso positivo” no contexto do pipeline de CI? Que risco isso traz?

**Solução:**

**Falso positivo** = o pipeline **passa** (fica verde) mesmo quando o código está **errado** (bug, quebra de contrato, etc.).  
**Risco:** o time confia no CI e faz merge/deploy; o defeito só aparece em produção ou em homologação, aumentando change failure rate e minando a confiança no pipeline. Por isso é importante manter testes e lint relevantes e atualizados.

---

## Exercício 5 — Priorização (PBL)

**Enunciado:** A DevPay mediu: lead time médio 14 dias, change failure rate 25%. Se você pudesse atacar apenas um deles primeiro com melhorias de versionamento e CI, qual escolheria e por quê?

**Solução (argumentação possível):**

- **Opção A — Reduzir change failure rate:** Cada falha gera custo (rollback, hotfix, perda de confiança). 25% é alto; reduzir isso pode dar mais segurança para depois aumentar a frequência de deploy. CI e testes bem desenhados atacam diretamente a qualidade do que sobe.
- **Opção B — Reduzir lead time:** 14 dias é muito para feedback; reduzir permite ciclos mais curtos e aprendizado mais rápido. Versionamento (branches curtas) + CI atacam o lead time.

Ambas são defensáveis. Uma justificativa coerente seria: atacar **change failure rate** primeiro (com CI e testes), para que ao **reduzir lead time** (deploys mais frequentes) não se multipliquem as falhas. Ou seja: primeiro estabilizar qualidade (reduzir taxa de falha), depois acelerar (reduzir lead time e aumentar frequência).

---

**Próximo:** [Exercícios progressivos — Parte 1: Diagnóstico](../exercicios-progressivos/parte-1-diagnostico.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Métricas e Impacto](04-metricas-impacto.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Exercícios Progressivos — Módulo 2](../exercicios-progressivos/README.md) |

<!-- nav:end -->

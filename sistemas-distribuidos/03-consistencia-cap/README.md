# 03 — Consistência e CAP (intuição)

**Conceito:** sob partição de rede, o sistema precisa escolher entre consistência e disponibilidade (visão didática do CAP).

**Stack:** Python 3 (dois nós + “partição” simulada)

**Status:** planejado

## Objetivo do mini-projeto

Dois nós; simular **partição** (bloquear comunicação entre eles); escrever em um e ler no outro. Comparar modo “prioriza consistência” vs “prioriza disponibilidade”.

## Experimento sugerido

1. Sem partição: escrita e leitura batem.
2. Com partição: um modo recusa escrita; outro modo aceita e gera leitura stale/divergente.
3. Remover a partição e discutir reconciliar estado.

## O que observar

- Partição é real (mesmo em lab: “não consigo falar com o outro processo”).
- Não dá para ter C e A “fortes” ao mesmo tempo sob P.
- Sistemas reais escolhem trade-offs (e modelos de consistência intermediários).

## Perguntas-guia

- Para um extrato bancário, o que você priorizaria?
- Para um feed de redes sociais, e para um carrinho de compras?

# 02 — Replicação

**Conceito:** copiar estado entre nós para disponibilidade e/ou desempenho de leitura.

**Stack:** Python 3 (vários processos / portas)

**Status:** planejado

## Objetivo do mini-projeto

Um nó **líder** aceita escritas; **réplicas** recebem cópias. O aluno lê de réplicas e vê atraso ou falha de sincronização.

## Experimento sugerido

1. Escrever no líder.
2. Ler nas réplicas (imediatamente e após um delay).
3. Derrubar uma réplica e continuar lendo nas outras.

## O que observar

- Replicação não é mágica: existe atraso (replication lag).
- Mais réplicas ≠ consistência automática.
- Disponibilidade de leitura sobe; consistência forte fica mais cara.

## Perguntas-guia

- Replicação síncrona vs assíncrona: o que se ganha e o que se perde?
- Quem decide o valor “certo” se duas réplicas divergirem?

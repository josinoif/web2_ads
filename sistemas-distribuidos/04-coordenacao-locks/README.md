# 04 — Coordenação e locks

**Conceito:** exclusão mútua entre processos que compartilham um recurso.

**Stack:** Python 3 · lock via arquivo ou Redis `SET NX` (opcional)

**Status:** planejado

## Objetivo do mini-projeto

Vários clientes incrementam o mesmo contador **sem lock** (corrida) e **com lock** distribuído simples.

## Experimento sugerido

1. N clientes incrementando sem sincronização → valor final errado.
2. Mesmo experimento com lock → valor correto, mais lento.
3. Simular cliente que pega o lock e “morre” (lock órfão / TTL).

## O que observar

- Concorrência sem coordenação corrompe estado.
- Lock corrige, mas cria ponto de contenção e risco de deadlock/órfão.
- TTL e renew são temas reais em locks distribuídos.

## Perguntas-guia

- Lock global escala bem? Quando preferir particionar o estado?
- O que é pior: perder uma atualização ou ficar sem progresso?

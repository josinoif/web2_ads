# 05 — Escalabilidade

**Conceito:** aumentar capacidade tratando **carga** — em especial escala **horizontal** (mais nós) e o papel do **balanceamento** de requisições.

**Stack:** Python 3 (gateway + N workers em portas distintas)

**Status:** planejado

## Objetivo do mini-projeto

Um **gateway** recebe HTTP e espalha requests entre N **workers**. Medir throughput/latência com 1, 2 e 3 workers; introduzir um worker lento e ver o efeito na cauda.

## Experimento sugerido

1. Gerar carga com 1 worker — anotar RPS e latência.
2. Subir para 3 workers (mesmo código) — comparar ganho.
3. Deixar um worker artificialmente lento — observar p50 vs p99.
4. Derrubar um worker — com e sem health check no gateway.

## O que observar

- Escala horizontal ajuda quando o trabalho é paralelizable e os workers são (quase) stateless.
- Balancear sem health check ainda quebra quando um nó cai.
- Média pode melhorar enquanto a cauda (p99) continua ruim.
- Gargalos se movem: CPU → rede → banco compartilhado.

## Perguntas-guia

- Vertical vs horizontal: quando cada um?
- O que impede o ganho linear ao adicionar workers?
- Round-robin basta? Quando sticky session vira problema?

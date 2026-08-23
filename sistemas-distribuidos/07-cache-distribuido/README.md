# 07 — Cache distribuído

**Conceito:** acelerar leituras com cópia rápida; lidar com invalidação e dados velhos (stale).

**Stack:** Python 3 · Redis (Docker) ou cache em processo separado

**Status:** planejado

## Objetivo do mini-projeto

API lenta “fonte da verdade” + cache compartilhado. Medir latência com/sem cache; atualizar a fonte e ver leitura stale até invalidar.

## Experimento sugerido

1. Benchmark de leitura sem cache.
2. Mesma leitura com cache hit.
3. Update na fonte sem invalidar → valor antigo.
4. Invalidação explícita ou TTL.

## O que observar

- Cache troca consistência por desempenho.
- Invalidação é o problema difícil (não o get/set).
- Cache compartilhado entre processos ≠ dict local do processo.

## Perguntas-guia

- TTL vs invalidação sob escrita: quando cada um?
- O que acontece no “thundering herd” quando o cache expira?

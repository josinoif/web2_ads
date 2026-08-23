# 06 — Falhas, timeout e retries

**Conceito:** falha parcial é o modo normal; timeouts e retries precisam de limite.

**Stack:** Python 3

**Status:** planejado

## Objetivo do mini-projeto

Cliente chama um servidor que às vezes atrasa ou falha. Comparar: sem timeout, com timeout, com retry limitado, e (opcional) circuit breaker mínimo.

## Experimento sugerido

1. Servidor com 50% de erro / delay alto.
2. Cliente sem proteção → trava ou satura.
3. Timeout + retry com backoff → comportamento controlável.
4. Retry em operação não idempotente → efeito colateral (duplicar cobrança fictícia).

## O que observar

- Retry sem idempotência piora o problema.
- Timeout curto demais gera falsos negativos; longo demais segura recursos.
- Circuit breaker protege o sistema sob falha em cascata.

## Perguntas-guia

- Quais operações do seu domínio são idempotentes?
- Retry infinito é aceitável em algum caso?

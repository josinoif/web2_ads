# 09 — Observabilidade (logs, APM, tracing)

**Conceito:** em sistema com vários nós, “olhar o log de um processo” não basta — é preciso **agregar**, **correlacionar** e **medir** latência/erro entre serviços.

**Stack:** Python 3 instrumentado · stack mínima via Docker (a definir no tutorial: ex. logs estruturados + Jaeger, ou Grafana/Loki/Tempo)

**Status:** planejado

## Objetivo do mini-projeto

Uma app com 2–3 serviços (ex.: gateway → worker → “db” fake). Gerar tráfego, **quebrar** um hop e diagnosticar só com:

1. **Logs agregados** (mesmo `request_id` / `trace_id` em todos os serviços)
2. **Tracing** (spans mostrando onde o tempo foi gasto)
3. **APM / métricas** (latência, taxa de erro, RPS) — visão mínima

## Experimento sugerido

1. Subir a stack de apoio + a app.
2. Disparar requests normais — achar um request do início ao fim pelo ID.
3. Injetar delay/erro no serviço do meio — ver no trace qual span cresceu.
4. Comparar “SSH em cada máquina catando log” vs painel agregado.

## O que observar

- Sem ID de correlação, logs de N nós são ruído.
- Trace mostra o caminho; log mostra o detalhe; métrica mostra a tendência.
- Observabilidade é requisito de operação de sistema distribuído, não “extra de DevOps”.

## Ferramentas de apoio (mapa mental)

| Papel | Exemplos (para citar em aula) |
|-------|-------------------------------|
| Agregação de logs | Loki, Elasticsearch/OpenSearch, CloudWatch Logs |
| Tracing distribuído | Jaeger, Zipkin, OpenTelemetry |
| APM / métricas | Prometheus + Grafana, Datadog, New Relic, Elastic APM |
| Padrão de instrumentação | OpenTelemetry (vendor-neutral) |

O mini-projeto usa **uma** combinação leve o bastante para rodar no lab; a tabela serve para o aluno reconhecer o ecossistema.

## Ligação com o repositório

Há material mais amplo em [`devops/08-observabilidade/`](../../devops/08-observabilidade/). Aqui o foco é **por que** um sistema distribuído precisa disso e um experimento mínimo de correlação.

## Perguntas-guia

- Log, métrica e trace resolvem perguntas diferentes — dê um exemplo de cada.
- O que quebra na depuração se cada serviço usar formato de log diferente?
- Instrumentar tudo vs amostrar traces: quando cada abordagem?

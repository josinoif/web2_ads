# Glossário — Observabilidade

**Módulo:** [09](README.md) · **Consulta sob demanda** (abra quando travar num termo).

| Termo | Definição curta |
|-------|-----------------|
| **Observabilidade** | Capacidade de inferir o estado interno do sistema a partir dos sinais externos (investigar o não previsto). |
| **Monitoramento** | Acompanhar condições conhecidas com métricas/alarmes definidos de antemão. |
| **Métrica** | Série temporal agregada (contador, histograma) com labels de baixa cardinalidade. |
| **Log estruturado** | Evento em formato máquina (JSON) com campos estáveis (`trace_id`, `service`, …). |
| **Agregador de logs** | Sistema que centraliza logs de N serviços (ex.: Loki). |
| **Loki** | Agregador de logs do ecossistema Grafana (indexa labels; conteúdo consultável). |
| **Promtail** | Agente que envia logs de arquivos/containers para o Loki. |
| **Trace** | História ponta a ponta de um request através de vários serviços. |
| **Span** | Unidade de trabalho dentro de um trace (tem início, fim, pai, status). |
| **trace_id** | Identificador compartilhado por todos os spans/logs de um request. |
| **Propagação de contexto** | Encaminhar `trace_id` / `traceparent` nos hops (headers HTTP). |
| **W3C Trace Context** | Padrão do header `traceparent` para correlacionar traces. |
| **OpenTelemetry (OTel)** | Padrão/SDK vendor-neutral para emitir métricas, logs e traces. |
| **OTLP** | Protocolo de exportação do OpenTelemetry. |
| **Tempo** | Backend de traces do Grafana (recebe OTLP). |
| **Jaeger** | Backend/UI clássico de tracing (alternativa citada; lab usa Tempo). |
| **Prometheus** | Sistema de métricas (pull em `/metrics`). |
| **Grafana** | UI de dashboards/Explore — no lab, console **APM** didático. |
| **APM** | Application Performance Monitoring — latência, erros, throughput, traces da app. |
| **Cardinalidade** | Número de combinações de labels; alta demais derruba o Prometheus. |
| **Golden Signals** | Latência, tráfego, erros, saturação (SRE). |
| **RED** | Rate, Errors, Duration — métricas típicas de microserviço HTTP. |
| **USE** | Utilization, Saturation, Errors — foco em recursos. |
| **SLI** | Service Level Indicator — medida da experiência (ex.: % OK < 2s). |
| **SLO** | Service Level Objective — meta sobre o SLI. |
| **Error budget** | Folga de falha permitida antes de frear mudanças. |
| **Amostragem (sampling)** | Guardar só uma fração dos traces para reduzir custo. |
| **OTEL_SAMPLE_RATIO** | Fração amostrada no SDK (`ParentBasedTraceIdRatio`); lab padrão `1.0`. |
| **Auto-instrumentation** | Spans criados por bibliotecas OTel sem código manual por rota. |
| **Drill-down** | Descer de visão agregada (métrica) para exemplo (trace) e detalhe (log). |
| **Injeção de falha** | Flags didáticas (`INJECT_DELAY_MS`, `INJECT_ERROR_RATE`) para forçar sintomas. |
| **Health mentiroso** | `/health` 200 enquanto o negócio (ex.: `POST /provas`) falha — monitoramento ≠ observabilidade. |
| **UNSTRUCTURED_LOG** | Flag do lab A: log em texto livre (contraste com JSON). |
| **PII** | Dado pessoal identificável — evitar em logs de produção (LGPD). |

Ver também: [`devops/08` — referências](../../devops/08-observabilidade/referencias.md).

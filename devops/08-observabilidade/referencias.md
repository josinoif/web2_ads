# Referências — Módulo 8 (Observabilidade)

> Priorize os **livros centrais** e a **documentação oficial**. Artigos e palestras complementam e atualizam.

---

## Livros centrais

- **Beyer, B. et al.** *Site Reliability Engineering: How Google Runs Production Systems.* O'Reilly, 2016.
  - Leitura aberta e completa em [sre.google/sre-book](https://sre.google/sre-book/table-of-contents/).
  - Capítulos essenciais: 4 (SLOs), 5 (toil), 6 (monitoring), 10 (practical alerting), 16 (postmortem culture).
- **Beyer, B. et al.** *The Site Reliability Workbook: Practical Ways to Implement SRE.* O'Reilly, 2018. Leitura em [sre.google/workbook](https://sre.google/workbook/table-of-contents/). Destaques: capítulos 2 (SLOs), 4 (alerting on SLOs), 5 (reducing toil).
- **Majors, C.; Fong-Jones, L.; Miranda, G.** *Observability Engineering: Achieving Production Excellence.* O'Reilly, 2022. Referência moderna para observabilidade como disciplina, não apenas ferramentas.
- **Brazil, B.** *Prometheus: Up & Running.* O'Reilly, 2018 (2ª edição: 2024). Referência de PromQL, arquitetura e operação do Prometheus.
- **Ewaschuk, R. & SRE team.** "Applying the Three Whys". Capítulo 16 do *SRE Book*. Disponível online.

## Documentação oficial

- [Prometheus](https://prometheus.io/docs/introduction/overview/) — conceitos, PromQL, melhores práticas.
- [Grafana Labs Learning](https://grafana.com/docs/learning-journeys/) — trilhas para Grafana, Loki, Tempo, Mimir, Alerting.
- [Loki](https://grafana.com/docs/loki/latest/) — logs como time series, LogQL.
- [Tempo](https://grafana.com/docs/tempo/latest/) — backend de traces compatível com OpenTelemetry.
- [Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/) — agrupamento, inibição, silence, rotas.
- [OpenTelemetry](https://opentelemetry.io/docs/) — especificação, SDKs e instrumentação para métricas, logs e traces.
- [kube-prometheus-stack chart](https://github.com/prometheus-community/helm-charts/tree/main/charts/kube-prometheus-stack) — chart Helm consolidado usado em quase toda produção K8s.

## Métodos e frameworks

- **Brendan Gregg.** "The USE Method". [brendangregg.com/usemethod.html](https://www.brendangregg.com/usemethod.html). Usado para diagnóstico de recursos.
- **Tom Wilkie.** "The RED Method — key metrics for microservices architecture". [thenewstack.io/monitoring-microservices-red-method](https://thenewstack.io/monitoring-microservices-red-method/).
- **Rob Ewaschuk.** "My Philosophy on Alerting". [link](https://docs.google.com/document/d/199PqyG3UsyXlwieHaqbGiWVa8eMWi8zzAn0YfcApr8Q/preview). Base histórica do *alerting on SLOs*.
- **Nygard, M.** *Release It!* Pragmatic, 2018. Padrões de estabilidade (circuit breaker, bulkhead, timeouts) que observabilidade expõe.

## Artigos e palestras

- **Majors, C.** "Observability: a 3-Year Retrospective". [honeycomb.io/blog/observability-3-year-retrospective](https://www.honeycomb.io/blog/observability-3-year-retrospective).
- **Beyer, B. & Jones, C.** "Error Budgets" (capítulo 3 do SRE Book).
- **Wiggins, T.** "The Twelve-Factor App — XI. Logs". [12factor.net/logs](https://12factor.net/logs). Fundamento para logs como stream de eventos.
- **Google Cloud.** "Latency is the new outage". [post](https://cloud.google.com/blog/products/management-tools/sre-tips-latency-is-the-new-outage).
- **Fred Hebert.** "Complexity Has to Live Somewhere". [ferd.ca](https://ferd.ca/complexity-has-to-live-somewhere.html). Contexto filosófico do porquê observabilidade moderna é necessária.
- **Blameless postmortem guide** — [postmortem.ai](https://postmortem.ai/) e [blameless.com/blog](https://www.blameless.com/blog/postmortem-templates).

## Vídeos e palestras

- Liz Fong-Jones — "Observability Has Three Pillars? SRECon". [youtube.com](https://www.youtube.com/results?search_query=liz+fong-jones+observability+three+pillars).
- Charity Majors — "Observability: The Hard Parts" (múltiplas edições em QCon/KubeCon).
- Brian Brazil — "Prometheus: a case study in a zero-trust monitoring system" (PromCon).
- SREcon (USENIX) — [usenix.org/conferences](https://www.usenix.org/conferences) — palestras anuais com práticas de campo.

## Padrões e especificações

- **OpenMetrics** — [openmetrics.io](https://openmetrics.io/). Formato de exposição de métricas (evolução do formato Prometheus).
- **W3C Trace Context** — [w3.org/TR/trace-context/](https://www.w3.org/TR/trace-context/). Propagação de `traceparent` entre serviços.
- **OpenTelemetry Protocol (OTLP)** — [opentelemetry.io/docs/specs/otlp](https://opentelemetry.io/docs/specs/otlp/). Protocolo unificado métricas/logs/traces.
- **CNCF Observability TAG** — [github.com/cncf/tag-observability](https://github.com/cncf/tag-observability).

## Ferramentas open source citadas

- **Prometheus** — armazenamento de métricas time series.
- **Grafana** — visualização.
- **Loki** — logs indexados por labels (não por conteúdo).
- **Tempo / Jaeger** — backends de traces.
- **OpenTelemetry Collector** — roteador universal de sinais.
- **Alertmanager** — roteamento e silencing de alertas.
- **Pyroscope** — profiling contínuo (citado, não aprofundado).
- **k6 / Locust** — carga para exercitar SLOs.

## Para aprofundar (pós-módulo)

- **Kleppmann, M.** *Designing Data-Intensive Applications.* O'Reilly, 2017. Contexto para compreender por que sistemas distribuídos falham de formas não triviais.
- **Rosenthal, C. & Jones, N.** *Chaos Engineering.* O'Reilly, 2020. Evolução natural pós-observabilidade: testar o sistema sob estresse real.
- **Google.** "The Site Reliability Workbook" + "Building Secure and Reliable Systems" — trilogia completa SRE.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega avaliativa — Módulo 8 (Observabilidade)](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](README.md) | **Próximo →**<br>[Módulo 9 — DevSecOps](../09-devsecops/README.md) |

<!-- nav:end -->

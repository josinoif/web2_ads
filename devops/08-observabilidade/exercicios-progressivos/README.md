# Exercícios Progressivos — Módulo 8 (Observabilidade)

> Cinco partes encadeadas. Cada parte se apoia no artefato produzido na anterior. Ao final, você terá uma **plataforma observável** para a LogisGo (ou seu próprio projeto), pronta para alimentar a entrega avaliativa.

---

## Visão geral

| Parte | Tema | Entregável principal |
|-------|------|----------------------|
| [Parte 1](./parte-1-stack-e-metricas.md) | Stack `kube-prometheus-stack` + app instrumentada com métricas RED | Prometheus coletando `pedidos`; dashboard RED provisionado |
| [Parte 2](./parte-2-logs-estruturados.md) | Logs JSON via Loki + correlação trace_id | Consulta em Loki encontra eventos filtráveis por campo |
| [Parte 3](./parte-3-traces-otel.md) | Traces OpenTelemetry + Tempo + OTel Collector | Trace distribuído visível no Grafana, correlacionado com logs |
| [Parte 4](./parte-4-slos-e-alertas.md) | 2 SLOs formais + alertas burn-rate + Alertmanager + runbooks | `PrometheusRule`s versionadas, rotas no AM, 2 runbooks |
| [Parte 5](./parte-5-incidente-e-postmortem.md) | Incidente simulado + postmortem blameless + CI | Incidente reproduzível, postmortem escrito, pipeline valida tudo |

---

## Entregáveis consolidados

Ao terminar as cinco partes, seu repositório terá ao menos:

- `k8s/manifests/` — Service, Deployment, ServiceMonitor da app.
- `k8s/prometheusrules/` — recording rules + alertas burn-rate.
- `k8s/alertmanager/` — configuração com rotas e inibições.
- `grafana/dashboards/` — dashboards em JSON provisionados.
- `app/` — código Python instrumentado (métricas + logs + traces).
- `docs/runbooks/` — ao menos 2 runbooks.
- `docs/slos.md` — SLIs, SLOs, error budgets.
- `docs/postmortem-simulado.md`.
- `docs/adr/` — 3+ ADRs (cardinalidade, burn-rate, escolha de stack).
- `tests/` — `promtool test rules` com pelo menos 3 testes.
- `.github/workflows/observability.yml` — pipeline CI.
- `Makefile` — alvos `up`, `down`, `load`, `incident`, `test-rules`.

---

## Pré-requisitos

- Módulos 5 (containers) e 7 (Kubernetes) concluídos.
- `kubectl`, `helm`, `k3d` instalados.
- Python 3.12+ com `pip install -r requirements.txt` (do Módulo 8).
- Cluster local de pelo menos 4GB RAM disponíveis para a stack.

---

## Critérios globais de aceitação

- `make up` sobe cluster + stack + app a partir de máquina limpa.
- Grafana acessível em `http://localhost:3000` (user `admin`, senha `admin`).
- Prometheus coletando a app com **0 erros de scrape**.
- Dashboard RED mostra latência e taxa de erro em tempo real.
- Em Loki, busca por `trace_id` de um request retorna todos os logs daquele request.
- Em Tempo, o mesmo `trace_id` mostra a árvore de spans.
- `make incident` quebra algo; o alerta correto dispara em **até 5 min**.
- `promtool test rules` passa; `alerts_sanity.py` passa.

---

## Como conduzir

Cada parte tem **objetivos**, **tarefas**, **validação**, **entregáveis**. Avance apenas quando a validação da parte anterior está verde — o acoplamento é forte e o problema fica oculto caso ignore.

Aproximadamente **60–90 min por parte**, dependendo de familiaridade.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Exercícios resolvidos](../bloco-4/04-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Parte 1 — Stack observabilidade + métricas RED](parte-1-stack-e-metricas.md) |

<!-- nav:end -->

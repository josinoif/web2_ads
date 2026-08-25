# Tecnologias e escolhas — Observabilidade

**Módulo:** [09](README.md) · Use no workshop ou quando travar em “qual ferramenta?”.

---

## 1. Qual sinal para qual pergunta

| Precisa saber… | Comece com… |
|----------------|-------------|
| Tendência (piorou nas últimas 2h?) | **Métrica** (RED) |
| Caminho deste request (qual hop?) | **Trace** |
| Detalhe / mensagem / payload resumido | **Log** estruturado |
| Os três juntos na operação | **APM** (Grafana no lab) |

---

## 2. Agregador de logs

| Opção | Quando faz sentido | Quando dói |
|-------|-------------------|------------|
| Loki | Stack Grafana, labels simples, lab | Busca full-text massiva estilo ELK |
| ELK / OpenSearch | Busca rica, compliance, volume enorme | RAM/CPU; complexidade |
| Só `docker logs` | Debug de 1 container | N serviços / N réplicas |
| SaaS (Datadog Logs, …) | Time pequeno, quer menos ops | Custo e vendor lock |

Neste módulo: **Loki + Promtail** (app → arquivo → Promtail). Em produção, prefira **stdout → agente**.

---

## 3. APM / tracing / métricas

| Opção | Papel | Lab? |
|-------|-------|------|
| Grafana + Prometheus + Tempo + Loki | Console APM **didático** (fatia: RED + traces + logs) | **Sim** (lab B) |
| Jaeger UI | Traces focados | Não (Tempo cobre) |
| Datadog / New Relic / Dynatrace | APM comercial (service map, RUM, profiling, retenção…) | Não — citar |
| Elastic APM | APM “clássico” + Kibana | Não — pesado demais para o lab |
| OpenTelemetry | Instrumentação portável (traces aqui; métricas OTLP opcional em prod) | **Sim** traces (lab B) |

**Simplificação do lab B:** métricas via `prometheus_client` + pull; traces via OTel/OTLP. Em produção dá para unificar no OTel e usar *auto-instrumentation*.

Regra: instrumente com **OTel** (pelo menos traces); troque o backend sem reescrever a app.

---

## 4. Cardinalidade e amostragem

| Faça | Evite |
|------|-------|
| Labels: `service`, `route`, `status` | `user_id`, `trace_id`, `email` em métrica |
| Trace com sampling em produção | 100% traces em tráfego alto sem orçamento |
| Log com `trace_id` (alta cardinalidade no **log** ok) | Métrica por aluno |

---

## 5. O que alertar (conceito)

| Alerta frágil | Alarme mais maduro |
|---------------|-------------------|
| CPU > 70% | Taxa de erro do `POST /provas` sobe |
| “Pod reiniciou” isolado | SLI de latência estourou o SLO |

Detalhe de Alertmanager / burn rate: [`devops/08`](../../devops/08-observabilidade/).

---

## 6. Cola mental

| Se você precisa… | Escolha |
|------------------|---------|
| Achar um request nos 3 hops | `trace_id` + **Loki** |
| Ver se a API está degradando | **Prometheus** RED no Grafana |
| Ver *onde* os 800ms foram | **Tempo** / trace |
| Pacote “operação do serviço” | **APM** (Grafana unificado no lab) |
| Não prender a um vendor | **OpenTelemetry** |

Detalhes de cenários: [decisoes.md](decisoes.md).

# Entrega avaliativa — Módulo 8 (Observabilidade)

**Peso:** 20% da nota final da disciplina (ajuste conforme seu plano pedagógico).
**Formato:** repositório Git público (ou acessível à banca) com código, manifestos e documentação.
**Prazo sugerido:** ao final da semana do módulo.
**Base:** este entregável evolui o cluster do **Módulo 7** (StreamCast ou projeto próprio) ou recria uma aplicação nova no contexto da **LogisGo**.

---

## Objetivo

Projetar e operar uma plataforma de observabilidade para um sistema em Kubernetes, com sinais bem instrumentados, SLOs declarados, alertas acionáveis e documentação capaz de sustentar operação por um plantonista novo.

---

## Produto final

O repositório deve conter, ao menos:

1. **Cluster local reproduzível** (k3d ou kind) com a stack observabilidade pré-instalada via `make up`.
2. **Aplicação demo** (pode reusar `auth` do Módulo 7 ou um "mini-LogisGo" com 2 serviços FastAPI) **instrumentada** com:
   - Métricas Prometheus em `/metrics` seguindo padrão **RED**.
   - Logs estruturados (JSON) com campo `trace_id`.
   - Traces distribuídos via OpenTelemetry OTLP.
3. **Stack de observabilidade** no cluster, via Helm:
   - `kube-prometheus-stack` (Prometheus, Alertmanager, Grafana, node-exporter, kube-state-metrics).
   - `loki` (ou `loki-stack`).
   - `tempo`.
   - `opentelemetry-collector` (recebendo OTLP dos serviços e repassando a Tempo/Loki/Prometheus).
4. **3 SLOs formais**, um por jornada crítica, com:
   - SLI bem definido (numerador, denominador, janela).
   - Meta (SLO) e error budget.
   - Política de queima de error budget.
5. **5 dashboards** em `grafana/dashboards/` provisionados via ConfigMap:
   - Painel executivo (SLO atual, budget consumido, tráfego).
   - RED por serviço (pelo menos 2 serviços).
   - USE nodes (CPU, memória, disco, rede dos nodes).
   - Painel de jornada (trace + logs correlacionados por `trace_id`).
   - Budget burn (queima do error budget nas últimas 4 semanas).
6. **8 alertas** nos `PrometheusRule`s:
   - 3 alertas **SLO-based** (multi-window, multi-burn-rate).
   - 2 alertas de infraestrutura (saturação, restart loop).
   - 2 alertas de negócio (ex.: "nenhum pedido criado há 10 min" na LogisGo).
   - 1 alerta `Watchdog` (para detectar falha de coleta).
7. **Alertmanager config** com:
   - Agrupamento por rota e severidade.
   - Silence policy documentada.
   - Ao menos 1 inibição (ex.: silenciar "pod-level" quando "node-level" já disparou).
   - Receiver: webhook local OU Slack/Discord webhook OU arquivo (para teste sem conta externa).
8. **Runbooks** (`docs/runbooks/`) para os alertas de severidade crítica, com o template do Bloco 4.
9. **Pipeline CI** (reuse do Módulo 4):
   - Valida sintaxe de `PrometheusRule`s com `promtool check rules`.
   - Valida dashboards (JSON válido).
   - Lança testes unitários de alertas (`promtool test rules`).
10. **Documentação completa** (`docs/`):
    - `arquitetura.md` — diagrama da stack e fluxo dos três sinais.
    - `slos.md` — SLIs, SLOs, SLAs e budgets.
    - `runbooks/` — um arquivo por alerta.
    - `postmortem-simulado.md` — postmortem sem culpa de um incidente provocado (você rompe algo de propósito e documenta).
    - `limites-e-custos.md` — discussão consciente de cardinalidade e retenção.
11. **3+ ADRs** em `docs/adr/`:
    - `001-promql-vs-logql-vs-traceql.md` — quando usar cada linguagem.
    - `002-cardinalidade.md` — regras adotadas para labels e justificativa.
    - `003-alerta-slo-based-vs-threshold.md` — por que abandonar (ou manter) thresholds.
12. **`Makefile`** com alvos: `up`, `down`, `apply`, `test-rules`, `load` (gerar tráfego), `incident` (rompe algo), `clean`.

---

## Entregáveis técnicos obrigatórios

### 1. Instrumentação da aplicação

- [ ] Métricas Prometheus expostas em `/metrics` com histograma de latência por rota/status/método.
- [ ] Contador de requests com label de rota e status.
- [ ] Logs JSON com campos: `timestamp`, `level`, `service`, `message`, `trace_id`, `span_id`, `user_id` (quando aplicável).
- [ ] Spans exportados via OTLP para o Collector. Spans devem incluir atributos mínimos (`http.method`, `http.status_code`, `http.route`).
- [ ] Serviço propaga `traceparent` em chamadas HTTP internas (exemplo: `serviçoA → serviçoB` aparece como um único trace).
- [ ] Cardinalidade controlada: **nunca** labels com IDs livres (userId, orderId) em **métricas** — esses vão apenas em **logs/traces**.

### 2. Stack observabilidade

- [ ] kube-prometheus-stack com Prometheus configurado para `ServiceMonitor`s da sua app.
- [ ] Grafana com 3 datasources: Prometheus, Loki, Tempo.
- [ ] Logs fluem de pods → Promtail/Alloy → Loki.
- [ ] Traces fluem de app → Collector OTLP → Tempo.
- [ ] Correlação funciona: no Grafana, a partir de um trace você consegue saltar para logs e métricas correspondentes.

### 3. SLO e burn rate

Para cada uma das 3 jornadas:

- [ ] Documento em `docs/slos.md` com: jornada, SLI, SLO, janela, error budget, responsável.
- [ ] `PrometheusRule` calculando `sli:good` e `sli:valid` como *recording rules*.
- [ ] Dashboard Grafana com budget consumido e tempo até exaustão.
- [ ] 2 alertas por SLO: **page (rápido, alta taxa)** e **ticket (lento, acumulado)** conforme *multi-window burn rate* (SRE Workbook cap. 5).

### 4. Alertas saudáveis

- [ ] Zero alertas em thresholds estáticos de CPU/memória sem justificativa documentada.
- [ ] Cada alerta tem `summary`, `description`, link para o runbook, e severidade (`critical`, `warning`, `info`).
- [ ] Ao menos 1 alerta **não** aciona pager fora de horário comercial (via rota Alertmanager).
- [ ] Watchdog configurado e aciona um receiver de teste.

### 5. Exercício de incidente

- [ ] Script `make incident` que **quebra** algo (ex.: aplica NetworkPolicy deny-all no namespace, corrompe uma variável, scale deployment para 0).
- [ ] Registro em `docs/postmortem-simulado.md`:
  - Timeline detalhada (ações e sinais).
  - MTTD (tempo até alerta disparar) e MTTR (tempo até ficar verde).
  - Causa-raiz técnica e sistêmica (sem culpar pessoa).
  - 3 itens de ação concretos, um já implementado neste entregável.

---

## Rubrica de avaliação (100 pts)

| Eixo | Peso | Critérios principais |
|------|------|----------------------|
| **Reprodutibilidade** | 10 | `make up` funciona do zero em máquina de terceiro. README completo. |
| **Instrumentação** | 20 | Métricas RED ricas e de baixa cardinalidade. Logs estruturados com `trace_id`. Traces propagados. |
| **Stack operacional** | 15 | Correlação métricas↔logs↔traces funciona no Grafana. Datasources OK. |
| **SLOs e burn rate** | 15 | 3 SLOs bem justificados, *recording rules* corretas, multi-window alerting. |
| **Alertas e Alertmanager** | 10 | Roteamento, inibição, silence, severidades, sem alertas de ruído óbvio. |
| **Dashboards** | 10 | 5 dashboards úteis (não decorativos) provisionados como código. |
| **Runbooks e postmortem** | 10 | Runbooks executáveis; postmortem sem culpa com itens de ação rastreáveis. |
| **ADRs e justificativas** | 5 | 3+ ADRs escritos no formato Michael Nygard. |
| **CI** | 5 | Pipeline valida regras e lança `promtool test rules` com ao menos 3 testes. |

### Bônus (até +10 pts, não compensam faltas)

- Trace exemplar com ≥ 3 spans pulando entre 2 serviços, visível no Tempo.
- Dashboard mobile-friendly.
- Profiling contínuo via Pyroscope.
- Teste de carga (k6/Locust) que deliberadamente queima error budget e demonstra o alerta.
- Receiver Alertmanager integrado a um chat real (Discord ou Slack, mesmo que pessoal).

---

## Formato de entrega

1. Link do repositório.
2. README na raiz com:
   - `make up` → quando tudo está saudável, que URLs visitar (Grafana, Prometheus, Alertmanager).
   - Credenciais (não sensíveis) para login local.
   - Tour guiado: "para ver o SLO de criação de pedido, vá em dashboards > SLO > Pedidos".
   - Como rodar `make incident` e o que esperar.
3. Gravação de ≤ 10 minutos (opcional) demonstrando um incidente e sua resolução **navegando apenas no Grafana**, sem `kubectl logs`.

---

## Checklist rápido antes de entregar

- [ ] `make up` e `make test-rules` funcionam em máquina limpa.
- [ ] Nenhum segredo real commitado (`.env`, tokens de Slack, etc.).
- [ ] Todos os alertas linkam para um runbook **que existe**.
- [ ] Cardinalidade foi checada: nenhuma métrica explode com `user_id` ou `request_id`.
- [ ] Dashboards abrem sem erros; correlação trace→logs funciona.
- [ ] Postmortem está em tom sem culpa, usa dados e aponta mudanças sistêmicas.
- [ ] README tem uma seção "limitações conhecidas" honesta.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Incidente simulado, postmortem e CI](exercicios-progressivos/parte-5-incidente-e-postmortem.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](README.md) | **Próximo →**<br>[Referências — Módulo 8 (Observabilidade)](referencias.md) |

<!-- nav:end -->

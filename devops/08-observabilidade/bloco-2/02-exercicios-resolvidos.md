# Bloco 2 — Exercícios resolvidos

Fundamentos: [02-metricas-prometheus.md](./02-metricas-prometheus.md).

---

## Exercício 1 — Identificar tipo de métrica

**Enunciado.** Para cada situação, indique o tipo (`counter`, `gauge`, `histogram`) mais adequado.

1. Total de pedidos criados desde o último restart.
2. Número de mensagens pendentes na fila RabbitMQ agora.
3. Tamanho em bytes de payloads recebidos (para detectar payloads grandes).
4. Temperatura reportada por um sensor IoT.
5. Memória do processo Python.
6. Duração em segundos de requisições HTTP.

**Resposta.**

| # | Tipo | Motivo |
|---|------|--------|
| 1 | counter | Só cresce; só é útil via `rate()`/`increase()`. Nome: `orders_created_total`. |
| 2 | gauge | Sobe e desce. `rabbitmq_queue_messages_ready`. |
| 3 | histogram | Distribuição; interessa p50/p95/p99 e média. `http_request_bytes`. |
| 4 | gauge | Valor instantâneo arbitrário. `sensor_temperature_celsius`. |
| 5 | gauge | Uso atual. `process_resident_memory_bytes`. |
| 6 | histogram | p95/p99 são a razão de ser. `http_request_duration_seconds`. |

---

## Exercício 2 — Descartar PromQL ruim

**Enunciado.** O dev júnior propôs três consultas para o dashboard. Identifique o problema e proponha a correção.

1. `http_requests_total{service="pedidos"}`
2. `avg(http_request_duration_seconds_sum{service="pedidos"})`
3. `rate(http_requests_total{service="pedidos"}[1s])`

**Resposta.**

1. **Counter crua no gráfico.** Linha reta ascendente sem significado; restart zera. **Correção:** `sum(rate(http_requests_total{service="pedidos"}[5m]))`.
2. **`_sum` sozinho é incorreto.** É soma cumulativa; dá apenas um tempo total acumulado (sem ordem de grandeza acionável). Também média de histogram cuida de quantis mal. **Correção:** usar `histogram_quantile(0.95, sum by (le)(rate(http_request_duration_seconds_bucket{service="pedidos"}[5m])))` para p95.
3. **Janela muito curta.** `[1s]` é instável — se scrape_interval é 15s, não tem amostras suficientes. Regra: `range >= 4 × scrape_interval`. **Correção:** `rate(...[1m])` no mínimo, `[5m]` no padrão.

---

## Exercício 3 — Cálculo de p95

**Enunciado.** Dado o snippet de um `/metrics`:

```
http_request_duration_seconds_bucket{service="pedidos",le="0.1"} 800
http_request_duration_seconds_bucket{service="pedidos",le="0.25"} 920
http_request_duration_seconds_bucket{service="pedidos",le="0.5"} 980
http_request_duration_seconds_bucket{service="pedidos",le="1"} 995
http_request_duration_seconds_bucket{service="pedidos",le="2.5"} 1000
http_request_duration_seconds_bucket{service="pedidos",le="+Inf"} 1000
http_request_duration_seconds_count{service="pedidos"} 1000
http_request_duration_seconds_sum{service="pedidos"} 180
```

1. Qual o p95 aproximado?
2. Como escreveria isso em PromQL?
3. O que o valor `_sum=180` significa?

**Resposta.**

1. **p95 = 0,95 × 1000 = request número 950.** O bucket `le=0.25` tem 920 (abaixo). O bucket `le=0.5` tem 980 (acima). Interpolando linearmente entre `(0.25, 920)` e `(0.5, 980)`:
   $$
   p95 \approx 0{,}25 + \frac{950 - 920}{980 - 920} \times (0{,}5 - 0{,}25) = 0{,}25 + \frac{30}{60} \times 0{,}25 = 0{,}375\text{ s}
   $$
2. ```promql
   histogram_quantile(0.95, sum by (le)(rate(http_request_duration_seconds_bucket{service="pedidos"}[5m])))
   ```
3. **Soma acumulada das latências observadas** (em segundos). Junto com `_count=1000`, permite calcular a **média**: `_sum / _count = 0,180s = 180ms`. **Média e quantile não substituem um ao outro** — média esconde caudas; p95 revela.

---

## Exercício 4 — Desenhar um alerta de taxa de erro (conceitual)

**Enunciado.** Escreva um `PrometheusRule` (apenas a regra, não todo o YAML do CR) para alertar quando o serviço `pedidos` tem > 2% de 5xx por 10 minutos. Indique a severidade adequada e justifique.

**Resposta.**

```yaml
- alert: PedidosHighErrorRate
  expr: |
    sum(rate(http_requests_total{service="pedidos", status=~"5.."}[5m]))
    /
    sum(rate(http_requests_total{service="pedidos"}[5m]))
    > 0.02
  for: 10m
  labels:
    severity: warning
    service: pedidos
  annotations:
    summary: "Pedidos: taxa de 5xx > 2% há mais de 10 min"
    description: "Taxa atual {{ $value | humanizePercentage }}. Ver runbook."
    runbook_url: "https://runbooks.logisgo/pedidos-high-error-rate"
```

**Justificativa da severidade:** `warning` (não `critical`). O alerta mede degradação; usuários provavelmente já sentem, mas ainda há budget. `critical` fica reservado para violação aguda de SLO ou indisponibilidade total (veremos isso no Bloco 4 com *burn rate*). O `for: 10m` evita ruído de picos pontuais (uma rajada de 5xx em 30s não dispara).

---

## Exercício 5 — Auditar cardinalidade com o script

**Enunciado.** Após rodar `python metrics_audit.py --url http://localhost:8000/metrics`, você vê:

```
Metrica                                         Series   Status
-------------------------------------------------------------
http_requests_total                              12480    alerta
http_request_duration_seconds_bucket             62400    alerta
orders_created_total                                 6    ok
process_cpu_seconds_total                            1    ok
```

Investigue: quais labels provavelmente causam a explosão em `http_requests_total` (12.480 séries)? Como confirmar?

**Resposta.**

Cardinalidade 12.480 é **muito alta** para um serviço HTTP razoável (espera-se algo como 5 serviços × 30 rotas × 4 métodos × 10 status ≈ 6 000 — e você tem 1 serviço). O culpado mais comum: **rotas expandidas** em vez do padrão, ou um label como `user_id`/`request_id`.

**Como confirmar.** No Prometheus UI:

```promql
count(count by (route)(http_requests_total))
```

Se retornar > 100, é rota expandida. Ou:

```promql
topk(10, count by (route)(http_requests_total))
```

mostra as rotas com mais variações — se vê `/orders/84271`, `/orders/84272`, etc., confirmou.

**Correção.** No middleware, trocar `request.url.path` por `request.scope["route"].path` (template da rota). Também checar se alguém adicionou `user_id` como label.

Depois de corrigido, reexecutar o auditor. Cardinalidade deve cair para < 200.

---

## Exercício 6 — Dashboard RED em JSON (análise)

**Enunciado.** Você herda um dashboard cujo painel "p95 de latência" tem a query:

```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

Um colega afirma que "parece certo mas dá valores estranhos". Diga por quê e corrija.

**Resposta.**

**Erro:** falta `sum by (le)`. A expressão agrega sem somar os buckets entre séries — o quantile é calculado em cada série isoladamente, resultando em mistura sem sentido (literalmente um p95 por combinação de labels).

**Versão correta:**

```promql
histogram_quantile(
  0.95,
  sum by (le) (rate(http_request_duration_seconds_bucket{service="pedidos"}[5m]))
)
```

**Por quê.** `histogram_quantile` opera sobre *buckets agregados*. Sem `sum by (le)`, cada série vira um "mini-histograma" próprio — o que não corresponde ao que o quantile modela. Com `sum by (le)`, somamos os counts de cada bucket `le=N` entre todas as séries relevantes, formando **um** histograma agregado ao qual o quantile faz sentido.

Se quiser quebrar por dimensão (p.ex., por rota), inclua a dimensão na agregação:

```promql
histogram_quantile(
  0.95,
  sum by (le, route) (rate(http_request_duration_seconds_bucket{service="pedidos"}[5m]))
)
```

---

## Autoavaliação

- [ ] Identifico o tipo certo para cada métrica nova.
- [ ] Escrevo PromQL usando `rate()`, `sum by`, razões, `histogram_quantile` corretamente.
- [ ] Monto um `PrometheusRule` com alerta que inclui runbook e severidade.
- [ ] Uso `metrics_audit.py` para detectar explosões de cardinalidade.
- [ ] Sei diagnosticar um dashboard que dá valores estranhos.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Métricas com Prometheus e Grafana](02-metricas-prometheus.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Bloco 3 — Logs (Loki) e Traces (Tempo) com OpenTelemetry](../bloco-3/03-logs-traces-otel.md) |

<!-- nav:end -->

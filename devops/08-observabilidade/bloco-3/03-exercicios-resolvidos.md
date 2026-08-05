# Bloco 3 — Exercícios resolvidos

Fundamentos: [03-logs-traces-otel.md](./03-logs-traces-otel.md).

---

## Exercício 1 — Refatorar log desestruturado

**Enunciado.** A LogisGo tem o seguinte log no serviço `pedidos`:

```
2026-04-21 14:32:11 INFO criando pedido 84271 para cliente zaffran via api enviando para postgres db1
```

Reescreva como JSON estruturado, respeitando os campos mínimos do Bloco 3. Explique em uma frase o ganho para quem investiga incidentes.

**Resposta.**

```json
{"ts":"2026-04-21T14:32:11Z","level":"INFO","service":"pedidos","env":"prod","version":"v2.14.0","msg":"criando pedido","order_id":"84271","customer":"zaffran","channel":"api","db":"db1","trace_id":"0af7651916cd43dd8448eb211c80319c","span_id":"b7ad6b7169203331"}
```

**Ganho:** buscas em Loki ficam filtráveis por campo (`| json | order_id="84271"`) em vez de regex frágil; a linha permite correlação imediata com traces via `trace_id`.

---

## Exercício 2 — Escolher label Loki certo

**Enunciado.** Para os candidatos abaixo, marque se é seguro como **label Loki** ou se deve ficar apenas **dentro do log**.

| Campo | Label seguro? | Justificativa |
|-------|---------------|---------------|
| `namespace` | sim | enum curto (ambiente + tenant). |
| `app` | sim | catálogo fechado. |
| `level` | sim | `DEBUG/INFO/WARN/ERROR/CRITICAL`. |
| `pod` | sim | limitado pelo replica count. |
| `trace_id` | não | 1 valor único por request; cardinalidade infinita. |
| `order_id` | não | IDs livres. Dentro do log. |
| `customer_tier` | sim | enum curto. |
| `user_id` | não | infinito. |
| `http_status` | sim | ~10 valores. |

**Regra geral confirmada:** seguros para label Loki = **conjuntos fechados e pequenos**. Restante vira campo no JSON.

---

## Exercício 3 — LogQL na prática

**Enunciado.** Escreva LogQL para:

1. Todos os logs de ERROR no namespace `logisgo` nas últimas 15 min.
2. Contagem de erros por minuto, quebrado por serviço.
3. Todos os logs de um `trace_id="0af7651916cd43dd8448eb211c80319c"`.
4. Logs que contêm "timeout" mas **não** em pods do serviço `tracking`.

**Resposta.**

```logql
# 1
{namespace="logisgo"} | json | level="ERROR"

# 2
sum by (app) (rate({namespace="logisgo"} | json | level="ERROR" [1m]))

# 3
{namespace="logisgo"} |= "0af7651916cd43dd8448eb211c80319c"
# (uso de |= direto pega em qualquer parte da linha; rapido e barato)

# 4
{namespace="logisgo", app!="tracking"} |= "timeout"
```

---

## Exercício 4 — Desenhar um trace da LogisGo

**Enunciado.** Descreva em spans uma chamada `POST /orders` que passa por `api-gateway → pedidos → validar_estoque (http em estoque) → persistir_pedido (db) → publicar_evento (rabbitmq)`. Indique nome do span, serviço responsável e 1 atributo relevante.

**Resposta.**

| Ordem | Nome span | Serviço | Atributos |
|-------|-----------|---------|-----------|
| 1 | `POST /orders` | api-gateway | `http.route=/orders`, `http.method=POST` |
| 2 | `POST /orders` | pedidos | `http.status=200`, `customer.id="zaffran"` |
| 3 | `validar_estoque` | pedidos (HTTP out) | `peer.service="estoque"`, `items.count=3` |
| 4 | `consultar_sku` | estoque | `sku="xyz"` |
| 5 | `persistir_pedido` | pedidos (db) | `db.system="postgresql"`, `db.statement_type="INSERT"` |
| 6 | `publicar_evento` | pedidos (queue) | `messaging.system="rabbitmq"`, `messaging.destination="orders"` |

Todos compartilham `trace_id`. `parent_span_id` encadeia (1 é raiz; 2 é filho de 1; 3 é filho de 2; 4 é filho de 3, e assim por diante).

---

## Exercício 5 — Analisar saída do script `log_trace_demo.py`

**Enunciado.** Execute:

```bash
python log_trace_demo.py --requests 2
```

Pegue uma requisição completa (logs + spans do mesmo `trace_id`) e responda:

1. Quantos spans fazem parte de uma request `POST /orders`?
2. Qual é o span de maior duração nos testes que você rodou?
3. Como você usaria `jq` para filtrar apenas o trace de maior duração?

**Resposta esperada (depende da aleatoriedade).**

1. Cada request gera 3 spans: `POST /orders` (raiz), `validar_estoque`, `persistir_pedido`. Exceto quando ocorre a falha rara de `publicar_evento`, nenhum span extra é criado (aquele caminho é apenas um log; para ilustrar como "log sem span" acontece).
2. Em geral, `persistir_pedido` — o random range é 0,02–0,30s vs. 0,01–0,05s de validar_estoque.
3. Filtro por `trace_id` específico:
   ```bash
   python log_trace_demo.py --requests 10 | jq -c 'select(.trace_id=="<id>")'
   ```
   Para descobrir o `trace_id` com maior duração raiz:
   ```bash
   python log_trace_demo.py --requests 10 | \
     jq -c 'select(.kind=="span" and .name=="POST /orders")' | \
     jq -s 'max_by(.duration_ms) | .trace_id'
   ```

---

## Exercício 6 — Redesenhar correlação trace↔log

**Enunciado.** Um colega fez o seguinte setup:
- Traces indo direto da app para Tempo.
- Logs indo direto da app para Loki.
- Configurou `FastAPIInstrumentor`, mas **esqueceu** `LoggingInstrumentor`.

O `trace_id` aparece no Tempo, mas **não** nos logs. O que fazer? Explique a correção e o mínimo que precisa mudar no código.

**Resposta.**

Sem `LoggingInstrumentor`, o handler do `logging` padrão não recebe injeção do contexto OpenTelemetry. Consequência: os logs saem sem `trace_id`/`span_id`, quebrando a correlação.

Correção mínima:

```python
from opentelemetry.instrumentation.logging import LoggingInstrumentor

LoggingInstrumentor().instrument(set_logging_format=False)
```

Isso adiciona atributos `otelTraceID`, `otelSpanID`, `otelServiceName` aos `LogRecord`s do stdlib. Com `structlog` configurado como na seção 3.1.3 do bloco, basta mapear/propagar esses campos no processor final.

Alternativa explícita (sem instrumentor):

```python
from opentelemetry import trace

def injetar_trace(logger, method, event_dict):
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if ctx.trace_id and ctx.is_valid:
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict

# Adicionar esse processor ao shared_processors do structlog.configure()
```

Depois da correção: cada log dentro de um span carrega o `trace_id`, e a correlação no Grafana (`"trace_id":"(...)"` → Tempo) volta a funcionar.

---

## Autoavaliação

- [ ] Emito logs estruturados em JSON com campos obrigatórios e sem PII.
- [ ] Escolho labels Loki de baixa cardinalidade e coloco IDs livres no conteúdo.
- [ ] Escrevo LogQL para filtrar, contar e parsear JSON.
- [ ] Entendo a anatomia de um trace (`trace_id`, spans, parent_span_id, atributos).
- [ ] Propago contexto W3C Trace Context entre serviços via `traceparent`.
- [ ] Uso OpenTelemetry SDK + Collector + Tempo sem abrir mão da configuração mínima.
- [ ] Configuro correlação logs↔traces no Grafana via `trace_id`.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Logs (Loki) e Traces (Tempo) com OpenTelemetry](03-logs-traces-otel.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Bloco 4 — Alertas, SLO-based alerting, runbooks e cultura on-call](../bloco-4/04-alertas-slo-cultura.md) |

<!-- nav:end -->

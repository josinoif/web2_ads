# Bloco 1 — Exercícios resolvidos

> Leia primeiro o conteúdo teórico em [01-fundamentos-observabilidade.md](./01-fundamentos-observabilidade.md). Estes exercícios consolidam decisões reais, não apenas memorização.

---

## Exercício 1 — Monitoramento vs. observabilidade (conceitual)

**Enunciado.** A LogisGo tem hoje 280 alertas/semana e um dashboard Grafana que fica verde, mas não resolveu o incidente Zaffrán (115 pedidos sumidos). A CTO declara: *"vamos comprar mais monitoramento"*. Explique, em no máximo 5 linhas, por que comprar **mais monitoramento** provavelmente não resolve e o que falta.

**Resposta esperada.**

Monitoramento responde a **perguntas pré-definidas** com thresholds fixos. O incidente Zaffrán era um **unknown-unknown**: pedidos *eram* criados (todas as checks de saúde passariam), mas não *persistiam no fluxo completo*. Aumentar monitoramento adiciona mais dashboards verdes sem a capacidade de **investigar uma pergunta nova em dados já coletados**. Falta observabilidade: logs estruturados correlacionados com `trace_id`, traces mostrando onde a jornada quebrou, métricas de negócio (pedidos persistidos / pedidos criados). O gap não é de ferramenta, é de **instrumentação e modelo mental**.

---

## Exercício 2 — Mapear perguntas aos pilares

**Enunciado.** Para cada pergunta abaixo, identifique o(s) pilar(es) mais adequado(s) e justifique em uma linha.

1. "A latência p99 do serviço `pedidos` hoje está pior que ontem?"
2. "O pedido 84271 do cliente Zaffrán falhou — por quê?"
3. "Quantos pedidos/s nosso sistema está processando agora?"
4. "Onde exatamente a requisição demorou 3s — em Postgres, RabbitMQ ou validação?"
5. "O deploy v2.14.0, feito ontem 14h, aumentou a taxa de erro?"
6. "Quem, entre nossos 200 clientes B2B, tem mais erros 500 no último dia?"

**Resposta esperada.**

| # | Pilar principal | Justificativa |
|---|-----------------|---------------|
| 1 | **Métricas** | Comparação temporal de histograma já agregado — PromQL resolve. |
| 2 | **Logs + trace** | Pergunta sobre *uma instância específica*; métrica não guarda o request individual. |
| 3 | **Métricas** | `rate(http_requests_total[1m])` — clássico. |
| 4 | **Traces** | Traces mostram o tempo por span na jornada; métricas não particionam por etapa interna. |
| 5 | **Métricas** | Série temporal com anotação de deploy; não precisa log. |
| 6 | **Logs agregados** (ou métricas **se** o número de clientes cabe em labels). Cliente é tipicamente dezenas a centenas — pode ir para métrica com cuidado; se milhares, fica em logs. |

---

## Exercício 3 — Aplicar RED e USE

**Enunciado.** O serviço `pedidos` da LogisGo tem 2 rotas HTTP (`POST /orders`, `GET /orders/{id}`) e usa um pool de conexões Postgres. Liste:

- 3 métricas **RED** (com nome, tipo e labels sugeridos).
- 2 métricas **USE** (para o recurso "pool de conexões Postgres").

**Resposta esperada.**

```
# RED
http_requests_total{service="pedidos", route="/orders", method="POST", status="200"}        counter
http_requests_total{service="pedidos", route="/orders", method="POST", status="500"}        counter
http_request_duration_seconds_bucket{service="pedidos", route="/orders", method="POST", le="0.5"} counter (histogram)

# USE — pool de conexões Postgres
db_pool_connections_active{service="pedidos", pool="primary"}    gauge    # Utilization
db_pool_connections_waiting{service="pedidos", pool="primary"}   gauge    # Saturation (fila)
db_pool_errors_total{service="pedidos", pool="primary"}          counter  # Errors
```

**Regras aplicadas:**
- Labels fechados (rota, método, status HTTP, nome do pool).
- Histograma para latência (permite p95/p99 via `histogram_quantile`).
- Separar 2xx de 5xx via `status` — respeita "não misturar sucesso com erro".
- Zero IDs livres em labels.

---

## Exercício 4 — Projetar um SLO

**Enunciado.** O CEO da LogisGo quer um SLO para "criar pedido". Usuário considera aceitável até **500 ms**. Tráfego: **50 req/s** em média, com picos de 200 req/s. Histórico sugere erro intrínseco ~0,2%. Proponha:

1. SLI (fórmula exata).
2. SLO (valor, janela).
3. Error budget (em minutos e em número de erros).
4. Política de queima (o que fazer se 50% do budget queimou em 3 dias?).

**Resposta esperada.**

1. **SLI.**
   $$
   SLI = \frac{\text{count de requests } / \text{orders POST com status 2xx E duration < 500ms}}{\text{count de todos os requests } /\text{orders POST}}
   $$
   No Prometheus (Bloco 2): a razão de `sum(rate(http_requests_total{service="pedidos", route="/orders", method="POST", status=~"2..", le="0.5"}[5m]))` pelo total — usando *histogram buckets* adequadamente (ver Bloco 2).

2. **SLO:** `99% em 28 dias`. Patamar conservador diante do erro intrínseco observado (~0,2% = muito abaixo da meta, deixando folga).

3. **Error budget.**
   - Total de requests em 28 dias a 50 req/s: `50 × 60 × 60 × 24 × 28 ≈ 120.960.000`.
   - Budget: `1% × 120.960.000 ≈ 1.209.600 requests ruins`.
   - Em minutos (se tráfego fosse constante, considerando indisponibilidade total): `1% × 28 × 24 × 60 ≈ 403 minutos ≈ 6 h 43 min`.

4. **Política de queima.**
   - 50% queimado em 3 dias (≈ 10% do tempo) = **5× mais rápido que o esperado**.
   - Ação: bloquear features não-críticas, rodar retrospectiva de mudanças da semana, priorizar estabilização. Alerta `warning` deve já ter disparado (veja Bloco 4 — burn rate alerting).
   - Se 90% queimado antes de metade da janela: **freeze total** de novas features.

---

## Exercício 5 — Auditar labels de métricas

**Enunciado.** Um PR adiciona a métrica:

```
http_request_duration_seconds{service, route, method, status, user_id, order_id, correlation_id, user_agent}
```

Você é revisor. Aponte os problemas e proponha versão corrigida. Estime a cardinalidade original.

**Resposta esperada.**

**Problemas:**
- `user_id`, `order_id`, `correlation_id`: cardinalidade teoricamente infinita. **Reprovado**.
- `user_agent`: string livre com centenas/milhares de valores. **Reprovado**.
- `service`, `route`, `method`, `status`: aceitáveis.

**Cardinalidade original estimada (catastrófica):**
- `service`: 5
- `route`: 30
- `method`: 4
- `status`: 10
- `user_id`: 1.000.000
- `order_id`: 10.000.000 (acumulativo)
- `correlation_id`: infinito (um por request)
- `user_agent`: ~5.000

Produto: **explosão** — matematicamente infinita por causa do `correlation_id`. Na prática, Prometheus OOM em horas.

**Versão corrigida:**

```
http_request_duration_seconds{service, route, method, status}
```

O que foi removido vai para **logs estruturados e traces**, onde cardinalidade alta é adequada:

```json
{"ts":"...","trace_id":"0af...","user_id":"u123","order_id":"o84271","correlation_id":"c..."}
```

Regra mnemônica: *"Se o valor é livre ou por-usuário, vai pra log/trace. Se é enum fechado, pode ser label de métrica."*

---

## Exercício 6 — Simulação de error budget

**Enunciado.** Execute o script `slo_simulator.py` com os seguintes parâmetros e interprete cada resultado.

```bash
# cenário A - saudável
python slo_simulator.py --slo 0.995 --janela-dias 28 --rps 50 --prob-erro 0.002

# cenário B - queima acelerada
python slo_simulator.py --slo 0.995 --janela-dias 28 --rps 50 --prob-erro 0.008

# cenário C - incidente
python slo_simulator.py --slo 0.995 --janela-dias 28 --rps 50 --prob-erro 0.02
```

**Resultados esperados (aproximados, semente fixa):**

| Cenário | SLI dia | Budget queimado dia | Classificação |
|---------|---------|---------------------|---------------|
| A (prob_erro = 0.2%) | ~99,80 % | ~40 % do budget dia / ~1,4% do budget da janela | **Saudável** — taxa de erro bem abaixo do SLO (0,2% < 0,5%). |
| B (prob_erro = 0.8%) | ~99,20 % | **acima** de 100 % do budget-dia esperado | **Atenção/Alerta** — SLI está abaixo do SLO. Se persistir 28 dias, violação certa. |
| C (prob_erro = 2 %) | ~98,00 % | ~380 % do budget-dia | **Crítico** — queima ~4× mais rápido; budget estoura em dias. |

**Interpretação pedagógica.**

- No cenário A, o sistema pode se dar ao luxo de experimentar (deploys agressivos, canários longos): o budget sobra.
- No cenário B, o SLO já está sendo violado em taxa. Ação: investigar o que degradou (deploy recente? dependência externa?) e reduzir risco até normalizar.
- No cenário C, a taxa é incompatível com o SLO pactuado. Duas saídas honestas: **(1)** consertar o sistema em regime de emergência, **(2)** renegociar o SLO com produto (menos comum; SLO deveria ser estável).

Esse exercício prepara o Bloco 4, onde traduzimos *taxas de queima* em alertas multi-window burn-rate.

---

## Autoavaliação final do bloco

- [ ] Sei distinguir monitoramento de observabilidade e justificar quando cada um basta.
- [ ] Escolho o pilar (métrica, log, trace) certo dada uma pergunta.
- [ ] Aplico RED/USE sem confundir sinais de serviço com sinais de recurso.
- [ ] Projeto um SLO com SLI preciso, janela adequada, budget calculado.
- [ ] Auditaria um PR rejeitando labels com cardinalidade explosiva.
- [ ] Diferencio dashboard de incidente de dashboard decorativo.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — Fundamentos da Observabilidade](01-fundamentos-observabilidade.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Bloco 2 — Métricas com Prometheus e Grafana](../bloco-2/02-metricas-prometheus.md) |

<!-- nav:end -->

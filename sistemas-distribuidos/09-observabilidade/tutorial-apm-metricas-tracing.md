# Tutorial — APM: métricas, tracing e drill-down

**Lab:** [lab-apm-metricas-tracing](lab-apm-metricas-tracing/) · Gateway `http://127.0.0.1:8110` · Grafana `http://127.0.0.1:3110`  
**Teoria:** [teoria.md](teoria.md) §7–12 · [glossario](glossario.md)

> **Antes:** `cd ../lab-logs-agregados && docker compose down -v`  
> **Núcleo (sala):** Exp. **1–4**. **Aprofundamento (casa/aula extra):** Exp. **5–7** + sampling OTel.  
> **Grafana (cola):** **Dashboards → APM → Portal RED (APM)** · Explore → Tempo / Loki / Prometheus · **Last 15 minutes**.  
> **Ponte lab A:** `trace_id` hex = mesmo papel do `X-Trace-Id`; hops usam **`traceparent` (W3C)** via OTel.

---

## Parte A — Tecnologia (o essencial)

| Peça | Papel |
|------|--------|
| OpenTelemetry → Tempo (OTLP) | Traces / spans |
| `prometheus_client` → `/metrics` → Prometheus | RED (simplificação: métricas **não** via OTLP neste lab — [teoria §12](teoria.md)) |
| Loki + Promtail | Logs (igual lab A) |
| Grafana | Console **APM didático** (fatia do APM comercial — [teoria §10](teoria.md)) |
| `INJECT_DELAY_MS` / `INJECT_ERROR_RATE` | Sintomas |

```text
Dashboard RED (p95 sobe)
  → Explore Tempo (span "analisar" longo)
    → Loki |= "trace_id" (detalhe)
```

> **Simplificações:** sem Alertmanager; sampling ~100%; store em memória; sem auto-instrumentation (spans manuais de propósito).

---

## Parte B — Contexto

Logs correlacionados bastam para “achar o request”. Em pico: *está degradando?* e *onde?* Métricas = tendência; trace = hop; APM (Grafana) junta os três.

Ponte [06](../06-falhas-timeout/): o **Exp. 7** (`provar-retry.sh`) mostra retries como vários spans no mesmo trace — delay/erro nos Exp. 2–3 localizam o hop; o retry mostra o *custo* da política.

---

## Parte C — Lab

### C.1 Subir

```bash
cd sistemas-distribuidos/09-observabilidade/lab-apm-metricas-tracing
./scripts/up.sh
./scripts/status.sh
```

Grafana: <http://127.0.0.1:3110> → **Dashboards → APM → Portal RED (APM)**.  
Aguarde ~15–20s após o primeiro tráfego (scrape Prometheus 5s).

### C.2 Experimento 1 — Tráfego normal + RED

```bash
for i in 1 2 3 4 5; do ./scripts/enviar.sh "aluno-$i"; done
```

**Exemplo de resposta (trecho):**

```json
{
  "status": "aceito",
  "trace_id": "6446bc4b2f889202…",
  "submission_id": "14e8044fe20c",
  "relatorio": { "duration_ms": 50 }
}
```

No dashboard: RPS por serviço, error rate ~0, p95 baixo.

**Esperado:** séries `gateway`, `analise`, `store` no gráfico Rate. Se vazio → confira Targets em <http://127.0.0.1:9091/targets> (UP) e time range.

### C.3 Experimento 2 — Delay no miolo

```bash
./scripts/provar-delay.sh 2000
```

Anote o `trace_id` da resposta (`duration_ms` ~2000+).

1. Dashboard: p95 da **analise** (e gateway) sobe.  
2. Explore → **Tempo**: Search por serviço `gateway` ou cole o `trace_id`.  
3. Waterfall (exemplo ASCII do que você deve ver):

```text
POST /provas                 ~2050ms   gateway
 └─ analisar                 ~2000ms   analise   ← culpado
     └─ persistir              ~15ms   store
```

**Esperado:** culpado = hop do meio — sem SSH.

### C.4 Experimento 3 — Erro + health mentiroso

```bash
./scripts/provar-erro.sh
```

**Esperado:** POST 500; `/health` 200; error rate sobe no dashboard; span com status ERROR; Loki `|="falha injetada"`.

### C.5 Experimento 4 — Drill-down APM

1. No dashboard, note o momento do erro/delay.  
2. Explore → Tempo → abra o trace do `trace_id`.  
3. Explore → Loki:

```logql
{job="portal"} |= "COLE_O_TRACE_ID"
```

**Esperado:** mesma história em métrica → trace → log.

### C.6 Experimento 5 — Cardinalidade (quiz + rubrica)

```bash
./scripts/quiz-cardinalidade.sh
```

Responda **antes** de ler a rubrica no final do script.

**Esperado (rubrica):** ~200k séries; Prometheus sofre; `aluno` vive no log/span; labels estáveis = service/route/status.

### C.7 Experimento 6 — Amostragem (papel + SDK)

**6a — conta no papel**

```bash
./scripts/quiz-sampling.sh 1000 1
```

**6b — sampling real no OTel** (recreate **só do gateway**, ~1 min)

```bash
./scripts/provar-sampling-otel.sh 0.2 40
```

**Esperado:** bem **menos** traces no Tempo que 40 requests (ordem ~8; varia); Loki com a tag do script ainda cobre os POSTs. Restaura `1.0` ao final.

### C.8 Experimento 7 — Retry no trace (ponte [06](../06-falhas-timeout/))

```bash
./scripts/provar-retry.sh
```

**Esperado no Tempo:**

```text
POST /provas
 ├─ chamar_analise_tentativa_1  ERROR
 └─ chamar_analise_tentativa_2  ERROR
```

Retry multiplica spans e carga — por isso [06](../06-falhas-timeout/) exige **idempotência**. O script restaura `retries=0`.

---

## O que observar

- Métrica = tendência; trace = caminho; log = detalhe.  
- Console APM do lab ≠ produto comercial completo — mesma ideia, menos embalagem.  
- Sampling 100% ok no lab; em produção combine sampling + logs com `trace_id` (Exp. 6).  
- Retry sem idempotência = mais spans e mais dor ([06](../06-falhas-timeout/), Exp. 7).

**Fechamento:** [decisoes.md](decisoes.md) · [tecnologias-e-escolhas.md](tecnologias-e-escolhas.md).

# Tutorial — Logs agregados e correlação

**Lab:** [lab-logs-agregados](lab-logs-agregados/) · Gateway `http://127.0.0.1:8100` · Grafana `http://127.0.0.1:3100`  
**Teoria:** [teoria.md](teoria.md) §1–6 · [glossario](glossario.md)

> **Caminho mínimo:** C.1 → **Exp. 1–5**.  
> **Grafana (cola):** menu → **Explore** → datasource **Loki** → cole a query → time range **Last 15 minutes** → **Run query**. Se vazio, espere ~15s (Promtail) e rode de novo.

---

## Parte A — Tecnologia (o essencial)

| Peça | Papel |
|------|--------|
| gateway → analise → store | Três hops do portal de provas |
| Log JSON (`trace_id`, `service`, `msg`) | Evento estruturado |
| Volume `app-logs` → **Promtail** → **Loki** | Pipeline de agregação (didático; prod ≠ volume — [teoria §6](teoria.md)) |
| Grafana Explore | LogQL |
| `PROPAGATE_TRACE` | `1` = header `X-Trace-Id`; `0` = história quebrada |
| `UNSTRUCTURED_LOG` | `1` no store = `print` texto (contraste) |
| `INJECT_ERROR_RATE` / `INJECT_DELAY_MS` | Falha/lentidão no miolo |

```text
POST /provas (gateway)
  → POST /analisar (analise)   [X-Trace-Id]
    → POST /persistir (store)
  ← 201 + trace_id + submission_id
```

> **Simplificações:** store em memória; Loki single-node; Grafana `admin`/`admin`. Campo `aluno` no log é didático — não copie PII para produção.

---

## Parte B — Contexto

Dia da entrega: três serviços no recibo. Aluno reclama; cada container tem log. Sem `trace_id` + agregador = caça ao tesouro.

Pergunta: *como remontar a história de um envio nos três hops em menos de um minuto?*

---

## Parte C — Lab

### C.1 Subir

```bash
cd sistemas-distribuidos/09-observabilidade/lab-logs-agregados
./scripts/up.sh
./scripts/status.sh
```

Abra <http://127.0.0.1:3100> (`admin`/`admin` ou anônimo Viewer).

### C.2 Experimento 1 — Request feliz + mesmo `trace_id`

```bash
./scripts/enviar.sh aluno-01
```

**Exemplo de resposta:**

```json
{
  "status": "aceito",
  "trace_id": "a1b2c3d4e5f6…",
  "submission_id": "8e94179f95fd",
  "aluno": "aluno-01",
  "relatorio": { "similaridade_pct": 12, "duration_ms": 50 }
}
```

Anote o `trace_id`. No Explore → Loki (Last 15 minutes):

```logql
{job="portal"} |= "COLE_O_TRACE_ID_AQUI"
```

**Esperado:** linhas dos três `service` (`gateway`, `analise`, `store`) com o **mesmo** `trace_id`. Se vazio → aguarde ~15s e Run de novo.

### C.3 Experimento 2 — Sem propagação

```bash
./scripts/provar-sem-propagacao.sh
```

Filtre no Loki pelo `trace_id` impresso pelo script (o da **resposta do gateway**).

**Esperado:** só o **gateway** com aquele ID; análise/store com outros IDs. O script restaura `PROPAGATE_TRACE=1`.

### C.4 Experimento 3 — Erro no miolo + health mentiroso

```bash
./scripts/provar-erro.sh
```

O script mostra: `GET /health` → **200** e `POST /provas` → **500**.

**Esperado:**

- HTTP 500 no POST; no Loki: `falha injetada na análise` (`service=analise`) e erro no `gateway` com o **mesmo** `trace_id`.
- Health continua “verde” — monitoramento de liveness ≠ observabilidade do negócio ([teoria §2](teoria.md)).

### C.5 Experimento 4 — Log texto vs JSON

```bash
./scripts/provar-log-texto.sh
```

**Esperado:** o **store** escreve linha tipo `INFO store: prova persistida …` (sem JSON). No Loki a linha aparece, mas filtrar por campo `trace_id` estruturado fica bem mais difícil — contraste com Exp. 1. O script restaura JSON.

### C.6 Experimento 5 — SSH vs agregador

```bash
./scripts/provar-ssh-vs-loki.sh
```

O script: (A) tenta achar o `trace_id` com `docker compose logs` em **3** serviços; (B) imprime **um** filtro LogQL para o Grafana.

**Esperado:** mesma pergunta; a abordagem B escala, a A não.

---

## O que observar

- Sem ID de correlação, logs de N nós são ruído.  
- Agregador sem estrutura ainda é difícil de filtrar.  
- `/health` 200 não prova que o POST funciona.  
- Lab A usa `X-Trace-Id`; no lab B o **mesmo papel** será `traceparent`/OTel ([teoria §5](teoria.md)).

**Próximo:** [tutorial-apm-metricas-tracing.md](tutorial-apm-metricas-tracing.md) (`down -v` neste lab antes).

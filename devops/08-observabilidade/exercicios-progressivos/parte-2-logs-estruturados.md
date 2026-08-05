# Parte 2 — Logs estruturados com Loki

## Objetivos

- Instalar Loki + agente de coleta no cluster.
- Migrar a app `pedidos` para logs JSON estruturados via `structlog`.
- Garantir campos obrigatórios: `ts`, `level`, `service`, `env`, `version`, `msg`.
- Consultar logs com LogQL no Grafana.
- Adicionar Loki como datasource no Grafana.

---

## Tarefas

### 2.1 Instalar Loki + agente

Use `loki-stack` (inclui Promtail) para simplicidade:

```makefile
loki:
	helm upgrade --install loki grafana/loki \
	  --namespace monitoring \
	  --set loki.auth_enabled=false \
	  --set singleBinary.replicas=1 \
	  --set loki.storage.type=filesystem \
	  --set loki.commonConfig.replication_factor=1
	helm upgrade --install promtail grafana/promtail \
	  --namespace monitoring \
	  --set "loki.serviceName=loki"
```

Adicione ao `up`:

```makefile
up:
	bash scripts/k3d-up.sh
	$(MAKE) stack
	$(MAKE) loki
```

Validação:

```bash
kubectl -n monitoring get pods | grep -E "loki|promtail"
```

Deve existir `loki-0` e daemonset de `promtail` em todos os nodes.

### 2.2 Configurar datasource Loki no Grafana

O chart `kube-prometheus-stack` permite provisionar datasources via ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-ds-loki
  namespace: monitoring
  labels:
    grafana_datasource: "1"
data:
  loki.yaml: |
    apiVersion: 1
    datasources:
      - name: Loki
        type: loki
        access: proxy
        url: http://loki.monitoring.svc.cluster.local:3100
        isDefault: false
        editable: true
```

Ajuste o `values-kps.yaml` para incluir o sidecar de datasources:

```yaml
grafana:
  sidecar:
    datasources:
      enabled: true
      searchNamespace: ALL
      label: grafana_datasource
      labelValue: "1"
```

### 2.3 Refatorar logs da app

Adicione ao `app/requirements.txt`:

```
structlog==24.4.0
```

Crie `app/src/obs/logging.py` copiando o código da seção 3.1.3 do Bloco 3.

No `main.py`, substitua `print`/`logging.info` por `log.info(...)`:

```python
from app.src.obs.logging import log

@app.post("/orders")
def criar(payload: dict):
    log.info("criando pedido", tier=payload.get("tier", "free"))
    time.sleep(random.uniform(0.02, 0.30))
    if random.random() < 0.03:
        log.error("erro interno simulado", source="payment-gateway")
        raise HTTPException(status_code=500, detail="erro interno simulado")
    oid = f"o-{random.randint(1000,9999)}"
    ORDERS_CREATED.labels(tenant_tier=payload.get("tier","free"), channel="api").inc()
    log.info("pedido criado", order_id=oid)
    return {"id": oid, "status": "created"}
```

Rebuild e re-import:

```bash
docker build -t logisgo/pedidos:0.2.0 app/
k3d image import logisgo/pedidos:0.2.0 -c obs-lab
kubectl -n logisgo set image deployment/pedidos pedidos=logisgo/pedidos:0.2.0
```

Valide no terminal:

```bash
kubectl -n logisgo logs -l app=pedidos --tail=20
# Deve mostrar linhas JSON
```

### 2.4 Consultas no Grafana (Loki)

Em **Explore → datasource Loki**:

```logql
{namespace="logisgo", app="pedidos"}
{namespace="logisgo", app="pedidos"} | json | level="ERROR"
{namespace="logisgo", app="pedidos"} | json | line_format "{{.msg}} tier={{.tier}}"
sum by (level) (rate({namespace="logisgo", app="pedidos"} | json [1m]))
```

Documente em `docs/queries-uteis.md` as consultas que respondem "quais erros agora?", "quais pedidos criados nos últimos 5 min?", "uma linha por erro do tipo X".

### 2.5 Painel "Eventos por nível" no dashboard RED

Adicione ao dashboard RED (Grafana) um painel tipo **stat** ou **bar gauge** usando datasource Loki:

```logql
sum by (level) (count_over_time({namespace="logisgo", app="pedidos"} | json [5m]))
```

Versione o JSON atualizado do dashboard.

---

## Validação da parte 2

- [ ] `kubectl -n monitoring get pods` inclui `loki` e `promtail`.
- [ ] Em Grafana, Explore → Loki retorna logs JSON da app.
- [ ] Consulta `| json | level="ERROR"` filtra corretamente.
- [ ] Logs contêm `ts`, `level`, `service`, `env`, `version`, `msg`.
- [ ] Nenhum log em texto corrido.
- [ ] Dashboard RED mostra painel de eventos por nível.

---

## Entregáveis

- `app/src/obs/logging.py`.
- `app/src/main.py` refatorado com `log.info`/`log.error`.
- ConfigMap datasource Loki.
- `docs/queries-uteis.md` com 5+ consultas LogQL comentadas.
- Painel novo no dashboard RED.

---

## Pontos de atenção

- **Não logue dados sensíveis**. Se precisar de campo de auditoria, use ID (order_id) — não dados pessoais completos.
- **Evite labels Loki explosivos**. Não adicione `user_id` como label; mantenha no conteúdo.
- **Linha única por evento**: `log.info("criando pedido ...")` **não** deve quebrar em múltiplas linhas. Evite newline no `msg`.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — Stack observabilidade + métricas RED](parte-1-stack-e-metricas.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Parte 3 — Traces distribuídos com OpenTelemetry + Tempo](parte-3-traces-otel.md) |

<!-- nav:end -->

# Troubleshooting — Labs do módulo 09

Faça **um lab por vez**. Ao trocar:

```bash
docker compose down -v
```

Encerre labs 01–08 se as portas conflitarem.

---

## Portas deste módulo

| Serviço | Host (lab A) | Host (lab B) |
|---------|--------------|--------------|
| Gateway (API) | **8100** | **8110** |
| Grafana | **3100** | **3110** |
| Loki | **3101** | **3102** |
| Prometheus | — | **9091** |
| Tempo (OTLP HTTP) | — | **3200** |

Grafana: usuário/senha padrão dos labs = `admin` / `admin` (só didático).

---

## Geral

| Sintoma | O que tentar |
|---------|----------------|
| `Cannot connect to Docker daemon` | Docker Desktop **ou** Podman: `export DOCKER_HOST=unix://$XDG_RUNTIME_DIR/podman/podman.sock` |
| Porta em uso | `docker ps`; `down -v` no outro lab |
| API 503 / connection refused no boot | Espere 30–60s; `./scripts/up.sh` |
| `COMPOSE_FILE` / projeto errado | `unset COMPOSE_FILE COMPOSE_PROJECT_NAME` |
| Scripts `compose: command not found` | Use `_compose.sh` via `./scripts/up.sh` |
| Grafana “No data” | Confirme datasource; gere tráfego com `./scripts/enviar.sh`; aguarde ~15s (scrape/Promtail) |
| Loki/Promtail: `config.yml does not exist` | SELinux (Fedora/RHEL): Compose já usa `:z` nos binds; se ainda falhar, `chcon -Rt container_file_t .` na pasta do lab |
| Loki sem linhas | Confira arquivos em volume (`./scripts/status.sh`); `compose logs promtail` |
| Trace não aparece no Tempo | Lab B: confira `OTEL_EXPORTER_OTLP_ENDPOINT`; gere request **depois** do up; Explore → Tempo |
| OOM / máquina lenta | Feche o outro lab; no mínimo use só lab A; aumente memória do Docker |

---

## Lab A (`lab-logs-agregados`, :8100 / Grafana :3100)

| Sintoma | O que tentar |
|---------|----------------|
| `trace_id` diferente em cada serviço | Exp. sem propagação — esperado; volte com `./scripts/enviar.sh` normal |
| LogQL não acha | Use o `trace_id` devolvido no JSON do POST; filtro `{job="portal"} |= "TRACE_ID"` |
| Análise sempre 500 | `INJECT_ERROR_RATE` alta — `./scripts/set-inject.sh 0 0` |
| Log do store sem JSON | Exp. log texto (`UNSTRUCTURED_LOG=1`) — restaure com o script ou `UNSTRUCTURED_LOG=0 compose up -d --no-deps store` |
| Serviços não se falam | Nomes DNS do Compose: `http://analise:8000`, `http://store:8000` |
| 1ª build lenta / OOM | Feche outros labs; lab B pede ~4–6 GB RAM; aguarde pull das imagens Grafana/Loki |

---

## Lab B (`lab-apm-metricas-tracing`, :8110 / Grafana :3110)

| Sintoma | O que tentar |
|---------|----------------|
| `/metrics` vazio no browser do host | Métricas ficam **dentro** da rede Compose; Prometheus scrapeia. No host: `curl -s localhost:8110/metrics \| head` (gateway expõe) |
| Dashboard sem séries | Prometheus → Targets (Status) devem estar UP; espere 2 scrapes |
| Span da análise não cresce | Confirme delay: `./scripts/set-inject.sh 2000 0` e **novo** POST |
| Correlação log↔trace | Mesmo `trace_id` hex (lab A era `X-Trace-Id`; aqui OTel/`traceparent` — mesmo conceito) |
| Dashboard vazio após enviar | Time range **Last 15 minutes**; espere 2 scrapes (~10s); <http://127.0.0.1:9091/targets> |

---

## Manutenção (docentes / contribuições)

**Lab A:** `lab-logs-agregados/gateway/common.py` → `./scripts/sync-common.sh`  
**Lab B:** `lab-apm-metricas-tracing/gateway/common.py` → `./scripts/sync-common.sh`  

Não misture `common.py` entre A e B (B tem OTel).  
Compose separados de propósito (caminho mínimo sem stack APM).  
**Adiado de propósito:** monorepo único A+B — custo de manutenção vs clareza didática do mínimo.

---

## Ponte com outros módulos

| Sintoma “parece 09” | Na verdade… |
|---------------------|-------------|
| Timeout / retry na matrícula | [06](../06-falhas-timeout/) — no lab B, Exp. 7 mostra retry no **trace** |
| Fila / vários workers sem ID | [01](../01-comunicacao/) — falta correlação |
| Operar Prometheus no K8s | [`devops/08`](../../devops/08-observabilidade/) |

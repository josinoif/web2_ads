# Fase 3 — Operação e resiliência

> **Propósito.** Na Fase 2 o sistema **existe**; na Fase 3 ele é **visto**, **protegido** e **testado sob stress**. Aqui você transforma bytes em um **serviço operável**.

**Duração sugerida:** 15-25h em ~3 semanas.

---

## 3.1 Objetivos da fase

- **Stack de observability** completo em uso real (métricas, logs, traces) — não só "instalado".
- **SLIs e SLOs** declarados e publicados; **Error Budget Policy** definida.
- **≥ 3 dashboards** Grafana e **≥ 3 alertas** SLO-based roteados.
- **Threat model STRIDE** documentado.
- **Admission control** (Kyverno/OPA) com pelo menos 2 políticas.
- **Controles LGPD** implementados (mínimo viável).
- **≥ 1 experimento de Chaos** executado com resultado registrado.
- **Backup Velero** agendado e **restore testado** em namespace alternativo.
- **DR playbook** com RPO/RTO medidos.
- **≥ 3 runbooks** operacionais testáveis.
- **Política de on-call** declarada (mesmo simulada).

Produto da fase: um sistema que **informa sobre si** e **se defende** de falhas previsíveis.

---

## 3.2 Observability — o mínimo que conta

### 3.2.1 Os três pilares

- **Métricas** (Prometheus): RED (Rate, Errors, Duration) + USE (Utilization, Saturation, Errors) para infra.
- **Logs estruturados** (Loki): JSON com trace_id, tenant_id, user_id anonimizado.
- **Traces** (OpenTelemetry → Tempo/Jaeger): HTTP + DB + Queue propagando `traceparent`.

### 3.2.2 Instrumentação (Python)

```python
# services/api/src/app/observability.py
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import Counter, Histogram

http_requests = Counter("http_requests_total", "Total requests", ["method", "path", "status"])
http_latency = Histogram("http_request_duration_seconds", "Latency", ["method", "path"])


def init_tracing(service_name: str, otlp_endpoint: str) -> None:
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)))
    trace.set_tracer_provider(provider)


def instrument(app) -> None:
    FastAPIInstrumentor.instrument_app(app)
    Psycopg2Instrumentor().instrument()
```

### 3.2.3 Logs estruturados

```python
import logging, json, sys

class JsonFormatter(logging.Formatter):
    def format(self, rec):
        d = {
            "ts": self.formatTime(rec, "%Y-%m-%dT%H:%M:%S"),
            "level": rec.levelname,
            "msg": rec.getMessage(),
            "logger": rec.name,
        }
        if hasattr(rec, "trace_id"):
            d["trace_id"] = rec.trace_id
        return json.dumps(d, ensure_ascii=False)


handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(handlers=[handler], level=logging.INFO)
```

### 3.2.4 SLIs / SLOs

Exemplo para CivicaBR:

| SLI | Fórmula | Janela | SLO |
|-----|---------|--------|-----|
| Disponibilidade da API | 1 - (5xx / total) | 30d rolling | ≥ 99,9% |
| Latência p95 POST /reports | p95(http_request_duration{method="POST"}) | 30d | ≤ 800ms |
| Latência notificação | p95 (status_change → email_sent) | 30d | ≤ 5 min |
| Sucesso do worker | success/total | 30d | ≥ 99,5% |

**Error Budget Policy** (ver Módulo 10):

```markdown
## EBP - CivicaBR API

- Budget 0.1% ao mês (~43 min).
- 0-25% consumido: verde. Deploys normais.
- 25-75% consumido: amarelo. Aumentar vigilância; deploys apenas com teste completo.
- 75-100% consumido: vermelho. Freeze de deploys de feature; focar em confiabilidade.
- 100%+ exaurido: toque imediato; rollback; deploys so de correcao; postmortem de causa raiz.
```

### 3.2.5 Dashboards (mínimo 3)

1. **Visão executiva** — SLOs vigentes, error budget, DORA.
2. **Golden signals por serviço** — Rate, Errors, Duration, Saturação.
3. **Saúde operacional** — status de jobs, backlog de fila, uso de DB/pool, uso de recursos por Pod.

### 3.2.6 Alertas (mínimo 3)

Preferir **SLO-based burn rate** (Módulo 8/10) a alertas brutos:

```yaml
# Prometheus alert rules
groups:
- name: civica-api-slo
  rules:
  - alert: ApiFastBurn
    expr: |
      (1 - (rate(http_requests_total{status=~"5.."}[5m])
            / rate(http_requests_total[5m]))) < 0.995
    for: 5m
    labels: { severity: page }
    annotations:
      summary: "API queimando budget rápido nos últimos 5 min"
      runbook_url: "https://github.com/.../docs/runbooks/api-5xx.md"

  - alert: ApiSlowBurn
    expr: |
      # 6h window at 2% budget burn rate
      (1 - (rate(http_requests_total{status=~"5.."}[6h])
            / rate(http_requests_total[6h]))) < 0.998
    for: 30m
    labels: { severity: ticket }

  - alert: WorkerBacklog
    expr: rabbitmq_queue_messages_ready{queue="notificacoes"} > 500
    for: 10m
    labels: { severity: page }
```

---

## 3.3 Segurança — shift-left + shift-right

### 3.3.1 Threat model STRIDE

Em `docs/security/threat-model.md`, para os 3-5 componentes mais críticos:

| Componente | S | T | R | I | D | E |
|-----------|---|---|---|---|---|---|
| API externa | Jwt roubado | MITM | Log adulterado | PII vazada em log | DDoS pico | Rota admin sem authz |

Para cada célula relevante: **ameaça**, **controle existente**, **gap**, **ação**.

### 3.3.2 LGPD mínimo

- **Inventário de dados** (da Fase 1) revisado e refinado.
- **DPA/DPO** declarado em documentação.
- **Endpoint de direitos do titular** (acesso, portabilidade, eliminação) — mesmo que mock.
- **Hash/pseudonimização** de e-mail em logs.
- **Retenção**: agendado script que anonimiza dados após 3 anos.

### 3.3.3 Admission Control (Kyverno)

Políticas mínimas:

```yaml
# kyverno/only-signed-images.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: only-signed-images
spec:
  validationFailureAction: enforce
  rules:
  - name: check-signature
    match:
      any:
        - resources:
            kinds: [Pod]
    verifyImages:
    - imageReferences: ["ghcr.io/civica/*"]
      attestors:
      - entries:
        - keyless:
            subject: "https://github.com/civica/*"
            issuer: "https://token.actions.githubusercontent.com"
```

```yaml
# kyverno/require-readonly-root.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-readonly-root-fs
spec:
  validationFailureAction: enforce
  rules:
  - name: check-readonly
    match:
      any:
        - resources:
            kinds: [Pod]
    validate:
      message: "Containers must run with readOnlyRootFilesystem=true"
      pattern:
        spec:
          containers:
          - securityContext:
              readOnlyRootFilesystem: true
```

Outras sugeridas: proibir `:latest`; exigir `runAsNonRoot`; exigir limits de recursos.

### 3.3.4 Secrets

Sealed Secrets (Bitnami) ou External Secrets Operator + Vault.
`Secret` em texto claro proibido em repositório.

### 3.3.5 Resposta a incidente de segurança

Runbook curto em `docs/runbooks/security-incident.md`:

1. **Detectar**: fontes (Gitleaks, Falco, logs anômalos).
2. **Conter**: rotacionar credenciais; desabilitar contas comprometidas.
3. **Erradicar**: corrigir causa; revogar tokens; aplicar patch.
4. **Recuperar**: validar sistemas; restaurar se comprometidos.
5. **Aprender**: postmortem blameless com foco em sistema.

---

## 3.4 Chaos Engineering mínimo

### 3.4.1 Hipótese antes do caos

Em `chaos/experimento-01.md`:

```markdown
# Experimento 01 - Pod kill na API

- Hipotese: ao matar 1 de 2 Pods de API, taxa 2xx permanece >= 99.9%
  por 5 min (readiness probes + HPA + PDB devem absorver).
- Steady state: taxa 2xx por minuto medida por Prometheus;
  error budget burn rate < 1%.
- Blast radius: namespace staging, 1 replica por vez.
- Abort criteria: queda de 2xx abaixo de 99% por > 2 min seguidos.
- Duracao: 10 min.
- Reversibilidade: automatica (Pod e recriado).
- Observabilidade: painel "chaos-current" pre-aberto.

## Execucao
- 2026-09-20 14h00: inicio.
- 14h03: Pod alvo killado.
- 14h04: novo Pod ready (30s).
- 14h05: metricas normais.
- 14h10: encerrado.

## Resultado
- Hipotese confirmada.
- Observacao: traces de 4 requests receberam 504 durante os 5s entre death e ready.
  ACAO: ajustar retry policy no client.
```

### 3.4.2 Chaos Mesh (K8s nativo)

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: kill-api-staging
  namespace: chaos
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces: [ staging ]
    labelSelectors: { app: api }
  duration: "30s"
```

Executar conforme agenda; nunca de surpresa. Game Day agendado ajuda adoção.

---

## 3.5 Backup e DR

### 3.5.1 Velero

Instalação com MinIO local (Módulo 10). Depois:

```bash
# Backup ad-hoc
velero backup create backup-$(date +%s) --include-namespaces staging

# Agendado diário
velero schedule create daily --schedule="0 3 * * *" --ttl 168h

# Restore em namespace alternativo (drill)
velero restore create --from-backup backup-XXXX --namespace-mappings staging:staging-dr
```

### 3.5.2 Postgres base + WAL

Se o capstone usa PG em container, simule estratégia:

- `pg_basebackup` diário armazenado em S3/MinIO.
- `archive_command = 'wal-g wal-push %p'` — envia WAL incrementais.
- PITR testado: restaurar a ponto T arbitrário.

Registre **RPO** (quanto perde) e **RTO** (quanto demora) medidos.

### 3.5.3 DR Playbook

`docs/runbooks/dr-cluster-perdido.md`:

```markdown
# Runbook DR - Perda total de cluster K8s

## Objetivo
Restaurar CivicaBR operacional em <= 2h (RTO) com <= 15 min de dados perdidos (RPO).

## Precondicoes
- Backups Velero diarios na regiao secundaria.
- Backups Postgres horarios.
- Senhas/tokens no Vault.

## Passos
1. [0-10 min] Criar novo cluster (terraform apply env=dr).
2. [10-20 min] Instalar Velero com bucket secundario.
3. [20-40 min] velero restore create --from-backup <daily-latest>.
4. [40-60 min] Restaurar DB Postgres via pg_restore + replay WAL.
5. [60-80 min] Validar: healthchecks, smoke tests.
6. [80-100 min] Redirecionar DNS (TTL 60s reduzido 24h antes para casos planejados).
7. [100-120 min] Comunicar clientes pela status page.
```

Drill **trimestral** (real ou simulado) — documente o último em `docs/dr-drills/YYYY-MM-DD.md`.

---

## 3.6 Runbooks

Estrutura padrão de runbook (`docs/runbooks/NOME.md`):

```markdown
# Runbook: nome do cenario

## Sintoma
O que se observa (logs, alertas, chamada de suporte).

## Severidade sugerida
Sev-1 / Sev-2 / Sev-3 com criterio objetivo.

## Diagnostico rapido
Comandos (`kubectl`, `curl`, `psql`) para confirmar.

## Acoes
1. Passo 1 (comando ou link).
2. Passo 2.
3. Passo 3.

## Rollback
Como reverter se a mitigacao nao funciona.

## Escalonamento
Para quem chamar se passos nao resolvem.

## Pos-incidente
- Registrar postmortem se Sev-1 ou Sev-2.
- Atualizar runbook com licoes.
```

Runbooks mínimos do capstone:

1. `api-5xx.md` — alerta ApiFastBurn.
2. `worker-backlog.md` — fila empilhando.
3. `db-conexoes-esgotadas.md` — pool exaurido.
4. (Opcional) `security-incident.md`.
5. (Opcional) `dr-cluster-perdido.md`.

---

## 3.7 On-call (simulado)

Mesmo solo, declare:

```markdown
## Politica de on-call (capstone)

- Papeis: IC (comando), Ops Lead, Comms Lead, Scribe. Em capstone solo,
  o mesmo humano rotaciona explicitamente (declara: "mudando para IC").
- Janela: 24x7 durante prova/demo; em rotina do capstone, horario comercial.
- Ferramentas: alertas Prometheus -> webhook -> Telegram/Slack pessoal.
- SLA de resposta: Sev-1 5 min, Sev-2 15 min, Sev-3 1h, Sev-4 melhor esforco.
- Toque: alertas Sev-1 e Sev-2; Sev-3 so ticket.
- Ferias/indisponibilidade: declarar em 24h de antecedencia.
- Compensacao (nao se aplica em capstone) - registrar em produto real.
```

---

## 3.8 Checklist de aceitação da Fase 3

### Observability
- [ ] Métricas expostas em `/metrics`; Prometheus coleta.
- [ ] Logs JSON com `trace_id` em todos os serviços.
- [ ] Traces chegam em Tempo/Jaeger.
- [ ] SLIs declarados; SLOs publicados em `docs/slos.md`.
- [ ] EBP documentada em `docs/ebp.md`.
- [ ] ≥ 3 dashboards + ≥ 3 alertas ativos.

### Segurança
- [ ] Threat model STRIDE escrito.
- [ ] Kyverno com ≥ 2 políticas ativas.
- [ ] Secrets só via Sealed/External.
- [ ] LGPD: inventário + controles implementados + endpoint de direitos.
- [ ] Runbook de security incident.

### SRE
- [ ] ≥ 1 experimento Chaos com resultado documentado.
- [ ] Velero agendado; 1 restore testado em namespace alternativo.
- [ ] DR playbook com RPO/RTO medidos.
- [ ] ≥ 3 runbooks prontos.
- [ ] Política on-call declarada.

### Documentação
- [ ] Postmortem template em `docs/postmortems/_TEMPLATE.md`.
- [ ] Ao menos 1 postmortem real/simulado registrado.
- [ ] README raiz atualizado com links para dashboards/runbooks.

---

## 3.9 Armadilhas comuns

- **Dashboard que não é usado.** Se você não abre há 2 semanas, está mentindo sobre obs.
- **SLO sem consequência.** SLO sem EBP é decoração. A política de ação precisa ter **ações vinculadas**.
- **Alerta gritão.** Se alerta toca sem ação possível, vira fadiga. *Todo alerta paginado tem runbook*.
- **Chaos sem hipótese.** Matar Pods aleatoriamente não é chaos, é sabotagem.
- **Backup sem restore testado.** "Temos backup" sem "já restauramos" = nada.
- **Runbook narrativo sem comando.** Operador sob estresse não lê parágrafo; lê comando.
- **Threat model genérico.** Copiar tabela STRIDE padrão sem aplicar ao domínio é perda.
- **Ignorar LGPD.** "Vemos depois" nunca chega. Agora é a hora.

---

## Próxima fase

O sistema está instrumentado, seguro e resiliente. A [Fase 4 — Plataforma e apresentação](../bloco-4/04-fase-plataforma.md) costura um portal interno, consolida métricas e prepara a **defesa ao vivo** com incidente simulado.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Fase 2 — Armadilhas, dicas e orientações de banca](../bloco-2/02-armadilhas-e-dicas.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Fase 3 — Armadilhas, dicas e orientações de banca](03-armadilhas-e-dicas.md) |

<!-- nav:end -->

# Bloco 4 — Alertas, SLO-based alerting, runbooks e cultura on-call

> **Pergunta do bloco.** Como projetar alertas que **só acordam** quando precisam acordar, capazes de sustentar um rodízio on-call sem queimar pessoas — e como transformar incidentes em aprendizado organizacional por meio de runbooks e postmortems sem culpa?

---

## 4.1 Anatomia de um alerta saudável

Um alerta é **um pedido de ação humana** (ou automática) diante de um sinal. Se dispara sem ação clara, é **ruído**.

### 4.1.1 Cinco propriedades

| Propriedade | Significado |
|-------------|-------------|
| **Acionável** | Existe ação possível *agora*. Se não há nada a fazer, não é alerta, é decoração. |
| **Urgente** | Requer atenção humana **antes** do próximo horário comercial. Se pode esperar, é ticket, não page. |
| **Relevante ao usuário** | Reflete degradação percebida ou iminente (latência, erros de jornada). |
| **Específico** | Fala *o que* está mal, *onde*, e *quão grave*. |
| **Rastreável a runbook** | Link direto para o procedimento de resposta. |

O **anti-padrão canônico**: "CPU > 80% por 5 min". CPU alta em si **não é sintoma de usuário**. Um serviço pode ficar em 95% de CPU e atender bem; outro pode estar em 30% e perdendo requests.

### 4.1.2 Rule of thumb (Rob Ewaschuk)

> *"Pages should be urgent, important, actionable, and real."*

Na prática, aplique ao revisar cada alerta:

- **Urgent?** (precisa agir agora?)
- **Important?** (alguém/algo real perde se ignorarmos?)
- **Actionable?** (temos um procedimento claro de resposta?)
- **Real?** (não é um alerta que dispara com 40% de falso positivo?)

Se qualquer das quatro respostas é "não", **não é page**. Vira log, ticket, ou deleção.

---

## 4.2 Alertas SLO-based (burn rate)

Thresholds estáticos (`cpu > 80%`, `latency > 500ms`) são frágeis. A alternativa madura é **alertar quando o error budget está sendo consumido rápido demais**.

### 4.2.1 Conceito de burn rate

Se SLO é 99,5% em 28 dias, budget = 0,5% de eventos podem ser ruins. **Burn rate** é **quão mais rápido** você está queimando comparado à taxa "normal":

$$ \text{burn rate} = \frac{\text{taxa atual de erro}}{1 - SLO} $$

- Burn rate **1.0**: queima na velocidade do budget (consome tudo na janela de 28 dias, exatamente).
- Burn rate **2.0**: 2× mais rápido — budget acaba em 14 dias.
- Burn rate **14.4**: consome 100% do budget em **1 hora**.

### 4.2.2 Alerting multi-window multi-burn-rate (SRE Workbook, cap. 5)

Use **duas janelas** e **dois thresholds** para balancear **precisão** (detectar rápido) e **recall** (não perder incidentes lentos).

Receita canônica (Google SRE) para SLO de **99,9%** (tolerância alta):

| Severidade | Burn rate | Janela rápida | Janela lenta |
|------------|-----------|---------------|---------------|
| Page | 14.4 | 5 min | 1 h |
| Page | 6 | 30 min | 6 h |
| Ticket | 3 | 2 h | 1 dia |
| Ticket | 1 | 6 h | 3 dias |

A regra é: **alerta dispara se burn rate está alto na janela rápida E na janela lenta**, evitando falsos positivos em picos isolados.

### 4.2.3 PromQL da regra

Para o serviço `pedidos`, SLI por request (erro = 5xx):

```yaml
# PrometheusRule - recording rules
- record: job:sli_errors_ratio_5m
  expr: |
    sum(rate(http_requests_total{service="pedidos", status=~"5.."}[5m]))
    /
    sum(rate(http_requests_total{service="pedidos"}[5m]))

- record: job:sli_errors_ratio_1h
  expr: |
    sum(rate(http_requests_total{service="pedidos", status=~"5.."}[1h]))
    /
    sum(rate(http_requests_total{service="pedidos"}[1h]))

- record: job:sli_errors_ratio_6h
  expr: |
    sum(rate(http_requests_total{service="pedidos", status=~"5.."}[6h]))
    /
    sum(rate(http_requests_total{service="pedidos"}[6h]))
```

```yaml
# PrometheusRule - alertas
- alert: PedidosSLOBurnRateFast
  expr: |
    job:sli_errors_ratio_5m  > (14.4 * (1 - 0.999))
    and
    job:sli_errors_ratio_1h  > (14.4 * (1 - 0.999))
  for: 2m
  labels:
    severity: critical
    slo: "pedidos-availability"
  annotations:
    summary: "Pedidos queimando 14.4x o budget (5m e 1h)"
    runbook_url: "https://runbooks.logisgo/pedidos-slo-burn-fast"

- alert: PedidosSLOBurnRateSlow
  expr: |
    job:sli_errors_ratio_6h  > (3 * (1 - 0.999))
    and
    job:sli_errors_ratio_1d  > (3 * (1 - 0.999))
  for: 15m
  labels:
    severity: warning
    slo: "pedidos-availability"
  annotations:
    summary: "Pedidos queimando 3x budget em 6h/1d"
    runbook_url: "https://runbooks.logisgo/pedidos-slo-burn-slow"
```

Para **SLOs de 99%** (mais tolerantes), ajuste os thresholds proporcionalmente (burn rate 14.4 vira taxa de erro ~14% — alto mas significativo para SLO 99%).

### 4.2.4 Por que esse padrão supera thresholds fixos

- **Adapta-se ao SLO real**, não a número mágico.
- **Não dispara em pico isolado** (precisa casar janela curta *e* longa).
- **Escala com o tráfego**: erros absolutos variam, a *razão* é estável.
- Dá tempo de resposta: há 4h de budget antes de violar o SLO, ao longo das duas janelas, permitindo ação deliberada.

---

## 4.3 Alertmanager em produção

[Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/) é o **roteador de alertas** — recebe do Prometheus, agrupa, inibe, silencia, e entrega a receivers.

### 4.3.1 Conceitos

- **Grouping**: alertas similares viram uma única notificação (ex.: 20 pods de uma Deployment com erro).
- **Inhibition**: um alerta silencia outros (ex.: "node down" silencia "pod crashloop" daquele node).
- **Silence**: supressão temporária manual (manutenção planejada).
- **Routing tree**: árvore de regras decidindo para qual receiver (Slack, PagerDuty, e-mail) cada alerta vai.

### 4.3.2 Config mínima com rotas por severidade

```yaml
# alertmanager.yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['service', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: default

  routes:
    - matchers:
        - severity="critical"
      receiver: oncall-page
      continue: true
      group_wait: 10s
      repeat_interval: 1h
    - matchers:
        - severity="warning"
      receiver: tickets
    - matchers:
        - alertname="Watchdog"
      receiver: watchdog

inhibit_rules:
  - source_matchers: [alertname="NodeDown"]
    target_matchers: [alertname="PodCrashLoop"]
    equal: ['node']

receivers:
  - name: default
    webhook_configs:
      - url: http://incident-webhook.internal/alerts
  - name: oncall-page
    webhook_configs:
      - url: http://incident-webhook.internal/oncall
  - name: tickets
    webhook_configs:
      - url: http://incident-webhook.internal/tickets
  - name: watchdog
    webhook_configs:
      - url: http://incident-webhook.internal/watchdog
```

### 4.3.3 Princípios de design de rotas

- **Um receiver por "destino"**, não por equipe. Equipes recebem do receiver via integração downstream.
- **Severidade decide rota**: `critical` → page (pager/PagerDuty), `warning` → ticket (Jira/GitHub Issue), `info` → canal de Slack.
- **Horário comercial**: algumas empresas desativam notificações de `warning` em fins de semana; use `active_time_intervals` no Alertmanager moderno.
- **Watchdog sempre ativo**: se o Watchdog **para de chegar**, outro sistema externo (dead-man's switch) aciona pager.
- **Silence curto, com motivo**: silenciar sem motivo = "esqueceram que está silenciado" por semanas.

### 4.3.4 Fadiga de alarme — como prevenir

Sinais de alerta com problema:

| Métrica | Limite saudável |
|---------|-----------------|
| Alertas/semana | < 30 para uma equipe pequena |
| % que vira ação concreta | > 80% |
| % falsos positivos | < 5% |
| Horas de sono perdidas/pessoa/mês | < 2h |

Se ultrapassou, **reveja o catálogo**. Delete, ajuste threshold, mova para `warning`, agrupe.

---

## 4.4 Runbooks: transformar conhecimento tácito em código

Um **runbook** é um procedimento para responder a um alerta específico. Sem runbook, cada plantonista reinventa a roda.

### 4.4.1 Estrutura de runbook (template obrigatório da entrega)

```markdown
# Runbook — PedidosSLOBurnRateFast

**Alerta:** `PedidosSLOBurnRateFast`
**Severidade:** critical (page)
**Dono:** squad Orders
**Última revisão:** 2026-04-15

## O que significa

O serviço `pedidos` está consumindo error budget 14.4x mais rápido que o esperado,
medido em janelas de 5m e 1h. Se persistir, violaremos o SLO de 99.9%/28d.

## Impacto ao negócio

Usuários estão recebendo erros 5xx. A cada 1000 requisições, ~14 falham.

## Passos de diagnóstico (em ordem)

1. **Abra o dashboard `RED - pedidos`** em Grafana → painel "erros por rota".
   Qual rota concentra os 5xx?

2. **Abra Tempo com TraceQL:**
   `{ service.name = "pedidos" && status = error }`
   Veja qual span falha (db, rabbitmq, http externo?).

3. **Abra Loki:** `{app="pedidos"} | json | level="ERROR"` últimos 10 min.
   Qual mensagem domina?

4. **Verifique dependências:**
    - Postgres: `db_pool_connections_waiting` > 0?
    - RabbitMQ: `rabbitmq_queue_messages_ready` ≥ 1000?
    - Serviço `estoque`: p95 em spike?

5. **Verifique deploys recentes (ArgoCD):** mudança nas últimas 2h?

## Ações prováveis

| Diagnóstico | Ação |
|-------------|------|
| Pool DB saturado | `kubectl scale` Deployment pedidos para +2 réplicas; criar ticket para revisar pool-size. |
| Deploy recente introduziu erro | `argocd app rollback pedidos` para última versão estável. |
| RabbitMQ congestionado | Investigar consumer `notificacoes`; se parado, `kubectl rollout restart`. |
| `estoque` lento (dependência) | Abrir incident cross-team; circuit-breaker manual em `pedidos` se existir flag. |

## Escala

Se em 20 min sem melhora, escalar para:
- Slack `#oncall-logisgo`
- Líder técnico on-call (rotação em PagerDuty)

## Pós-evento

- Abrir issue de postmortem em `logisgo/incidents` com template blameless.
- Atualizar este runbook com qualquer aprendizado novo.
```

### 4.4.2 Princípios

- **Versionado em git**, junto com o código da app.
- **Revisado trimestralmente** — runbook desatualizado mata.
- **Testado**: treino com *game days* (simula o alerta, plantonista executa o runbook, mede tempo).
- **Ligado ao alerta**: o `runbook_url` no annotation é clicável.

---

## 4.5 Postmortem sem culpa

Incidentes são **inevitáveis**. O que diferencia equipes maduras é o que fazem **depois**.

### 4.5.1 Por que "blameless"

Se postmortem vira caça-ao-culpado:
- Pessoas escondem incidentes pequenos (⇒ problemas sistêmicos não aparecem).
- Ninguém mais quer estar no plantão no dia de mudança grande.
- Aprendizado organizacional vira teatro.

Resposta (SRE Book, cap. 15 e 16):
> *"Blameless postmortem assumes that everyone involved in an incident had good intentions, acted on the best information they had, and did the best they could."*

### 4.5.2 Estrutura mínima

```markdown
# Postmortem — Incidente Zaffrán (2026-04-14)

**Severidade:** P1
**Duração:** 48 min (14:32 → 15:20)
**Autor:** Alice Souza
**Revisão:** 2026-04-17, com equipe Orders + Plataforma

## Resumo executivo
Entre 14:32 e 15:20, 115 pedidos de clientes falharam silenciosamente
ao serem publicados na fila RabbitMQ devido a uma NetworkPolicy
restritiva aplicada 7 dias antes em um namespace específico.

## Impacto
- 115 pedidos perdidos, representando R$ 47.000 em transações.
- Cliente Zaffrán notificou rescisão de contrato três dias depois.

## Timeline
| Horário | Evento |
|---------|--------|
| 14:32 | Primeira falha silenciosa no app. |
| 14:34 | Prometheus dispara `HighErrorRate` (ignorado — 40 falsos na semana). |
| 14:41 | CTO é acionada via chat por cliente. |
| 14:43 | Plantão olha `kubectl get pods` — tudo Running. |
| ... | ... |
| 15:20 | Mitigação aplicada, fluxo normaliza. |

## Causa-raiz
Técnica: NetworkPolicy `deny-egress-default` em `logisgo-prod`
bloqueia egresso para RabbitMQ, que está em namespace distinto.

Sistêmica: não tínhamos teste de fluxo ponta-a-ponta após mudanças
em NetworkPolicy. Observabilidade cega para este caso específico
— métrica de "pedidos publicados" não existia.

## O que correu bem
- PDB manteve pods healthy durante a mitigação.
- Rollout de correção foi em 2 minutos via ArgoCD.

## O que correu mal
- Alerta existente foi ignorado (fadiga).
- Sem SLI de negócio: impossível quantificar perda em tempo real.
- Runbook de "falha de publicação" não existia.

## Ações (com responsável e prazo)
1. Criar SLI `orders_published_total / orders_created_total`
   (Maria, sprint atual).
2. Alerta SLO-based burn rate (Alice, sprint atual).
3. Runbook específico para NetworkPolicy mudanças (Carlos, próximo sprint).
4. Política: PRs com NetworkPolicy exigem aprovação de SRE (plataforma, imediato).
5. Revisão trimestral do catálogo de alertas para podar ruído (SRE, próximos 3 meses).

## Não-aprendizados
Este postmortem **não** atribui culpa ao engenheiro que aplicou o NP.
O sistema permitiu que a mudança fosse feita sem validação ponta-a-ponta,
e o monitoramento não capturou o efeito. São falhas do sistema, não da pessoa.
```

### 4.5.3 Regra dos "3 porquês" (Toyota)

Para cada "por que isso aconteceu?", faça a pergunta de novo. A 3ª resposta geralmente aponta o problema sistêmico:

1. **Por que os pedidos sumiram?** NetworkPolicy bloqueou egresso.
2. **Por que ninguém notou antes?** Alerta existente foi ignorado por fadiga.
3. **Por que havia fadiga?** Catálogo de alertas nunca foi revisado, apesar de 87% de falsos positivos.

Ação: revisar catálogo trimestralmente.

---

## 4.6 Cultura on-call sustentável

> Observabilidade é **técnica**. On-call é **humana**.

### 4.6.1 Princípios

- **Rodízio**: ninguém sozinho. Primário + secundário. Revezar semanalmente.
- **Limite**: no máximo 1 semana/mês em plantão noturno; recuperação paga (compensação ou folga).
- **Protege quem está fora**: plantonista não é dono do bug; é quem mitiga.
- **Learnings circulam**: toda semana, 30 min de "o que aconteceu no plantão", aberto.
- **Baseline de saúde**: < 2 pages / semana é aceitável; > 5 é crise.

### 4.6.2 Práticas que ajudam

- **Onboarding de plantonista**: antes de entrar na escala, shadow (3 plantões acompanhando), reverse-shadow (plantonista responde, senior acompanha), só então solo.
- **Game days mensais**: simule falhas (NetworkPolicy quebrada, pod OOM, DNS lento) e meça resposta.
- **Catálogo de runbooks** mantido e testado.
- **Retrospectiva de alertas**: quais alertas mais dispararam esta semana? Vale a pena mantê-los?

### 4.6.3 Anti-padrões

- **Heróis**: pessoa X "resolve tudo". O sistema está frágil; o herói é vulnerabilidade.
- **"Vamos manter silenciado"**: um silence Alertmanager esquecido por meses.
- **Plantão sem compensação**: esgota equipe, vira churn.
- **Plantonista vira "responsável pelo bug"**: incentivo perverso; ninguém quer entrar na escala.

---

## 4.7 CI para observabilidade

Toda regra, dashboard e runbook vira **código**. Portanto, entram no pipeline.

### 4.7.1 Validar `PrometheusRule`s

```bash
# instalar promtool (junto com prometheus release)
promtool check rules ./k8s/prometheusrules/*.yaml
```

### 4.7.2 Teste unitário de alertas

Sim, alertas têm **teste unitário** — via `promtool test rules`:

```yaml
# tests/alerts_test.yaml
rule_files:
  - ../k8s/prometheusrules/pedidos-slo.yaml

evaluation_interval: 1m

tests:
  - interval: 1m
    input_series:
      - series: 'http_requests_total{service="pedidos", status="200"}'
        values: '100 200 300 400 500 600 700 800 900 1000 1100 1200'
      - series: 'http_requests_total{service="pedidos", status="500"}'
        values: '0 0 0 0 0 0 0 5 15 25 40 60'
    alert_rule_test:
      - eval_time: 10m
        alertname: PedidosSLOBurnRateFast
        exp_alerts:
          - exp_labels:
              severity: critical
              slo: pedidos-availability
            exp_annotations:
              summary: "Pedidos queimando 14.4x o budget (5m e 1h)"
              runbook_url: "https://runbooks.logisgo/pedidos-slo-burn-fast"
```

Rodar:

```bash
promtool test rules tests/alerts_test.yaml
```

### 4.7.3 Pipeline GitHub Actions

```yaml
# .github/workflows/observability.yml
name: observability-ci

on:
  pull_request:
    paths:
      - 'k8s/prometheusrules/**'
      - 'grafana/dashboards/**'
      - 'tests/**'

jobs:
  validar:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup promtool
        run: |
          PROM_VER=2.54.1
          curl -L https://github.com/prometheus/prometheus/releases/download/v$PROM_VER/prometheus-$PROM_VER.linux-amd64.tar.gz | tar xz
          sudo install prometheus-$PROM_VER.linux-amd64/promtool /usr/local/bin/

      - name: Lint regras
        run: promtool check rules k8s/prometheusrules/*.yaml

      - name: Testes unitarios de alertas
        run: promtool test rules tests/*.yaml

      - name: Valida JSON dos dashboards
        run: |
          for f in grafana/dashboards/*.json; do
            python -m json.tool "$f" > /dev/null
          done
```

---

## 4.8 Script Python: `alerts_sanity.py`

O script lê um arquivo de `PrometheusRule` e aplica sanity checks:

- Alerta tem `summary`, `description`, `runbook_url`?
- Severidade é uma das aceitas?
- O `for:` é razoável (≥ 1m, ≤ 1h)?
- Existe `Watchdog`?

```python
"""
alerts_sanity.py - sanity check de PrometheusRule para higiene de alertas.

Uso:
    python alerts_sanity.py k8s/prometheusrules/*.yaml

Retorna codigo de saida != 0 se qualquer violacao for encontrada.
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from dataclasses import dataclass
from typing import Iterable

import yaml

SEVERIDADES = {"critical", "warning", "info"}
CAMPOS_ANNOT_OBRIGATORIOS = {"summary", "description", "runbook_url"}
FOR_MIN_MIN = 1
FOR_MAX_H = 1


@dataclass(frozen=True)
class Achado:
    arquivo: str
    alerta: str
    severidade: str
    motivo: str


def _for_em_minutos(texto: str) -> int:
    if not texto:
        return 0
    m = re.match(r"^(\d+)([smhd])$", texto.strip())
    if not m:
        return 0
    n, u = int(m.group(1)), m.group(2)
    mult = {"s": 1 / 60, "m": 1, "h": 60, "d": 1440}[u]
    return int(n * mult)


def auditar_arquivo(path: str) -> Iterable[Achado]:
    with open(path, "r", encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    if not doc or doc.get("kind") != "PrometheusRule":
        return
    groups = (doc.get("spec") or {}).get("groups") or []
    for grp in groups:
        for rule in grp.get("rules", []):
            alerta = rule.get("alert")
            if not alerta:
                continue
            labels = rule.get("labels", {}) or {}
            annots = rule.get("annotations", {}) or {}
            sev = labels.get("severity", "") or ""
            if sev not in SEVERIDADES:
                yield Achado(path, alerta, sev, f"severidade invalida ou ausente ({sev!r})")
            faltando = CAMPOS_ANNOT_OBRIGATORIOS - set(annots)
            if faltando:
                yield Achado(path, alerta, sev, f"annotation(s) faltando: {sorted(faltando)}")
            for_min = _for_em_minutos(rule.get("for", ""))
            if for_min and (for_min < FOR_MIN_MIN or for_min > FOR_MAX_H * 60):
                yield Achado(path, alerta, sev, f"campo 'for' fora do intervalo razoavel: {rule.get('for')}")


def tem_watchdog(paths: list[str]) -> bool:
    for p in paths:
        with open(p, "r", encoding="utf-8") as fh:
            doc = yaml.safe_load(fh) or {}
        groups = (doc.get("spec") or {}).get("groups") or []
        for grp in groups:
            for rule in grp.get("rules", []):
                if rule.get("alert") == "Watchdog":
                    return True
    return False


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Sanity check de PrometheusRule")
    p.add_argument("paths", nargs="+", help="arquivos YAML (ou globs)")
    args = p.parse_args(argv)

    arquivos: list[str] = []
    for padrao in args.paths:
        arquivos.extend(glob.glob(padrao))
    if not arquivos:
        print("ERRO: nenhum arquivo encontrado", file=sys.stderr)
        return 2

    achados: list[Achado] = []
    for f in arquivos:
        achados.extend(auditar_arquivo(f))

    if not tem_watchdog(arquivos):
        achados.append(Achado("(global)", "Watchdog", "info", "nenhuma regra Watchdog encontrada"))

    for a in achados:
        print(f"[{a.severidade or '-'}] {a.arquivo}::{a.alerta} -> {a.motivo}")

    print(f"\nTotal achados: {len(achados)}")
    return 0 if not achados else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 4.9 Checklist do bloco

- [ ] Reconheço as 5 propriedades de um alerta saudável (actionable, urgent, etc.).
- [ ] Modelo alertas SLO-based com multi-window burn rate.
- [ ] Configuro Alertmanager com rotas, agrupamento, inibição, silence.
- [ ] Escrevo runbooks executáveis, versionados e linkados do alerta.
- [ ] Conduzo postmortem sem culpa com timeline e ações concretas.
- [ ] Sustento on-call com rodízio, limites e game days.
- [ ] Valido regras em CI com `promtool check rules` e `promtool test rules`.
- [ ] Uso `alerts_sanity.py` para higiene contínua.

Vá aos [exercícios resolvidos do Bloco 4](./04-exercicios-resolvidos.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Exercícios resolvidos](../bloco-3/03-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Bloco 4 — Exercícios resolvidos](04-exercicios-resolvidos.md) |

<!-- nav:end -->

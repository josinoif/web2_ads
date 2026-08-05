# Bloco 4 — Exercícios resolvidos

Fundamentos: [04-alertas-slo-cultura.md](./04-alertas-slo-cultura.md).

---

## Exercício 1 — Revisar catálogo de alertas

**Enunciado.** A LogisGo tem 28 alertas ativos. Ao revisar, você encontra:

1. `HighCpuNodeUsage` — CPU do node > 80% por 5 min (dispara 40× por semana).
2. `PodRestart` — qualquer restart de pod (dispara 200× por semana).
3. `HttpErrorRate` — `rate(http_requests_total{status=~"5.."}[1m]) > 0` (dispara sempre).
4. `PedidosDown` — `up{job="pedidos"} == 0` por 2 min.
5. `RabbitMQBacklog` — `rabbitmq_queue_messages_ready > 10000` por 5 min.
6. `DiskFull` — `node_filesystem_avail_bytes / node_filesystem_size_bytes < 0.05`.

Classifique cada um (manter/ajustar/remover) e justifique.

**Resposta.**

| # | Decisão | Justificativa |
|---|---------|---------------|
| 1 | **Remover** | CPU alta sem correlação com usuário = ruído. Substituir por alertas SLO-based (que capturam degradação **percebida**). |
| 2 | **Remover** | Restart único é esperado (K8s faz rolling update). Substituir por `ContainerCrashLoopBackOff` (estado persistente). |
| 3 | **Ajustar** | `>0` é absurdo. Deve ser razão, janela maior, e SLO-based. Ex.: `rate 5xx / rate total > 2%` por 10 min. |
| 4 | **Manter** (ajustar `for: 5m`) | Detecta indisponibilidade real. 2 min é agressivo — pode ser rolling update em curso; 5 min dá folga sem perder incidente. |
| 5 | **Manter** (adicionar severidade e runbook) | Backlog crescendo é sintoma real. Assegure-se de ter runbook para "escale consumers". |
| 6 | **Manter** (ajustar `for`) | Disco cheio é ação clara. Ajuste `for: 10m` (variações de rollover de log são normais). |

Diretrizes gerais demonstradas: priorizar sintoma **percebido pelo usuário**, remover sinais sem ação clara, sempre casar com runbook.

---

## Exercício 2 — Derivar burn rate de um SLO concreto

**Enunciado.** Serviço `rotas`, SLO 99,5% em 28 dias. Calcule:

1. Budget total em eventos ruins permitidos, assumindo 10 req/s.
2. Threshold de burn rate para consumir **todo** o budget em **1 hora**.
3. Threshold para consumir em **6 horas**.
4. Como expressaria as duas condições em PromQL?

**Resposta.**

1. Total de requests em 28d: `10 × 86.400 × 28 ≈ 24.192.000`. Budget: `0,5% × 24.192.000 ≈ 120.960` erros.
2. 1 hora = `1 / (28 × 24) ≈ 0,149%` do tempo total. Para consumir 100% em 1h, taxa de erro precisa ser `1 / 0,149% ≈ 672×` a taxa normal… mas normalmente se trabalha com burn rate relativo ao `(1 - SLO) = 0,005`. Para "queimar tudo em 1h": a taxa de erro precisa ser **`28 × 24 = 672`**× o `(1 - SLO)`. Em valores absolutos: taxa de erro `≈ 672 × 0,005 = 3,36` — inviável (>100%). Na prática, Google usa ~14.4 para "rápido" porque quer atuar **antes** de consumir tudo, ainda dentro do budget.
   - **Para 100% em 1h em SLOs mais elásticos (99%)**: burn rate 672; para 100% em um **período mais realista (2h)**: burn rate 336; para uso prático (Google): **14.4** → consome ~2% do budget em 1h.
3. Análogo. Para 100% em 6h: `28 × 24 / 6 = 112`. Uso prático: **6** (Google receita).
4. PromQL:
   ```promql
   # rápido (14.4x)
   (
     sum(rate(http_requests_total{service="rotas", status=~"5.."}[5m]))
     /
     sum(rate(http_requests_total{service="rotas"}[5m]))
   ) > 14.4 * (1 - 0.995)
   AND
   (
     sum(rate(http_requests_total{service="rotas", status=~"5.."}[1h]))
     /
     sum(rate(http_requests_total{service="rotas"}[1h]))
   ) > 14.4 * (1 - 0.995)

   # lento (6x)
   (
     sum(rate(...[30m])) / sum(rate(...[30m]))
   ) > 6 * (1 - 0.995)
   AND
   (
     sum(rate(...[6h])) / sum(rate(...[6h]))
   ) > 6 * (1 - 0.995)
   ```

Observação pedagógica: 14.4 e 6 são escolhas da receita Google (SRE Workbook cap. 5). Você pode escolher outros números, mas mantenha o **princípio**: duas janelas, duas taxas, evitar falsos positivos em picos curtos.

---

## Exercício 3 — Roteamento no Alertmanager

**Enunciado.** Projete uma `route:` que:

- Envia `severity=critical` para `receiver=oncall-pager` fora de horário comercial E receiver `critical-chat` sempre.
- Envia `severity=warning` para `receiver=tickets`.
- Envia `severity=info` apenas para Slack `#obs-logs` com `repeat_interval: 12h`.
- Nunca silencia o `Watchdog`.

Rascunhe em YAML.

**Resposta.**

```yaml
route:
  group_by: ['service', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: default

  routes:
    - matchers: [alertname="Watchdog"]
      receiver: watchdog
      repeat_interval: 5m
      continue: false

    - matchers: [severity="critical"]
      receiver: critical-chat
      continue: true
      routes:
        - active_time_intervals: [fora-comercial]
          receiver: oncall-pager

    - matchers: [severity="warning"]
      receiver: tickets
      repeat_interval: 12h

    - matchers: [severity="info"]
      receiver: slack-obs-logs
      repeat_interval: 12h

time_intervals:
  - name: fora-comercial
    time_intervals:
      - weekdays: ['monday:friday']
        times:
          - start_time: '18:01'
            end_time: '23:59'
          - start_time: '00:00'
            end_time: '07:59'
      - weekdays: ['saturday', 'sunday']
```

Notas: `continue: true` permite fluir para a próxima rota. `active_time_intervals` é o mecanismo moderno (AM ≥ 0.24). O Watchdog fica na primeira rota para **nunca** ser engolido por outra regra.

---

## Exercício 4 — Escrever runbook

**Enunciado.** Escreva um runbook para o alerta `PedidosHighErrorRate` (descrito no Bloco 2), seguindo o template do Bloco 4. Inclua ao menos 3 passos de diagnóstico e 2 ações prováveis.

**Resposta.**

```markdown
# Runbook — PedidosHighErrorRate

**Alerta:** `PedidosHighErrorRate`
**Severidade:** warning
**Dono:** squad Orders
**Última revisão:** 2026-04-21

## O que significa

Taxa de erro 5xx do serviço `pedidos` ficou acima de 2% por pelo menos
10 minutos. Ainda não é violação aguda de SLO, mas sinaliza degradação
visível para clientes B2B.

## Impacto

A cada 100 pedidos, 2+ retornam erro. Clientes grandes (Zaffrán, FarmaExpress)
costumam reportar rapidamente.

## Diagnóstico

1. **Dashboard RED — pedidos**:
   - Qual rota concentra os 5xx? (`/orders` POST vs. `/orders/:id` GET?)
   - É pico ou sustentado?

2. **Traces em Tempo**:
   `{ service.name = "pedidos" && status = error }`
   Qual span falha? db, rabbitmq, chamada externa?

3. **Logs em Loki**:
   `{app="pedidos"} | json | level="ERROR" [15m]`
   Agrupe por `error_type`. Uma mensagem domina?

4. **Deploys recentes**:
   `argocd app history pedidos` — há mudança nas últimas 2h?

## Ações prováveis

| Diagnóstico | Ação |
|-------------|------|
| Erro concentrado em rota de criação + exceção DB | `kubectl rollout undo deployment/pedidos` se coincidir com deploy recente; senão, checar `postgres_pool_connections_active`. |
| Backlog RabbitMQ alto | Escalar `notificacoes` (HPA deveria, mas se HPA travou, `kubectl scale`). |
| Erro em chamada a `estoque` | Abrir incident cross-team com squad Inventory. Ativar fallback se existir. |
| Pico isolado sem padrão claro | Monitorar 10 min; se não reincidir, fechar com nota. |

## Escala

- Se em 30 min persistir, subir para `critical` e envolver oncall de plataforma.
- Se burn rate acelerar, o alerta `PedidosSLOBurnRateFast` disparará automaticamente.

## Pós-evento

- Registrar em `logisgo/incidents` o que foi mudado.
- Revisar se este runbook precisa de novo caso ("Diagnóstico X → Ação Y").
```

---

## Exercício 5 — Postmortem a partir de fatos

**Enunciado.** A LogisGo teve um incidente no dia 2026-05-03, 02:14–03:07, em que a API retornou 503 em 100% dos requests. Causa: certificado TLS do Ingress expirou, e o `cert-manager` estava com CRD errado desde 15 dias antes. Plantonista Júnior ligou para o CTO às 02:40.

Escreva o postmortem em tom blameless, incluindo timeline, causa-raiz técnica e sistêmica, e 3 ações.

**Resposta.**

```markdown
# Postmortem — TLS expirado em 2026-05-03

**Severidade:** P1
**Duração:** 53 min (02:14 → 03:07)
**Autor:** Plantonista Júnior (com apoio Alice Souza)
**Revisão blameless:** 2026-05-06 com Orders + Plataforma

## Resumo executivo
O certificado TLS do Ingress de produção expirou às 02:14. Retornos 503
em 100% dos requests até renovação manual às 03:07. Cliente detectou
antes do alerta interno chegar ao plantão por Slack.

## Impacto
- ~4.800 requisições falhadas.
- 6 clientes reportaram via chat; 2 com contratos críticos.

## Timeline
| Horário | Evento |
|---------|--------|
| 02:14 | Certificado expira; Ingress começa a retornar 503. |
| 02:17 | Alertmanager dispara `IngressReturning5xx` (canal Slack `#alerts-low`). |
| 02:35 | Cliente Zaffrán reporta no chat. |
| 02:40 | Plantonista Júnior é acionado por Slack privado. |
| 02:42 | Plantonista Júnior liga para CTO. |
| 02:52 | CTO + plantonista identificam certificado expirado. |
| 02:58 | Tentativa de renovar via `cert-manager` falha — CRD incompatível. |
| 03:02 | Renovação manual com `certbot`. |
| 03:07 | Serviço normalizado. |

## Causa-raiz
- **Técnica**: Certificado wildcard expirou e `cert-manager` não renovou
  porque sua CRD estava em versão v1alpha2 descontinuada.
- **Sistêmica**:
  1. Alerta `CertExpiryWarning` existia, porém roteado para canal de baixa
     prioridade (`#alerts-low`) há 6 meses; plantonista não monitora esse canal.
  2. Upgrade de `cert-manager` de 2024 não foi testado em staging.
  3. Não há dashboard para "coisas que vão expirar em 30 dias" (DB licenses,
     certs, chaves API).

## O que correu bem
- Quando acionado, o plantonista conseguiu diagnosticar em 12 min.
- Rollback manual foi rápido graças à documentação do `certbot`.

## O que correu mal
- Alerta de expiração em canal errado = funcionalmente inexistente.
- Dependência crítica (cert-manager) sem teste.
- Time descobriu pelo cliente, não pelo monitoramento.

## Ações
1. **Mover `CertExpiryWarning` para rota de severidade `critical` com `for: 1h`**
   (Plataforma, próximo sprint).
2. **Criar dashboard "Renovações e expirações próximas"** (Plataforma, 2 sprints).
3. **Incluir `cert-manager` em game day mensal** (SRE, contínuo).

## Não-aprendizados
- Esta não é falha do plantonista júnior; ele agiu no que tinha.
- O sistema permitiu que um alerta crítico fosse roteado para um canal
  negligenciado — responsabilidade de governança do catálogo.
```

---

## Exercício 6 — Validar regras no CI

**Enunciado.** Você tem três arquivos `PrometheusRule` em `k8s/prometheusrules/`:
- `pedidos.yaml`
- `infra.yaml`
- `watchdog.yaml`

Algum deles tem `for: 30s` (abaixo do mínimo razoável). Qual comando do script `alerts_sanity.py` (do Bloco 4) detecta isso? E como você integraria no pipeline CI (exemplo completo de step)?

**Resposta.**

**Execução local:**

```bash
python bloco-4/alerts_sanity.py k8s/prometheusrules/*.yaml
```

Saída esperada (exemplo):
```
[critical] k8s/prometheusrules/pedidos.yaml::PedidosInstantDown -> campo 'for' fora do intervalo razoavel: 30s

Total achados: 1
```

O script retorna `exit 1`, o que faz o step do CI falhar.

**Step no GitHub Actions:**

```yaml
jobs:
  observability:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Instalar dependências do auditor
        run: pip install pyyaml

      - name: Sanity check de alertas
        run: python devops/08-observabilidade/bloco-4/alerts_sanity.py k8s/prometheusrules/*.yaml
```

Combine com `promtool check rules` e `promtool test rules` para cobertura dupla (sintaxe + lógica + higiene).

---

## Autoavaliação

- [ ] Classifico alertas em manter/ajustar/remover usando as 5 propriedades.
- [ ] Derivo thresholds de burn rate a partir de um SLO concreto.
- [ ] Configuro rotas Alertmanager por severidade, janela e Watchdog protegido.
- [ ] Escrevo runbook executável ligando diagnóstico a ação.
- [ ] Conduzo postmortem blameless com timeline, causa-raiz técnica e sistêmica, ações.
- [ ] Integro validação de regras em CI (`promtool` + `alerts_sanity.py`).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Alertas, SLO-based alerting, runbooks e cultura on-call](04-alertas-slo-cultura.md) | **↑ Índice**<br>[Módulo 8 — Observabilidade](../README.md) | **Próximo →**<br>[Exercícios Progressivos — Módulo 8 (Observabilidade)](../exercicios-progressivos/README.md) |

<!-- nav:end -->

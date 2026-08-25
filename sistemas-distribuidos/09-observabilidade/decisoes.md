# Workshop de decisões — Observabilidade

**Módulo:** [09](README.md)  
Faça depois da [teoria](teoria.md) e, de preferência, do [lab de logs](tutorial-logs-agregados.md).  
Termos: [glossario.md](glossario.md).

---

## Como usar

Para cada cenário:

1. Escreva a **abordagem** (ex.: “Loki + trace_id”, “só Prometheus”, “APM SaaS”).  
2. Liste **2 vantagens** e **2 custos/riscos**.  
3. Diga o que você **monitoraria** (métrica, log ou trace).  
4. (Opcional) Compare com um colega — o desacordo é o exercício.

| Critério | Pergunta rápida |
|----------|-----------------|
| Nº de serviços | 1 processo ou N hops? |
| Pergunta | Tendência, caminho ou detalhe? |
| Custo | RAM do lab / fatura SaaS / cardinalidade |
| Maturidade do time | Aguenta operar stack ou prefere SaaS? |

> **Não abra o gabarito agora.** Espelho enxuto só **depois**: [decisoes-gabarito.md](decisoes-gabarito.md).

---

## Cenário 1 — Portal no dia da entrega

120 alunos enviam prova entre 22h e 23h59. Há gateway, análise e store ([01](../01-comunicacao/)). Um aluno liga: “enviei às 23h50 e não veio recibo”. Ops tem SSH nos três containers. O `/health` do gateway está 200.

**Perguntas**

1. Só `docker logs` resolve na pressa?  
2. O que muda com logs estruturados + `trace_id` + Loki?  
3. Depois do lab A: o que o Exp. sem propagação e o Exp. de health mentiroso mostraram?

---

## Cenário 2 — Startup com dois serviços

Time de 3 pessoas. “Precisamos de Datadog já” vs “sobe Grafana no Compose”.

**Perguntas**

1. Quando SaaS APM vale o custo?  
2. O que o lab B cobre com Grafana+OTel — e o que ainda falta (alertas 24/7, retenção)?  
3. Instrumentar com OTel agora ajuda a trocar de backend depois?

---

## Cenário 3 — Alertar CPU ou erro de negócio?

NOC quer alerta de CPU do host. Produto quer saber se `POST /provas` falha.

**Perguntas**

1. Qual alarme acorda alguém às 3h?  
2. Relacione com Golden Signals / RED.  
3. Onde SLO entra (mesmo sem Alertmanager neste módulo)?

---

## Cenário 4 — Trace 100% vs amostragem

Compliance pede “guardar tudo”. FinOps reclama da fatura de traces.

**Perguntas**

1. Quando 100% faz sentido (lab, baixo QPS)?  
2. O que se perde com 1% de sampling?  
3. Logs com `trace_id` compensam parte da amostragem?

---

## Cenário 5 — Label `aluno_id` na métrica

Alguém propõe `provas_total{aluno_id=...}` para “gráfico por aluno”.

**Perguntas**

1. O que acontece com a cardinalidade?  
2. Onde esse dado deveria viver (log/trace)?  
3. Depois do lab B: o que o Exp./aviso de cardinalidade reforçou?

---

## Cenário 6 — Falha só em um campus

Latência boa no agregado; alunos do campus B reclamam.

**Perguntas**

1. Métrica global esconde o quê?  
2. Que dimensões (labels / campos de evento) ajudam sem explodir cardinalidade?  
3. Relacione com “unknown unknowns” da [teoria §2](teoria.md).

---

## Cenário 7 — Fronteira com plataforma

Time de app quer Prometheus no notebook de cada dev. Time de plataforma oferece stack no cluster.

**Perguntas**

1. O que o módulo 09 treina vs [`devops/08`](../../devops/08-observabilidade/)?  
2. O que a app **deve** expor de qualquer forma (independente da plataforma)?

---

## Rubrica rápida

| Nível | Evidência |
|-------|-----------|
| Fraco | Só nomeia ferramenta (“usa Datadog”) |
| Ok | Liga pergunta → sinal (métrica/log/trace) + 1 trade-off |
| Forte | Inclui correlação, cardinalidade ou custo + o que faria no lab |

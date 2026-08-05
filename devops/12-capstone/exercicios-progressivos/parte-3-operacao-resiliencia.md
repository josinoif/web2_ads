# Marco 3 — Sistema observável e resiliente

**Tag alvo:** `v0.3.0-operable`.
**Tempo sugerido:** 3 semanas.
**Fase correspondente:** [Fase 3](../bloco-3/03-fase-operacao.md) + [armadilhas](../bloco-3/03-armadilhas-e-dicas.md).

---

## Objetivo

Transformar o sistema que "roda" num sistema **visível, defensável e testado sob stress**. Métricas, logs e traces fluindo; SLOs declarados; segurança endurecida; 1 experimento chaos real; backup + restore testados.

---

## Entregáveis

### Observability
- [ ] `/metrics` Prometheus exposto; scrape funcional.
- [ ] Logs JSON com `trace_id` em API e worker.
- [ ] Traces OpenTelemetry → Tempo/Jaeger, com propagação correta.
- [ ] SLIs/SLOs publicados em `docs/slos.md`.
- [ ] Error Budget Policy em `docs/ebp.md`.
- [ ] ≥ 3 dashboards Grafana (execução/golden/saúde).
- [ ] ≥ 3 alertas SLO-based com `runbook_url`.

### Segurança
- [ ] Threat model STRIDE em `docs/security/threat-model.md`.
- [ ] Admission control Kyverno com ≥ 2 policies `enforce`.
- [ ] Secrets via Sealed Secret ou External Secrets.
- [ ] Controles LGPD implementados: inventário atualizado, consentimento, endpoint de direitos, anonimização de logs.
- [ ] Runbook security-incident.md.

### SRE
- [ ] ≥ 1 experimento chaos com hipótese/steady state/resultado documentado em `chaos/experimento-01.md`.
- [ ] Velero agendado + restore em namespace alternativo testado e documentado.
- [ ] DR playbook em `docs/runbooks/dr-cluster-perdido.md` com RPO/RTO medidos.
- [ ] ≥ 3 runbooks em `docs/runbooks/`.
- [ ] Política on-call em `docs/on-call.md`.
- [ ] Postmortem template em `docs/postmortems/_TEMPLATE.md`.
- [ ] ≥ 1 postmortem real/simulado registrado.

### Evidências
- [ ] Retrospectiva em `docs/retro/marco3.md`.
- [ ] `CHANGELOG.md` com `v0.3.0`.
- [ ] Tag `v0.3.0-operable`.

---

## Demonstração esperada

Na defesa parcial deste marco, você consegue em ≤ 5 min:

1. Abrir dashboard → apontar SLO atual e budget restante.
2. Fazer um request real; achar o trace; abrir correspondente log (ligados por `trace_id`).
3. Disparar experimento chaos (Pod kill); ver alerta; abrir runbook; mitigar.
4. Mostrar backup Velero recente + log do último restore drill.

Fique de olho: esta é a fase em que o projeto **parece mais próximo de produto**.

---

## Critérios de avaliação deste marco

| Item | Peso local |
|------|------------|
| Três pilares instrumentados + correlacionados | 20% |
| SLOs + EBP operantes | 15% |
| Alertas SLO-based com runbook | 10% |
| Threat model STRIDE | 10% |
| Kyverno + LGPD controles | 15% |
| Chaos experiment com resultado honesto | 10% |
| Backup + restore drill | 10% |
| Runbooks testáveis | 5% |
| Retrospectiva | 5% |

---

## Armadilhas comuns

- Dashboard lindo mas **ninguém usa**.
- SLO sem EBP — ou EBP sem ações.
- Alerta page sem runbook vinculado.
- Chaos sem hipótese escrita — apenas sabotagem.
- Backup sem restore testado.
- Threat model que não mudou nada no sistema.
- LGPD "vemos depois".
- Postmortem que culpa pessoa.

---

## Antes de fechar o marco

Sanity checks que **você** faz:

1. Em qual dashboard você vê "impacto de um deploy" nos últimos 10 min?
2. Quanto budget você tem nesta janela?
3. Se a foto de um cidadão for perdida, em quanto tempo você a recupera? (RPO/RTO de storage de mídia.)
4. Se um dev pede "remover meus dados" (LGPD), quais **comandos** você roda?

Se sabe responder as quatro sem consultar, Marco 3 está pronto.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Marco 2 — Sistema entregando em staging](parte-2-entrega-end-to-end.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Marco 4 — Plataforma interna e métricas](parte-4-plataforma-metricas.md) |

<!-- nav:end -->

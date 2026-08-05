# Entrega avaliativa — Módulo 10 (SRE e Operações)

**Peso:** 20% da nota final da disciplina (ajuste conforme seu plano pedagógico).
**Formato:** repositório Git (pode ser o mesmo da entrega do Módulo 8/9) com código, manifestos, runbooks, experimentos e documentos.
**Prazo sugerido:** ao final da semana do módulo.
**Base:** cluster k3d (com observabilidade do Módulo 8 e segurança do Módulo 9) ou o projeto **PagoraPay-mini** descrito nos exercícios.

---

## Objetivo

Demonstrar que você é capaz de **operar** um sistema em Kubernetes com disciplina SRE: SLOs acionáveis, toil controlado, capacidade monitorada, resiliência **validada por experimento**, DR **exercitado de verdade**, incidentes **comandados** e postmortems que **mudam o sistema**.

---

## Produto final

O repositório deve conter:

1. **Documento de SLOs + Error Budget Policy** (`docs/slo-policy.md`):
   - ≥ 3 SLOs com SLIs, janelas e racional.
   - Política com **gatilhos acionáveis** em 3 níveis (verde / amarelo / vermelho), decisões pré-acordadas e escalamento.
2. **Toil tracker** operacional:
   - `docs/toil.md` — taxonomia, metodologia de medição, toil budget adotado.
   - Planilha/CSV (`data/toil-log.csv`) com 2+ semanas de registros.
   - Uso de `toil_tracker.py` para relatório.
3. **Capacity planning**:
   - `docs/capacity.md` — headroom alvo, limites atuais, plano de ação.
   - Dashboard Grafana provisionado com saturação e previsão (pode reusar do Módulo 8).
4. **Programa de Chaos Engineering**:
   - Chaos Mesh instalado no cluster.
   - ≥ 3 experimentos em `chaos/` com: hipótese, blast radius, critério de abortar, aprendizado.
   - Pelo menos 1 foi um **game day** documentado em `docs/game-days/`.
   - `chaos_plan.py` valida um experimento antes de aplicar.
5. **Disaster Recovery real**:
   - Velero instalado e configurado com storage local (MinIO ou file-backed).
   - Backup agendado, restore ensaiado em cluster alternativo (ou namespace alternativo).
   - `docs/dr-playbook.md` com cenários, RPO/RTO **medidos**, comunicação.
   - `dr_simulator.py` usado para planejar cenários.
6. **Incident Command System**:
   - `docs/incident-command.md` com papéis (IC, Ops, Comms, Scribe), severidades, comunicação.
   - ≥ 1 **tabletop** (exercício de mesa) documentado.
   - `docs/runbooks/` com ≥ 5 runbooks operacionais vivos (cada um exercitado).
7. **Postmortem e aprendizado**:
   - ≥ 2 postmortems reais (podem derivar dos chaos experiments ou game days) com timeline, contributing factors, ações com dono/prazo/verificação.
   - `docs/learning-review.md` — revisão organizacional trimestral (template + exemplo preenchido).
   - `incident_timeline.py` usado para construir timeline a partir de eventos.
8. **On-call sustentável**:
   - `docs/on-call.md` — política com rotação, limites, compensação, game days periódicos.
9. **Makefile** com alvos: `slo-check`, `toil-report`, `chaos-run`, `dr-backup`, `dr-restore`, `tabletop`.

---

## Rubrica de avaliação (100 pts)

| Eixo | Peso | Critérios principais |
|------|------|----------------------|
| **SLOs e Error Budget Policy** | 15 | SLOs refletem cliente; policy tem ações, não só aspirações |
| **Toil tracking** | 10 | Medição real; budget definido; plano de eliminação com prioridade |
| **Capacity planning** | 10 | Headroom explícito; saturação monitorada; previsão documentada |
| **Chaos Engineering** | 20 | 3 experimentos com hipótese + blast radius + abort + aprendizado; 1 game day |
| **Disaster Recovery** | 20 | Restore de verdade validado; RPO/RTO **medidos** (não só alvos); playbook testado |
| **Incident Command + Runbooks** | 15 | ICS adotado; tabletop documentado; runbooks vivos |
| **Postmortem e aprendizado** | 10 | Blameless; ações acionadas; revisão organizacional |

### Bônus (até +10 pts, não compensam faltas)

- Integração com PagerDuty/Opsgenie (trial) para rotação de on-call real.
- Dashboard Grafana de **confiabilidade global** (SLO burn + toil + MTTR + frequência de deploy).
- Automação da execução de experimentos no CI noturno.
- Uso de **Litmus Chaos** além do Chaos Mesh para comparar.
- Política de **Just Culture** documentada com exemplos.

---

## Formato de entrega

1. Link do repositório.
2. README na raiz com:
   - Arquitetura operacional do projeto.
   - Dashboard global (print).
   - Como rodar chaos (`make chaos-run EXPERIMENT=pod-kill-pix-core`).
   - Como rodar DR (`make dr-backup && make dr-restore`).
   - Link para cada documento principal.
3. Para bancas presenciais: gravação ≤ 12 min **executando**:
   - Mostra SLO em Grafana e explica o budget atual.
   - Mostra um experimento de chaos rodando + hipótese confirmada/refutada.
   - Mostra restore Velero entre namespaces com dados reais.
   - Mostra um tabletop de 3 min com papéis declarados.

---

## Checklist rápido antes de entregar

- [ ] `docs/slo-policy.md` contém pelo menos 3 ações automáticas diferentes por gatilho.
- [ ] `data/toil-log.csv` tem registros reais (≥ 2 semanas).
- [ ] Dashboard Grafana mostra saturação do DB **e** previsão linear.
- [ ] `chaos/` tem 3 experimentos versionados; cada um tem `README.md` com hipótese.
- [ ] Velero restaurou um namespace num cluster/namespace alternativo **e** foi validado com healthcheck.
- [ ] RPO e RTO medidos estão no playbook — não só alvos.
- [ ] Ao menos 2 postmortems seguem template e têm ações acompanhadas.
- [ ] Tabletop tem ata, papéis declarados, aprendizado registrado.
- [ ] Runbooks têm timestamp da última execução (mostrando que são vivos).
- [ ] On-call policy inclui **limite** (ex.: ≤ 2 paging fora de horário/sem.) com ação quando ultrapassa.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Postmortem Blameless e Learning Review](exercicios-progressivos/parte-5-postmortem-learning.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](README.md) | **Próximo →**<br>[Referências — Módulo 10 (SRE e Operações)](referencias.md) |

<!-- nav:end -->

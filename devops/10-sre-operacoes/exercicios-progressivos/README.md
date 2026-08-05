# Exercícios progressivos — Módulo 10 (SRE e Operações)

Série de 5 atividades **encadeadas** que constroem uma operação SRE completa para a PagoraPay, a partir do cenário caótico do [00-cenario-pbl.md](../00-cenario-pbl.md).

Cada parte gera artefato versionado no repositório e base para a seguinte.

---

## Sequência

| Parte | Tema | Arquivo |
|-------|------|---------|
| 1 | SLOs, Error Budget Policy e toil tracker | [parte-1-slo-toil.md](parte-1-slo-toil.md) |
| 2 | Programa de Chaos Engineering com Chaos Mesh | [parte-2-chaos-engineering.md](parte-2-chaos-engineering.md) |
| 3 | DR real com Velero e DR Game Day | [parte-3-dr-velero.md](parte-3-dr-velero.md) |
| 4 | Incident Command e Tabletop | [parte-4-incident-command.md](parte-4-incident-command.md) |
| 5 | Postmortem blameless e Learning Review | [parte-5-postmortem-learning.md](parte-5-postmortem-learning.md) |

---

## O que você vai construir ao final

```
pagorapay-sre/
├── Makefile
├── docs/
│   ├── slo-policy.md              # Parte 1
│   ├── toil.md
│   ├── capacity.md
│   ├── chaos/                     # Parte 2
│   │   ├── experiment-1.md
│   │   ├── experiment-2.md
│   │   └── experiment-3.md
│   ├── game-days/
│   │   └── 2026-04-20-chaos.md
│   ├── dr-playbook.md             # Parte 3
│   ├── runbooks/                  # Parte 3 e 4
│   │   ├── dr-cluster-lost.md
│   │   ├── db-slow.md
│   │   └── redis-flush.md
│   ├── incident-command.md        # Parte 4
│   ├── on-call.md
│   ├── postmortem-<N>.md          # Parte 5
│   └── learning-review-Q1.md      # Parte 5
├── chaos/
│   ├── pod-kill-pix-core.yaml
│   ├── network-latency.yaml
│   └── stress-cpu-node.yaml
├── data/
│   └── toil-log.csv
├── scripts/
│   ├── toil_tracker.py
│   ├── chaos_plan.py
│   ├── dr_simulator.py
│   └── incident_timeline.py
└── k8s/
    ├── velero-schedule.yaml
    └── app/
```

---

## Pré-requisitos

- Cluster k3d rodando (pode reusar do Módulo 8/9).
- Kubectl, Helm, Velero CLI instalados.
- Python 3.11+ com `pip install -r requirements.txt` do módulo.
- MinIO (ou outro S3-like) disponível para Velero.
- Chaos Mesh instalado (instruções no [Bloco 2](../bloco-2/02-chaos-engineering.md)).
- Opcional: um app mínimo de exemplo (`pix-core` com 3 replicas, expondo `/healthz` e `/metrics`).

---

## Critério de aceitação global

- Cada parte entrega **artefatos rastreáveis** (commit dedicado + PR).
- Documentos seguem os templates dos blocos.
- Scripts Python rodam e produzem saída correta.
- Chaos/DR/Tabletop foram **exercitados de verdade**, não só descritos.
- Pelo menos 2 postmortems com ações com dono e prazo.

---

## Sugestão de cronograma

| Semana | Parte | Duração estimada |
|--------|-------|------------------|
| 1 | 1 — SLOs/Toil | 3 h |
| 2 | 2 — Chaos | 4 h |
| 3 | 3 — DR | 4 h |
| 4 | 4 — Incident Command | 3 h |
| 5 | 5 — Postmortem/Learning | 2 h |

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Exercícios resolvidos](../bloco-4/04-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Parte 1 — SLOs, Error Budget Policy e Toil Tracker](parte-1-slo-toil.md) |

<!-- nav:end -->

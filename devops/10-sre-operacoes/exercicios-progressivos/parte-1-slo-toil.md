# Parte 1 — SLOs, Error Budget Policy e Toil Tracker

> **Meta.** Dar à PagoraPay o vocabulário operacional: SLOs claros, EBP com ações executáveis, toil mensurado, capacidade com headroom explícito.

---

## Contexto

Volte ao [cenário PBL](../00-cenario-pbl.md): achados #1 (sem EBP), #3 (toil não medido), #5 (capacidade no "feeling"), #10 (on-call sem limites). Essa parte ataca os 4.

---

## Passo 1 — Repositório base

```bash
mkdir pagorapay-sre && cd pagorapay-sre
git init
mkdir -p docs/runbooks scripts data k8s
touch Makefile
git add -A && git commit -m "chore: repo skeleton"
```

Copie `toil_tracker.py` do Bloco 1 para `scripts/`.

## Passo 2 — `docs/slo-policy.md`

Escreva um documento com:

1. **Introdução** — contexto, quem aprova (CTO, head de pagamentos, SRE lead), revisão trimestral.
2. **SLIs e SLOs** — mínimo **3**, com:
   - Descrição e fórmula exata (numerador/denominador).
   - Janela (30 dias rolante para disponibilidade; 7 dias para frescor).
   - Alvo e racional.
3. **Error budgets derivados** (tabela minuto/requisição).
4. **Error Budget Policy** em 3 níveis (verde/amarelo/vermelho) com ações executáveis.
5. **Escalamento** — quem é notificado em cada nível, como, em que prazo.

SLOs sugeridos:

| SLI | Janela | SLO |
|-----|--------|-----|
| `POST /pix/enviar` 2xx / total | 30d | ≥ 99,95% |
| `POST /pix/enviar` p95 ≤ 500 ms | 30d | ≥ 99% |
| `GET /saldo` frescor ≤ 3 s | 7d | ≥ 99,5% |
| ledger consistência 24h | 7d | ≥ 99,99% |

## Passo 3 — `docs/toil.md` + log

1. Escreva `docs/toil.md`:
   - Definição operacional (as 6 propriedades).
   - Taxonomia adotada: categorias (ex.: `rotacao-segredo`, `incidente`, `conciliacao`, `atendimento`, `deploy-manual`, `limpeza`).
   - Metodologia de coleta (Slack slash-command, Google Form, script — escolha).
   - Toil budget adotado (sugestão: **15 h / pessoa / semana**; se ≥ 20 h por 3 semanas, **stop-the-line**).
2. Crie `data/toil-log.csv` e preencha com **ao menos 2 semanas** (pode ser simulado; use cenário PBL para inspirar).
3. Rode `python scripts/toil_tracker.py data/toil-log.csv --budget-horas 15` e colete saída.
4. Anexe à `docs/toil.md` seção "Relatório da semana X" com tabela, principais toils, **3 ações de eliminação** priorizadas.

## Passo 4 — `docs/capacity.md`

1. Identifique 3 recursos a monitorar: CPU DB, conexões Postgres, Kafka consumer lag.
2. Para cada:
   - Medida atual (pode ser estimada).
   - Limite de saturação.
   - Headroom alvo (%).
   - Previsão simples (linear) de quando atinge saturação.
3. Proponha 2 ações (uma short-term, uma structural).

Opcional: dashboard Grafana com painel "Capacidade" (provisioned via ConfigMap).

## Passo 5 — `docs/on-call.md`

Política mínima com:

- Pool de pessoas (≥ 4).
- Turno (1 semana), primário + secundário.
- Limite: ≤ 2 pagings fora do horário/semana.
- Compensação.
- Gatilho de revisão quando limite é ultrapassado.
- Onboarding (shadowing).

## Passo 6 — Makefile e commit

```makefile
.PHONY: slo-check toil-report capacity-check

slo-check:
	@echo "Consulte docs/slo-policy.md e o dashboard."

toil-report:
	python scripts/toil_tracker.py data/toil-log.csv --budget-horas 15

capacity-check:
	@echo "Consulte docs/capacity.md e o dashboard Grafana Capacidade."
```

```bash
git add -A && git commit -m "feat(sre-p1): slo-policy, toil, capacity, on-call"
```

---

## Entrega

- `docs/slo-policy.md` com 3+ SLOs, EBP em 3 níveis, escalamento.
- `docs/toil.md` + `data/toil-log.csv` com 2 semanas, + relatório semanal.
- `docs/capacity.md` com headroom e previsão.
- `docs/on-call.md` com política.
- `Makefile` com `toil-report` funcional.

## Critérios de aceitação

- [ ] 3+ SLOs com janela e racional.
- [ ] EBP com **ação executável** em cada nível (não só "revisar").
- [ ] Toil log com ≥ 14 dias, rodado pelo tracker sem erros.
- [ ] Capacity doc com headroom quantificado.
- [ ] On-call com pool ≥ 4 e limites numéricos.

## Sinais de sucesso

Se um novo membro do time ler os 4 documentos numa tarde, ele entende:

- O que se mede (SLIs).
- Quando parar (EBP).
- O que não é feature (toil).
- Quando escalar (alerta).

Essa é a **base cultural** sobre a qual as próximas partes constroem.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios progressivos — Módulo 10 (SRE e Operações)](README.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Parte 2 — Programa de Chaos Engineering](parte-2-chaos-engineering.md) |

<!-- nav:end -->

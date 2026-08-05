# Parte 5 — Postmortem Blameless e Learning Review

> **Meta.** Fechar o ciclo. Transformar incidentes em **aprendizado organizacional** rastreado. Produzir 2 postmortems blameless completos e 1 Learning Review trimestral.

---

## Contexto

Do PBL, achado #9 (postmortems viraram teatro: 8 em 2025, 0 ações concluídas). Essa parte prova que cultura blameless + rigor de acompanhamento de ações mudam o sistema.

---

## Passo 1 — Template oficial

Crie `docs/postmortems/_TEMPLATE.md` seguindo o template do [Bloco 4](../bloco-4/04-incidentes-escala.md). Adicione no seu repositório como **template fixo** (PR que cria um postmortem deve copiá-lo).

## Passo 2 — Postmortem #1: migração presa (PBL original)

Escreva `docs/postmortems/ph-2026-03-09-ledger-migration.md`:

- **Resumo** (1 parágrafo).
- **Impacto**: 41.200 requisições falhadas; R$ 3,8 mi não processado; 42 min Sev-1; aviso BACEN.
- **Timeline** (use a saída de `incident_timeline.py` da Parte 4).
- **O que funcionou**:
  - Detecção do monitor foi rápida (~90s).
  - `pg_terminate_backend` no fim foi decisivo.
- **O que não funcionou**:
  - Sem IC: 6 pessoas decidindo em paralelo nos primeiros 15 min.
  - Runbook "migração presa" não existia.
  - Comunicação pública atrasada (30 min).
  - Staging não representava o cenário (tabela pequena).
- **Contributing factors** (lista):
  1. Pipeline permite DDL direto em produção sem revisão DBA.
  2. Ambiente staging não reflete volume real da tabela `movimentos`.
  3. Runbook "schema lock" ausente.
  4. Sem protocolo ICS → decisões descoordenadas.
  5. Dev responsável fora no momento.
  6. Status page não atualizada entre 14:20 e 14:50 — cliente sem info.
  7. `pg_cancel_backend` foi tentado antes de `pg_terminate` — sem orientação prévia.
- **Ações** (tabela com dono e prazo):

| # | Ação | Dono | Prazo | Verificação |
|---|------|------|-------|-------------|
| 1 | Adicionar gate "DBA approval" em CI para migrações em tabelas > 10 GB | Tech lead @ pagamentos | 2026-03-25 | PR merged + review em 1 migração real |
| 2 | Criar staging com dump amostrado (10 M linhas) de `movimentos` | Squad infra | 2026-04-10 | Migração de teste roda em staging em < 5 min |
| 3 | Escrever runbook "schema lock em produção" | SRE | 2026-03-20 | Exercitado em game day 2026-04-15 |
| 4 | Treinar time em ICS com tabletop mensal | SRE lead | 2026-03-30 | 2 tabletops realizados até 2026-05 |
| 5 | Automatizar update de status page via bot (cada 15 min) | Platform | 2026-04-30 | Bot responde a `/status` em `#incident-*` |
| 6 | Pipeline de postmortem: template obrigatório para Sev-1/2 | SRE lead | 2026-03-25 | 100% dos Sev-1 últimos 3 meses |

- **Aprendizado organizacional**: migrações DDL em tabelas grandes **são** classe de risco; precisam de processo dedicado (online schema change com `pg-osc` ou `pt-online-schema-change`).

## Passo 3 — Postmortem #2: derivado do Game Day (Parte 2)

Se no Game Day/experiment a hipótese foi refutada (ou surgiu surpresa), gere um **postmortem secundário**. Mesmo que tenha sido no ambiente de laboratório, o aprendizado é real.

Caso hipóteses tenham sido todas confirmadas, invente um "quase-incidente": durante o experimento de latência de 200 ms, o retry entrou em loop por `MAX_RETRIES` muito alto, queimando 2% de throughput adicional. Isso é aprendizado.

Estrutura igual, mas:

- Impacto: interno/experimental.
- Timeline curta.
- Contributing factors focados na descoberta.
- Ações mais técnicas.

## Passo 4 — Acompanhamento de ações

Crie `docs/actions-tracker.md`:

```markdown
# Tracker de acoes de postmortem

| Acao | Dono | Prazo | Status | Postmortem | Evidencia |
|------|------|-------|--------|------------|-----------|
| Gate DBA em CI | ... | 2026-03-25 | done | ph-2026-03-09 | PR #142 |
| Staging sampled | ... | 2026-04-10 | in_progress | ph-2026-03-09 | |
| Runbook schema lock | ... | 2026-03-20 | done | ph-2026-03-09 | docs/runbooks/ledger-db-lock.md |
| ... | | | | | |
```

Regra: toda reunião semanal do time revisa "ações `in_progress`/`atrasadas`". Postmortem sem follow-up volta a ser teatro.

## Passo 5 — Learning Review trimestral

Escreva `docs/learning-review-Q1-2026.md`:

```markdown
# Learning Review - Q1 2026

## Periodo
2026-01-01 a 2026-03-31.

## Incidentes analisados
- 3 Sev-1, 7 Sev-2, 14 Sev-3.

## Padroes identificados
1. **Migracao de schema sem revisao DBA** aparece em 2 Sev-1 distintos (09/03 e 22/02).
   -> Alem do gate (acao 1), propor workshop sobre "online schema change".
2. **Comunicacao com cliente regulado atrasa** em 4 Sev-1/2.
   -> Templates BACEN/LGPD integrados ao repo; Comms tem acesso 1-click.
3. **On-call pagamentos sobrecarregado** (engenheiro A: 18 pagings).
   -> Redistribuir. Incluir 2 pessoas de plataforma na rotacao.

## Conquistas
- MTTR medio Sev-1: 42 min -> 28 min (promissor, n=3).
- Postmortems com acao concluida: 0/8 (2025) -> 5/7 no Q1.
- 2 tabletops realizados; 1 game day.

## Pendencias estruturais
- Sharding da tabela `movimentos` (discutido, nao iniciado).
- SLO de frescor de saldo ainda sem medicao automatica.

## Acoes para Q2
| Acao | Dono | Prazo |
|------|------|-------|
| Workshop online schema change | SRE | 2026-04-30 |
| Templates BACEN/LGPD em runbooks/ | Comms | 2026-04-15 |
| Revisao do pool de on-call pagamentos | CTO | 2026-04-10 |

## Aprovado por
CTO, Head de pagamentos, SRE lead.
```

## Passo 6 — Makefile

```makefile
.PHONY: postmortem-new learning-review

postmortem-new:
	@read -p "Slug (ex.: ledger-migration): " slug; \
	DATE=$$(date +%Y-%m-%d); \
	cp docs/postmortems/_TEMPLATE.md docs/postmortems/ph-$$DATE-$$slug.md && \
	echo "Criado docs/postmortems/ph-$$DATE-$$slug.md"

learning-review:
	@echo "Crie docs/learning-review-Q<N>-<ANO>.md a cada trimestre."
```

Commit final:

```bash
git add -A && git commit -m "feat(sre-p5): postmortem blameless + actions tracker + learning review"
```

---

## Entrega

- `docs/postmortems/_TEMPLATE.md`.
- `docs/postmortems/ph-2026-03-09-ledger-migration.md` completo.
- `docs/postmortems/ph-<data>-<slug>.md` secundário (Game Day ou quase-incidente).
- `docs/actions-tracker.md` com ≥ 8 ações reais/ficcionadas com dono e prazo.
- `docs/learning-review-Q1-2026.md` com padrões e ações Q2.
- Makefile com `postmortem-new`.

## Critérios de aceitação

- [ ] Ambos os postmortems são **blameless** (nenhum nome pessoal culpando).
- [ ] Contributing factors listados (≥ 3 por postmortem).
- [ ] Cada ação tem **dono**, **prazo** e **critério de verificação**.
- [ ] Tracker mostra ≥ 50% de ações concluídas com evidência.
- [ ] Learning Review agrega e propõe ações trimestrais.

## Bônus

- Publicar um postmortem "redigido" externamente (GitHub público ou blog) — postmortems públicos são marca de maturidade.
- Integrar o tracker a um board Jira/GitHub Projects automático.
- Adicionar dashboard "Saúde SRE" no Grafana: MTTR, MTTA, MTTD, % ações concluídas.

---

## Fechamento do módulo

Ao concluir as 5 partes, você tem **uma operação SRE funcional de ponta a ponta**:

- SLOs claros, EBP executável, toil medido, capacidade pensada.
- Resiliência validada por experimento.
- DR real com RPO/RTO medidos.
- Processo humano de incidente com papéis e comunicação.
- Aprendizado organizacional rastreado.

Isso difere de **apenas ter observabilidade** — é o que o Módulo 10 acrescenta à pilha DevOps.

Pronto para o Módulo 11 (Plataforma Interna) ou Módulo 12 (Capstone).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 4 — Incident Command System + Tabletop](parte-4-incident-command.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Entrega avaliativa — Módulo 10 (SRE e Operações)](../entrega-avaliativa.md) |

<!-- nav:end -->

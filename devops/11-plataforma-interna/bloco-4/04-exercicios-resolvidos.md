# Bloco 4 — Exercícios resolvidos

> Leia [04-metricas-plataforma.md](./04-metricas-plataforma.md) antes.

---

## Exercício 1 — Classificar DORA

**Enunciado.** Com os dados da OrbitaTech (deploy 5/dia agregado, lead time mediano 9 dias, CFR 22%, MTTR mediano 4h), classifique DORA e diagnostique.

**Resposta.**

Aplicando as regras:
- DF = 5/dia ~ 35/semana → elite/high.
- Lead time 9 dias → medium.
- CFR 22% → high/medium.
- MTTR 4h → high/medium.

O **elo mais fraco determina**: Lead Time 9 dias → classe **Medium**.

**Diagnóstico**: empresa "entrega rápido no micro" (muitos deploys) mas **acumula no macro** (código demora a chegar em prod). Causas prováveis:
- CI/CD lento em alguns serviços.
- PRs ficam parados aguardando review.
- Gates manuais adicionando semanas.
- Mudanças grandes (não fatiadas) acumulando.

CFR 22% também alto — qualidade no caminho precisa melhorar. Agenda de plataforma:
1. Reduzir lead time: CI 20→10 min, review SLA.
2. Reduzir CFR: gates de teste/segurança embutidos no golden path.
3. Evoluir continuously deploys (feature flags, canary).

---

## Exercício 2 — Desenhar survey SPACE

**Enunciado.** Desenhe um survey SPACE para a plataforma com **máximo 8 questões** cobrindo as 5 dimensões.

**Resposta.**

```markdown
## Survey SPACE - Plataforma OrbitaTech

1. [0-10] Quanto voce recomenda a plataforma a outro engenheiro? (SAT)
2. [1-5] Quao satisfeito voce esta com ritmo de entrega do seu squad? (SAT)
3. [dias] Quantos dias levaram entre seu primeiro commit e seu primeiro deploy em prod? (PERF)
4. [quantidade] Quantas vezes na ultima sprint voce teve que reescrever ou refazer um deploy? (PERF)
5. [1-5] Quao rapidamente uma PR sua recebe primeira review? (COMM) 5=min 1=dias
6. [% do tempo] Qual % do seu tempo voce gasta "alem do codigo" (config, pipeline, migracao)? (EFF)
7. [horas/dia] Quantas horas/dia voce consegue ter em "deep work" sem interrupcoes? (EFF)
8. [aberta] Maior friccao que voce encontra hoje? (context)
```

**Cobertura**:
- Satisfaction: Q1, Q2.
- Performance: Q3, Q4.
- Activity: deduzida pela Q3 (implícita; evitei "quantos commits?" por ser vaidade).
- Communication: Q5.
- Efficiency: Q6, Q7.
- Contexto aberto: Q8.

---

## Exercício 3 — Calcular NPS

**Enunciado.** 20 respostas: scores `[9, 8, 10, 7, 6, 9, 9, 5, 10, 8, 3, 7, 9, 6, 10, 8, 2, 9, 8, 7]`. Calcule NPS, categorize e descreva próximo passo.

**Resposta.**

- Promotores (9-10): 7 (9,10,9,9,10,10,9) → 35%.
- Passivos (7-8): 8 (8,7,8,7,8,8,7) — reconte: scores 7: {7,7,7} 3; 8: {8,8,8,8} 4; total 7. Confirmando: 7 passivos → 35%.
- Detratores (0-6): 6 (6,5,3,6,2,...?) — reconte com cuidado:

Agrupando:
- 10: 3 (posições 3, 9, 15).
- 9: 5 (posições 1, 6, 7, 13, 18).
- 8: 4 (posições 2, 10, 16, 19).
- 7: 3 (posições 4, 12, 20).
- 6: 2 (posições 5, 14).
- 5: 1 (posição 8).
- 3: 1 (posição 11).
- 2: 1 (posição 17).

Total = 20. Confere.

- Promotores: 3 + 5 = 8 → 40%.
- Passivos: 4 + 3 = 7 → 35%.
- Detratores: 2 + 1 + 1 + 1 = 5 → 25%.

**NPS = 40 - 25 = +15**.

**Categorização**: faixa 0-20, **mediana** com sinais positivos porém detratores significativos (25%).

**Próximo passo**: agendar 5 calls de 20 min (uma com cada detrator). Objetivo: diagnosticar 2-3 temas comuns que, atacados, movam a agulha 10+ pontos no próximo trimestre. Publicar resultado + plano de ação na próxima reunião All Hands.

---

## Exercício 4 — Rodar `platform_metrics.py`

**Enunciado.** Com dados simulados, calcule DORA e NPS.

**`data/deployments.csv`:**

```csv
data,squad,status
2026-04-01,aluguel,success
2026-04-01,pagamentos,success
2026-04-02,aluguel,failed
2026-04-02,condominios,success
2026-04-03,aluguel,success
2026-04-04,pagamentos,success
2026-04-05,condominios,rolled-back
2026-04-06,aluguel,success
2026-04-07,pagamentos,success
2026-04-07,condominios,success
2026-04-08,aluguel,success
```

**`data/leadtime.csv`:**

```csv
commit_at,deploy_at
2026-04-01T09:00:00,2026-04-01T14:00:00
2026-04-02T10:30:00,2026-04-03T09:00:00
2026-04-03T08:00:00,2026-04-04T18:00:00
2026-04-05T11:00:00,2026-04-06T12:00:00
2026-04-07T10:00:00,2026-04-07T15:00:00
```

**`data/incidents.csv`:**

```csv
detect_at,restore_at
2026-04-02T15:00:00,2026-04-02T15:45:00
2026-04-05T09:00:00,2026-04-05T11:30:00
```

**`data/survey.csv`:**

```csv
respondente,score_nps
dev1,9
dev2,8
dev3,10
dev4,7
dev5,6
dev6,9
dev7,5
dev8,10
```

**Saída esperada:**

```
DORA (agregado)
  Deploy Frequency (deploys/semana)  ~6-7
  Lead Time (dias, mediana)          ~0.8
  Change Failure Rate                18.2%
  MTTR (horas, mediana)              ~1.6
  Classe DORA                        High

Deploy Frequency por squad
  aluguel       ~3
  pagamentos    ~2
  condominios   ~1.5

NPS Interno
  Promotores (9-10): 4
  Passivos (7-8):    2
  Detratores (0-6):  2
  NPS               +25.0
```

**Interpretação**: classe High é bom mas não Elite. Lead time ok, CFR 18% — acima do ideal (<15% Elite). Dois incidentes com MTTR razoável. NPS +25: bom; focar nos 2 detratores (pontuações 5 e 6).

---

## Exercício 5 — Métrica de vaidade

**Enunciado.** Um membro do time propõe medir "número de pull requests abertos na plataforma por semana". Você recebe a proposta — o que responde?

**Resposta.**

```markdown
Obrigado, mas vamos pensar antes de adotar. PRs abertos por semana e uma
metrica de **activity**, da familia SPACE. Activity sem contexto e
**vaidade**: ela pode subir por razoes neutras (PRs triviais, dependabot)
ou ruins (PRs fragmentados para parecer produtivo).

Perguntas:
1. **Que decisao** essa metrica nos ajudaria a tomar?
2. **Goodhart**: se virar meta, o que incentivamos? (resposta provavel:
   fragmentar PRs ou abrir PR apenas para aparecer).
3. **Ha metrica melhor** na mesma dimensao?

Proposta de substituicao:
- **Lead time de PR** (opening -> merge) por squad.
- **Review latency** (opening -> primeira review).
- **PR throughput** (mergeados / semana), **complementado com CFR**.

Se ainda assim quisermos ter "PRs abertos", tratamos como dashboard
de **context** (lateral), nunca como KPI.
```

---

## Exercício 6 — Diagnóstico com métricas

**Enunciado.** A plataforma reporta:
- DORA **Elite**.
- NPS **+60**.
- Adoção golden path em **90%** dos novos serviços.
- Mas cresceu de **70%** para **90%** em 3 meses só depois que o CTO obrigou.

Você como líder Platform faria alguma coisa? O que?

**Resposta.**

```markdown
Sim. Mesmo com numeros aparentemente bons, ha tensao oculta.

**O que esta OK:**
- DORA Elite comprova eficacia operacional.
- NPS +60 e excelente.
- Adocao alta.

**O problema:**
Os ultimos 20 pontos de adocao vieram **por mandato**, nao por escolha.
Isso pode:
1. Esconder descontentamento dos adotantes forcados (nao representados no
   NPS se estao calados por medo).
2. Quebrar a premissa "plataforma por atratividade, nao por obrigacao".
3. Criar **dependencia cultural** do mandato para manter adocao.

**Acao:**
1. **Survey segmentado**: voluntarios vs forcados. Investigar separadamente.
2. **Entrevistas qualitativas** com os squads dos ultimos 20%: o que os
   deteve antes? Plataforma falhou em perceber?
3. **Roadmap data-driven**: se o feedback dos forcados aponta gap real,
   atacar em 1-2 sprints.
4. **Politica**: mandato fica ate esses 20% "adotarem por escolha" (NPS
   e engajamento voluntario equivalem aos 70% originais). So entao
   suspendemos o mandato — como sinal publico de confianca na plataforma.

Metrica de saude: **% de adocao voluntaria** (exclui forcados). Meta:
tender a 100%.
```

**Chave**: números agregados escondem heterogeneidade. Plataforma saudável exige **adoção voluntária**; mandato é paliativo, não solução.

---

## Autoavaliação

- [ ] Classifico DORA (Elite/High/Medium/Low).
- [ ] Sei distinguir métrica de **atividade** (vaidade) de métrica de **valor**.
- [ ] Desenho survey SPACE cobrindo 5 dimensões.
- [ ] Calculo NPS e faço follow-up com detratores.
- [ ] Interpreto saída do `platform_metrics.py`.
- [ ] Reconheço quando "números bons" escondem problema (mandato vs. escolha).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Métricas de Plataforma: DORA, SPACE, DevEx e NPS interno](04-metricas-plataforma.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Exercícios progressivos — Módulo 11 (Plataforma Interna)](../exercicios-progressivos/README.md) |

<!-- nav:end -->

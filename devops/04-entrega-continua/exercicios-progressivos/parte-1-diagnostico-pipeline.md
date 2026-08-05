# Parte 1 — Diagnóstico do Pipeline da LogiTrack

> **Duração:** 45 minutos.
> **Objetivo:** localizar a LogiTrack no espectro **CI → CDelivery → CDeployment** com rigor, e extrair **prioridades de intervenção**.

---

## Contexto

A VP de engenharia quer **dados objetivos** antes de aprovar o plano de transformação. Você foi escalado para produzir o **diagnóstico de maturidade**. O resultado da Parte 1 é a **base** para as próximas partes.

Reveja o [cenário PBL](../00-cenario-pbl.md) e os [benchmarks DORA](../bloco-1/01-ci-cd-deployment.md#32-benchmarks-state-of-devops-2023).

---

## Tarefas

### 1. Aplicar o checklist de 8 perguntas (do Bloco 1)

Para cada um dos 4 serviços — **Tracking API**, **Consulta**, **Notificações**, **Billing** — responda as 8 perguntas do checklist (Exercício 6 do Bloco 1).

**Formato sugerido (Markdown):**

```markdown
## Serviço: Tracking API

| # | Pergunta | SIM/NÃO | Evidência |
|---|----------|---------|-----------|
| 1 | Pipeline a cada push? | SIM | .github/workflows/ci.yml existe |
| 2 | Testes bloqueantes no pipeline? | SIM | pytest com cov-fail-under |
| 3 | Artefato idêntico de staging e prod? | NÃO | Pipeline recompila em cada etapa (sintoma 3) |
| ... | ... | ... | ... |

**Pontuação: 2/8 → pré-CDelivery**
```

Faça para os 4 serviços.

### 2. Calcular DORA atual da LogiTrack

Usando o [`calc_dora.py`](../bloco-1/01-ci-cd-deployment.md#4-calculadora-dora-em-python), gere o relatório com os **dados do cenário**:

- DF: 1 deploy a cada ~4 semanas → ≈ 0,036/dia.
- LT: 25 dias médios.
- CFR: 18%.
- MTTR: 90 minutos.

**Entregável:** produza um arquivo `deploys.csv` e `incidentes.csv` sintéticos que, ao passar pelo script, geram essas métricas. Rode e capture a saída.

### 3. Diagrama atual vs alvo (Mermaid)

Dois diagramas:

**a) Estado atual**

Represente o pipeline que existe hoje — com os 87 passos manuais, a fila mensal, a recompilação múltipla. Identifique os gargalos com cor vermelha.

**b) Estado-alvo em 6 meses**

Represente o pipeline-alvo conforme Blocos 2 e 3 — multi-estágio, artefato único, feature flags, rollback instantâneo.

### 4. Priorizar intervenções

Monte uma tabela com **pelo menos 8 intervenções**, priorizadas por **impacto esperado em DORA** × **esforço de implementação**.

Use escala 1 a 5 para ambos.

**Exemplo inicial (adicione pelo menos 6 linhas):**

| # | Intervenção | Impacto DORA (1-5) | Esforço (1-5) | Prioridade |
|---|-------------|--------------------|---|------------|
| 1 | Artefato único (build once) | 4 (melhora LT, CFR) | 2 | **P1** |
| 2 | Pipeline multi-estágio em GitHub Environments | 5 (DF, LT, MTTR) | 3 | **P1** |
| 3 | Feature flags básicos para kill switch | 4 (MTTR) | 2 | **P1** |
| ... | ... | ... | ... | ... |

Classificação sugerida:

- **P1** — alto impacto + baixo esforço.
- **P2** — alto impacto + alto esforço (grandes, mas vale).
- **P3** — baixo impacto ou ainda cedo demais.

### 5. Identificar o "Primeiro Pino do Dominó"

Em uma transformação, **uma** intervenção geralmente destrava várias outras. Qual é ela para a LogiTrack? Justifique em 4 a 5 linhas.

---

## Entregáveis

Crie no repositório:

```
exercicios/parte-1/
├── diagnostico-maturidade.md       # checklist dos 4 serviços
├── dora-atual.md                    # saída do calc_dora.py + análise
├── deploys.csv
├── incidentes.csv
├── estado-atual.mmd                 # Mermaid
├── estado-alvo.mmd                  # Mermaid
├── priorizacao.md                   # tabela + justificativas
└── primeiro-pino.md                 # intervenção-chave
```

---

## Critérios de sucesso

- [ ] Checklist aplicado aos **4 serviços**, com evidência por pergunta.
- [ ] DORA atual computada — script rodou e saída está colada.
- [ ] Dois diagramas Mermaid (atual e alvo) **visualmente distintos**.
- [ ] Tabela de priorização com **pelo menos 8 intervenções**.
- [ ] "Primeiro Pino" justificado — **não pode ser** genérico ("cultura"). Tem que ser uma ação concreta do pipeline.

---

## Dicas

- **Seja justo** na aplicação do checklist — a LogiTrack tem CI razoável (Módulo 2). Não dê zero à toa.
- **Não confunda** "meta" com "realidade" — o objetivo é descrever o **estado atual**, não desejar.
- Para o estado-alvo, **inspire-se** no diagrama do Bloco 2 (`deployment-pipeline`), mas adapte para o domínio logístico.
- **Priorização** exige justificar. "P1" com 0 frases não serve.

---

## Próximo passo

Ao terminar, abra a **[Parte 2 — Pipeline multi-estágio](parte-2-pipeline-multi-estagio.md)**, onde você vai **construir** o pipeline que desenhou.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Progressivos — Módulo 4](README.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](../README.md) | **Próximo →**<br>[Parte 2 — Pipeline Multi-estágio com Artefato Único](parte-2-pipeline-multi-estagio.md) |

<!-- nav:end -->

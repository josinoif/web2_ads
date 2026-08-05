# Parte 5 — Métricas, survey e evolução

**Objetivo.** Instrumentar DORA + SPACE + NPS; montar dashboard; basear o roadmap em dado.

**Pré-requisitos.** Partes 1-4 concluídas.

**Entregáveis em `orbita-idp/`:**

1. `docs/metrics.md` — métricas escolhidas, justificativa.
2. `data/` — CSVs reais ou simulados (deploys, lead time, incidents, survey).
3. `scripts/platform_metrics.py` (ou reuso de Bloco 4) rodando.
4. `grafana/dashboards/platform.json` — dashboard provisioned.
5. `docs/survey-Q2-2026.md` — survey aplicado + resultados.
6. `docs/platform-roadmap-evolutivo.md` — decisões baseadas nos dados.
7. `docs/deprecations-updates.md` — revisão do plano da Parte 4 com base em dados.

---

## 5.1 `docs/metrics.md`

Template:

```markdown
## Metricas de plataforma (Q2/2026)

### DORA
- Deploy Frequency: % novos servicos + % servicos ativos que fazem deploy na semana.
- Lead Time: mediana commit->prod.
- Change Failure Rate: incidentes atribuidos a deploy / total deploys.
- MTTR: mediana detect->restore.

### SPACE
- **Satisfaction**: NPS trimestral.
- **Performance**: % servicos no golden path em prod.
- **Activity**: deploys por squad/semana (dashboard, nao meta).
- **Communication**: tempo medio de review de PR na plataforma.
- **Efficiency**: onboarding (primeiro deploy em dias).

### DevEx
- CI feedback time (push -> red/green): meta <= 8 min p95.
- Time to rollback: meta <= 3 min.
- Local build time (docker): meta <= 2 min.
- Cognitive load (survey 1-5): meta <= 3.0 media por squad.

### Metricas que NAO adotamos
- LOC produzida (vaidade).
- PRs abertos/semana sem contexto (vaidade).
- Uptime do K8s (prereq, nao conquista).

### Goodhart
Toda meta e vigiada para evitar gaming. Revisao trimestral.
```

## 5.2 Dados e script

Popular `data/`:

- `deployments.csv` com ≥ 30 registros (≥ 4 squads, ≥ 2 semanas).
- `leadtime.csv` com ≥ 20 pares (commit_at, deploy_at).
- `incidents.csv` com ≥ 3 incidentes.
- `survey.csv` com ≥ 8 respostas NPS.

Rodar:

```bash
make metrics-report
```

Salvar output em `docs/metrics-report-2026-Q2.md`.

## 5.3 Dashboard Grafana

Criar `grafana/dashboards/platform.json` (Bloco 4 §4.8.1 como base). Dashboard deve ter:

- Linha temporal de DORA (DF, Lead Time, CFR, MTTR).
- NPS gauge.
- Piechart de adoção de golden path.
- Tabela top-10 serviços por custo (se showback ativo).
- Painel de onboarding time (histograma).

Subir com:

```yaml
# docker-compose.yml (trecho)
services:
  grafana:
    image: grafana/grafana:10.4.0
    ports: ["3001:3000"]
    volumes:
      - ./grafana/dashboards:/var/lib/grafana/dashboards
      - ./grafana/provisioning:/etc/grafana/provisioning
```

## 5.4 Survey aplicado

`docs/survey-Q2-2026.md`:

- Perguntas (do Bloco 4 §4.4.2, adaptadas).
- Canal de divulgação (email, slack).
- Resultado: NPS, distribuição, temas dos comentários abertos.
- Plano de ação baseado nos resultados.
- Follow-up com detratores: quem, quando.

## 5.5 Roadmap evolutivo

`docs/platform-roadmap-evolutivo.md` compara:

- O que havia na Parte 1 (roadmap inicial).
- O que **mudou** com base nos dados da Parte 5.
- Nova priorização.

Exemplo:

```markdown
## Mudancas baseadas em dado (Q2 -> Q3)

### Antes (roadmap da Parte 1)
- S1: template go-http.
- S2: plugin ArgoCD no Backstage.
- S3: melhorar onboarding.

### Depois (dados de Q2)
- **NPS +12** (abaixo da meta +20). Detratores (5 calls): 4/5 citam CI lento.
- **CFR 22%**: alto, plataforma impacta (2 dos 4 golden paths geraram template com bug de probes).

### Nova priorizacao Q3
- S1: otimizar CI do python-fastapi (meta: 8 min p95). 
- S2: auditar probes default; publicar correcao automatica em golden path v2.
- S3: replanejar go-http (impacto menor em NPS).

### Adiado
- Plugin ArgoCD (baixo impacto no NPS).

### Confirmado
- Survey seguiu 78% de resposta - bom engajamento; mantemos trimestral.
```

## 5.6 Revisão das deprecations

`docs/deprecations-updates.md`:

- Para cada deprecation da Parte 4, revisar com dados reais (quantos squads ainda usam?).
- Ajustar cronograma se necessário.
- Prepare comunicação.

---

## Critérios de aceitação da Parte 5

- [ ] `docs/metrics.md` lista DORA + SPACE + DevEx + evita vaidade.
- [ ] `data/` com ≥ 30 deploys, ≥ 20 leadtimes, ≥ 3 incidents, ≥ 8 NPS.
- [ ] `make metrics-report` gera relatório salvo em `docs/`.
- [ ] Dashboard Grafana funcional (painéis carregam).
- [ ] Survey aplicado com > 5 respostas reais/simuladas.
- [ ] NPS computado e discutido.
- [ ] Roadmap evolutivo compara "antes" e "depois" com dados.
- [ ] Deprecations revisadas com base em dados.

---

## Critério geral final (agregado)

Seu `orbita-idp/` contém:

- [x] Estratégia (Parte 1).
- [x] Portal + catálogo (Parte 2).
- [x] Golden paths (Parte 3).
- [x] Contratos (Parte 4).
- [x] Métricas (Parte 5).

Um novo engenheiro da OrbitaTech, ao clonar seu repo e seguir o README, consegue:

1. Subir o portal.
2. Entender a oferta (capabilities, tiers).
3. Criar um serviço via template.
4. Ver seu serviço no catálogo, com dashboard e docs.

Essa é a **prova definitiva** de que sua plataforma é um **produto** — não só código.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 4 — Capabilities, tiers e contratos](parte-4-contratos.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Entrega avaliativa — Módulo 11 (Plataforma Interna)](../entrega-avaliativa.md) |

<!-- nav:end -->

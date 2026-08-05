# Entrega avaliativa — Módulo 11 (Plataforma Interna)

**Peso:** 20% da nota final (ajuste conforme plano pedagógico).
**Formato:** repositório Git com Backstage em execução local, templates versionados, catálogo populado, documentos e scripts.
**Prazo sugerido:** ao final da semana do módulo.

---

## Objetivo

Demonstrar que você é capaz de **tratar plataforma como produto interno**: definir clientes e jobs-to-be-done, entregar portal (Backstage) + golden paths + contratos + métricas — tudo com evidência de **adoção voluntária** e **valor entregue**.

---

## Produto final

1. **Documento de estratégia** (`docs/platform-strategy.md`):
   - Personas (engenheiro júnior, tech lead, squad lead de produto).
   - Jobs-to-be-done mapeados.
   - Golden paths escolhidos (≥ 2) com justificativa.
   - Anti-golden paths declarados.
   - Team Topologies: declarar o tipo (Platform) e modos de interação.
2. **Backstage em execução** (`idp/`):
   - App gerado com `create-app`, rodando localmente com `yarn dev`.
   - Software Catalog com **≥ 8 entidades reais/fictícias** (serviços, APIs, bancos).
   - TechDocs ativo em ≥ 1 serviço.
   - Pelo menos 1 **Software Template (Scaffolder)** funcional.
3. **Golden Paths versionados** (`templates/`):
   - Template 1: **serviço FastAPI** com CI/CD, Dockerfile hardened, Helm chart, observability e segurança por padrão.
   - Template 2: **outro** — à sua escolha: banco Postgres, tópico Kafka, job CronJob, worker Go, etc.
   - Cada template tem README explicando decisões.
4. **Software Catalog completo** (`catalog/`):
   - Arquivos `catalog-info.yaml` para cada entidade.
   - Ownership declarado (groups/users).
   - Relations (dependsOn, providesApi).
5. **Contratos de plataforma** (`docs/platform-contracts.md`):
   - Capability catalog com **≥ 4 capabilities** (ex.: `postgres-db`, `k8s-namespace`, `kafka-topic`, `observability-stack`).
   - Tiers (bronze/silver/gold) com SLOs internos.
   - Preços internos (pode ser modelo de chargeback conceitual).
   - Processo de deprecation (RFC + prazo).
6. **Métricas e survey**:
   - `docs/metrics.md` — quais métricas e por quê.
   - Dashboard Grafana (JSON provisioned) com DORA + adoção.
   - Survey SPACE/DevEx aplicado (real ou simulado com ≥ 5 respostas).
   - Cálculo de **NPS interno** (script `nps_calc.py`).
7. **Learning e evolução**:
   - `docs/platform-roadmap.md` — próximas 2 sprints com decisões baseadas em dado.
   - `docs/deprecations.md` — tabela de itens a remover, prazo, comunicação.
8. **Makefile** com alvos: `portal-up`, `catalog-validate`, `template-test`, `metrics-report`, `nps-report`.

---

## Rubrica de avaliação (100 pts)

| Eixo | Peso | Critérios |
|------|------|-----------|
| **Estratégia** | 15 | Personas, JTBD, golden/anti-golden paths, Team Topologies declarado |
| **Backstage em uso** | 20 | Portal rodando, Catalog ≥ 8 entidades, TechDocs, ≥ 1 Template |
| **Golden paths** | 20 | 2 templates geram serviço funcional com CI/CD, segurança e obs por padrão |
| **Catalog** | 10 | Entidades com ownership e relations; consistência |
| **Contratos** | 15 | Capabilities com tiers, SLO interno, deprecation |
| **Métricas e survey** | 15 | DORA computado, survey aplicado, NPS calculado, dashboard |
| **Roadmap e evolução** | 5 | Próximos passos baseados em dado; deprecations claras |

### Bônus (até +10 pts)

- **TechDocs** em todos os serviços principais.
- Integração Backstage ↔ Kubernetes (plugin) mostrando pods/deployments.
- Chat/bot (`/platform ask`) que responda perguntas de catálogo (pode ser mock com FAQ).
- **Score-spec** (score.dev) usado como workload spec.
- Template "destrutivo" (deprecation): gera aviso amarelo quando algo proibido é detectado.

---

## Formato de entrega

1. Link do repositório.
2. README raiz com:
   - Arquitetura da plataforma.
   - Como rodar (`make portal-up`).
   - Personas e golden paths.
   - Link para documentos principais.
   - Screenshot do Backstage (catálogo + template).
3. Vídeo ≤ 12 min (banca presencial):
   - Dev hipotético abre o portal.
   - Cria um serviço novo via Scaffolder.
   - O serviço aparece no catálogo, com TechDocs.
   - Dashboard mostra adoção crescente.
   - Você explica decisões (por que esses golden paths, por que essa tier).

---

## Checklist rápido antes de entregar

- [ ] Portal Backstage sobe e exibe catálogo com ≥ 8 entidades.
- [ ] Scaffolder de 1 template **cria um repositório funcional** (teste!).
- [ ] Serviço gerado pelo template tem CI rodando verde.
- [ ] `catalog-info.yaml` passam no `backstage-cli config:check`.
- [ ] Capabilities têm tier + SLO documentados.
- [ ] DORA metrics são calculadas por script real (não inventadas).
- [ ] Survey tem pelo menos 5 respostas; NPS > -20 (mesmo em cenário "crítico").
- [ ] Roadmap cita **2 decisões baseadas em dado** do survey ou métricas.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Métricas, survey e evolução](exercicios-progressivos/parte-5-metricas.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](README.md) | **Próximo →**<br>[Referências — Módulo 11 (Plataforma Interna)](referencias.md) |

<!-- nav:end -->

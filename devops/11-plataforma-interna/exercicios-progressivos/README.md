# Exercícios progressivos — Módulo 11 (Plataforma Interna)

> Cinco exercícios encadeados que, somados, **constroem a plataforma interna da OrbitaTech** do zero. Cada exercício se apoia no anterior. Ao final você terá o material exigido pela [entrega avaliativa](../entrega-avaliativa.md).

---

## Visão geral

| Parte | Foco | Entregáveis |
|-------|------|-------------|
| **1** | Estratégia, personas, Team Topologies | `docs/platform-strategy.md`, `docs/personas.md`, `docs/team-topologies.md` |
| **2** | Backstage: portal + catálogo | `idp/` com `yarn dev`, `catalog/` ≥ 8 entidades, `Makefile portal-up` |
| **3** | Golden paths: 2 templates funcionais | `templates/python-fastapi-service/`, `templates/<outro>/`, `template_audit.py` OK |
| **4** | Capabilities e contratos | `docs/platform-contracts.md`, `docs/capability-catalog.md`, RFC/ADR, `catalog_validator.py` OK |
| **5** | Métricas e evolução | `docs/metrics.md`, `platform_metrics.py`, dashboard Grafana, `docs/platform-roadmap.md` |

---

## Pré-requisitos

Antes da parte 1:

- Leituras dos 4 blocos.
- Node 20+, yarn, Python 3.12, Docker, `make`.
- Conta GitHub com permissão para criar repositórios (para Scaffolder publicar).
- Opcional: Grafana local (docker compose) para dashboard.

---

## Critérios globais

Para cada parte, você produz **PR único** no repositório `orbita-idp`. Eles são avaliados por:

1. **Artefatos concretos** (o material requerido).
2. **Decisões documentadas** (por que esta escolha?).
3. **Rastreabilidade** (uma decisão na Parte 1 se reflete em escolhas da Parte 3).
4. **Valor ao cliente interno** (os engenheiros da OrbitaTech usariam isso de verdade?).

---

## Cronograma sugerido (12 dias)

| Dia | Parte | Horas |
|-----|-------|-------|
| 1-2 | Parte 1 | ~6h |
| 3-5 | Parte 2 | ~10h |
| 6-8 | Parte 3 | ~12h |
| 9-10 | Parte 4 | ~6h |
| 11-12 | Parte 5 | ~6h |

Total ~40h — alinha com carga prática do módulo.

---

## Antes de começar: cria base

```bash
mkdir orbita-idp && cd orbita-idp
git init
python -m venv .venv && source .venv/bin/activate
pip install -r ../requirements.txt

mkdir -p docs scripts templates catalog idp data

cat > Makefile <<'EOF'
.PHONY: portal-up catalog-validate template-test metrics-report nps-report

portal-up:
	cd idp && yarn dev

catalog-validate:
	python ../bloco-3/catalog_validator.py catalog/

template-test:
	python ../bloco-2/template_audit.py templates/python-fastapi-service

metrics-report:
	python ../bloco-4/platform_metrics.py \
		--deployments data/deployments.csv \
		--leadtime    data/leadtime.csv \
		--incidents   data/incidents.csv \
		--survey      data/survey.csv
EOF
```

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Exercícios resolvidos](../bloco-4/04-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Parte 1 — Estratégia, personas e Team Topologies](parte-1-estrategia.md) |

<!-- nav:end -->

# Parte 4 — Capabilities, tiers e contratos

**Objetivo.** Formalizar o que a plataforma oferece (capability catalog), com tiers, SLOs internos, deprecation e governança (RFC/ADR).

**Pré-requisitos.** Partes 1-3 concluídas.

**Entregáveis em `orbita-idp/docs/`:**

1. `capability-catalog.md` — capability catalog com ≥ 4 capabilities.
2. `platform-contracts.md` — tiers (bronze/silver/gold) com SLO, preço, features.
3. `rfcs/000X-score-adoption.md` — ao menos 1 RFC escrita.
4. `adrs/0001-xxx.md` — ao menos 1 ADR.
5. `deprecations.md` — ao menos 1 deprecation declarada com cronograma.
6. `responsibility-matrix.md` — quem responde pelo quê.
7. `catalog/` passa em `catalog_validator.py`.

---

## 4.1 `capability-catalog.md`

Para cada capability:

```markdown
## postgres-db

| Atributo | Valor |
|----------|-------|
| Interface | CRD DatabaseClaim (K8s) + form no portal |
| SLO interno | provisao <= 10 min p95; availability >= 99.9% |
| Owner | platform-data |
| Tiers | bronze (1 replica, backup semanal), silver (HA standby, diario), gold (sync replication, PITR continuo) |
| Custo | bronze 1x (ref), silver 3x, gold 10x |
| Lifecycle | GA desde 2026-Q1 |
| Suporte | office hours ter/qui 10h; #platform-data |
```

Mínimo 4 capabilities: ex. `postgres-db`, `kafka-topic`, `service-workload`, `observability-stack`.

## 4.2 `platform-contracts.md`

Seções:

- Introdução: o que é contrato.
- Tiers: tabela completa com diferenças técnicas (Bloco 3).
- Como escolher tier (árvore de decisão simples).
- O que o squad dono compromete-se a fazer (tabela responsabilidade).
- O que a plataforma compromete-se a fazer.
- SLOs internos (quais métricas, janela, ação quando violado).

## 4.3 RFC

Escreva uma RFC real (não `TODO:`). Exemplos:
- Adotar Score.dev.
- Introduzir `kafka-topic` como capability.
- Deprecar template `flask-service`.

Use o template do Bloco 3 (§3.7.1).

## 4.4 ADR

Registre pelo menos 1 ADR dentro de um dos serviços gerados (Parte 3). Ex.: "ADR-001: uso de pgBouncer em tier-gold".

## 4.5 Deprecation

Declare ao menos 1 item a deprecar. Template no Bloco 3. Inclui:
- Motivo.
- Cronograma (≥ 6 meses).
- Substituto.
- Plano de migração.
- Consequência se não migrar.

## 4.6 Matriz de responsabilidade

```markdown
## Responsabilidade

| Ação                                        | Squad dono | Platform Team |
|---------------------------------------------|:----------:|:-------------:|
| Decidir roadmap do servico                  | X          |               |
| On-call 24x7 (se tier gold)                 | X          |               |
| Escolher tier                               | X          |               |
| Manter base image hardened                  |            | X             |
| Manter golden path                          |            | X             |
| Operar cluster K8s                          |            | X             |
| Corrigir CVE no codigo do servico           | X          |               |
| Corrigir CVE na base image                  |            | X             |
| Aprovar mudanca de schema DB                | X          |               |
| Prover DB (infra)                           |            | X             |
```

---

## Critérios de aceitação da Parte 4

- [ ] `capability-catalog.md` com ≥ 4 capabilities; cada uma com SLO, tiers, owner, suporte.
- [ ] `platform-contracts.md` define 3 tiers claramente.
- [ ] ≥ 1 RFC publicada em `docs/rfcs/`.
- [ ] ≥ 1 ADR em algum serviço gerado.
- [ ] ≥ 1 deprecation declarada com cronograma explícito.
- [ ] `responsibility-matrix.md` presente.
- [ ] `make catalog-validate` exit 0.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Golden paths: dois templates funcionais](parte-3-golden-paths.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Parte 5 — Métricas, survey e evolução](parte-5-metricas.md) |

<!-- nav:end -->

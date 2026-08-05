# Entrega Avaliativa do Módulo 4

**Módulo:** Entrega Contínua (5h)
**Cenário:** LogiTrack — ver [00-cenario-pbl.md](00-cenario-pbl.md)

---

## Objetivo da entrega

Construir o **pipeline de entrega contínua completo** de um serviço da LogiTrack (o serviço de **Tracking API**, fornecido nos exercícios progressivos), cobrindo:

1. **Deployment pipeline multi-estágio** com promoção de artefato único.
2. **Estratégia de release** (Feature Flag + Blue-Green ou Canary) documentada e parcialmente implementada.
3. **Plano de rollback** documentado com simulação.
4. **Documento de estratégia** articulando tudo e conectando às **métricas DORA**.

Diferente do Módulo 3 (testes), o foco aqui é no **pipeline e nas políticas de release**. Código novo é mínimo — o valor está nas decisões de engenharia.

---

## O que entregar

### 1. Repositório GitHub com a aplicação + pipeline

Repositório contendo:

```
logitrack-tracking/
├── src/tracking/
│   ├── __init__.py
│   ├── api.py              # FastAPI app
│   ├── config.py           # configuração por ambiente (pydantic-settings)
│   ├── features.py         # feature flags
│   └── health.py           # liveness e readiness
├── tests/
│   ├── unit/
│   └── smoke/              # smoke tests pós-deploy
├── migrations/             # SQL versionado
├── scripts/
│   ├── deploy.sh           # (ou ansible/terraform ainda preview)
│   └── rollback.sh
├── .github/workflows/
│   ├── ci.yml              # pipeline CI (herdado do Módulo 3)
│   └── cd.yml              # pipeline CD (foco deste módulo)
├── docs/
│   ├── estrategia-release.md   # documento principal
│   ├── runbook-rollback.md
│   └── adr/                # pelo menos 2 ADRs (Architecture Decision Records)
├── pyproject.toml
├── requirements.txt
├── VERSION
└── README.md
```

### 2. Workflow `cd.yml` — Deployment Pipeline funcional

O arquivo `.github/workflows/cd.yml` deve:

- **Construir o artefato UMA vez** (build stage) e publicá-lo como release do GitHub (ou artefato de workflow).
- **Promover** o mesmo artefato por **3 estágios**: `dev` → `staging` → `production`.
- Cada estágio deve ter **critério explícito** de promoção (ex.: smoke test passou; aprovação manual para prod).
- **Usar GitHub Environments** com aprovação manual em pelo menos um estágio.
- **Taguear** a versão com **semver** ao promover para production (ex.: `v1.4.2`).

### 3. Feature Flags implementadas

Pelo menos **2 feature flags** reais no código:

- **1 flag de release**: ativa progressivamente uma feature "nova".
- **1 flag operacional** (kill switch): desliga rapidamente um comportamento se algo der errado (ex.: desabilitar chamada a serviço externo).

A configuração da flag deve vir de **variável de ambiente** ou arquivo — nada de código hardcoded.

### 4. Estratégia de release documentada

`docs/estrategia-release.md` (2 a 3 páginas) descrevendo:

1. **Escolha da estratégia** (Blue-Green, Canary, Rolling ou combinação). **Por quê** ela é adequada à LogiTrack.
2. **Fluxo completo** ilustrado com diagrama Mermaid.
3. **Critérios de promoção** de um estágio ao próximo.
4. **Critérios de rollback automatizado** (ex.: taxa de 5xx > X% nos últimos Y min → rollback).
5. **Tratamento de migrations de banco** com padrão **expand/contract**.
6. **Riscos e mitigações** conhecidos.

### 5. Runbook de rollback

`docs/runbook-rollback.md` (1 página) com:

- Cenários de rollback: "último deploy quebrou", "regressão de comportamento detectada após 2h", "feature flag causando caos".
- **Comandos exatos** para cada cenário.
- **Decisão explícita**: quando NÃO fazer rollback (ex.: migrations irreversíveis; preferir forward-fix).

### 6. Dois ADRs (Architecture Decision Records)

Em `docs/adr/`:

- **ADR 001 — Artefato imutável e promoção entre ambientes**: justificar o "build once, deploy many".
- **ADR 002 — Estratégia de release escolhida**: registrar a escolha técnica e alternativas descartadas.

Formato sugerido: [adr.github.io](https://adr.github.io/) (Título, Status, Contexto, Decisão, Consequências).

### 7. Evidências

Dentro do README do repositório, links diretos para:

- Run de CD **passando** (promoção até staging).
- Run de CD **com rollback automatizado** acionado (pode ser forçado com commit proposital quebrado).
- **Tag de versão** criada pelo pipeline (ex.: `v1.0.0`).

---

## Critérios de avaliação

| Critério | Peso | O que se espera |
|----------|------|------------------|
| **Pipeline multi-estágio com artefato único** | 20% | Build once, promote many. Artefato do `build` é o MESMO que vai para production. |
| **Estratégia de release implementada** | 15% | Feature flag funciona; código exercita as flags. |
| **Estratégia de release documentada** | 15% | Diagrama, critérios claros de promoção, trade-offs discutidos. |
| **Runbook de rollback** | 10% | Comandos concretos; distingue casos reversíveis de forward-fix. |
| **ADRs** | 10% | 2 ADRs coerentes, alternativas consideradas. |
| **Smoke tests pós-deploy** | 10% | Pelo menos 3 smoke tests automatizados validando o deploy. |
| **Conexão com DORA** | 10% | Documento cita e projeta ganhos em DF, LT, CFR, MTTR. |
| **Reconhece limites** | 10% | Admite o que **não** cabe em 5h (ex.: "canary real precisa de proxy L7 que fica para Mod. 7"). |

---

## Formato e prazo

- **Formato:** link do repositório GitHub com todo o material.
- **README** deve conter:
  - Instruções de setup.
  - Diagrama do pipeline.
  - Links para evidências (runs, tags, PR de rollback).
- **Prazo:** conforme definido pelo professor. Sugestão: **1 semana após o encerramento do módulo**.

---

## Dicas

- **Comece pelo exercício progressivo Parte 2** — ele já entrega o esqueleto da aplicação.
- **Não tente fazer canary real** sem proxy (isso é Módulo 7). Canary **simulado** com feature flag percentual é aceito.
- **Use GitHub Environments** — permite aprovação manual, secrets por ambiente e histórico de deploys gratuitamente.
- **Migrations** são a parte mais escorregadia da CD. Foco em 1 migration simples demonstrando **expand/contract**.
- **Admita onde o Módulo 5/6/7 entrará** — isso é **maturidade técnica**, não fraqueza.
- **Use Conventional Commits** desde o primeiro commit — facilita versionamento automático.

---

## Referência rápida do módulo

- [Cenário PBL — LogiTrack](00-cenario-pbl.md)
- [Bloco 1 — CI / CDelivery / CDeployment](bloco-1/01-ci-cd-deployment.md)
- [Bloco 2 — Deployment Pipeline](bloco-2/02-deployment-pipeline.md)
- [Bloco 3 — Estratégias de Release](bloco-3/03-estrategias-release.md)
- [Bloco 4 — Release Engineering](bloco-4/04-release-engineering.md)
- [Exercícios progressivos](exercicios-progressivos/)
- [Referências bibliográficas](referencias.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Plano de Transformação e Projeção DORA](exercicios-progressivos/parte-5-plano-transformacao.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](README.md) | **Próximo →**<br>[Referências Bibliográficas — Módulo 4](referencias.md) |

<!-- nav:end -->

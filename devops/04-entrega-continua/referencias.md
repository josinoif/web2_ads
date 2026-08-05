# Referências Bibliográficas — Módulo 4

Material de apoio ao Módulo 4 — Entrega Contínua.

---

## Livros centrais do módulo

### 1. Continuous Delivery (Entrega Contínua)

- **Autores:** Jez Humble, David Farley
- **Título em português:** *Entrega Contínua: como entregar software de forma confiável e rápida*
- **Arquivo de referência:** `devops/books/Entrega Contínua - Como Entregar Software de Forma Rápida e Confiável - Auto (Jez Humble).pdf`

**Uso no módulo:**

- **Texto canônico** sobre entrega contínua. Leitura obrigatória.
- Cap. 1 (*O problema de entregar software*) — contexto histórico do "projeto de integração" eterno.
- Cap. 5 (*Anatomia do pipeline de entrega*) — base do Bloco 2.
- Cap. 10 (*Estratégias de release*) — base do Bloco 3.
- Cap. 13 (*Gerenciando componentes e dependências*) — artefatos imutáveis.

**Capítulos sugeridos:** 1, 5, 8, 10, 12, 13.

---

### 2. The DevOps Handbook

- **Autores:** Gene Kim, Jez Humble, Patrick Debois, John Willis
- **Arquivo de referência:** `devops/books/DevOps_Handbook_Intro_Part1_Part2.pdf`

**Uso no módulo:**

- Cap. 9 (*Create the Foundations of Our Deployment Pipeline*).
- Cap. 12 (*Automate and Enable Low-Risk Releases*) — base do Bloco 3.
- Cap. 14 (*Create Telemetry to Enable Seeing Problems and Solving Them*) — feedback de deploy.

---

### 3. Accelerate — The Science of Lean Software and DevOps

- **Autores:** Nicole Forsgren, Jez Humble, Gene Kim
- **Referência externa (pesquisa DORA).**

**Uso no módulo:**

- Origem rigorosa das **métricas DORA** (Deployment Frequency, Lead Time, CFR, MTTR).
- Pesquisa empírica conectando práticas de CD a performance de negócio.
- Referência obrigatória para defender métricas na entrega avaliativa.

> Versão em português: *Accelerate — A ciência por trás do alto desempenho de organizações de tecnologia* (Alta Books).

---

### 4. DevOps na Prática (Casa do Código)

- **Arquivo:** `devops/books/DevOps na Prática - Entrega de Software Confiável e Automatizada - Autor (Casa do Código).pdf`

**Uso no módulo:**

- Conteúdo em português sobre pipeline, ambientes, rollback.
- Exemplos práticos de deploy em cenários reais.

---

## Obras complementares

### 5. Release It! — Michael T. Nygard

- **Editora:** Pragmatic Bookshelf, 2ª ed., 2018.
- **Uso:** padrões de projeto para sistemas que precisam estar em produção 24×7 — circuit breaker, bulkhead, timeouts. Crítico para deploy seguro.

### 6. Google SRE Book — Beyer, Jones, Petoff, Murphy

- **Uso:** Cap. 8 (*Release Engineering*) — como o Google pensa releases em escala. Cap. 21 (*Handling Overload*) e Cap. 22 (*Addressing Cascading Failures*).
- **Link:** [sre.google/books](https://sre.google/books/).

### 7. "Feature Toggles" — Pete Hodgson / Martin Fowler (2017)

- **Link:** [martinfowler.com/articles/feature-toggles.html](https://martinfowler.com/articles/feature-toggles.html)
- **Uso:** texto canônico sobre feature flags — os 4 tipos (Release, Experiment, Ops, Permission). Base do Bloco 3.

### 8. "BlueGreenDeployment" — Martin Fowler (2010)

- **Link:** [martinfowler.com/bliki/BlueGreenDeployment.html](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- **Uso:** definição canônica de Blue-Green.

### 9. "CanaryRelease" — Danilo Sato / Martin Fowler (2014)

- **Link:** [martinfowler.com/bliki/CanaryRelease.html](https://martinfowler.com/bliki/CanaryRelease.html)
- **Uso:** definição canônica de Canary Release.

### 10. "ParallelChange" (Expand/Contract) — Danilo Sato (2014)

- **Link:** [martinfowler.com/bliki/ParallelChange.html](https://martinfowler.com/bliki/ParallelChange.html)
- **Uso:** padrão fundamental para migrations compatíveis com CD.

---

## Documentação oficial de ferramentas

### GitHub Actions — Environments e Reviewers

- **Link:** [docs.github.com/en/actions/deployment/targeting-different-environments](https://docs.github.com/en/actions/deployment/targeting-different-environments)
- **Uso:** ambientes com aprovação manual, secrets por ambiente, proteção de branches.

### Semantic Versioning

- **Link:** [semver.org](https://semver.org/)
- **Uso:** política de versionamento usada no Bloco 4.

### Conventional Commits

- **Link:** [conventionalcommits.org](https://www.conventionalcommits.org/)
- **Uso:** base para automação de changelog e versionamento semântico.

### Unleash (Feature Flags open-source)

- **Link:** [docs.getunleash.io](https://docs.getunleash.io/)
- **Uso:** exemplo de plataforma real de feature flags (além da implementação in-house do Bloco 3).

### Argo Rollouts (Canary / Blue-Green em Kubernetes)

- **Link:** [argoproj.github.io/argo-rollouts](https://argoproj.github.io/argo-rollouts/)
- **Uso:** ferramenta madura — preview do Módulo 7 (Kubernetes).

---

## Artigos clássicos

- **Facebook (2017):** *"Rapid Release at Massive Scale"* — [engineering.fb.com/2017/08/31/web/rapid-release-at-massive-scale](https://engineering.fb.com/2017/08/31/web/rapid-release-at-massive-scale/).
- **Etsy (2011):** *"Deploys at Etsy"* — [codeascraft.com/2011/02/04/pushing-millions-of-lines-of-code-five-days-a-week](https://codeascraft.com/2011/02/04/pushing-millions-of-lines-of-code-five-days-a-week/).
- **Martin Fowler:** *"ContinuousDelivery"* — [martinfowler.com/bliki/ContinuousDelivery.html](https://martinfowler.com/bliki/ContinuousDelivery.html).

---

## Como citar nas suas entregas

Exemplos aceitos na disciplina:

> Conforme Humble e Farley (2014), a **Continuous Delivery** diferencia-se do *Continuous Deployment* pelo fato de que a decisão de ir a produção é **de negócio**, enquanto o software **está sempre pronto** para tal.

> A pesquisa DORA (Forsgren, Humble & Kim, 2018), em *Accelerate*, demonstra empiricamente correlação entre **Deployment Frequency** e performance organizacional.

> Fowler (2010), em *BlueGreenDeployment*, define a técnica como "dois ambientes de produção idênticos, onde apenas um recebe tráfego por vez".

---

## Referências rápidas na web

- **ContinuousDelivery (Fowler):** [martinfowler.com/bliki/ContinuousDelivery.html](https://martinfowler.com/bliki/ContinuousDelivery.html)
- **FeatureToggle (Fowler/Hodgson):** [martinfowler.com/articles/feature-toggles.html](https://martinfowler.com/articles/feature-toggles.html)
- **BlueGreenDeployment:** [martinfowler.com/bliki/BlueGreenDeployment.html](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- **CanaryRelease:** [martinfowler.com/bliki/CanaryRelease.html](https://martinfowler.com/bliki/CanaryRelease.html)
- **DORA State of DevOps:** [cloud.google.com/devops/state-of-devops](https://cloud.google.com/devops/state-of-devops)
- **Google SRE Book:** [sre.google/books](https://sre.google/books/)

---

*Use estas referências para fundamentar suas decisões na transformação do pipeline da LogiTrack e na entrega avaliativa.*

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega Avaliativa do Módulo 4](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](README.md) | **Próximo →**<br>[Módulo 5 — Containers](../05-containers/README.md) |

<!-- nav:end -->

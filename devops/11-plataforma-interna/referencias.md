# Referências — Módulo 11 (Plataforma Interna)

> Três camadas: **livros canônicos**, **whitepapers/padrões da indústria**, e **documentação oficial de ferramentas**.

---

## Livros canônicos

- **Skelton, M.; Pais, M.** *Team Topologies: Organizing Business and Technology Teams for Fast Flow.* IT Revolution, 2019. O livro que estruturou o vocabulário (stream-aligned, platform, complicated-subsystem, enabling; 3 modos de interação).
- **Salatino, M.** *Platform Engineering on Kubernetes.* Manning, 2023. Base prática recente; trata abstrações, golden paths, capabilities.
- **Forsgren, N.; Humble, J.; Kim, G.** *Accelerate.* IT Revolution, 2018. Base empírica DORA.
- **Kim, G. et al.** *The DevOps Handbook (2ª ed.).* IT Revolution, 2021. Revisão com plataforma interna em destaque.
- **Beyer, B. et al.** *The Site Reliability Workbook.* O'Reilly, 2018. Capítulo sobre times "customer SRE" e produto interno.
- **Cagan, M.** *Inspired: How to Create Tech Products Customers Love.* Wiley, 2017. Fundamento de "produto" aplicável à plataforma.
- **Reinertsen, D.** *The Principles of Product Development Flow.* Celeritas, 2009. Flow como foco do platform team.

## Whitepapers e padrões

- **CNCF Platforms White Paper** (2023) — [tag-app-delivery.cncf.io/whitepapers/platforms/](https://tag-app-delivery.cncf.io/whitepapers/platforms/). Referência CNCF para IDP.
- **CNCF Platform Maturity Model** (2023). Quatro níveis (provisional, operational, scalable, optimizing).
- **Humanitec — A Guide to Internal Developer Platforms** (2023). Vendor whitepaper, conceitual-mente denso.
- **Thoughtworks Technology Radar** — entradas "platform engineering product thinking". Atual e pragmática.
- **DORA State of DevOps Report** (anual, Google Cloud) — empírico, metodologicamente sólido.
- **Westrum, R.** "A Typology of Organisational Cultures" (2004). Base cultural para plataformas saudáveis.
- **Conway, M.** "How Do Committees Invent?" (1968). Lei de Conway — fundamento de por que plataforma muda arquitetura e vice-versa.

## Frameworks de produtividade

- **The SPACE of Developer Productivity** — Forsgren, Storey, Maddila, Zimmermann, Houck, Butler. *ACM Queue*, 2021. Fundação do SPACE.
- **DevEx** — Noda, Storey, Forsgren, Greiler. "DevEx: What Actually Drives Productivity." *ACM Queue*, 2023. Foca em friction, feedback, cognitive load.
- **GitHub Engineering Effectiveness** (blog series) — métricas aplicadas na prática.

## Ferramentas oficiais

- **Backstage** — [backstage.io](https://backstage.io/docs/overview/what-is-backstage). Projeto CNCF, criado pela Spotify.
- **Backstage Software Catalog** — [backstage.io/docs/features/software-catalog](https://backstage.io/docs/features/software-catalog/).
- **Backstage Scaffolder** — [backstage.io/docs/features/software-templates](https://backstage.io/docs/features/software-templates/).
- **Backstage TechDocs** — [backstage.io/docs/features/techdocs](https://backstage.io/docs/features/techdocs/).
- **Port** — [port.io](https://www.port.io/). Alternativa SaaS ao Backstage (conceitos semelhantes).
- **Cortex** — [cortex.io](https://www.cortex.io/). Outro competidor.
- **Humanitec** — [humanitec.com](https://humanitec.com/). Workload specs e platform orchestrator.
- **Score** — [score.dev](https://score.dev/). Spec aberta para workloads (Humanitec + CNCF sandbox).

## Golden paths e templating

- **Spotify Engineering Blog** — "How We Use Backstage for Golden Paths." Posts de 2020-2023.
- **Cookiecutter** — [cookiecutter.readthedocs.io](https://cookiecutter.readthedocs.io/). Alternativa leve a Scaffolder.
- **Copier** — [copier.readthedocs.io](https://copier.readthedocs.io/). Similar, com updates incrementais.
- **Backstage software templates repo** — [github.com/backstage/software-templates](https://github.com/backstage/software-templates).

## DORA e métricas

- **Four Keys** — [github.com/dora-team/fourkeys](https://github.com/dora-team/fourkeys). Referência aberta do Google para coletar as 4 métricas.
- **DevEx Research** — [getdx.com/research](https://getdx.com/research/). Compilado prático de DevEx.
- **Atlassian DevEx posts** — pragmáticos, citam armadilhas.

## Comunidade e leitura complementar

- **Platform Engineering Community** — [platformengineering.org](https://platformengineering.org/). Conteúdo, comunidade, conferências.
- **CNCF TAG App Delivery** — grupo que mantém whitepapers de plataforma.
- **Evan Bottcher** — "What I Talk About When I Talk About Platforms." Artigo-manifesto (2018).
- **Camille Fournier** — *The Manager's Path*. Boa base para tech lead de plataforma.

## Palestras

- **Manuel Pais** — várias palestras em DevOps Enterprise Summit.
- **Nicole Forsgren** — apresentações DORA.
- **Spotify Engineering** — talks do time que criou Backstage.
- **PlatformCon** — conferência anual dedicada.

## Para aprofundar

- **"Monolith to Microservices"** (Sam Newman) — base para entender por que a plataforma precisa abstrair.
- **"Working in Public"** (Nadia Eghbal) — insights sobre produtos para desenvolvedores.
- **"Shape Up"** (Ryan Singer / Basecamp) — ciclo de produto aplicado à plataforma.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega avaliativa — Módulo 11 (Plataforma Interna)](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](README.md) | **Próximo →**<br>[Módulo 12 — Capstone: da ideia à operação](../12-capstone/README.md) |

<!-- nav:end -->

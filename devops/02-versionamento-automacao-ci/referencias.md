# Referências Bibliográficas

Material de apoio ao Módulo 2 — Versionamento, Automação e CI. Utilize estas obras para aprofundar e para citar nas justificativas técnicas e na entrega avaliativa.

---

## Livros citados no contexto do módulo

### 1. Entrega Contínua (Continuous Delivery)

- **Autores:** Jez Humble, David Farley  
- **Título em português:** *Entrega Contínua: como entregar software de forma confiável e rápida*  
- **Editora:** Alta Books (edição em português)  
- **Título em inglês:** *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*

**Uso no módulo:**

- Integração contínua como base da entrega contínua; integração frequente reduz risco de integração tardia.
- Pipeline como “linha de produção de software”; build e deploy automatizados e confiáveis.
- Gestão de configuração e versionamento no fluxo de entrega.

**Sugestão de capítulos:** Integração contínua; Build e deploy; Gestão de configuração.

---

### 2. Site Reliability Engineering (SRE)

- **Organização/organizadores:** Google (O'Reilly)  
- **Título:** *Site Reliability Engineering* (O'Reilly)  
- **Referência comum:** “OReilly.Site.Reliability.Engineering” (como citado no contexto)

**Uso no módulo:**

- **Eliminating Toil** — automação para eliminar trabalho manual repetitivo.
- Simplicidade e automação como princípios; conexão com estratégias de branching e pipelines.
- Confiabilidade e métricas (preparação para DORA em módulos posteriores).

**Sugestão de capítulos:** Eliminating Toil; Introdução e princípios de SRE.

---

### 3. AWS Certified DevOps Engineer

- **Contexto:** Material de certificação e estudo para *AWS Certified DevOps Engineer*  
- **Título típico:** *AWS Certified DevOps Engineer - Professional* (ou equivalente da AWS)

**Uso no módulo:**

- **AWS CodeBuild** — build gerenciado na nuvem; `buildspec.yml`, fases de build, artefatos.
- Integração com CodePipeline, CodeCommit, S3.
- Visão de CI/CD em ambiente cloud (complementar a GitHub Actions e GitLab CI).

**Sugestão:** Seção sobre CodeBuild e pipelines de CI na AWS.

---

## Material da disciplina

- **Slides / material do Módulo 1:** `devops/books/slides.txt` — fundamentos de DevOps e cultura; conexão com automação e CI nos módulos seguintes.

---

## Onde encontrar os livros

- **Livrarias e bibliotecas:** Alta Books (Humble & Farley); O'Reilly (SRE); material AWS (site da AWS ou editoras de certificação).
- **PDFs e cópias:** Se o professor disponibilizar PDFs ou links, eles podem ser referenciados na pasta `devops/books/` ou em link indicado no AVA.
- **Citações:** Nas entregas, cite autor, título e ano (ex.: “Conforme Humble e Farley (2011), a integração contínua...”).

---

## Referências rápidas na web (complementares)

- **Semantic Versioning:** [semver.org](https://semver.org/)
- **GitHub Actions:** [docs.github.com/actions](https://docs.github.com/en/actions)
- **GitLab CI:** [docs.gitlab.com/ee/ci](https://docs.gitlab.com/ee/ci/)
- **DORA metrics:** State of DevOps Report (métricas de lead time, deployment frequency, change failure rate, MTTR — aprofundadas em módulos posteriores).

---

*Use estas referências para fundamentar suas respostas nos exercícios, na estratégia de versionamento e na justificativa técnica da entrega avaliativa.*

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega Avaliativa do Módulo 2](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](README.md) | **Próximo →**<br>[Módulo 3 — Testes Automatizados e Qualidade de Software](../03-testes-qualidade/README.md) |

<!-- nav:end -->

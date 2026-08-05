# Referências — Módulo 10 (SRE e Operações)

> Três camadas de referência: **livros canônicos** (vocabulário e modelos mentais), **manuais de prática** (como executar), e **documentação oficial de ferramentas**.

---

## Livros canônicos

- **Beyer, B.; Jones, C.; Petoff, J.; Murphy, N.** *Site Reliability Engineering: How Google Runs Production Systems.* O'Reilly, 2016. **[Gratuito online](https://sre.google/sre-book/table-of-contents/).** A obra que formalizou SRE.
- **Beyer, B. et al.** *The Site Reliability Workbook: Practical Ways to Implement SRE.* O'Reilly, 2018. **[Gratuito online](https://sre.google/workbook/table-of-contents/).** Complementa o primeiro com receitas práticas, error budget policies exemplares, capacity planning.
- **Adkins, H.; Beyer, B. et al.** *Building Secure and Reliable Systems.* O'Reilly, 2020. **[Gratuito online](https://google.github.io/building-secure-and-reliable-systems/).** Interseção de segurança e confiabilidade.
- **Rosenthal, C.; Jones, N.** *Chaos Engineering: System Resiliency in Practice.* O'Reilly, 2020. Fundação moderna do Chaos Engineering, por quem inventou a disciplina na Netflix.
- **Miles, R.** *Learning Chaos Engineering.* O'Reilly, 2019. Introdução acessível com exemplos práticos.
- **Blank-Edelman, D. (ed.).** *Seeking SRE.* O'Reilly, 2018. Antologia sobre SRE em diferentes contextos empresariais.
- **Majors, C.; Fong-Jones, L.; Miranda, G.** *Observability Engineering.* O'Reilly, 2022. Boa ponte com Módulo 8 para operar com observabilidade de verdade.
- **Forsgren, N.; Humble, J.; Kim, G.** *Accelerate.* IT Revolution, 2018. Base empírica das métricas DORA (ver Módulo 4).

## Padrões e frameworks

- **FEMA Incident Command System (ICS)** — [training.fema.gov/is/courseoverview.aspx?code=IS-100.c](https://training.fema.gov/is/courseoverview.aspx?code=IS-100.c). Referência mundial para comando de incidentes. A indústria tech adaptou (Google, PagerDuty, Facebook).
- **ICS adaptado para tech**: PagerDuty Incident Response Guide — [response.pagerduty.com](https://response.pagerduty.com/).
- **Etsy Debriefing Facilitation Guide** — [extfiles.etsy.com/DebriefingFacilitationGuide.pdf](https://extfiles.etsy.com/DebriefingFacilitationGuide.pdf). Referência histórica (John Allspaw et al.) sobre postmortems blameless.
- **Google Learning from Incidents** — [learningfromincidents.io](https://www.learningfromincidents.io/). Comunidade e papers sobre aprendizado organizacional.

## Chaos Engineering

- **Principles of Chaos Engineering** — [principlesofchaos.org](https://principlesofchaos.org/). Manifesto original.
- **Chaos Mesh documentation** — [chaos-mesh.org/docs](https://chaos-mesh.org/docs/). CNCF project, nativo Kubernetes.
- **Litmus Chaos documentation** — [litmuschaos.io](https://litmuschaos.io/). CNCF project alternativo.
- **AWS Fault Injection Simulator / Gremlin** — referências comerciais; não usaremos, mas bom conhecer.

## Disaster Recovery

- **Velero documentation** — [velero.io/docs](https://velero.io/docs/). Backup/restore nativo K8s.
- **Postgres PITR (Point-in-Time Recovery)** — [postgresql.org/docs/current/continuous-archiving.html](https://www.postgresql.org/docs/current/continuous-archiving.html).
- **NIST SP 800-34 Rev.1** — Contingency Planning Guide for Federal Information Systems. Boa referência para taxonomia de plano de DR.
- **AWS DR white paper** — [docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/). Os 4 padrões (Backup & Restore, Pilot Light, Warm Standby, Multi-site) valem como conceito mesmo fora da AWS.

## Gestão de incidentes e aprendizado

- **Google SRE Book cap. 14** — Managing Incidents.
- **Google SRE Book cap. 15** — Postmortem Culture.
- **Google SRE Workbook cap. 9** — Incident Response. Traz *incident command* adaptado.
- **Woods, D. et al.** *Behind Human Error.* Ashgate, 2010. Livro-referência em engenharia humana de falhas (base do pensamento blameless).
- **Dekker, S.** *The Field Guide to Understanding "Human Error".* Ashgate, 2014. Complementa Woods.

## Toil, on-call, sustentabilidade

- **SRE Workbook cap. 6** — Eliminating Toil.
- **SRE Book cap. 11** — Being On-Call.
- **Google docs — "Setting SLOs and Error Budgets"** — [landing.google.com/sre/workbook/chapters/error-budget-policy/](https://sre.google/workbook/chapters/error-budget-policy/).
- **Sidney Dekker** (vários papers) — "Just Culture" e como desenhar organizações que aprendem.

## Cultura e liderança

- **Edmondson, A.** *The Fearless Organization.* Wiley, 2018. Psychological safety como base para falar de erros sem medo.
- **Westrum, R.** "A Typology of Organisational Cultures." 2004. Modelo pathological/bureaucratic/generative muito citado em pós-mortems.

## Vídeos e palestras

- **SREcon** (USENIX) — qualquer ano; palestras canônicas (Cindy Sridharan, Charity Majors, Matt Klein).
- **"Meltdown at Netflix"** — palestras da Casey Rosenthal sobre como chaos engineering nasceu na Netflix.
- **Google Cloud Next** e **KubeCon** — trilhas de SRE.
- **Resilience Engineering Association** — [resilience-engineering-association.org](https://www.resilience-engineering-association.org/).

## Para aprofundar (pós-módulo)

- **Catchpoint SRE Report** (anual, gratuito) — radiografia da indústria.
- **Humble, J.** *The Art of DevOps* vídeos (vários).
- **Nicole Forsgren, Gene Kim** — qualquer publicação DORA/State of DevOps.
- **"Normal Accidents"** (Charles Perrault, 1984) — livro-clássico sobre acidentes em sistemas complexos; muda perspectiva.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega avaliativa — Módulo 10 (SRE e Operações)](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](README.md) | **Próximo →**<br>[Módulo 11 — Plataforma Interna de Desenvolvimento (IDP)](../11-plataforma-interna/README.md) |

<!-- nav:end -->

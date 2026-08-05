# Referências — Módulo 9 (DevSecOps)

> Combine **livros de fundamentos**, **padrões normativos** (NIST, CIS, OWASP) e **documentação oficial** das ferramentas. Segurança muda rápido — priorize fontes oficiais atualizadas.

---

## Livros

- **Rice, L.** *Container Security: Fundamental Technology Concepts That Protect Containerized Applications.* O'Reilly, 2020. Referência canônica para a camada de contêiner/host.
- **Bird, J.** *DevOpsSec: Securing Software Through Continuous Delivery.* O'Reilly, 2016 (gratuito). Uma introdução madura a segurança em pipelines modernos.
- **Hsu, T.; Stoddard, M.** *Practical Vulnerability Management.* No Starch Press, 2020. Como operar programas de gestão de vulnerabilidades sem afogar.
- **Felten, E. et al.** *Designing Secure Software.* No Starch Press, 2022. Princípios e padrões para arquitetura segura.
- **Bicking, L.; Kim, G.** *The DevOps Handbook* (2ª ed., 2021). Capítulo "Information Security" contextualiza Sec dentro de DevOps.

## Normas e padrões

- **NIST SSDF** (Secure Software Development Framework) — [SP 800-218](https://csrc.nist.gov/publications/detail/sp/800-218/final). O "currículo" que muitos governos e empresas adotam para prática segura.
- **OWASP Top 10** web — [owasp.org/Top10](https://owasp.org/Top10/).
- **OWASP API Security Top 10** — [owasp.org/API-Security](https://owasp.org/API-Security/).
- **OWASP SAMM** (Software Assurance Maturity Model) — [owaspsamm.org](https://owaspsamm.org/).
- **OWASP ASVS** (Application Security Verification Standard) — [owasp.org/asvs](https://owasp.org/www-project-application-security-verification-standard/).
- **CIS Docker Benchmark** — [cisecurity.org/benchmark/docker](https://www.cisecurity.org/benchmark/docker).
- **CIS Kubernetes Benchmark** — [cisecurity.org/benchmark/kubernetes](https://www.cisecurity.org/benchmark/kubernetes).
- **Kubernetes Pod Security Standards** — [kubernetes.io/docs/concepts/security/pod-security-standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/).
- **SLSA** (Supply-chain Levels for Software Artifacts) — [slsa.dev](https://slsa.dev/).
- **in-toto** — [in-toto.io](https://in-toto.io/). Atestações de etapas do pipeline.
- **LGPD** (Lei 13.709/2018) — [planalto.gov.br](http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm).

## Modelagem de ameaças

- Shostack, A. *Threat Modeling: Designing for Security.* Wiley, 2014. O livro-referência.
- OWASP Threat Modeling — [owasp.org/threat-modeling](https://owasp.org/www-community/Threat_Modeling).
- Microsoft **STRIDE** — [aka.ms/threatmodeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats).
- **LINDDUN** (privacidade) — [linddun.org](https://linddun.org/).

## Documentação oficial das ferramentas

- **Trivy** — [trivy.dev](https://trivy.dev/). Scanner universal (imagem, FS, repo git, IaC, K8s).
- **Syft** — [github.com/anchore/syft](https://github.com/anchore/syft). Geração de SBOM (SPDX, CycloneDX).
- **Grype** — [github.com/anchore/grype](https://github.com/anchore/grype). Vulnerabilidades em SBOM/imagem.
- **Semgrep** — [semgrep.dev/docs](https://semgrep.dev/docs/). SAST baseado em regras semânticas.
- **Bandit** — [bandit.readthedocs.io](https://bandit.readthedocs.io/). SAST específico para Python.
- **Gitleaks** — [gitleaks.io](https://github.com/gitleaks/gitleaks). Secrets detection.
- **pip-audit** — [github.com/pypa/pip-audit](https://github.com/pypa/pip-audit). SCA para Python.
- **Checkov** — [checkov.io](https://www.checkov.io/). IaC scan (Terraform, K8s, Dockerfile).
- **Cosign / Sigstore** — [sigstore.dev](https://www.sigstore.dev/). Assinatura e verificação de artefatos OCI.
- **Kyverno** — [kyverno.io](https://kyverno.io/). Admission controller declarativo para K8s.
- **OPA / Gatekeeper** — [open-policy-agent.org](https://www.openpolicyagent.org/) e [open-policy-agent.github.io/gatekeeper](https://open-policy-agent.github.io/gatekeeper/). Alternativa a Kyverno.
- **Sealed Secrets** — [github.com/bitnami-labs/sealed-secrets](https://github.com/bitnami-labs/sealed-secrets).
- **External Secrets Operator** — [external-secrets.io](https://external-secrets.io/).
- **HashiCorp Vault** — [developer.hashicorp.com/vault](https://developer.hashicorp.com/vault).

## Artigos e palestras

- **Executive Order 14028** (2021) — catalisador da adoção de SBOM nos EUA.
- **Google — "SLSA: End-to-End Supply Chain Security"** — [blog](https://slsa.dev/blog).
- **Datadog — "State of Application Security 2024/2025"** — reports anuais com dados reais.
- **Kim Zetter** — *Countdown to Zero Day* (Stuxnet) — contexto histórico de supply chain attack.
- **Solarwinds case study** — qualquer análise técnica pós-incidente mostra por que SBOM importa.

## Bases de dados de vulnerabilidades

- **NVD (NIST)** — [nvd.nist.gov](https://nvd.nist.gov/).
- **OSV (Google)** — [osv.dev](https://osv.dev/). Dados consolidados para open source.
- **GitHub Advisory Database** — [github.com/advisories](https://github.com/advisories).
- **Snyk Vulnerability DB** — [security.snyk.io](https://security.snyk.io/).

## Vídeos e cursos

- **OWASP** — canal no YouTube com gravações de AppSec USA/Europe/LATAM.
- **KubeCon + CloudNativeCon** — trilhas de segurança anuais, com foco em Kyverno, Sigstore, falco.
- **Kelsey Hightower** — palestras sobre secrets management e K8s security.

## Para aprofundar (pós-módulo)

- **Shostack, A.** *Threats: What Every Engineer Should Learn From Star Wars.* Wiley, 2023.
- **Anderson, R.** *Security Engineering* (3ª ed., 2020) — referência clássica; muito além de DevSecOps.
- **The Open Source Security Foundation (OpenSSF)** — [openssf.org](https://openssf.org/). Scorecards e guias.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega avaliativa — Módulo 9 (DevSecOps)](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](README.md) | **Próximo →**<br>[Módulo 10 — Site Reliability Engineering (SRE) e Operações](../10-sre-operacoes/README.md) |

<!-- nav:end -->

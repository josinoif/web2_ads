# Referências Bibliográficas — Módulo 6

Material de apoio ao Módulo 6 — Infraestrutura como Código (IaC).

---

## Livros centrais do módulo

### 1. Infrastructure as Code — Dynamic Systems for the Cloud Age

- **Autor:** Kief Morris
- **Editora:** O'Reilly Media, 3ª ed., 2024
- **Uso:** **livro-texto** deste módulo. Cap. 1-3 (conceitos e valores), 5-6 (declarativo, state), 8 (módulos), 17 (qualidade), 18 (governança e policy). Leitura fortemente recomendada.

### 2. Terraform: Up & Running — Writing Infrastructure as Code

- **Autor:** Yevgeniy (Jim) Brikman
- **Editora:** O'Reilly Media, 3ª ed., 2022
- **Uso:** **referência prática** de HCL e Terraform. 90% vale para **OpenTofu** (sintaxe praticamente idêntica). Cap. 3-6 indispensáveis.

### 3. Pulumi Up & Running

- **Autor:** (vários), editorias especializadas
- **Documentação oficial** preferível ao livro: [pulumi.com/docs/](https://www.pulumi.com/docs/)
- **Uso:** complementar ao Bloco 3.

### 4. Google SRE Book — Cap. 19 "Load Balancing at the Frontend" + Cap. 3 "Embracing Risk"

- **Link aberto:** [sre.google/books/](https://sre.google/books/)
- **Uso:** contexto de risco/mudança em infraestrutura; justifica rigor de PR/plan.

---

## Documentação oficial de ferramentas

### OpenTofu

- **Site:** [opentofu.org](https://opentofu.org/)
- **Docs:** [opentofu.org/docs/](https://opentofu.org/docs/)
- **Providers:** [registry.opentofu.org](https://registry.opentofu.org/)
- **Uso:** ferramenta do Bloco 2.

> OpenTofu é o **fork aberto do Terraform** após a mudança de licença da HashiCorp para BSL (agosto/2023). A sintaxe HCL é idêntica e a maior parte dos providers é compatível. Usamos OpenTofu por ser **software livre**; as mesmas páginas do Bloco 2 funcionam com `terraform` sem mudança.

### Terraform (HashiCorp)

- **Site:** [terraform.io](https://www.terraform.io/)
- **Docs:** [developer.hashicorp.com/terraform/docs](https://developer.hashicorp.com/terraform/docs)
- **Uso:** compatível com OpenTofu na maior parte do módulo.

### Pulumi

- **Site:** [pulumi.com](https://www.pulumi.com/)
- **Docs Python:** [pulumi.com/docs/languages-sdks/python/](https://www.pulumi.com/docs/languages-sdks/python/)
- **Provider Docker:** [pulumi.com/registry/packages/docker/](https://www.pulumi.com/registry/packages/docker/)
- **Uso:** ferramenta do Bloco 3.

### Providers utilizados

- **Docker provider (OpenTofu):** [registry.terraform.io/providers/kreuzwerker/docker/latest/docs](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs) — também funciona em OpenTofu.
- **Docker provider (Pulumi):** [pulumi.com/registry/packages/docker/](https://www.pulumi.com/registry/packages/docker/).

---

## Secrets e Policy

### SOPS (Mozilla)

- **Repositório:** [github.com/getsops/sops](https://github.com/getsops/sops)
- **Uso:** criptografia de arquivos YAML/JSON com chaves age/GPG/KMS. Alternativa 100% local.

### HashiCorp Vault

- **Docs:** [developer.hashicorp.com/vault/docs](https://developer.hashicorp.com/vault/docs)
- **Uso:** cofre de segredos. Citado no Bloco 4 como alternativa robusta.

### age

- **Repositório:** [github.com/FiloSottile/age](https://github.com/FiloSottile/age)
- **Uso:** ferramenta simples de criptografia assimétrica; usada com SOPS.

### Checkov

- **Site:** [checkov.io](https://www.checkov.io/)
- **Uso:** lint de Policy as Code para Terraform/OpenTofu/Pulumi/K8s.

### Open Policy Agent (OPA) + Rego

- **Site:** [openpolicyagent.org](https://www.openpolicyagent.org/)
- **Uso:** engine genérica de policy; integrável via `conftest` para IaC.

### Conftest

- **Repositório:** [github.com/open-policy-agent/conftest](https://github.com/open-policy-agent/conftest)
- **Uso:** aplicar policies Rego a arquivos de configuração (incluindo `tfplan.json`).

---

## Backends e registros de state

### MinIO (S3 compatível self-hosted)

- **Site:** [min.io](https://min.io/)
- **Uso:** backend S3 local para `tofu` state (Bloco 4).

### `tofu` HTTP backend

- **Docs:** [opentofu.org/docs/language/settings/backends/http/](https://opentofu.org/docs/language/settings/backends/http/)
- **Uso:** backend HTTP com locking — pode ser servido por um serviço Python mínimo self-hosted.

### GitLab Managed Terraform State

- **Docs:** [docs.gitlab.com/ee/user/infrastructure/iac/terraform_state.html](https://docs.gitlab.com/ee/user/infrastructure/iac/terraform_state.html)
- **Uso:** mencionado como opção se a empresa usa GitLab.

---

## Obras complementares

### The DevOps Handbook

- **Autores:** Kim, Humble, Debois, Willis
- **Editora:** IT Revolution, 2ª ed., 2021
- **Uso:** Cap. 10 (automation of environments) reforça o **porquê**.

### Accelerate

- **Autoras:** Nicole Forsgren, Jez Humble, Gene Kim
- **Editora:** IT Revolution, 2018
- **Uso:** conecta IaC à performance de engenharia (DORA).

### Team Topologies

- **Autores:** Skelton & Pais
- **Uso:** contexto para "platform team" — o que é a Nimbus dentro da fintech.

---

## Artigos e posts recomendados

- **HashiCorp** — *"What is Infrastructure as Code?"*: [hashicorp.com/resources/what-is-infrastructure-as-code](https://www.hashicorp.com/resources/what-is-infrastructure-as-code)
- **Martin Fowler** — *"InfrastructureAsCode"*: [martinfowler.com/bliki/InfrastructureAsCode.html](https://martinfowler.com/bliki/InfrastructureAsCode.html)
- **ThoughtWorks** — *"Architecture Decision Records"*: [thoughtworks.com/insights/blog/architecture-decision-records](https://www.thoughtworks.com/insights/blog/architecture-decision-records)
- **Atlassian** — *"GitOps: from guide to best practices"*: [atlassian.com/git/tutorials/gitops](https://www.atlassian.com/git/tutorials/gitops)
- **CNCF GitOps Working Group** — *"OpenGitOps Principles"*: [opengitops.dev](https://opengitops.dev/)

---

## Vídeos sugeridos

- **Mitchell Hashimoto** — *"Terraform: A Complete Guide"* (HashiConf archive).
- **Kief Morris** — talks em O'Reilly/Velocity sobre IaC.
- **Kelsey Hightower** — *"GitOps and Infrastructure as Code"* (KubeCon).

---

## Como citar nas suas entregas

Exemplos aceitos na disciplina:

> Morris (2024) define Infrastructure as Code como a prática de **versionar, revisar e testar infraestrutura** com os mesmos rigores aplicados a software de produção.

> A separação **plan × apply** em OpenTofu (adotada também por Terraform e Pulumi) operacionaliza o princípio de que **mudanças em infraestrutura devem ser simuladas e aprovadas antes de executadas** (Brikman, 2022).

> Seguimos a recomendação do Google SRE Book (Cap. 3) de tratar mudanças de infraestrutura como **experimentos com risco mensurável**, o que se materializa em Policy as Code aplicada no PR.

---

## Referências rápidas na web

- **OpenTofu registry:** [registry.opentofu.org](https://registry.opentofu.org/)
- **Pulumi registry:** [pulumi.com/registry/](https://www.pulumi.com/registry/)
- **HCL language spec:** [github.com/hashicorp/hcl](https://github.com/hashicorp/hcl)
- **CIS Benchmarks (policy base):** [cisecurity.org/cis-benchmarks](https://www.cisecurity.org/cis-benchmarks)

---

*Use estas referências para fundamentar suas decisões na entrega avaliativa do Módulo 6.*

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega Avaliativa do Módulo 6](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](README.md) | **Próximo →**<br>[Módulo 7 — Kubernetes](../07-kubernetes/README.md) |

<!-- nav:end -->

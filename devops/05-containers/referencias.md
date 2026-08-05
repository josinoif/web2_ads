# Referências Bibliográficas — Módulo 5

Material de apoio ao Módulo 5 — Containers.

---

## Livros centrais do módulo

### 1. Docker — Up & Running

- **Autores:** Sean P. Kane, Karl Matthias
- **Editora:** O'Reilly Media, 3ª ed., 2023
- **Uso:** referência **prática** de Docker. Cap. 1-2 (conceitos), 3-4 (imagens e containers), 7 (Dockerfile best practices). Leitura recomendada como livro-texto.

### 2. Container Security — Fundamental Technology Concepts that Protect Containerized Applications

- **Autora:** Liz Rice
- **Editora:** O'Reilly Media, 1ª ed., 2020
- **Uso:** **leitura canônica** sobre o que há por baixo. Cap. 3 (Control Groups), Cap. 4 (Container Namespaces), Cap. 5 (Container Isolation), Cap. 6 (Container Security and Rootkits), Cap. 8 (Image Security).

> Complemento: vídeo da autora *"What Have Namespaces Done For You Lately?"* ([YouTube](https://www.youtube.com/watch?v=MHv6cWjvQjM)) — excelente intro de 40 min.

### 3. Docker Deep Dive

- **Autor:** Nigel Poulton
- **Edição atualizada anualmente**
- **Uso:** cobre desde fundamentos até multi-host, networking e orchestration. Leitura linear recomendada.

### 4. The Kubernetes Book

- **Autor:** Nigel Poulton
- **Uso:** **apenas preview** — para o Módulo 7. Aqui, os Cap. 1-3 servem para entender o **destino** da imagem.

---

## Obras complementares

### 5. NIST SP 800-190 — Application Container Security Guide

- **Autores:** NIST (National Institute of Standards and Technology)
- **Ano:** 2017, revisado 2019
- **Link:** [nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
- **Uso:** guia **oficial** sobre riscos de segurança em containers. Base do Bloco 4.

### 6. CIS Docker Benchmark

- **Link:** [cisecurity.org/benchmark/docker](https://www.cisecurity.org/benchmark/docker)
- **Uso:** checklist de endurecimento para hosts e imagens Docker. Útil para auditoria.

### 7. OCI Specifications

- **Image Spec:** [github.com/opencontainers/image-spec](https://github.com/opencontainers/image-spec)
- **Runtime Spec:** [github.com/opencontainers/runtime-spec](https://github.com/opencontainers/runtime-spec)
- **Uso:** especificação formal. Lê-se seletivamente no Bloco 1.

---

## Documentação oficial de ferramentas

### Docker

- **Documentação oficial:** [docs.docker.com](https://docs.docker.com/)
- **Dockerfile reference:** [docs.docker.com/engine/reference/builder/](https://docs.docker.com/engine/reference/builder/)
- **Best practices:** [docs.docker.com/develop/develop-images/dockerfile_best-practices/](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

### Docker Compose

- **Referência de formato:** [docs.docker.com/compose/compose-file/](https://docs.docker.com/compose/compose-file/)
- Compose specification: [compose-spec.io](https://compose-spec.io/)

### Podman (alternativa rootless)

- **Site:** [podman.io](https://podman.io/)
- **Uso:** API idêntica a Docker, mas rootless por padrão. Muito citado no Bloco 4.

### GitHub Container Registry (GHCR)

- **Documentação:** [docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- **Uso:** registry que integra com o GitHub do Módulo 4.

### Ferramentas de segurança

- **Trivy** (scan de CVEs + SBOM): [aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy/)
- **Grype** (scan de CVEs): [github.com/anchore/grype](https://github.com/anchore/grype)
- **Syft** (SBOM): [github.com/anchore/syft](https://github.com/anchore/syft)
- **Hadolint** (lint de Dockerfile): [github.com/hadolint/hadolint](https://github.com/hadolint/hadolint)
- **Dive** (inspeção de camadas): [github.com/wagoodman/dive](https://github.com/wagoodman/dive)

---

## Artigos e posts recomendados

- **Julia Evans** — *"How containers work"* (zine e blog). [jvns.ca/blog/2016/10/10/what-even-is-a-container](https://jvns.ca/blog/2016/10/10/what-even-is-a-container/)
- **Jérôme Petazzoni** (ex-Docker) — *"Namespaces in operation"* LWN.
- **Google Cloud** — *"Best practices for building containers"*: [cloud.google.com/architecture/best-practices-for-building-containers](https://cloud.google.com/architecture/best-practices-for-building-containers)
- **Snyk** — *"10 Docker image security best practices"*: [snyk.io/blog/10-docker-image-security-best-practices](https://snyk.io/blog/10-docker-image-security-best-practices/)
- **Distroless** (Google): [github.com/GoogleContainerTools/distroless](https://github.com/GoogleContainerTools/distroless) — imagens mínimas de produção.

---

## Vídeos sugeridos

- Liz Rice — *"What Have Namespaces Done For You Lately?"* (40 min).
- Liz Rice — *"Containers From Scratch"* (CNCF KubeCon) — construir "container" com `unshare`, `chroot`, `cgroups`.
- Docker — *"Compose Watch"* (30 min) — rebuild automático em dev.

---

## Como citar nas suas entregas

Exemplos aceitos na disciplina:

> Rice (2020) enfatiza que a **isolação** em contêineres OCI se apoia em três primitivas do kernel Linux — **namespaces**, **cgroups** e **union filesystems** — e não em virtualização de hardware.

> A OCI Image Specification (2016) estabelece que uma imagem é composta por **camadas imutáveis** que são combinadas por um filesystem de união em runtime.

> O NIST SP 800-190 (2019) identifica como risco crítico a **execução de containers como root** no namespace de usuário do host — justificativa para `USER` não-root em todo Dockerfile de produção.

---

## Referências rápidas na web

- **Dockerfile best practices (Docker):** [docs.docker.com/develop/develop-images/dockerfile_best-practices/](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- **Distroless:** [github.com/GoogleContainerTools/distroless](https://github.com/GoogleContainerTools/distroless)
- **OWASP Docker Security Cheat Sheet:** [cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- **12-Factor App (preview do bloco 4 aplicado a contêineres):** [12factor.net](https://12factor.net/)

---

*Use estas referências para fundamentar suas decisões na containerização da CodeLab e na entrega avaliativa.*

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega Avaliativa do Módulo 5](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](README.md) | **Próximo →**<br>[Módulo 6 — Infraestrutura como Código (IaC)](../06-infraestrutura-como-codigo/README.md) |

<!-- nav:end -->

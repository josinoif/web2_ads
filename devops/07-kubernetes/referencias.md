# Referências Bibliográficas — Módulo 7

Material de apoio ao Módulo 7 — Kubernetes.

---

## Livros centrais do módulo

### 1. Kubernetes Up & Running

- **Autores:** Brendan Burns, Joe Beda, Kelsey Hightower, Lachlan Evenson
- **Editora:** O'Reilly Media, 3ª ed., 2022
- **Uso:** **livro-texto** da disciplina. Caps. 1-2 (motivação, arquitetura), 5-7 (Pods, labels, Service), 9-11 (Deployment, DaemonSet, Job), 14-15 (RBAC, policy).

### 2. The Kubernetes Book

- **Autor:** Nigel Poulton
- **Editora:** autopublicado (atualizado anualmente)
- **Uso:** referência de leitura ágil; ótima para fixar vocabulário. Capítulos curtos e diretos.

### 3. Programming Kubernetes

- **Autores:** Michael Hausenblas, Stefan Schimanski
- **Editora:** O'Reilly Media, 1ª ed., 2019
- **Uso:** aprofundamento em API, controllers, CRDs. Leitura **opcional** para alunos que querem ir além.

### 4. Site Reliability Engineering (SRE Book) — Google

- **Link aberto:** [sre.google/books/](https://sre.google/books/)
- **Uso:** Cap. 1 (contexto histórico de Borg → K8s); Cap. 12 (effective troubleshooting).

---

## Documentação oficial

### Kubernetes

- **Conceitos:** [kubernetes.io/docs/concepts/](https://kubernetes.io/docs/concepts/)
- **Tutoriais:** [kubernetes.io/docs/tutorials/](https://kubernetes.io/docs/tutorials/)
- **Reference da API:** [kubernetes.io/docs/reference/kubernetes-api/](https://kubernetes.io/docs/reference/kubernetes-api/)
- **`kubectl` cheatsheet:** [kubernetes.io/docs/reference/kubectl/cheatsheet/](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

### Helm

- **Docs:** [helm.sh/docs/](https://helm.sh/docs/)
- **Best practices:** [helm.sh/docs/chart_best_practices/](https://helm.sh/docs/chart_best_practices/)

### ArgoCD

- **Docs:** [argo-cd.readthedocs.io](https://argo-cd.readthedocs.io/)
- **Getting started:** [argo-cd.readthedocs.io/en/stable/getting_started/](https://argo-cd.readthedocs.io/en/stable/getting_started/)

### k3d e kind

- **k3d:** [k3d.io](https://k3d.io/)
- **kind:** [kind.sigs.k8s.io](https://kind.sigs.k8s.io/)

---

## CNCF Landscape & Benchmarks

- **CNCF Landscape:** [landscape.cncf.io](https://landscape.cncf.io/) — catálogo de ferramentas do ecossistema.
- **CIS Kubernetes Benchmark:** [cisecurity.org/benchmark/kubernetes](https://www.cisecurity.org/benchmark/kubernetes) — baseline de segurança.
- **NSA/CISA Kubernetes Hardening Guide:** [media.defense.gov/.../CTR_KUBERNETES_HARDENING_GUIDANCE.PDF](https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF).

---

## Ferramentas citadas no módulo

| Ferramenta | Uso | Link |
|------------|-----|------|
| `kubectl` | CLI oficial | [kubernetes.io](https://kubernetes.io/docs/reference/kubectl/) |
| `k3d` | K8s local via k3s-in-docker | [k3d.io](https://k3d.io/) |
| `kind` | K8s local via Docker | [kind.sigs.k8s.io](https://kind.sigs.k8s.io/) |
| `helm` | Gerenciador de pacotes | [helm.sh](https://helm.sh/) |
| `kustomize` | Overlays YAML (integrado ao kubectl) | [kustomize.io](https://kustomize.io/) |
| `argocd` | GitOps | [argo-cd.readthedocs.io](https://argo-cd.readthedocs.io/) |
| `k9s` | TUI para operação | [k9scli.io](https://k9scli.io/) |
| `stern` | Log tail multi-pod | [github.com/stern/stern](https://github.com/stern/stern) |
| `kubectx` / `kubens` | Troca rápida de contexto/namespace | [github.com/ahmetb/kubectx](https://github.com/ahmetb/kubectx) |
| `metrics-server` | Fornece métricas para HPA | [github.com/kubernetes-sigs/metrics-server](https://github.com/kubernetes-sigs/metrics-server) |
| `kube-state-metrics` | Métricas de estado de objetos | [github.com/kubernetes/kube-state-metrics](https://github.com/kubernetes/kube-state-metrics) |
| `cert-manager` | Certificados automáticos | [cert-manager.io](https://cert-manager.io/) |

---

## Artigos e posts recomendados

- **Google Cloud Blog** — *"Borg, Omega, and Kubernetes"* (Burns, Grant, Oppenheimer, Brewer, Wilkes): raízes do K8s.
- **Martin Fowler** — *"ContainerOrchestration"*: [martinfowler.com/bliki/ContainerOrchestration.html](https://martinfowler.com/bliki/ContainerOrchestration.html).
- **CNCF Blog** — *"GitOps: The Path to Operational Excellence"*.
- **Kelsey Hightower** — *"Kubernetes The Hard Way"* (github.com/kelseyhightower/kubernetes-the-hard-way) — para entender em profundidade, montando tudo manualmente.

---

## Vídeos sugeridos

- **TGIK** (Joe Beda) — série antiga, mas ouro puro sobre fundamentos.
- **KubeCon talks** (CNCF YouTube) — focar em "Introductory" track.
- **Kelsey Hightower** — *"Everything you wanted to know about Kubernetes but were afraid to ask"* (KubeCon).

---

## Obras complementares

### Cloud Native Patterns (Cornelia Davis)

- **Editora:** Manning, 2019
- **Uso:** padrões arquiteturais que K8s assume (twelve-factor, sidecar, circuit-breaker).

### Designing Data-Intensive Applications (Martin Kleppmann)

- **Editora:** O'Reilly, 2017
- **Uso:** contexto sobre **estado** — por que K8s começou como "stateless" e hoje endereça stateful, mas com cuidado.

### The DevOps Handbook (2ª ed.)

- **Uso:** cap. sobre operações enxutas em larga escala.

---

## Como citar nas suas entregas

Exemplos aceitos na disciplina:

> O modelo de **reconciliação** — controllers observando diferença entre estado desejado (etcd) e estado real — é a base conceitual que separa Kubernetes de orquestradores imperativos (Burns, Beda, Hightower & Evenson, 2022).

> Adotamos **namespaces por tenant** seguindo a recomendação de Poulton (2024) e os [CIS Benchmarks para Kubernetes](https://www.cisecurity.org/benchmark/kubernetes) para isolamento lógico entre universidades clientes da StreamCast.

> A escolha de **ArgoCD** como motor de GitOps segue o princípio *"git is the single source of truth"* consolidado pelo CNCF GitOps Working Group.

---

## Referências rápidas na web

- **kubernetes.io/docs**
- **helm.sh/docs**
- **argo-cd.readthedocs.io**
- **k3d.io**
- **CNCF landscape:** landscape.cncf.io
- **Awesome Kubernetes:** github.com/ramitsurana/awesome-kubernetes

---

*Use estas referências para fundamentar suas decisões na entrega avaliativa do Módulo 7.*

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Entrega Avaliativa do Módulo 7](entrega-avaliativa.md) | **↑ Índice**<br>[Módulo 7 — Kubernetes](README.md) | **Próximo →**<br>[Módulo 8 — Observabilidade](../08-observabilidade/README.md) |

<!-- nav:end -->

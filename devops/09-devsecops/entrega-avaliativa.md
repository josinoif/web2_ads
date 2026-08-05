# Entrega avaliativa — Módulo 9 (DevSecOps)

**Peso:** 20% da nota final da disciplina (ajuste conforme seu plano pedagógico).
**Formato:** repositório Git público (ou acessível à banca) com código, pipelines, manifestos e documentação.
**Prazo sugerido:** ao final da semana do módulo.
**Base:** evoluir o cluster/app do Módulo 7/8 (StreamCast/LogisGo/projeto próprio) ou recriar a aplicação **MedVault** (mínima) para este entregável.

---

## Objetivo

Endurecer um produto software **em todas as camadas do ciclo de vida** (código → dependências → imagem → manifesto → cluster → runtime), com **pipelines que falham** diante de vulnerabilidades não aceitas, artefatos **assinados e rastreáveis**, cluster com **segurança em profundidade**, e **resposta a incidente** documentada.

---

## Produto final

O repositório deve conter, ao menos:

1. **Modelagem de ameaças** (`docs/threat-model.md`) de uma jornada crítica, com diagrama, STRIDE por componente, mitigações propostas e aceitas.
2. **Aplicação demo** (FastAPI, reuso do Módulo 7/8 ou "MedVault-mini") com pelo menos 1 vulnerabilidade **proposital**, documentada e **corrigida** em commit separado.
3. **Dockerfile endurecido** (multi-stage, base distroless/alpine, `USER` não-root, `HEALTHCHECK`, sem pacotes extras) — demonstrar redução de vulnerabilidades vs. o Dockerfile "gordo" original.
4. **Pipeline CI completo** em GitHub Actions, com os gates:
   - **SAST**: Bandit + Semgrep (com config customizada).
   - **SCA**: pip-audit + Trivy FS.
   - **Secrets**: Gitleaks com baseline.
   - **IaC**: Checkov ou Trivy config.
   - **Image scan**: Trivy image.
   - **Gera SBOM**: Syft (CycloneDX + SPDX).
   - **Assina imagem**: cosign sign com chave OIDC (ou keyless).
   - **Verifica**: cosign verify no stage de deploy.
5. **Política de exceção**: arquivo `.trivyignore` e/ou `security-exceptions.yaml` com CVEs aceitas e **justificativas datadas**.
6. **Admission control** no cluster via **Kyverno**: ≥ 3 políticas (bloqueia imagem sem assinatura; exige `runAsNonRoot`; proíbe `:latest`).
7. **Cluster endurecido**:
   - Namespaces com **Pod Security Standards `restricted`** em dois ambientes (dev e prod).
   - **NetworkPolicy default-deny** + regras explícitas para tráfego necessário.
   - **RBAC**: ServiceAccounts por app, `Role` com verbos específicos, não usar `cluster-admin`.
   - **Audit logging** habilitado (via config do kube-apiserver; em k3d via flag).
8. **Secrets**: zero segredo em git ou ConfigMap em produção.
   - **Sealed Secrets** ou **External Secrets + Vault (em modo dev)** configurado.
   - Manifest de Secret "normal" está `.gitignore`ado; no git vai a versão selada/referência.
9. **SBOM e atestado**: SBOM publicado como release asset; cosign attest com `predicate-type=cyclonedx`.
10. **Runbook de incidente de segurança** (`docs/runbooks/security-incident.md`):
    - Papéis (IR lead, comunicações, LGPD officer).
    - Etapas: detectar, conter, erradicar, recuperar, lições aprendidas.
    - Modelo de comunicação a cliente e à ANPD (se aplicável).
11. **Plano SLSA** (`docs/slsa.md`): nível atual (geralmente L1 ou L2), lacunas para chegar a L3, cronograma.
12. **`Makefile`** com alvos: `scan`, `sbom`, `sign`, `verify`, `apply`, `policy-test`, `incident`.

---

## Entregáveis técnicos obrigatórios

### 1. Dockerfile endurecido

- [ ] Multi-stage: estágio `builder` separado do `runtime`.
- [ ] Imagem final `gcr.io/distroless/python3-debian12:nonroot` ou `python:3.12-alpine` com `adduser`.
- [ ] `USER` não-root (UID ≥ 10000).
- [ ] `HEALTHCHECK` funcional.
- [ ] `.dockerignore` exclui `.git`, `.venv`, `tests/`, `*.md`.
- [ ] OCI labels (`org.opencontainers.image.source`, `version`, `licenses`).
- [ ] **Demonstração** (tabela no README): Trivy encontra X vulnerabilidades na "v1 gorda" e Y (<= 5 `LOW`) na "v2 endurecida".

### 2. Pipeline

- [ ] Cada ferramenta roda em **job paralelo** com `continue-on-error: false` (falha o build).
- [ ] `trivy image --exit-code 1 --severity HIGH,CRITICAL`.
- [ ] Ao menos 1 CVE **aceita** está documentada em `.trivyignore` com motivo e data de revisão.
- [ ] Artefatos anexados à execução: `sbom.cdx.json`, `trivy-report.sarif`.
- [ ] Relatórios de SAST publicados como **GitHub Code Scanning** (formato SARIF).
- [ ] Cosign: imagem é assinada após passar em todos os gates; tag e digest publicados.

### 3. Cluster

- [ ] `kubectl get namespaces` mostra namespaces `medvault-dev`, `medvault-prod` com labels `pod-security.kubernetes.io/enforce=restricted`.
- [ ] `kubectl describe netpol` mostra `default-deny` + allows explícitos.
- [ ] `kubectl get clusterrolebinding` **não** tem `cluster-admin` concedido a ServiceAccounts de app.
- [ ] Kyverno/Gatekeeper em execução; políticas aplicadas listadas.
- [ ] Teste negativo: uma tentativa de deploy inseguro é **rejeitada** no `kubectl apply`, com log claro do motivo.

### 4. Secrets

- [ ] `kubeseal` funcional OU ESO + Vault em modo dev funcional.
- [ ] Demonstração: passo-a-passo em `docs/secrets.md` para **criar, atualizar e rotacionar** um segredo.
- [ ] `rg -i "DATABASE_URL|API_KEY|SECRET" -- :!**/SECURITY.md` não encontra valor real no repositório.

### 5. Incidente

- [ ] Runbook em `docs/runbooks/security-incident.md` segue template.
- [ ] Comunicação LGPD em `docs/comunicacao-incidente-lgpd.md` (modelo de notificação ao titular e à ANPD, prazos).
- [ ] Exercício de mesa (tabletop) documentado: dado um cenário (ex.: chave AWS vaza), time simula resposta por escrito.

---

## Rubrica de avaliação (100 pts)

| Eixo | Peso | Critérios principais |
|------|------|----------------------|
| **Threat model e design** | 10 | STRIDE por componente, mitigações priorizadas, decisões explícitas sobre risco aceito. |
| **Dockerfile e imagem** | 15 | Multi-stage, distroless/alpine, não-root, scan limpo; redução quantificada. |
| **Pipeline SAST/SCA/Secrets/IaC** | 20 | Jobs rodam e falham corretamente; exceções documentadas; SARIF integrado. |
| **SBOM e supply chain** | 15 | Syft + cosign sign + attest; verificação no deploy; plano SLSA. |
| **Admission e policy** | 10 | ≥ 3 políticas Kyverno efetivas; prova de bloqueio. |
| **Cluster endurecido** | 15 | PSS restricted, NetworkPolicy default-deny, RBAC mínimo, audit habilitado. |
| **Secrets management** | 10 | Sealed ou ESO funcionando; nenhum segredo em git. |
| **Runbook e resposta** | 5 | Runbook executável; tabletop documentado; comunicação LGPD. |

### Bônus (até +10 pts, não compensam faltas)

- Integração de **Falco** para runtime detection (detecta shell em container).
- Uso de **OpenSSF Scorecard** no repositório (CI adicional).
- Integração **OPA Gatekeeper** como alternativa/comparação a Kyverno.
- **Cosign keyless** (OIDC via GitHub Actions, sem gerenciar chave) com verificação no Kyverno via `policies.kyverno.io/verify-images`.
- Política automática de rotação de segredos via External Secrets + Vault.

---

## Formato de entrega

1. Link do repositório (GitHub/GitLab).
2. README na raiz com:
   - Arquitetura endurecida (diagrama).
   - Tabela "antes × depois" de vulnerabilidades.
   - Como rodar CI localmente (`act` ou comandos manuais).
   - Como aplicar no cluster (`make apply`).
   - Link para threat model, runbook, plano SLSA.
3. Para bancas presenciais, **gravação ≤ 10 min** executando: scan falha → correção → scan passa → deploy bloqueado por política → correção → deploy aceito.

---

## Checklist rápido antes de entregar

- [ ] `git log -p | grep -i -E "password|secret|token"` não mostra valor real.
- [ ] `trivy image` na imagem final não reporta `HIGH`/`CRITICAL` não justificada.
- [ ] `cosign verify` passa no artefato publicado.
- [ ] Cluster rejeita manifesto sem `runAsNonRoot: true`.
- [ ] Existe pelo menos 1 exceção de segurança documentada com data de revisão (< 90 dias).
- [ ] README inclui seção "limitações e riscos residuais" honesta.
- [ ] Runbook de incidente foi **lido em voz alta** por alguém que não o escreveu (teste de clareza).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Secrets management, incidente simulado e postmortem](exercicios-progressivos/parte-5-secrets-incidente.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](README.md) | **Próximo →**<br>[Referências — Módulo 9 (DevSecOps)](referencias.md) |

<!-- nav:end -->

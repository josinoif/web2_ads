# Bloco 1 — Exercícios resolvidos

> Leia primeiro [01-fundamentos-devsecops.md](./01-fundamentos-devsecops.md). Estes exercícios consolidam vocabulário e decisão de risco.

---

## Exercício 1 — Shift-left argumentado

**Enunciado.** A CTO da MedVault escreve num canal interno: "*Não posso parar o dev para rodar Bandit em toda PR. Só rodamos Trivy quando preparamos release. Isso basta, certo?*". Em 6 linhas, explique por que essa abordagem é frágil e proponha um caminho alternativo proporcional.

**Resposta esperada.**

Esperar o release significa que um commit inseguro feito hoje só aparece dias (ou semanas) depois, quando o contexto já foi esquecido e corrigi-lo exige re-imaginar a PR. Vulnerabilidades em dependências e *secrets* vazados **já foram expostos ao público** se o repo é aberto. Proposta proporcional: (1) **pre-commit** com Gitleaks + Bandit rápido (hook leve, 2 s); (2) **SAST em CI** apenas em arquivos alterados, bloqueando PR mas não o pipeline inteiro; (3) **Trivy a cada merge em main**, com resultado publicado como check do repositório. Nada disso "para o dev"; mantém o ciclo de feedback curto **e** barato.

---

## Exercício 2 — STRIDE aplicado

**Enunciado.** Para o endpoint `GET /prontuarios/{id}` da MedVault, descreva pelo menos **uma ameaça por letra do STRIDE**, com uma mitigação concreta para cada.

**Resposta.**

| Letra | Ameaça | Mitigação |
|-------|--------|-----------|
| **S** | Atacante reutiliza JWT vazado via log externo | TTL curto (≤ 15 min) + rotação de chave de assinatura; HttpOnly/Secure em cookies |
| **T** | Middleware intermediário reescreve campos no payload de saída | TLS mútuo entre api-gateway e `prontuario`; assinatura de resposta |
| **R** | Médico alega "eu não acessei prontuário X" | Log imutável com IP, user-id, trace_id; retenção 6 meses; append-only em bucket WORM |
| **I** | Response inclui CPF do paciente quando o contexto exige só nome | Projeção mínima no serializer (Pydantic com exclude); testes de contrato |
| **D** | Scraper repetindo `GET /prontuarios/{id}` com IDs sequenciais | Rate-limit por usuário + WAF + IDs não-incrementais (UUID/v4); detecção de enumeração |
| **E** | Médico da clínica A acessa `/prontuarios/` de paciente da clínica B (IDOR) | Autorização de **objeto** — verificar `paciente.tenant_id == medico.tenant_id` antes de retornar; testes automáticos de IDOR no CI |

Observação: o **E** é a vulnerabilidade mais comum em SaaS multi-tenant; caiu como A01 na OWASP API 2023.

---

## Exercício 3 — Priorizando com o catálogo

**Enunciado.** Dado o `threats.yaml` de exemplo do bloco, execute `python threat_catalog.py threats.yaml`. Identifique (a) a ameaça de maior risco, (b) as que estão "aberto alto", (c) qual decisão de priorização é razoável para o próximo sprint.

**Resposta esperada.**

Saída (aproximada):

```
Catalogo de Ameacas (STRIDE)
id      componente   categoria              likelihood impact risco status         descricao
T-010   prontuario   E - Elevation          H          H      9     in-progress    Medico de uma clinica acessa paciente de outra
T-001   auth         S - Spoofing           M          H      6     in-progress    Credencial roubada via phishing
T-002   auth         I - Info Disclosure    M          M      4     mitigated      JWT logado em erro expose claims

Total ameacas: 3
Alto risco em aberto (>=6 e nao mitigada): 2
  - T-010 [prontuario] Medico de uma clinica acessa paciente de outra (status: in-progress)
  - T-001 [auth] Credencial roubada via phishing (status: in-progress)
```

- **(a)** Maior risco: **T-010** (IDOR multi-tenant), risco 9.
- **(b)** Abertas alto: T-010 e T-001.
- **(c)** Priorização razoável: concluir T-010 **este sprint** (IDOR multi-tenant é *business-critical* para SaaS de saúde). T-001 em paralelo, mas depende de integração com provedor de MFA — pode ser um sprint adicional.

Decisão operacional: manter T-002 como `mitigated`, revisar trimestralmente.

---

## Exercício 4 — Mapear OWASP Top 10 a controles

**Enunciado.** A MedVault já tem alguns controles: (1) WAF no ingress, (2) TLS enforced, (3) code review com 2 aprovadores, (4) logs estruturados com `trace_id`, (5) RBAC K8s com namespaces. Para cada categoria da OWASP Top 10 Web 2021, indique se os controles **cobrem, cobrem parcialmente ou não cobrem** o risco principal e justifique em uma linha.

**Resposta.**

| # | Categoria | Cobertura | Justificativa |
|---|-----------|-----------|---------------|
| A01 | Broken Access Control | parcial | RBAC K8s é **infra**; não cobre autorização de objeto no app (IDOR) |
| A02 | Cryptographic Failures | parcial | TLS cobre em trânsito; faltam avaliações de cripto em repouso e hashes de senha |
| A03 | Injection | parcial | Code review ajuda, mas não garante; precisa SAST + parametrização |
| A04 | Insecure Design | não cobre | Nenhum controle cobre design; preciso threat modeling e ADRs |
| A05 | Security Misconfiguration | parcial | RBAC e WAF ajudam; falta scan de configuração (Checkov) |
| A06 | Vulnerable Components | não cobre | Nenhum SCA mencionado |
| A07 | Auth Failures | parcial | TLS ajuda em trânsito, mas nada cobre sessão, MFA, lockout |
| A08 | Integrity Failures | não cobre | Sem assinatura de imagem/SBOM |
| A09 | Logging/Monitoring Failures | cobre | Logs estruturados com `trace_id` + stack do Módulo 8 |
| A10 | SSRF | não cobre | Precisa sanitização e *allowlist* de URLs chamadas pelo backend |

**Lacunas grandes:** A04, A06, A08, A10. Priorize para os próximos sprints.

---

## Exercício 5 — Decidir risco

**Enunciado.** Um dev trouxe uma CVE `HIGH` em `jinja2 3.1.2` (SSTI se template vem de usuário). O time nunca renderiza template com conteúdo de usuário — usa só templates internos. Justifique por escrito uma decisão de **aceite** de risco e liste o mínimo que precisa registrar.

**Resposta.**

Decisão: **aceite** por 90 dias, revisão em 2026-07-20.

Registro obrigatório (`.trivyignore` e `SECURITY.md`):

- **CVE ID**: CVE-XXXX-XXXXX
- **Componente e versão**: `jinja2 3.1.2`
- **Gravidade original**: HIGH
- **Vetor de ataque**: requer template controlado por atacante.
- **Mitigação compensatória**: template engine recebe **apenas** templates estáticos do repo, versionados; nenhum endpoint aceita template de input.
- **Evidência**: grep no repo (`rg "Template\(" src/`) confirma nenhum uso com variável de entrada de usuário.
- **Responsável pela revisão**: squad Infra, em até 90 dias.
- **Plano de fallback**: atualizar para `jinja2 >= 3.1.4` no próximo upgrade rotineiro (quando `jinja2` sair com quebra de API aceitável).

**Por que aceitar é correto.** Bloquear sem contexto é tão ruim quanto ignorar: trava releases legítimos e adultera a percepção de risco. A aceitação **explícita** e documentada é a forma madura de conviver com CVEs em tempo real.

---

## Exercício 6 — Avaliar nível SLSA

**Enunciado.** Olhe para um repositório típico de graduação (`main` branch, CI em GitHub Actions, imagem publicada em GHCR, sem assinatura). Qual é o **nível SLSA** atual? O que falta para chegar a L2?

**Resposta.**

**Nível atual: L1 (Documented).**

- Build roda em script automatizado (GitHub Actions): atende L1.
- Proveniência: não gerada. L1 aceita "proveniência mínima" mesmo sem ser assinada; muitos repos ficam entre L0 e L1.

**Para L2 (Hosted build):**

1. Usar plataforma hospedada (GitHub Actions/GitLab CI/Cloud Build) — **já atendido**.
2. Gerar **proveniência assinada** automaticamente. Caminho mais prático: `slsa-framework/slsa-github-generator` + cosign.
3. Imagens/artefatos publicados com **digest** referenciado na proveniência.
4. Cadeia de verificação no deploy: verificar assinatura **antes** de aplicar.

**Caminho L2 → L3:** isolamento do runner (self-hosted em sandbox), builds herméticos, restrição de dependências externas durante build (proxy que só serve de cache assinado).

Nenhum repositório de graduação precisa estar em L3; L2 é meta realista de fim de semestre.

---

## Autoavaliação

- [ ] Explico shift-left e as etapas onde segurança se integra.
- [ ] Aplico STRIDE com mitigações concretas.
- [ ] Prioridade ameaças por risco (prob × impacto).
- [ ] Mapeio OWASP Top 10 a controles existentes e identifico lacunas.
- [ ] Documento aceite de risco com data de revisão e mitigação compensatória.
- [ ] Sei avaliar nível SLSA de um projeto e roteirizar subida de nível.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — Fundamentos de DevSecOps](01-fundamentos-devsecops.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](../README.md) | **Próximo →**<br>[Bloco 2 — Segurança do código e das dependências](../bloco-2/02-codigo-dependencias.md) |

<!-- nav:end -->

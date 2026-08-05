# Exercícios Resolvidos — Bloco 4

Exercícios do Bloco 4 ([Produção, Segurança, Registries e SBOM](04-producao-seguranca.md)).

---

## Exercício 1 — Tagging em produção

Um colega sugere a seguinte política de tagging:

> *"Publicamos sempre como `:latest` e também como `:main`. Em produção, puxamos `:latest`. Simples."*

Liste **5 problemas** dessa política e proponha alternativa.

### Solução

**Problemas:**

1. **`:latest` é mutável** — o que subiu hoje pode não ser o que sobe em rollback amanhã.
2. **Sem rastreabilidade** — dado um incidente, "qual versão estava rodando às 14h?" é impossível de responder.
3. **Rollback é ambíguo** — rollback para `:latest` pré-acidente exige saber qual era; `:latest` atual já é outro.
4. **Impossível imutabilidade** — qualquer push re-publica o mesmo tag; digest muda sob a mesma tag.
5. **Cache-miss injustificado** — Docker pode não detectar que houve mudança até invalidar cache; ou, pior, **pode reaproveitar em cenários onde deveria rebuildar**.
6. **Viola "Build Once, Deploy Many" do Módulo 4** — não dá para *promover* uma imagem por ambientes se a referência é mutável.

**Alternativa:**

- CI constrói com **três** tags: `sha-<curto>`, `vX.Y.Z` (quando em tag git), e opcional `main`.
- Produção puxa sempre por `vX.Y.Z@sha256:...` — imutável.
- `latest` só em dev/local.

```bash
# Produção (em Compose ou K8s):
image: ghcr.io/codelab/api:v0.3.0@sha256:abc123...

# Rollback inequívoco:
image: ghcr.io/codelab/api:v0.2.9@sha256:def456...
```

---

## Exercício 2 — Decodificando flags de `docker run`

Leia o comando abaixo e explique o efeito de **cada flag** em 1 linha. Identifique se é adequado para um runner da CodeLab.

```bash
docker run -d \
  --privileged \
  --network=host \
  -v /:/host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --user root \
  -e AWS_SECRET_ACCESS_KEY=AKIA... \
  ghcr.io/codelab/runner-python:latest \
  python /submissao/main.py
```

### Solução

| Flag | Efeito | Adequado? |
|------|--------|-----------|
| `-d` | background | ok |
| `--privileged` | **todas** capabilities + acesso a todos devices + desativa AppArmor/SELinux | **PROIBIDO** |
| `--network=host` | reutiliza rede do host (sem isolação de rede) | **PROIBIDO** para código não-confiável |
| `-v /:/host` | monta **raiz do host** como leitura-escrita | **PROIBIDO**; fuga trivial |
| `-v /var/run/docker.sock:/var/run/docker.sock` | acesso à API do Docker | **PROIBIDO** em runner (escalada total) |
| `--user root` | processo como UID 0 | **PROIBIDO** |
| `-e AWS_SECRET_ACCESS_KEY=...` | segredo no processo do container | **ERRO** — segredo embutido |
| `:latest` | tag mutável | **NÃO em produção** |

**Resumo brutal:** este comando concede acesso equivalente a root no host. Um código de aluno malicioso teria controle total da infraestrutura.

**Versão correta para um runner:**

```bash
docker run -d \
  --rm \
  --network=none \
  --read-only \
  --tmpfs /tmp:rw,size=64m,mode=1777 \
  --user 10001:10001 \
  --cap-drop=ALL \
  --security-opt=no-new-privileges:true \
  --pids-limit=50 \
  --memory=256m --memory-swap=256m \
  --cpus=1.0 \
  -v "/tmp/sub-${SUB_ID}:/submissao:ro" \
  ghcr.io/codelab/runner-python:v0.5.0@sha256:abc... \
  python /submissao/main.py
```

---

## Exercício 3 — Política de CVE

Você recebe do Trivy a seguinte lista para a imagem `api:v0.3.0`:

| CVE | Severity | Fixed version | Observação |
|-----|----------|---------------|------------|
| CVE-2024-A | CRITICAL | 1.1.0 | há fix disponível |
| CVE-2024-B | HIGH | 2.5.1 | há fix disponível |
| CVE-2024-C | HIGH | — | unfixed upstream |
| CVE-2024-D | MEDIUM | 3.0.0 | afeta lib de build-time apenas |
| CVE-2024-E | LOW | 1.0.2 | sem fix |

Defina a ação de pipeline para cada caso.

### Solução

| CVE | Ação | Justificativa |
|-----|------|----------------|
| A (CRITICAL fixable) | **Falha o build.** Atualizar a base ou a lib. | Política não-negociável. |
| B (HIGH fixable) | **Falha o build.** Atualizar. | Patch disponível; postergar é dívida. |
| C (HIGH unfixed) | **Trivy com `ignore-unfixed: true`**: não falha, mas registra. Criar issue de tracking. Se houver workaround, aplicar; se não, aceitar risco com data. | Você não pode consertar o que upstream não patchou. |
| D (MEDIUM, build-time apenas) | **Avaliar**: se a lib só está em builder-stage e não vai para imagem final, mitigação é multi-stage (já aplicada). Se vai para final, atualizar. | Bloco 2 — multi-stage resolve. |
| E (LOW unfixed) | **Registrar** e seguir. Adicionar ao `.trivyignore` com comentário + data revisão (trimestral). | LOW sem fix não deve bloquear produção. |

**Política escrita em texto (para README/ADR):**

> Builds de imagem falham em CVEs CRITICAL ou HIGH **com fix disponível**. CVEs unfixed são registrados e não bloqueiam, exceto CRITICAL com CVSS ≥ 9.8 **explorável remotamente**, que bloqueia independente de fix. `.trivyignore` é revisado trimestralmente em cerimônia formal.

---

## Exercício 4 — Gerando SBOM na mão

Você precisa saber qual versão de `urllib3` está em uma imagem publicada. Três formas, usando três ferramentas.

### Solução

**Forma 1 — Syft (SBOM offline):**

```bash
syft ghcr.io/codelab/api:v0.3.0 -o table | grep -i urllib3
```

**Forma 2 — pip dentro do container efêmero:**

```bash
docker run --rm --entrypoint pip ghcr.io/codelab/api:v0.3.0 show urllib3
```

**Forma 3 — extrair layer e grep:**

```bash
docker save ghcr.io/codelab/api:v0.3.0 -o /tmp/api.tar
mkdir -p /tmp/api && tar -xf /tmp/api.tar -C /tmp/api
# procurar metadata de pacote python (qualquer *.dist-info/METADATA)
find /tmp/api -name "METADATA" -path "*urllib3*" -exec grep Version {} \;
```

**Vantagem do SBOM publicado:** o mesmo `grep urllib3` roda sobre o arquivo `.spdx.json` sem precisar da imagem — resposta em ms. Vital em resposta a incidente com muitas imagens.

---

## Exercício 5 — Runner_isolation numa PR

Um PR altera o Dockerfile do `runner-python` para usar base distroless. No CI, você adiciona um **smoke test** que sobe o container temporariamente e roda `runner_isolation.py`. O container sobe com:

```bash
docker run -d --name smoke \
  --network=none --read-only --user 10001:10001 \
  --cap-drop=ALL --security-opt=no-new-privileges:true \
  --memory=256m --cpus=1.0 \
  ghcr.io/codelab/runner-python:sha-${GIT_SHA} sleep 20
```

O script reporta:

```
[PASS] network, readonly-fs, nao-root, cap-drop-all, cap-add-vazio, no-new-privileges,
       memory-limit, cpu-limit, not-privileged
[FAIL] [HIGH] pids-limit       PidsLimit=0. (esperado: 1 < n <= 100).
[FAIL] [MED]  tmpfs-tmp        Tmpfs=[]. (esperado: inclui '/tmp').
```

a) Quais flags estão faltando no `docker run`?
b) O build deve falhar?
c) Em K8s (Módulo 7), esses limites são definidos no mesmo lugar?

### Solução

**a)** Faltam:

- `--pids-limit=50` (ou outro valor ≤ 100)
- `--tmpfs /tmp:rw,size=64m,mode=1777`

**b)** `pids-limit` é **HIGH → build falha** (o Relatório.fatal é True quando há CRIT ou HIGH). `tmpfs` é MED → não é fatal sozinho. Neste caso, sim, build falha.

**c)** Em **Kubernetes**:

- **PidsLimit** → campo `spec.containers[].resources.limits."pids"` (em clusters com feature gate habilitado) ou via LimitRange no namespace.
- **Tmpfs** → via `volumes[].emptyDir.medium: Memory` e `mountPath: /tmp`.
- Não é idêntico, mas **toda flag `docker run`** tem um equivalente em Pod spec — não em linha de comando.

Em K8s, essas verificações seriam feitas por **admission controllers** (Kyverno, Gatekeeper). Detalhado no Módulo 7.

---

## Exercício 6 — Fechando o loop com o Módulo 4

Um workflow do Módulo 4 fazia:

```yaml
- Build wheel
- Upload artifact
- Promote to staging (downloads + deploys .whl)
- Promote to production (downloads + deploys .whl)
```

Agora, integrando containers, reescreva em alto nível (sem YAML) a nova sequência, destacando o que **muda** e o que **permanece**:

### Solução

| Etapa | Antes (Módulo 4) | Depois (Módulo 4 + Módulo 5) | Muda? |
|-------|------------|-------------------|--------|
| 1 | CI Commit Stage | CI Commit Stage | — |
| 2 | `python -m build` (wheel) | `docker buildx build` (imagem OCI) | **muda** |
| 3 | `actions/upload-artifact` do wheel | `docker push` ao registry com tags `sha-X` + digest | **muda** |
| 4 | Testes de aceitação contra a build | Testes de aceitação **dentro do container** | **muda o como** |
| 5 | **Scan de segredos no código** (já no Módulo 4) | **+ scan de CVE da imagem** (Trivy) e **SBOM** | **adiciona** |
| 6 | **Assinatura** do artefato (opcional) | Assinatura da **imagem** com cosign | **reforça** |
| 7 | Promote to Staging: deploy do wheel | Promote to Staging: **deploy da imagem pelo digest** | **muda** |
| 8 | Promote to Prod com approval gate | idem, igual ao digest de staging | **idem** |
| 9 | Smoke tests | Smoke tests (inclusive `runner_isolation.py` em runners) | **reforça** |
| 10 | Postmortem em falha | idem + "qual digest estava ativo" fica trivial de responder | **reforça** |

**O que **permanece**:** o princípio "**Build Once, Deploy Many**". A imagem com digest X construída no commit C é **a mesma** promovida para staging e depois produção. Nada é reconstruído.

**O que **muda**:** o artefato deixa de ser um `.whl` e vira uma imagem OCI. Mas a semântica do pipeline é idêntica. Isso é valor do alinhamento Módulo 4 → Módulo 5.

---

## Próximo passo

- Faça os **[exercícios progressivos](../exercicios-progressivos/)** — o módulo se integra aqui.
- [Voltar ao README do módulo](../README.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Produção, Segurança, Registries e SBOM](04-producao-seguranca.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](../README.md) | **Próximo →**<br>[Exercícios Progressivos — Módulo 5](../exercicios-progressivos/README.md) |

<!-- nav:end -->

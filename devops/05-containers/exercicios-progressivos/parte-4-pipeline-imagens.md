# Parte 4 — Pipeline de Imagens (CI com scan, SBOM, assinatura)

**Duração:** 90 a 150 minutos
**Pré-requisitos:** Partes 1 a 3 concluídas, Bloco 4 ([Produção e Segurança](../bloco-4/04-producao-seguranca.md)) estudado.

---

## Contexto

Você tem imagens funcionais (Parte 2) e um stack que roda local (Parte 3). Falta **publicar** cada imagem com rastreabilidade, scan, SBOM e assinatura — e amarrar tudo ao GitHub Container Registry, preservando as lições do Módulo 4.

---

## Tarefas

### 1. Preparar o repositório para publicação

- Repositório deve estar em uma **organização** ou **usuário** no GitHub com **Packages** habilitado.
- No `Settings > Actions > General` do repositório, verifique **Workflow permissions** = "Read and write".
- Alternativamente, no workflow, defina `permissions: packages: write` (o que fazemos aqui).

### 2. `hadolint` + `.hadolint.yaml`

Adicione um arquivo `.hadolint.yaml` configurando severidades:

```yaml
failure-threshold: warning
ignored:
  - DL3008  # usar versão específica de pacote apt — aceitamos com pin por base
trusted-registries:
  - ghcr.io
  - docker.io
  - gcr.io
```

### 3. Metadata e tagging

O workflow usa `docker/metadata-action@v5`. Garantir que os **3 tags** sejam produzidos:

- `sha-<curto>` — a cada push.
- `vX.Y.Z` — quando o evento é uma tag git semver.
- `main` — a cada merge em main (convenção; não usar em produção).

### 4. Workflow `.github/workflows/images.yml`

Crie o workflow **completo**. Requisitos:

- **Trigger**: push em `main`, push de tag `v*`, `pull_request`.
- **Matrix**: `api`, `worker`, `runner-python` (mínimo 3 imagens).
- **Passos** (mínimos):
  1. `actions/checkout@v4`
  2. `hadolint` no Dockerfile da matriz.
  3. `docker/setup-buildx-action@v3`.
  4. `docker/login-action@v3` para GHCR.
  5. `docker/metadata-action@v5` para tags e labels.
  6. `docker/build-push-action@v5` com:
     - `push: true` (exceto em PR).
     - `sbom: true`, `provenance: mode=max`.
     - `cache-from`/`cache-to`.
     - Build args `GIT_SHA`, `VERSION`.
  7. `aquasecurity/trivy-action` — severity CRITICAL,HIGH; `exit-code: "1"`; `ignore-unfixed: true`; SARIF out.
  8. `github/codeql-action/upload-sarif` para upload do scan ao Security tab (`if: always()`).
  9. `anchore/sbom-action@v0.15.0` gerando SBOM SPDX-JSON.
  10. `sigstore/cosign-installer@v3` + `cosign sign --yes` (somente fora de PR).

Use o exemplo completo do Bloco 4 como **guia** — adapte ao seu repositório.

### 5. Primeira execução

Faça push em branch de feature:

```bash
git checkout -b feat/pipeline-imagens
git add .github .hadolint.yaml
git commit -m "ci: pipeline de imagens com scan, sbom e cosign"
git push -u origin feat/pipeline-imagens
```

Abra PR. O workflow deve rodar **sem publicar** (porque é PR).

Depois do merge em `main`, o workflow deve:

- Publicar as 3 imagens no GHCR com tag `sha-...` e `main`.
- Subir SARIF ao Security tab.
- Publicar SBOMs como artefatos.

Verifique:

```bash
# Imagem visível?
docker pull ghcr.io/<org>/<repo>/api:sha-<curto>

# Digest
docker inspect ghcr.io/<org>/<repo>/api:sha-<curto> --format '{{index .RepoDigests 0}}'
```

### 6. Primeiro release versionado

Crie uma tag git semver:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Workflow roda novamente, gerando tags `v0.1.0` e `0.1` nas três imagens. Confira no GHCR.

### 7. Política de CVE em texto

Adicione `docs/politica-cve.md`:

```markdown
# Política de CVE — Imagens CodeLab

## Regras (resumo)

- Builds falham em CVE **CRITICAL** ou **HIGH** com fix disponível.
- `.trivyignore` exige justificativa datada; revisão trimestral.
- CVE unfixed ainda é registrado e **não** bloqueia build, exceto
  CRITICAL com CVSS ≥ 9.8 explorável remotamente.

## Processo

1. Trivy roda no CI a cada build.
2. SARIF vai para Security tab.
3. Time SRE analisa semanalmente CVEs unfixed.
4. `.trivyignore` revisado em cerimônia trimestral com engenharia + segurança.
```

### 8. ADR-002 — Estratégia de isolamento do runner

Em `docs/adr/002-isolamento-runner.md`:

```markdown
# ADR-002: Estratégia de isolamento do runner

## Status
Aprovado em 2026-05-XX.

## Contexto

Runners executam código não-confiável de alunos. Risco de escape direto de
container é real, especialmente em kernel sem patches recentes. A CodeLab
hoje roda Docker padrão (não rootless, sem user-ns separado).

## Decisão

Adotamos, em runtime, o conjunto mínimo:

- `--network=none`
- `--read-only`
- `--tmpfs /tmp:rw,size=64m,mode=1777`
- `--user 10001:10001`
- `--cap-drop=ALL`
- `--security-opt=no-new-privileges:true`
- `--pids-limit=50`
- `--memory=256m --memory-swap=256m`
- `--cpus=1.0`

`runner_isolation.py` é rodado em pipeline como smoke test. Build falha em CRIT/HIGH.

## Consequências

- Bloqueia a maior parte dos vetores do NIST SP 800-190.
- **Não** bloqueia CVE de kernel. Mitigação futura: gVisor ou Kata (Mod 7/9).
- Código do aluno que precise abrir socket é **negado** — documentação para o aluno.

## Alternativas consideradas

- `--privileged` + `--cap-add=...` — rejeitado por princípio.
- gVisor — benefício real, mas complexidade de deploy alta; avaliar no Mod 7.
- Firecracker/Kata — overhead operacional + migração para orquestração; fora do escopo atual.
```

### 9. Smoke test `runner_isolation.py` no CI

Integre o script ao pipeline:

```yaml
      - name: Smoke isolamento do runner
        if: matrix.service == 'runner-python'
        run: |
          docker run -d --name smoke --rm \
            --network=none --read-only \
            --tmpfs /tmp:rw,size=32m,mode=1777 \
            --user 10001:10001 --cap-drop=ALL \
            --security-opt=no-new-privileges:true \
            --pids-limit=30 \
            --memory=128m --memory-swap=128m --cpus=0.5 \
            ghcr.io/${{ github.repository }}/runner-python:sha-$(echo ${{ github.sha }} | cut -c1-7) \
            sleep 30
          pip install --quiet pytest
          python scripts/runner_isolation.py smoke
          docker stop smoke
```

Ou, se usar cópia local do script em `scripts/runner_isolation.py` do repositório.

---

## O que entregar

1. **Código:**
   - `.github/workflows/images.yml`
   - `.hadolint.yaml`
   - `scripts/runner_isolation.py` (cópia do Bloco 4)
2. **Evidências:**
   - URL do workflow verde (após merge em main).
   - URL da imagem no GHCR (ex.: `https://ghcr.io/ORG/REPO/api`).
   - Screenshot do **Security tab** mostrando CVEs scaneados (mesmo que zero).
   - SBOM SPDX-JSON baixado dos artefatos.
   - Saída do cosign verify (se keyless).
3. **Documentação:**
   - `docs/politica-cve.md`
   - `docs/adr/002-isolamento-runner.md`

## Critérios de aceitação

- Workflow **falha** quando injetamos uma CVE CRITICAL via base antiga (teste exploratório opcional, mas valioso).
- 3 imagens (mínimo) publicadas com tags `sha-*` e `v0.1.0`.
- SBOM presente para **cada** imagem.
- Cosign signature verificável.
- ADR-002 reconhece limites (CVE de kernel, necessidade de runtime reforçado no futuro).

---

## Dicas e armadilhas

- Em **PR** de forks, `GITHUB_TOKEN` não tem `write:packages`. Workflow deve **não publicar** em PR — só buildar e scanear.
- `cosign keyless` depende de `id-token: write` no `permissions`. Sem isso, falha silenciosamente.
- `hadolint` pode reclamar de `DL3008` (apt sem versão) — configure o `.hadolint.yaml` para ignorar com justificativa.
- Se Trivy não acha a imagem, verifique se o push do build-push-action terminou **antes** do job de scan (ou rode scan localmente com `--input` no TAR).

---

## Próximo passo

Avance para a **[Parte 5 — Plano e limites](parte-5-plano-e-limites.md)** — fechamento do módulo.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Stack Local com Docker Compose](parte-3-compose-stack.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](../README.md) | **Próximo →**<br>[Parte 5 — Plano de Adoção e Reconhecimento de Limites](parte-5-plano-e-limites.md) |

<!-- nav:end -->

# Bloco 3 — Exercícios resolvidos

> Leia [03-imagens-supply-chain.md](./03-imagens-supply-chain.md) primeiro.

---

## Exercício 1 — Refatorar Dockerfile "gordo"

**Enunciado.** A MedVault tem este Dockerfile legado:

```dockerfile
FROM python:3.11
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y curl vim git
RUN pip install -r requirements.txt
CMD uvicorn main:app --host 0.0.0.0 --port 8000
```

Liste problemas e proponha versão endurecida.

**Resposta.**

Problemas:

1. Base `python:3.11` (full Debian, ~1 GB) sem pinagem precisa.
2. `COPY . .` leva `.git`, `.env`, testes, docs.
3. Instala `curl`, `vim`, `git` — úteis para atacante, inúteis em runtime.
4. Sem multi-stage — build tools ficam na imagem final.
5. `pip install` como root; depois roda como root.
6. Sem `USER`, sem `HEALTHCHECK`, sem LABEL.
7. `CMD` string (executa via shell) — prefira exec form.
8. Sem `.dockerignore` documentado.

Versão refatorada:

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -U pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY src/ src/

FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app
COPY --from=builder --chown=nonroot:nonroot /opt/venv /opt/venv
COPY --from=builder --chown=nonroot:nonroot /build/src /app/src
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD ["python","-c","import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/healthz')"]
ENTRYPOINT ["python","-m","uvicorn","src.main:app","--host","0.0.0.0","--port","8000"]

LABEL org.opencontainers.image.source="https://github.com/medvault/api" \
      org.opencontainers.image.licenses="Apache-2.0"
```

E `.dockerignore`:

```
.git
.env
.env.*
tests/
docs/
.venv
__pycache__
*.md
```

**Resultado esperado**: imagem ~80 MB, sem shell, sem `curl`/`vim`/`git`, sem pacotes root, Trivy quase silencioso.

---

## Exercício 2 — Auditoria com `dockerfile_audit.py`

**Enunciado.** Rode `python dockerfile_audit.py Dockerfile` sobre o Dockerfile original (ex. 1) e explique cada achado.

**Resposta esperada.**

Saída aproximada:

```
Auditoria Dockerfile
id        linha severidade mensagem
DOCK-008  3     high       USER root/0           # se a imagem estava rodando como root (via ausencia)
DOCK-002  0     high       Dockerfile nao define USER explicitamente
DOCK-003  4     medium     Instala pacote util a atacante: curl
DOCK-003  4     medium     Instala pacote util a atacante: vim
DOCK-003  4     medium     Instala pacote util a atacante: git
DOCK-004  3     medium     COPY . . sem .dockerignore ao lado
DOCK-005  0     low        Sem HEALTHCHECK
DOCK-006  0     low        Sem LABEL org.opencontainers.image.source
```

Interpretação:

- `DOCK-002/008`: maior impacto — imagem roda como root.
- `DOCK-003`: reduz ruído e superfície; ninguém em produção precisa de vim.
- `DOCK-004`: `.dockerignore` é barreira simples contra vazar `.env`/`.git`.
- `DOCK-005/006`: não são críticos, mas sinalizam baixa maturidade.

---

## Exercício 3 — Assinatura e verificação

**Enunciado.** Escreva (a) um trecho de workflow GitHub Actions que assina a imagem com cosign keyless após passar no Trivy, e (b) um comando shell que verifica a assinatura.

**Resposta.**

(a) Workflow (simplificado):

```yaml
permissions:
  id-token: write
  packages: write
  contents: read

steps:
  - uses: actions/checkout@v4
  - uses: docker/login-action@v3
    with:
      registry: ghcr.io
      username: ${{ github.actor }}
      password: ${{ secrets.GITHUB_TOKEN }}
  - uses: docker/build-push-action@v6
    id: build
    with:
      context: .
      push: true
      tags: ghcr.io/medvault/api:${{ github.sha }}
  - name: Trivy image
    uses: aquasecurity/trivy-action@master
    with:
      image-ref: ghcr.io/medvault/api@${{ steps.build.outputs.digest }}
      severity: HIGH,CRITICAL
      exit-code: '1'
  - uses: sigstore/cosign-installer@v3
  - name: Sign
    env:
      COSIGN_EXPERIMENTAL: "1"
    run: cosign sign --yes ghcr.io/medvault/api@${{ steps.build.outputs.digest }}
```

(b) Verificação:

```bash
cosign verify \
  --certificate-identity-regexp "https://github.com/medvault/.*/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/medvault/api@sha256:...
```

**Ponto:** `--certificate-identity[-regexp]` é o **controle real**. Sem ele, qualquer assinatura válida passa — o que não é o que você quer.

---

## Exercício 4 — Política Kyverno

**Enunciado.** Escreva política Kyverno que, **em namespaces `medvault-prod`**, exige **todas** as condições:
- Imagem vem de `ghcr.io/medvault/*` OU `registry.medvault.local/*`.
- Container define `runAsNonRoot: true` e `readOnlyRootFilesystem: true`.
- `resources.limits` definidos.

**Resposta.**

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: medvault-prod-hardening
spec:
  validationFailureAction: Enforce
  rules:
    - name: registry-allowlist
      match:
        any:
          - resources:
              kinds: [Pod]
              namespaces: ["medvault-prod"]
      validate:
        message: "Imagem deve vir de ghcr.io/medvault ou registry.medvault.local."
        pattern:
          spec:
            containers:
              - image: "ghcr.io/medvault/*|registry.medvault.local/*"

    - name: non-root-readonly
      match:
        any:
          - resources:
              kinds: [Pod]
              namespaces: ["medvault-prod"]
      validate:
        message: "Containers exigem runAsNonRoot=true e readOnlyRootFilesystem=true."
        pattern:
          spec:
            containers:
              - securityContext:
                  runAsNonRoot: true
                  readOnlyRootFilesystem: true

    - name: resources-limits
      match:
        any:
          - resources:
              kinds: [Pod]
              namespaces: ["medvault-prod"]
      validate:
        message: "Containers devem definir resources.limits.cpu e memory."
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    cpu: "?*"
                    memory: "?*"
```

Como testar:

```bash
kubectl apply -f medvault-prod-hardening.yaml
kubectl apply -f pod-bom.yaml    # deve passar
kubectl apply -f pod-ruim.yaml   # deve falhar com mensagens
kubectl get policyreports -n medvault-prod
```

---

## Exercício 5 — Proveniência SLSA

**Enunciado.** Explique o que é **proveniência SLSA** em 4 linhas, por que é útil, e qual a diferença prática entre ter a imagem **assinada** vs. ter **proveniência assinada**.

**Resposta.**

Proveniência é um documento (JSON) que descreve **como** o artefato foi construído: qual repositório, qual commit, qual workflow, quais materiais (deps) entraram. Em SLSA, ela é **assinada** para não ser forjada. É útil porque permite responder, diante de um incidente: "essa imagem veio mesmo do nosso pipeline, do commit X, no tag Y?".

Diferença prática:

- **Imagem assinada** (cosign sign): "Este artefato foi produzido por algum pipeline autorizado." Integridade mínima.
- **Proveniência assinada** (SLSA L2+): "Este artefato foi produzido pelo pipeline `release.yml` da branch `main` do repo `medvault/api`, a partir do commit `abc123`, consumindo estas dependências." Rastreabilidade completa.

Em um ataque de supply chain (ex.: push indevido por credencial roubada), **só a proveniência** diferencia uma imagem legítima de uma feita por atacante que conseguiu rodar `cosign sign` — porque o atacante **não** tem OIDC do seu workflow oficial.

---

## Exercício 6 — VEX contra CVE

**Enunciado.** Trivy reportou CVE-2024-12345 HIGH em `openssl 3.0.11` na sua imagem. Análise mostra que o vetor exige que o serviço use **TLS client certificate validation** com callbacks customizados, coisa que você não faz. Descreva o mínimo que você escreve como VEX para "desligar" o alerta legitimamente.

**Resposta.**

VEX em formato CycloneDX:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "vulnerabilities": [
    {
      "id": "CVE-2024-12345",
      "source": { "name": "NVD" },
      "ratings": [{ "severity": "high" }],
      "analysis": {
        "state": "not_affected",
        "justification": "vulnerable_code_not_in_execute_path",
        "detail": "MedVault usa OpenSSL via urllib3/httpx para HTTPS client; nao valida certificados de cliente com callback customizado; fluxo afetado nao existe no produto. Reavaliar em 2026-06-01."
      },
      "affects": [{ "ref": "pkg:oci/medvault/api@sha256:..." }]
    }
  ]
}
```

Estados VEX padrão:

- `not_affected` (este caso) — produto não usa o caminho vulnerável.
- `affected` — produto é vulnerável; precisa corrigir.
- `fixed` — já corrigido na versão X.
- `under_investigation` — em análise.

Justification (por que not_affected) segue vocabulário VEX: `vulnerable_code_not_in_execute_path`, `vulnerable_code_not_present`, `inline_mitigations_already_exist`, etc.

O VEX é publicado junto do SBOM/release e pode ser consumido por scanners modernos (Grype, Trivy) via `--vex`.

---

## Autoavaliação

- [ ] Refatoro Dockerfile para multi-stage distroless com USER não-root.
- [ ] Gero SBOM e assino imagem + SBOM com cosign keyless.
- [ ] Entendo a diferença entre "imagem assinada" e "proveniência SLSA".
- [ ] Escrevo política Kyverno para hardening (registry, runAsNonRoot, limits).
- [ ] Emito VEX para CVEs não aplicáveis ao produto.
- [ ] Uso `dockerfile_audit.py` como checklist rápido.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Imagens e supply chain: endurecendo o artefato](03-imagens-supply-chain.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](../README.md) | **Próximo →**<br>[Bloco 4 — Segurança do cluster em produção](../bloco-4/04-k8s-producao.md) |

<!-- nav:end -->

# Bloco 3 — Imagens e supply chain: endurecendo o artefato

> **Pergunta do bloco.** Sua imagem OCI é **tudo** que vai para produção. Como reduzi-la ao mínimo necessário, escaneá-la continuamente, **assinar** o artefato, gerar atestações verificáveis, e bloquear no cluster qualquer imagem que não passe pelo processo?

---

## 3.1 A imagem como artefato de segurança

Cada linha de Dockerfile é uma **decisão de segurança**. Uma imagem "gorda" de 900 MB com `python:3.11` como base arrasta:

- Shell (`bash`), `curl`, `apt`, pacotes de desenvolvimento.
- Múltiplas bibliotecas nativas (libssl, libcrypto, libxml2...) cada uma com CVEs próprias.
- Ferramentas que um atacante usa **imediatamente** ao comprometer o container: shell, editor, downloader.

Reduzir a imagem é reduzir **superfície de ataque** e **ruído de varredura**.

### 3.1.1 Comparação típica

| Imagem base | Tamanho | CVEs (aprox.) | Observação |
|-------------|---------|---------------|-----------|
| `python:3.12` | 1.0 GB | 150–300 | Debian full + dev tools |
| `python:3.12-slim` | 150 MB | 20–60 | Debian slim |
| `python:3.12-alpine` | 50 MB | 5–20 | musl libc; cuidado com wheels nativas |
| `gcr.io/distroless/python3` | 50 MB | 0–5 | Sem shell, sem pkg manager |
| `cgr.dev/chainguard/python` | 50 MB | tipicamente 0 CVE conhecida | Chainguard, atualizada diária |

A escolha ideal para Python é **distroless** ou **Chainguard** (se disponível). Ambas não têm shell — o que **dificulta** o trabalho do atacante em runtime.

---

## 3.2 Dockerfile endurecido — padrão

### 3.2.1 Multi-stage

```dockerfile
# ===== Builder =====
FROM python:3.12-slim AS builder
WORKDIR /build

# Otimizar cache: copiar so deps primeiro
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copiar app
COPY src/ src/

# ===== Runtime =====
FROM gcr.io/distroless/python3-debian12:nonroot
WORKDIR /app

# Copiar apenas o que precisa de runtime
COPY --from=builder --chown=nonroot:nonroot /opt/venv /opt/venv
COPY --from=builder --chown=nonroot:nonroot /build/src /app/src

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# USER 65532 ja e padrao no distroless :nonroot
EXPOSE 8000

# Healthcheck (distroless nao tem curl; usar python)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()"]

ENTRYPOINT ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

# OCI labels
LABEL org.opencontainers.image.source="https://github.com/medvault/api" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="1.0.0"
```

### 3.2.2 `.dockerignore` — tão importante quanto Dockerfile

```
.git
.venv
__pycache__
*.pyc
tests/
docs/
.env
.env.*
*.md
.github
.vscode
```

Motivos:
- Impede `COPY . .` de levar `.env` acidentalmente.
- Reduz contexto do build.
- Evita vazamento de `.git/config` com credenciais.

### 3.2.3 Regras (checklist)

- [ ] Multi-stage com `builder` isolado.
- [ ] Imagem final **distroless** ou **alpine slim**.
- [ ] `USER` não-root (UID ≥ 10000).
- [ ] **Sem** `apt install` desnecessário no stage final.
- [ ] **Sem** shell / curl / wget na imagem final.
- [ ] `HEALTHCHECK` definido.
- [ ] `.dockerignore` exclui `.git`, `.env`, `tests/`.
- [ ] OCI labels com `source`, `version`, `licenses`.
- [ ] `COPY --chown` para garantir ownership.
- [ ] Pin de versão de base (evite `:latest`).

### 3.2.4 Build com BuildKit e secrets

Para o build precisar de credencial (ex.: índice Python privado), use `--secret` do BuildKit (já visto no Módulo 5):

```dockerfile
# syntax=docker/dockerfile:1.6
RUN --mount=type=secret,id=pip_idx \
    PIP_INDEX_URL=$(cat /run/secrets/pip_idx) \
    pip install -r requirements.txt
```

```bash
docker build --secret id=pip_idx,src=./.secrets/pip_idx -t medvault/api:v1 .
```

O segredo **nunca** entra na imagem final; só existe em memória durante o RUN.

---

## 3.3 Trivy image — varredura pré-registry

```bash
# Varrer imagem
trivy image medvault/api:v1.0.0

# Falhar em HIGH/CRITICAL
trivy image --severity HIGH,CRITICAL --exit-code 1 medvault/api:v1.0.0

# SARIF para GitHub
trivy image --format sarif -o trivy-image.sarif medvault/api:v1.0.0

# Ignorar CVEs aceitas em .trivyignore
trivy image --ignorefile .trivyignore medvault/api:v1.0.0

# Scan somente de vulns com fix disponivel (reduz ruido)
trivy image --ignore-unfixed medvault/api:v1.0.0
```

### 3.3.1 Grype como alternativa

```bash
grype medvault/api:v1.0.0 --fail-on high
grype sbom:sbom.cdx.json --fail-on high
```

Vantagem de Grype: trabalha bem com SBOM, permite **reanalisar** artefato antigo contra feed novo de CVEs.

### 3.3.2 Trivy + SBOM integrado

```bash
trivy image --format cyclonedx -o sbom-trivy.json medvault/api:v1.0.0
trivy image --format spdx-json -o sbom-trivy.spdx.json medvault/api:v1.0.0
```

Trivy gera SBOM **e** varre na mesma passagem.

---

## 3.4 Syft: SBOM detalhado

Syft é o gerador de SBOM de referência aberta (Anchore). Cobre muitos ecossistemas e formatos.

```bash
# SBOM de imagem
syft medvault/api:v1.0.0 -o cyclonedx-json=sbom.cdx.json -o spdx-json=sbom.spdx.json

# SBOM de filesystem (durante build)
syft dir:. -o cyclonedx-json=sbom-fs.cdx.json
```

Um bom SBOM:
- Inclui **todos** os pacotes OS + aplicação (não só Python).
- Tem `purl` (package URL) para cada componente — identificador universal.
- Tem `licenses` (ajuda em conformidade).
- Tem `metadata.component` do artefato principal.

### 3.4.1 Onde publicar

1. **GitHub Release** como asset anexado.
2. **OCI registry** como artefato relacionado via `cosign attest`.
3. **Dashboard interno** (Dependency-Track, Anchore Enterprise).

---

## 3.5 Assinatura com cosign

A assinatura garante: *"esta imagem foi produzida **por este pipeline** a partir **deste commit**"*. Sem assinatura, qualquer um com credencial de push pode injetar imagem maliciosa com o mesmo nome.

### 3.5.1 Modos de operação

| Modo | Chave | Quando usar |
|------|-------|------------|
| **Keyed** | Par pública/privada explícito | CI com HSM, ambientes enterprise |
| **Keyless** (OIDC) | Identidade efêmera (GitHub Actions, Google Cloud Build) | Cloud-native, padrão emergente |

### 3.5.2 Keyless em GitHub Actions (recomendado para graduação)

Pré-requisitos: `id-token: write` no workflow (OIDC habilitado).

```yaml
jobs:
  release:
    permissions:
      id-token: write          # cosign OIDC
      packages: write          # push no GHCR
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

      - uses: sigstore/cosign-installer@v3

      - name: Sign
        env:
          COSIGN_EXPERIMENTAL: "1"
        run: |
          cosign sign --yes ghcr.io/medvault/api@${{ steps.build.outputs.digest }}

      - name: Attest SBOM
        run: |
          syft ghcr.io/medvault/api@${{ steps.build.outputs.digest }} \
            -o cyclonedx-json=sbom.cdx.json
          cosign attest --yes --predicate sbom.cdx.json \
            --type cyclonedx \
            ghcr.io/medvault/api@${{ steps.build.outputs.digest }}
```

### 3.5.3 Verificação

```bash
cosign verify \
  --certificate-identity "https://github.com/medvault/api/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/medvault/api@sha256:...
```

Verifica que:
- Assinatura é válida.
- Quem assinou foi **este workflow** (pelo `--certificate-identity`).
- Emissor OIDC é o GitHub.

Essa verificação deve rodar **antes do deploy** — e de novo **no cluster** via admission (seção 3.7).

### 3.5.4 Rekor — transparency log

Toda assinatura vai para [Rekor](https://docs.sigstore.dev/rekor/overview/), log público imutável. Você pode auditar historicamente quem assinou o quê, quando:

```bash
cosign tree ghcr.io/medvault/api@sha256:...
rekor-cli search --sha <sha do manifesto>
```

---

## 3.6 Supply chain — os degraus do SLSA

Vamos recapitular com foco prático:

| SLSA | Requisito | Na MedVault |
|------|-----------|-------------|
| **L1** | Build script versionado + proveniência mínima | CI no GitHub, Dockerfile versionado; adicionar provenance = L1 atingido |
| **L2** | Build hospedado + proveniência assinada | Cosign keyless + SLSA generator |
| **L3** | Build isolado, materials verificados, proveniência não-forjável | Runner dedicado, build hermético, não atingível sem maturidade |

### 3.6.1 SLSA generator para GitHub Actions

```yaml
# .github/workflows/slsa-provenance.yml
jobs:
  provenance:
    permissions:
      id-token: write
      packages: write
      contents: read
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v2.0.0
    with:
      image: ghcr.io/medvault/api
      digest: ${{ needs.build.outputs.digest }}
      registry-username: ${{ github.actor }}
    secrets:
      registry-password: ${{ secrets.GITHUB_TOKEN }}
```

O workflow oficial gera proveniência **assinada** e anexa ao artefato.

---

## 3.7 Admission control — porteiro do cluster

O cluster precisa **recusar** manifestos que violem política **antes** de aplicá-los. Duas ferramentas lideram:

- **Kyverno**: policies em YAML puro, curva baixa.
- **OPA Gatekeeper**: policies em Rego, mais poderoso, curva mais alta.

Vamos usar **Kyverno** para exemplos.

### 3.7.1 Instalar

```bash
kubectl create ns kyverno
helm repo add kyverno https://kyverno.github.io/kyverno/
helm upgrade --install kyverno kyverno/kyverno -n kyverno
```

### 3.7.2 Política: imagem assinada

```yaml
apiVersion: kyverno.io/v2beta1
kind: ClusterPolicy
metadata:
  name: verify-medvault-images
spec:
  validationFailureAction: Enforce
  background: false
  rules:
    - name: check-cosign-signature
      match:
        any:
          - resources:
              kinds: [Pod]
      verifyImages:
        - imageReferences:
            - "ghcr.io/medvault/*"
          attestors:
            - entries:
                - keyless:
                    subject: "https://github.com/medvault/*/.github/workflows/release.yml@refs/heads/main"
                    issuer: "https://token.actions.githubusercontent.com"
```

Resultado: qualquer Pod com imagem `ghcr.io/medvault/*` precisa ter sido assinada pelo workflow `release.yml` na `main`. Caso contrário, o apply falha.

### 3.7.3 Política: bloquear `:latest`

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-latest-tag
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-tag-pinning
      match:
        any:
          - resources:
              kinds: [Pod]
      validate:
        message: "Imagem nao pode usar :latest. Use tag semver ou digest."
        pattern:
          spec:
            containers:
              - image: "!*:latest"
```

### 3.7.4 Política: exigir `runAsNonRoot`

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-run-as-nonroot
spec:
  validationFailureAction: Enforce
  rules:
    - name: pod-security-context
      match:
        any:
          - resources:
              kinds: [Pod]
              namespaces: ["medvault-prod", "medvault-dev"]
      validate:
        message: "Pods devem definir securityContext.runAsNonRoot=true."
        pattern:
          spec:
            =(securityContext):
              runAsNonRoot: true
            containers:
              - =(securityContext):
                  runAsNonRoot: true
```

### 3.7.5 Modo Audit vs. Enforce

- **Audit**: registra violação em `PolicyReport`, **não** bloqueia. Útil para rollout sem quebrar produção.
- **Enforce**: bloqueia. Usar após validar em audit.

Rota típica: audit por 1–2 sprints → ajustar workloads → enforce.

### 3.7.6 Testando política

Aplicar Pod insegura e verificar rejeição:

```yaml
# pod-inseguro.yaml
apiVersion: v1
kind: Pod
metadata:
  name: test-root
  namespace: medvault-dev
spec:
  containers:
    - name: bad
      image: nginx:latest
      securityContext:
        runAsUser: 0
```

```bash
$ kubectl apply -f pod-inseguro.yaml
Error from server: admission webhook "validate.kyverno.svc-fail" denied the request:
  - policy disallow-latest-tag: Imagem nao pode usar :latest
  - policy require-run-as-nonroot: Pods devem definir securityContext.runAsNonRoot=true
```

Exatamente o que queremos.

---

## 3.8 Script Python: `dockerfile_audit.py`

Auditor estático focado em boas práticas de Dockerfile. Complementa Trivy/Checkov com mensagens pedagógicas.

```python
"""
dockerfile_audit.py - audita Dockerfile para boas praticas de seguranca.

Checa (independente de Trivy/Checkov):
  DOCK-001: usa :latest na FROM
  DOCK-002: nao define USER
  DOCK-003: instala pacotes comuns de ataque (curl, wget, nc, ssh, vim)
  DOCK-004: COPY . . sem .dockerignore visivel
  DOCK-005: sem HEALTHCHECK
  DOCK-006: sem LABEL org.opencontainers.image.source
  DOCK-007: usa ADD para URL remota
  DOCK-008: USER 0/root

Uso:
    python dockerfile_audit.py Dockerfile [--fail-on medium]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

SEV_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3}
PKGS_RISCO = {"curl", "wget", "netcat", "nc", "ssh", "openssh", "vim", "nano", "git"}


@dataclass(frozen=True)
class Issue:
    id: str
    linha: int
    severidade: str
    mensagem: str


def _escanear(dockerfile: str, base_dir: str) -> list[Issue]:
    linhas = dockerfile.splitlines()
    issues: list[Issue] = []

    tem_user = False
    usuario_ultimo = None
    tem_healthcheck = False
    tem_label_source = False

    for i, raw in enumerate(linhas, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        up = line.upper()

        if up.startswith("FROM "):
            m = re.match(r"FROM\s+([^\s]+)", line, re.I)
            if m and ":" in m.group(1) and m.group(1).endswith(":latest"):
                issues.append(Issue("DOCK-001", i, "high", f"FROM usa :latest ({m.group(1)})"))

        if up.startswith("USER "):
            tem_user = True
            usuario_ultimo = line.split()[1]
            if usuario_ultimo in ("0", "root"):
                issues.append(Issue("DOCK-008", i, "high", "USER root/0"))

        if up.startswith("RUN ") and ("apt-get install" in line or "apk add" in line):
            for p in PKGS_RISCO:
                if re.search(rf"\b{p}\b", line):
                    issues.append(Issue("DOCK-003", i, "medium",
                                        f"Instala pacote util a atacante: {p}"))

        if up.startswith("COPY ") and (line.split()[1] == "." if len(line.split()) >= 2 else False):
            dockerignore = os.path.join(base_dir, ".dockerignore")
            if not os.path.exists(dockerignore):
                issues.append(Issue("DOCK-004", i, "medium",
                                    "COPY . . sem .dockerignore ao lado"))

        if up.startswith("HEALTHCHECK "):
            tem_healthcheck = True

        if up.startswith("LABEL ") and "org.opencontainers.image.source" in line:
            tem_label_source = True

        if up.startswith("ADD ") and re.search(r"https?://", line):
            issues.append(Issue("DOCK-007", i, "medium",
                                "ADD de URL remota (preferir RUN curl + verificacao)"))

    if not tem_user:
        issues.append(Issue("DOCK-002", 0, "high", "Dockerfile nao define USER explicitamente"))
    if not tem_healthcheck:
        issues.append(Issue("DOCK-005", 0, "low", "Sem HEALTHCHECK"))
    if not tem_label_source:
        issues.append(Issue("DOCK-006", 0, "low", "Sem LABEL org.opencontainers.image.source"))
    return issues


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("dockerfile")
    p.add_argument("--fail-on", default="high", choices=list(SEV_ORDER.keys()))
    args = p.parse_args(argv)

    try:
        with open(args.dockerfile, "r", encoding="utf-8") as fh:
            conteudo = fh.read()
    except OSError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    issues = _escanear(conteudo, base_dir=os.path.dirname(os.path.abspath(args.dockerfile)))

    console = Console()
    if not issues:
        console.print(":sparkles: Dockerfile passou em todas as checagens.")
        return 0

    tabela = Table(title=f"Auditoria {args.dockerfile}")
    for c in ("id", "linha", "severidade", "mensagem"):
        tabela.add_column(c)
    for iss in sorted(issues, key=lambda x: -SEV_ORDER[x.severidade]):
        tabela.add_row(iss.id, str(iss.linha), iss.severidade, iss.mensagem)
    console.print(tabela)

    lim = SEV_ORDER[args.fail_on]
    piores = [x for x in issues if SEV_ORDER[x.severidade] >= lim]
    console.print(f"\nTotal: {len(issues)} | >= {args.fail_on}: {len(piores)}")
    return 0 if not piores else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## 3.9 Checklist do bloco

- [ ] Sei escrever Dockerfile multi-stage distroless com `USER` não-root.
- [ ] Rodo Trivy image e trato CVEs com critério.
- [ ] Gero SBOM (Syft) e anexo como artefato do release.
- [ ] Assino imagens com cosign (keyless no GitHub Actions).
- [ ] Emito proveniência SLSA L2 via generator oficial.
- [ ] Aplico políticas Kyverno: verify-images, disallow-latest, require-nonroot.
- [ ] Testo a rejeição de Pod insegura com `kubectl apply`.
- [ ] Uso `dockerfile_audit.py` para verificação rápida local.

Vá aos [exercícios resolvidos do Bloco 3](./03-exercicios-resolvidos.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Exercícios resolvidos](../bloco-2/02-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](../README.md) | **Próximo →**<br>[Bloco 3 — Exercícios resolvidos](03-exercicios-resolvidos.md) |

<!-- nav:end -->

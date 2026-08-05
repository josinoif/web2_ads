# Bloco 4 — Produção, Segurança, Registries e SBOM

> **Duração estimada:** 80 a 90 minutos. Inclui `runner_isolation.py`, que testa **de verdade** se um `docker run` aplicou os isolamentos pedidos.

Você tem imagens idiomáticas (Bloco 2) e ambiente local multi-serviço (Bloco 3). Agora vamos tratar as **quatro frentes** que separam "rodar em contêiner" de **"rodar em contêiner em produção"**:

1. **Registries** — publicação versionada e controlada de imagens.
2. **Flags de runtime** — isolamento e limites que **o Dockerfile não garante sozinho**.
3. **Scanning de vulnerabilidades** e **SBOM**.
4. **Padrões de produção** — tagging, assinatura, healthchecks, observabilidade embutida.

---

## 1. Registries — onde a imagem vive após o build

Um **registry** é um servidor HTTP(S) que **armazena e distribui** imagens OCI. Toda vez que você `docker pull` ou `docker push`, está falando com um registry.

### Categorias

| Tipo | Exemplos | Quando usar |
|------|----------|-------------|
| **SaaS público** | Docker Hub, GHCR, GitLab Registry, Quay.io | Open source, projetos de ensino, times sem infra dedicada |
| **SaaS privado** (mesmos acima com conta paga) | ECR (AWS), GCR/Artifact Registry (GCP), ACR (Azure) | Produção em cloud, controle fino de IAM |
| **Self-hosted** | Harbor, GitLab self-hosted, Nexus, Zot | Compliance, air-gapped, equipes grandes |

Para a CodeLab, o **Módulo 4** já estabeleceu o CI em **GitHub Actions** — então **GHCR** (GitHub Container Registry) é o encaixe natural. Sem novas credenciais, sem novo provider.

### Autenticação em GHCR

```bash
# token pessoal com escopo write:packages ou GITHUB_TOKEN no CI
echo "$GHCR_TOKEN" | docker login ghcr.io -u USUARIO --password-stdin

docker tag codelab-runner-python:local ghcr.io/codelab/runner-python:0.3.0
docker push ghcr.io/codelab/runner-python:0.3.0
```

No GitHub Actions, use `GITHUB_TOKEN` com permissões:

```yaml
permissions:
  contents: read
  packages: write
```

### O que é um "nome completo" de imagem?

```
ghcr.io/codelab/runner-python:0.3.0@sha256:abc123...
│     │ │             │          │     │
│     │ │             │          │     └─ digest (hash imutável do conteúdo)
│     │ │             │          └─────── tag (rótulo mutável!)
│     │ │             └────────────────── nome do repositório
│     │ └──────────────────────────────── organização/usuário
│     └────────────────────────────────── registry
```

Em produção, **ancore sempre pelo digest** para garantir imutabilidade:

```yaml
# docker-compose.prod.yml
services:
  runner-python:
    image: ghcr.io/codelab/runner-python:0.3.0@sha256:abc123...
```

Mesmo que alguém sobrescreva a tag `:0.3.0`, o digest protege você.

---

## 2. Estratégia de tagging

### Conjunto mínimo para cada build

Todo build no CI deveria produzir **três** tags:

| Tag | Função |
|-----|--------|
| `sha-<curto>` (ex.: `sha-abc1234`) | rastreabilidade — casa 1:1 com o commit git |
| `vX.Y.Z` (ex.: `v0.3.0`) | semver da release — **só em tags git** |
| `latest` ou `main` | conveniência (opcional) — **jamais** usar em produção |

Exemplo no workflow:

```yaml
- name: Metadata
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: ghcr.io/codelab/runner-python
    tags: |
      type=sha,prefix=sha-,format=short
      type=semver,pattern={{version}}
      type=ref,event=branch

- name: Build e push
  uses: docker/build-push-action@v5
  with:
    context: .
    file: docker/runner-python.Dockerfile
    push: true
    tags: ${{ steps.meta.outputs.tags }}
    labels: ${{ steps.meta.outputs.labels }}
```

Produção **sempre** puxa por `sha-` ou `vX.Y.Z@sha256:...`; **nunca** por `latest`.

---

## 3. Flags de runtime — o isolamento que falta

O Dockerfile define **o que está na imagem**. O comando `docker run` define **como ela roda**. A lista abaixo é a **base mínima** para rodar código não-confiável (runners da CodeLab):

| Flag | Efeito | Por que importa |
|------|--------|-----------------|
| `--read-only` | FS raiz imutável | programa malicioso não altera binários |
| `--tmpfs /tmp:rw,size=64m,mode=1777` | `/tmp` em RAM, efêmero | escrita legítima sem persistência |
| `--network=none` | sem interface de rede | **crítico** para código não-confiável |
| `--user 10001:10001` | processo como UID não-root | reduz severidade de escape |
| `--cap-drop=ALL` | sem capabilities | bloqueia operações privilegiadas no kernel |
| `--security-opt=no-new-privileges:true` | setuid não escala privilégios | defesa em profundidade |
| `--pids-limit=50` | limita fork bomb | grupo não explode o host |
| `--memory=256m --memory-swap=256m` | limite de RSS | OOM kill contido |
| `--cpus=1.0` | limite de CPU | quota garantida pelo kernel |
| `--stop-timeout=5` | tempo máximo de graceful shutdown | término previsível |

Exemplo completo para um runner Python da CodeLab:

```bash
docker run --rm \
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
  ghcr.io/codelab/runner-python:0.5.0@sha256:abc... \
  python /submissao/main.py
```

### O que essas flags **não** resolvem

- **CVEs do kernel** — se o kernel tem bug, todo container sofre.
- **Side-channel attacks** (Spectre, Meltdown) — mitigados por patches de kernel + CPU, não por flags.
- **Escape por bug do runtime** (runc, containerd) — mitigação via `seccomp` avançado ou runtimes como gVisor.

Para **isolamento robusto**, camada adicional:

- **seccomp profile customizado** — lista explícita de syscalls permitidas.
- **AppArmor / SELinux** — perfis de segurança do kernel.
- **gVisor** (`--runtime=runsc`) — reexecuta syscalls em user-space.
- **Kata Containers** — microVM por container.
- **Firecracker** — AWS Lambda / Fargate.

Em produção, runners da CodeLab **merecem gVisor ou Kata**. Este módulo mostra o caminho; implementação vai além da graduação.

---

## 4. Scanning de vulnerabilidades

Imagem base tem Python 3.12.7, libssl, zlib... cada uma com seu histórico de CVEs. **Toda imagem nasce com vulnerabilidades conhecidas** — o que importa é quais, quão sérias, e o que fazer.

### Ferramentas principais

| Ferramenta | Tipo | Diferencial |
|------------|------|-------------|
| **Trivy** (Aqua) | scanner SCA + IaC + segredos | de-facto padrão; rápido; offline mode; múltiplos formatos |
| **Grype** (Anchore) | scanner SCA | excelente integração com Syft (SBOM) |
| **Snyk** | SaaS (pago) | UX de policy enterprise |
| **Docker Scout** | SaaS (Docker) | integrado ao Docker Desktop |

### Rodando Trivy

```bash
# Instalar (Linux):
sudo apt install trivy

# Scanear imagem:
trivy image --severity HIGH,CRITICAL ghcr.io/codelab/runner-python:0.5.0

# Falhar em CVEs não ignoradas:
trivy image --exit-code 1 --severity CRITICAL ghcr.io/codelab/runner-python:0.5.0

# Ignorar CVEs específicos (arquivo .trivyignore):
echo "CVE-2023-12345  # aceito: workaround já aplicado" > .trivyignore
trivy image --ignorefile .trivyignore ...
```

Saída típica (abreviada):

```
ghcr.io/codelab/runner-python:0.5.0 (debian 12.5)
Total: 3 (CRITICAL: 1, HIGH: 2)

┌─────────────┬────────────────┬──────────┬──────────┬─────────────────┐
│ Library     │ Vulnerability  │ Severity │ Fixed V. │ Title           │
├─────────────┼────────────────┼──────────┼──────────┼─────────────────┤
│ libssl3     │ CVE-2024-5535  │ CRITICAL │ 3.0.13-1 │ openssl: SSL... │
│ libzstd1    │ CVE-2024-7341  │ HIGH     │ 1.5.5-2  │ zstd: integer...│
│ python3.12  │ CVE-2024-XXXX  │ HIGH     │ 3.12.8   │ urllib: ...     │
└─────────────┴────────────────┴──────────┴──────────┴─────────────────┘
```

### Política pragmática

- **CRITICAL** → **falha o build**. Obrigatório corrigir.
- **HIGH** → **falha o build**, com escape possível via `.trivyignore` revisado e datado.
- **MEDIUM/LOW** → não falha o build; tracking em issue backlog semanal.

No CI:

```yaml
- name: Trivy scan
  uses: aquasecurity/trivy-action@0.24.0
  with:
    image-ref: ghcr.io/codelab/runner-python:${{ github.sha }}
    severity: CRITICAL,HIGH
    exit-code: "1"
    ignore-unfixed: true
```

`ignore-unfixed: true` ignora CVEs que ainda **não têm correção disponível** upstream — você não pode consertar o que não tem patch; reaparece quando há patch.

---

## 5. SBOM — "bill of materials" de uma imagem

**SBOM (Software Bill of Materials)** lista todos os componentes dentro da imagem, com versões e licenças. É **contrato** com:

- **Auditoria** — evidência do que está rodando.
- **Compliance** — muitas normas (DoD, EU Cyber Resilience Act) começam a exigir.
- **Resposta a incidentes** — novo CVE na lib X → `grep X` em todos os SBOMs → lista de imagens afetadas em 1 minuto.

### Gerando SBOM com Syft

```bash
syft ghcr.io/codelab/runner-python:0.5.0 -o spdx-json > sbom.spdx.json
# ou cyclonedx:
syft ghcr.io/codelab/runner-python:0.5.0 -o cyclonedx-json > sbom.cdx.json
```

Saída enxuta em SPDX-JSON (trecho):

```json
{
  "SPDXID": "SPDXRef-DOCUMENT",
  "packages": [
    {"name": "python3.12", "versionInfo": "3.12.7-1", "licenseConcluded": "PSF-2.0"},
    {"name": "fastapi",    "versionInfo": "0.110.0",  "licenseConcluded": "MIT"},
    {"name": "libssl3",    "versionInfo": "3.0.11-1", "licenseConcluded": "OpenSSL"}
  ]
}
```

### Anexando SBOM como artefato

```yaml
- name: Gerar SBOM
  uses: anchore/sbom-action@v0.15.0
  with:
    image: ghcr.io/codelab/runner-python:${{ github.sha }}
    format: spdx-json
    artifact-name: sbom-runner-python-${{ github.sha }}.spdx.json

- name: Anexar SBOM ao release
  uses: softprops/action-gh-release@v2
  with:
    files: sbom-runner-python-*.spdx.json
```

### SBOM embutido na imagem (attestation)

Com BuildKit moderno + `docker buildx`:

```bash
docker buildx build \
  --sbom=true \
  --provenance=true \
  -t ghcr.io/codelab/runner-python:0.5.0 \
  --push .
```

Gera SBOM + atestação de proveniência (SLSA v0.2) anexados à imagem no registry.

---

## 6. Assinatura — cosign

Depois de scanear e documentar, falta **assinar** — garantir criptograficamente que aquela imagem foi construída pelo seu CI, não adulterada no caminho.

**cosign** (parte do projeto Sigstore) é o padrão.

```bash
# Gerar chave
cosign generate-key-pair

# Assinar
cosign sign --key cosign.key ghcr.io/codelab/runner-python:0.5.0

# Verificar
cosign verify --key cosign.pub ghcr.io/codelab/runner-python:0.5.0
```

Keyless (sem chave, usa OIDC do GitHub):

```bash
cosign sign ghcr.io/codelab/runner-python:0.5.0
# assinatura amarrada à identidade do GitHub Actions workflow
```

Em produção K8s (Módulo 7), uma policy admission controller (Kyverno, cosigned) **recusa** imagens não assinadas — completa o ciclo.

---

## 7. Inspecionando o isolamento — `runner_isolation.py`

Um script Python que **testa** se o `docker run` foi invocado com os isolamentos esperados. Útil para:

- Auditar manualmente um container rodando.
- Prova de conceito em aula.
- Integrar em CI como verificação pós-deploy.

```python
"""runner_isolation.py — verifica, via docker inspect, se um container está
com os isolamentos que consideramos mínimos para runners de código
não-confiável (CodeLab).

Uso:
  python runner_isolation.py <container-id-ou-nome>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field


@dataclass
class Check:
    ok: bool
    severidade: str  # "CRIT", "HIGH", "MED", "INFO"
    chave: str
    mensagem: str


@dataclass
class Relatorio:
    checks: list[Check] = field(default_factory=list)

    def add(self, ok, severidade, chave, mensagem):
        self.checks.append(Check(ok, severidade, chave, mensagem))

    @property
    def fatal(self) -> bool:
        return any((not c.ok) and c.severidade in ("CRIT", "HIGH") for c in self.checks)


def _docker_inspect(ctn: str) -> dict:
    r = subprocess.run(
        ["docker", "inspect", ctn],
        capture_output=True, text=True, check=True,
    )
    data = json.loads(r.stdout)
    if not data:
        raise RuntimeError(f"Container não encontrado: {ctn}")
    return data[0]


def avaliar(info: dict) -> Relatorio:
    r = Relatorio()
    host = info.get("HostConfig", {})
    cfg = info.get("Config", {})

    # 1. network
    net_mode = host.get("NetworkMode", "default")
    r.add(
        ok=(net_mode == "none"),
        severidade="CRIT",
        chave="network",
        mensagem=f"NetworkMode={net_mode} (esperado: 'none' para runners sem egress).",
    )

    # 2. read-only rootfs
    ro = host.get("ReadonlyRootfs", False)
    r.add(ok=bool(ro), severidade="HIGH", chave="readonly-fs",
          mensagem=f"ReadonlyRootfs={ro} (esperado: true).")

    # 3. user
    user = cfg.get("User", "")
    is_nonroot = user not in ("", "root", "0", "0:0")
    r.add(ok=is_nonroot, severidade="CRIT", chave="nao-root",
          mensagem=f"User='{user}' (esperado: UID não-root).")

    # 4. capabilities
    cap_drop = set(host.get("CapDrop") or [])
    cap_add = set(host.get("CapAdd") or [])
    dropou_tudo = "ALL" in cap_drop or "all" in cap_drop
    r.add(ok=dropou_tudo, severidade="HIGH", chave="cap-drop-all",
          mensagem=f"CapDrop={sorted(cap_drop)} (esperado: inclui 'ALL').")
    r.add(ok=len(cap_add) == 0, severidade="MED", chave="cap-add-vazio",
          mensagem=f"CapAdd={sorted(cap_add)} (esperado: vazio para runners).")

    # 5. security-opt
    sec_opts = host.get("SecurityOpt") or []
    nnp = any("no-new-privileges:true" in s or "no-new-privileges=true" in s for s in sec_opts)
    r.add(ok=nnp, severidade="HIGH", chave="no-new-privileges",
          mensagem=f"SecurityOpt={sec_opts} (esperado: 'no-new-privileges:true').")

    # 6. pids-limit
    pids = host.get("PidsLimit")
    ok_pids = (pids is not None) and (pids > 0) and (pids <= 100)
    r.add(ok=ok_pids, severidade="HIGH", chave="pids-limit",
          mensagem=f"PidsLimit={pids} (esperado: 1 < n <= 100).")

    # 7. memory
    mem = host.get("Memory", 0)
    r.add(ok=mem > 0, severidade="HIGH", chave="memory-limit",
          mensagem=f"Memory={mem} bytes (esperado: > 0).")

    # 8. cpus (via NanoCpus)
    ncpus = host.get("NanoCpus", 0)
    r.add(ok=ncpus > 0, severidade="MED", chave="cpu-limit",
          mensagem=f"NanoCpus={ncpus} (esperado: > 0, ex.: 1_000_000_000 = 1 CPU).")

    # 9. privileged
    priv = host.get("Privileged", False)
    r.add(ok=(not priv), severidade="CRIT", chave="not-privileged",
          mensagem=f"Privileged={priv} (esperado: false). **SEMPRE** false.")

    # 10. tmpfs /tmp
    tmpfs = host.get("Tmpfs") or {}
    r.add(ok=("/tmp" in tmpfs), severidade="MED", chave="tmpfs-tmp",
          mensagem=f"Tmpfs={list(tmpfs.keys())} (esperado: inclui '/tmp').")

    return r


def imprimir(r: Relatorio) -> None:
    for c in r.checks:
        status = "PASS" if c.ok else "FAIL"
        print(f"[{status}] [{c.severidade:<4}] {c.chave:<20} {c.mensagem}")
    fail = sum(1 for c in r.checks if not c.ok)
    print(f"\nResumo: {len(r.checks) - fail} PASS, {fail} FAIL" +
          ("  -> NÃO PROMOVER" if r.fatal else ""))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("container", help="ID ou nome do container")
    args = p.parse_args(argv)

    try:
        info = _docker_inspect(args.container)
    except subprocess.CalledProcessError as e:
        print(f"docker inspect falhou: {e.stderr}", file=sys.stderr)
        return 2

    rel = avaliar(info)
    imprimir(rel)
    return 1 if rel.fatal else 0


if __name__ == "__main__":
    sys.exit(main())
```

### Uso

```bash
# Container "bom":
docker run -d --name run-ok --rm \
  --network=none --read-only --tmpfs /tmp:rw,size=64m,mode=1777 \
  --user 10001:10001 --cap-drop=ALL \
  --security-opt=no-new-privileges:true \
  --pids-limit=50 --memory=256m --memory-swap=256m --cpus=1.0 \
  alpine:3.20 sleep 30

python runner_isolation.py run-ok

# Container "ruim":
docker run -d --name run-ruim --rm alpine:3.20 sleep 30
python runner_isolation.py run-ruim
```

Saída típica do "bom":

```
[PASS] [CRIT] network              NetworkMode=none (...)
[PASS] [HIGH] readonly-fs          ReadonlyRootfs=True (...)
[PASS] [CRIT] nao-root             User='10001:10001' (...)
[PASS] [HIGH] cap-drop-all         CapDrop=['ALL'] (...)
[PASS] [MED ] cap-add-vazio        CapAdd=[] (...)
[PASS] [HIGH] no-new-privileges    ...
[PASS] [HIGH] pids-limit           PidsLimit=50 (...)
[PASS] [HIGH] memory-limit         Memory=268435456 (...)
[PASS] [MED ] cpu-limit            NanoCpus=1000000000 (...)
[PASS] [CRIT] not-privileged       Privileged=False (...)
[PASS] [MED ] tmpfs-tmp            Tmpfs=['/tmp'] (...)

Resumo: 11 PASS, 0 FAIL
```

Saída do "ruim" — tudo FAIL, exit code 1.

---

## 8. 12-Factor em contêiner — o que importa

Reforce os pontos cruciais em imagem OCI:

| Fator | Como aplica ao container |
|-------|--------------------------|
| **III — Config** | Variáveis de ambiente; **nunca** `ENV` com segredo na imagem |
| **IV — Backing services** | Banco, cache via URL na env — container não sabe onde estão |
| **V — Build, release, run** | Build = imagem; release = imagem + config; run = container |
| **VI — Processes** | Stateless; `--read-only` é possibilidade real |
| **IX — Disposability** | SIGTERM propagado em < 10s; cuidado com PID 1 |
| **XI — Logs** | stdout/stderr; nada de arquivo de log dentro do container |

Logs em container: **não escreva `/var/log/app.log`**. Escreva em **stdout/stderr**; o runtime coleta e redireciona. Isso é pré-requisito para Módulo 8 (observabilidade).

---

## 9. Anatomia de um workflow CD de imagens (completo)

Consolidando Bloco 2, 3 e 4 — `.github/workflows/images.yml`:

```yaml
name: Build, Scan, Sign e Publish

on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:

permissions:
  contents: read
  packages: write
  id-token: write         # para cosign keyless
  security-events: write  # para upload SARIF ao Security tab

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [api, worker, runner-python, runner-javascript, runner-c]
    steps:
      - uses: actions/checkout@v4

      - name: Hadolint
        uses: hadolint/hadolint-action@v3
        with:
          dockerfile: docker/${{ matrix.service }}.Dockerfile
          failure-threshold: warning

      - name: Docker buildx
        uses: docker/setup-buildx-action@v3

      - name: Login GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}/${{ matrix.service }}
          tags: |
            type=sha,prefix=sha-,format=short
            type=semver,pattern={{version}}
            type=ref,event=branch

      - name: Build + push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/${{ matrix.service }}.Dockerfile
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          build-args: |
            GIT_SHA=${{ github.sha }}
            VERSION=${{ steps.meta.outputs.version }}
          sbom: true
          provenance: mode=max

      - name: Trivy scan
        uses: aquasecurity/trivy-action@0.24.0
        with:
          image-ref: ghcr.io/${{ github.repository }}/${{ matrix.service }}:sha-${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: "1"
          ignore-unfixed: true
          format: sarif
          output: trivy-${{ matrix.service }}.sarif

      - name: Upload Trivy SARIF
        if: always()
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-${{ matrix.service }}.sarif
          category: trivy-${{ matrix.service }}

      - name: SBOM (Syft)
        uses: anchore/sbom-action@v0.15.0
        with:
          image: ghcr.io/${{ github.repository }}/${{ matrix.service }}:sha-${{ github.sha }}
          format: spdx-json
          artifact-name: sbom-${{ matrix.service }}.spdx.json
          upload-artifact: true

      - name: Cosign install
        if: github.event_name != 'pull_request'
        uses: sigstore/cosign-installer@v3

      - name: Assinar imagem (keyless)
        if: github.event_name != 'pull_request'
        run: cosign sign --yes ghcr.io/${{ github.repository }}/${{ matrix.service }}@${{ steps.build.outputs.digest }}
```

Esse workflow cobre: lint → build → push → scan → SBOM → sign. **Tudo artefato.** Em PR, só constrói (não publica). Em merge para `main` ou push de tag `v*`, publica com tudo.

---

## 10. Pitfalls de produção

| Sintoma | Causa | Correção |
|---------|-------|----------|
| `latest` em produção | esquecimento | política: `latest` só em dev; pin em digest em produção |
| Imagem cresce 500 MB entre versões | build layers não limpas | `--no-install-recommends` + `rm -rf /var/lib/apt/lists` na **mesma** RUN |
| CVEs acumulam por meses | scanner no CI mas **warning** | escalar severidade; falhar build |
| Registry enche | tags acumuladas | política de retenção (GHCR: `actions/delete-package-versions`) |
| Pull lento em produção | imagem base gigante | slim/distroless; `--compress` no push |
| `docker stop` leva 10s | PID 1 não propaga SIGTERM | forma exec do `CMD`/`ENTRYPOINT`; usar `tini` |
| Logs perdidos | app escreve em arquivo dentro do container | stdout/stderr; log rotation no runtime |

---

## Resumo do bloco

- **Registry** é onde a imagem vive; pinne por **digest** em produção.
- **Flags de runtime** (`--read-only`, `--network=none`, `--user`, `--cap-drop=ALL`, limites) **completam** o que o Dockerfile sozinho não garante.
- **Trivy/Grype** escaneiam CVEs; integrar no CI falhando em **CRITICAL/HIGH**.
- **Syft** gera **SBOM** — contrato de transparência e resposta a incidentes.
- **cosign** assina imagens; no K8s (Mod 7), policy recusa não-assinadas.
- **12-factor em contêiner** é regra de ouro para observabilidade (Mod 8) e orquestração (Mod 7).
- Workflow unificado: **lint → build → push → scan → SBOM → sign**.

---

## Próximo passo

- Faça os **[exercícios resolvidos do Bloco 4](04-exercicios-resolvidos.md)**.
- Inicie os **[exercícios progressivos](../exercicios-progressivos/)**.

---

## Referências deste bloco

- **Rice, L.** *Container Security.* O'Reilly, 2020. Caps. 6-9.
- **NIST SP 800-190** — *Application Container Security Guide*, 2019.
- **CIS Docker Benchmark** — [cisecurity.org/benchmark/docker](https://www.cisecurity.org/benchmark/docker).
- **Trivy docs:** [aquasecurity.github.io/trivy](https://aquasecurity.github.io/trivy/).
- **Syft docs:** [github.com/anchore/syft](https://github.com/anchore/syft).
- **Sigstore cosign:** [docs.sigstore.dev/signing/quickstart/](https://docs.sigstore.dev/signing/quickstart/).
- **SLSA framework:** [slsa.dev](https://slsa.dev/).
- **GitHub — Container Registry:** [docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Resolvidos — Bloco 3](../bloco-3/03-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](../README.md) | **Próximo →**<br>[Exercícios Resolvidos — Bloco 4](04-exercicios-resolvidos.md) |

<!-- nav:end -->

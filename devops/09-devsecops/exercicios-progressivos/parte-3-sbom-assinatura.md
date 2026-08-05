# Parte 3 — SBOM, assinatura e proveniência

**Entrega desta parte:**

- `.github/workflows/release.yml` com build, Trivy, SBOM (Syft), `cosign sign` + `cosign attest`.
- SBOM publicado como release asset (CycloneDX + SPDX).
- Proveniência SLSA gerada via generator oficial.

---

## 1. Release workflow

`.github/workflows/release.yml`:

```yaml
name: release

on:
  push:
    tags: ["v*"]

permissions:
  contents: write      # release assets
  id-token: write      # cosign keyless OIDC
  packages: write      # GHCR push

env:
  REGISTRY: ghcr.io
  IMAGE: ${{ github.repository }}   # ex.: owner/medvault-api

jobs:
  build-and-sign:
    runs-on: ubuntu-latest
    outputs:
      digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build & push
        id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ github.ref_name }}
            ${{ env.REGISTRY }}/${{ env.IMAGE }}:${{ github.sha }}
          provenance: false         # gerar via generator oficial abaixo

      - name: Trivy image (bloqueia HIGH/CRITICAL)
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE }}@${{ steps.build.outputs.digest }}
          severity: HIGH,CRITICAL
          exit-code: '1'
          ignorefile: .trivyignore

      - uses: anchore/sbom-action@v0
        with:
          image: ${{ env.REGISTRY }}/${{ env.IMAGE }}@${{ steps.build.outputs.digest }}
          format: cyclonedx-json
          output-file: sbom.cdx.json
      - uses: anchore/sbom-action@v0
        with:
          image: ${{ env.REGISTRY }}/${{ env.IMAGE }}@${{ steps.build.outputs.digest }}
          format: spdx-json
          output-file: sbom.spdx.json

      - uses: sigstore/cosign-installer@v3

      - name: Cosign sign image
        env:
          COSIGN_EXPERIMENTAL: "1"
        run: |
          cosign sign --yes \
            ${{ env.REGISTRY }}/${{ env.IMAGE }}@${{ steps.build.outputs.digest }}

      - name: Cosign attest SBOM
        env:
          COSIGN_EXPERIMENTAL: "1"
        run: |
          cosign attest --yes --type cyclonedx --predicate sbom.cdx.json \
            ${{ env.REGISTRY }}/${{ env.IMAGE }}@${{ steps.build.outputs.digest }}

      - name: Upload SBOMs to release
        uses: softprops/action-gh-release@v2
        with:
          files: |
            sbom.cdx.json
            sbom.spdx.json

  provenance:
    needs: build-and-sign
    permissions:
      id-token: write
      packages: write
      contents: read
      actions: read
    uses: slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@v2.0.0
    with:
      image: ghcr.io/${{ github.repository }}
      digest: ${{ needs.build-and-sign.outputs.digest }}
      registry-username: ${{ github.actor }}
    secrets:
      registry-password: ${{ secrets.GITHUB_TOKEN }}
```

Notas:

- `generator_container_slsa3.yml` gera proveniência **L3** automaticamente (mas a declaração real depende de sua organização).
- Use `@v2.0.0` ou versão pinada; não use `@main`.

---

## 2. Verificação local

```bash
export IMG=ghcr.io/$OWNER/medvault-api@sha256:...

cosign verify \
  --certificate-identity-regexp "https://github.com/$OWNER/medvault-api/.github/workflows/release.yml@refs/tags/v.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  $IMG

# Verificar attestation de SBOM
cosign verify-attestation \
  --certificate-identity-regexp "https://github.com/$OWNER/medvault-api/.*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  --type cyclonedx $IMG | jq '.'
```

Adicionar ao Makefile:

```makefile
verify:
	cosign verify \
	  --certificate-identity-regexp "https://github.com/$(OWNER)/medvault-api/.*" \
	  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
	  $(IMG)

sbom:
	syft $(IMG) -o cyclonedx-json=sbom.cdx.json -o spdx-json=sbom.spdx.json

sbom-scan:
	grype sbom:sbom.cdx.json --fail-on high
```

---

## 3. Política de registry

Documente em `docs/supply-chain.md`:

- Só `main` e tags `v*` produzem imagens no GHCR.
- Todas imagens são **assinadas** por `release.yml`; runner local não assina.
- SBOM é anexado **a cada release** e revalidado trimestralmente com Grype.
- Proveniência SLSA é publicada junto; verificação automática acontece no cluster (Parte 4).

---

## 4. Plano SLSA

`docs/slsa.md`:

```markdown
# SLSA roadmap — MedVault

## Estado atual
- Build script versionado (Dockerfile no repo): sim.
- Build em plataforma hospedada (GHA): sim.
- Proveniencia assinada (via generator): sim.
- Nivel atual: **L2** — com generator SLSA L3 em producao, mas nao hardened conforme L3 completo.

## Proximos passos para L3 real
- Builds hermeticos (sem dependencia de internet em tempo de build alem do proxy cacheado).
- Runner dedicado e isolado (self-hosted em sandbox).
- Dependencias verificadas via OPA antes do build.

## Revisao
Trimestral. Proxima: 2026-07-21.
```

---

## 5. SBOM re-scan scheduled

`.github/workflows/sbom-rescan.yml`:

```yaml
name: sbom-rescan
on:
  schedule:
    - cron: "0 6 * * 1"    # segunda 06:00 UTC
  workflow_dispatch:

jobs:
  rescan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Grype sobre ultimas 3 releases
        run: |
          for tag in $(gh release list --limit 3 --json tagName -q '.[].tagName'); do
            gh release download $tag -p "sbom.cdx.json" -D "sbom-$tag"
            grype sbom:"sbom-$tag/sbom.cdx.json" --fail-on high || echo "::warning::$tag afetada"
          done
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Critérios de aceitação

- [ ] `release.yml` executa no push de tag `v*` e publica imagem + SBOM + assinatura.
- [ ] `cosign verify` local passa com `--certificate-identity-regexp` apontando para seu workflow.
- [ ] SBOM (CycloneDX e SPDX) está anexado a cada release.
- [ ] Proveniência gerada pelo `slsa-github-generator` aparece no ecossistema OCI (`cosign tree IMG`).
- [ ] `docs/slsa.md` documenta nível atual + roteiro.
- [ ] Workflow agendado de re-scan existe.

Próxima: [Parte 4 — admission e cluster endurecido](./parte-4-admission-cluster.md).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — Pipeline de segurança no CI](parte-2-pipeline-seguranca.md) | **↑ Índice**<br>[Módulo 9 — DevSecOps](../README.md) | **Próximo →**<br>[Parte 4 — Admission control e cluster endurecido](parte-4-admission-cluster.md) |

<!-- nav:end -->

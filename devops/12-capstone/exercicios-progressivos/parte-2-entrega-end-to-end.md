# Marco 2 — Sistema entregando em staging

**Tag alvo:** `v0.2.0-delivery-ready`.
**Tempo sugerido:** 3 semanas.
**Fase correspondente:** [Fase 2](../bloco-2/02-fase-entrega.md) + [armadilhas](../bloco-2/02-armadilhas-e-dicas.md).

---

## Objetivo

Provar que você consegue **entregar software até produção com um caminho pavimentado**: CI completo, containers hardened, IaC, K8s, estratégia de release escolhida, migrations expand/contract.

Ao final: um `git push` resulta num **Pod atualizado em staging**, sem intervenção manual.

---

## Entregáveis

### Aplicação
- [ ] API FastAPI com ≥ 5 endpoints funcionais (incl. `/healthz`, `/ready`).
- [ ] Worker consumindo fila com idempotência.
- [ ] Schema DB versionado com Alembic; ≥ 1 migration expand/contract.
- [ ] `docker compose up` sobe tudo local em ≤ 3 min.

### CI/CD
- [ ] Pipeline com lint, test, coverage ≥ 70%, Bandit, pip-audit, Gitleaks.
- [ ] Build Docker multi-stage, distroless, nonroot.
- [ ] SBOM gerado (Syft) + image signed (Cosign).
- [ ] Trivy bloqueando Critical.
- [ ] Deploy automático em **staging** a cada merge em `main`.
- [ ] Deploy em prod sob gate manual (GitHub Environments).

### IaC + K8s
- [ ] IaC em OpenTofu ou Pulumi versionado.
- [ ] Kustomize com `base/` + `overlays/{dev,staging,prod}`.
- [ ] K8s: Deployment, Service, Ingress, HPA, PDB, NetworkPolicy, RBAC mínimo.
- [ ] Checkov e/ou Kyverno rodando em CI.
- [ ] Cluster k3d/kind documentado para criação local.

### Release
- [ ] Estratégia escolhida (blue-green, canary, rolling) documentada em ADR.
- [ ] Rollback testado e registrado em `docs/retro/marco2.md`.

### Evidências
- [ ] Retrospectiva em `docs/retro/marco2.md` incluindo: tempo de CI, primeiros gaps identificados.
- [ ] `CHANGELOG.md` com entrada `v0.2.0`.
- [ ] Tag `v0.2.0-delivery-ready`.

---

## Demonstração esperada (prévia de banca)

Você abre um PR trivial (muda um texto). Em ≤ 20 min:

1. CI roda verde.
2. Imagem é construída, assinada, publicada.
3. ArgoCD (ou equivalente) atualiza staging.
4. Pod novo em ready.
5. `curl` contra staging retorna 200.

Filme isso (mesmo curto) e salve em `docs/media/marco2-rollout.mp4` ou similar.

---

## Critérios de avaliação deste marco

| Item | Peso local |
|------|------------|
| CI completo e rápido (< 15 min) | 20% |
| Imagem hardened + SBOM + Cosign | 15% |
| K8s manifests com probes/recursos/PDB/NetworkPolicy | 15% |
| IaC funcional | 10% |
| Deploy staging automatizado | 15% |
| Estratégia de release documentada e testada | 10% |
| Rollback funcional | 10% |
| Retrospectiva | 5% |

---

## Armadilhas

- "Temos SBOM" mas **nunca** verificamos.
- Imagem com CVE Critical em main sem VEX declarado.
- CI que nunca testou rollback real.
- IaC que "aplica tudo" num único ambiente indistinto.
- Manifest K8s sem `resources.limits` — HPA some no cluster; custo explode.
- Migration destrutiva misturada com deploy de app.

---

## Antes de fechar o marco

1. Derrube 1 Pod manualmente (`kubectl delete`). O sistema se recompõe em ≤ 60s? Quem detecta?
2. Mude um env var no `values.yaml`. Re-roll faz em quanto tempo?
3. Reverta para a imagem anterior. Quanto tempo para concluir rollback? Mede!
4. Rode Trivy local contra imagem de staging. Há Critical? Aceito com VEX? Ou bloqueia merge?

Se essas 4 respostas são positivas, o Marco 2 está fechado.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Marco 1 — Design e fundação](parte-1-design-fundacao.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Marco 3 — Sistema observável e resiliente](parte-3-operacao-resiliencia.md) |

<!-- nav:end -->

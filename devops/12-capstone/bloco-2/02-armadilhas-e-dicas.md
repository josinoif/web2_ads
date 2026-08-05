# Fase 2 — Armadilhas, dicas e orientações de banca

> Complemento à [Fase 2 — Entrega contínua](./02-fase-entrega.md).

---

## 1. O que a banca testa aqui

1. *"Derrube um Pod — o que acontece?"* Você precisa mostrar HPA ou replicaSet recriando.
2. *"Altere a versão da imagem para a tag anterior — como rollba?"* Você precisa **saber**, não improvisar.
3. *"Rode uma migration nova. Mostre o passo expand/contract."* Precisa estar **automatizado**.
4. *"Fale da cadeia de supply chain: do seu commit até produção, o que garante integridade?"* Cosign + SBOM + admission precisa ser narrativa, não adereço.
5. *"Por que essa estratégia de release?"* ADR-0003 guia a resposta; se não há ADR, ruim.

---

## 2. Sinais de CI saudável

- Tempo de PR < 15 min. Se passa disso, algo está ocioso (builds sem cache, testes redundantes).
- Cobertura não cai sem aviso — use `coverage-gate`.
- Deploy é **comum** (várias vezes/semana), não drama.
- Rollback testado ao menos 1× — na Fase 2.

---

## 3. Hierarquia de custos típicos

Quando algo atrasa nessa fase, costuma ser (em ordem):

1. **Build Docker lento** por falta de cache de camadas.
2. **Testes com DB real** sem Testcontainers — inflam tempo.
3. **Scan de imagem** rodado 3× no mesmo pipeline.
4. **Deploy sem observar** — você "empurra" e não verifica o rollout.

Reduções rápidas:

- `docker buildx` com `cache-from` e `cache-to`.
- `pytest-xdist` para paralelismo.
- `trivy --skip-dirs` em paths não-relevantes.
- `kubectl rollout status deployment/api -w` após deploy; falha se não converge em 3 min.

---

## 4. Supply chain: o que precisa existir

Na Fase 2 você precisa mostrar a **cadeia**:

```
commit -> CI -> imagem ----cosign-sign----> registry
           |                                    |
           |---> SBOM (Syft)                    |
           |---> SCA/SAST                       |
                                                |
cluster <---- admission Kyverno ---- digest + sig verificada
```

Se qualquer seta falta, há um elo fraco. A banca vai apontar.

---

## 5. Perguntas que a banca faz

### 5.1 Sobre CI

- *"Como esse pipeline roda offline?"* → resposta boa: *"Precisamos acesso a registry/repositório; Sim/Não cobre uso desconectado; fallback é cache local."*
- *"O que acontece se o gitleaks encontra uma chave?"* → *"Falha CI; rotação obrigatória; evento abre incidente Sev-3; postmortem."*

### 5.2 Sobre containers

- *"Por que distroless e não alpine?"* → *"Alpine usa musl, libc quebra algumas libs Python; distroless usa glibc + menor superfície; trade-off é debugging difícil (faltam shell). Compensamos com ephemeral containers."*
- *"Como você debuga um pod sem shell?"* → `kubectl debug pod -it --image=busybox --target=api`.

### 5.3 Sobre K8s

- *"Por que HPA CPU-based e não custom metric?"* → resposta ok: *"CPU covers 80% dos casos; custom (req/s via Prometheus Adapter) está no backlog se uso mostrar que CPU não reflete carga real."*
- *"Seu NetworkPolicy cobre egress?"* → precisa cobrir, sim. Default-deny, então allow DB/Redis/Kafka/Prometheus explicitamente.

### 5.4 Sobre release

- *"Em canary, qual % você promove e por quê?"* → *"10% inicial, 25%, 50%, 100%, cada etapa com gate SLO por 5 min; se burn rate > x, aborta automático."*
- *"O que diferencia canary de blue-green aqui?"* → *"Canary testa com usuários reais parciais; blue-green troca tudo de uma vez; escolhemos canary por estarmos em crescimento e termos prefeituras que podem servir como canário."*

---

## 6. Erros que reprovam instantaneamente

- Imagens sem scan entrando em prod.
- Secret versionado como YAML claro em Git público.
- `latest` em deployment produtivo.
- `imagePullPolicy: Always` sem digest explícito.
- CI que passa com coverage trivial ("`assert True`").
- Migração destrutiva misturada com deploy de app (perde dados).

---

## 7. Ferramentas que ajudam (não obrigatórias, mas fazem diferença)

- **`pre-commit`** — lint e format antes de commit.
- **`commitizen`** — commits padronizados (Conventional Commits).
- **`release-please`** (Google) — changelog + tag semver automático.
- **`argo-rollouts`** — canary/blue-green nativo.
- **`kustomize`** — overlays sem copiar YAMLs entre ambientes.
- **`tilt`** / **`skaffold`** — DX de dev no K8s local.
- **`kind-network-policy`** — CNI com suporte a NetworkPolicy em `kind` (o default não suporta).

---

## 8. Sinais de que você está pronto para a Fase 3

- `make up` sobe ambiente e você consegue criar um report via `curl`.
- PR que muda um texto deploya em staging em < 20 min sem intervenção.
- Imagem é assinada; registry admite só assinadas (policy).
- Rollback testado.
- Ao menos 2 ADRs novos surgiram nesta fase (decisões que não existiam na Fase 1).
- README raiz atualizado com links funcionais.

Se tudo marcado, `git tag v0.2.0-delivery-ready` e parta para a Fase 3.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Fase 2 — Entrega contínua end-to-end](02-fase-entrega.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Fase 3 — Operação e resiliência](../bloco-3/03-fase-operacao.md) |

<!-- nav:end -->

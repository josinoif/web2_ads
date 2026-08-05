# Parte 5 — Pipeline CI/CD + Policy + Plano de Adoção

**Objetivo:** fechar o MVP da Nimbus com:

1. **Pipeline CI/CD de IaC** (plan em PR, apply em merge).
2. **Policy as Code** (Checkov + `iac_policy_check.py` + opcional OPA).
3. **Runbook de onboarding** tempo-medido.
4. **Plano de adoção** para os 39 times restantes.
5. **Apresentação executiva** (bônus).

Esta parte encerra o módulo. O resultado é o material da **entrega avaliativa**.

---

## Pré-requisitos

- Partes 1-4 concluídas.
- Repositório no GitHub com o código.
- Permissões para configurar GitHub Actions Secrets e Environments.

---

## Tarefa 1 — Secrets no GitHub

Configure em **Settings → Secrets and variables → Actions**:

| Secret | Valor |
|--------|-------|
| `MINIO_ACCESS_KEY` | `minio-admin` (ou dedicado para CI) |
| `MINIO_SECRET_KEY` | senha |
| `SOPS_AGE_KEY` | conteúdo do seu `~/.config/sops/age/keys.txt` (private key inclusive) |
| `MINIO_ENDPOINT` | `https://minio.nimbus.internal:9000` (ou túnel) |

**Observação:** em uma fintech real, um SRE distinto gera credenciais específicas de CI (separadas das humanas). Para o estudo, reusamos a do bootstrap — **documentar isso como dívida técnica** em `docs/limites-reconhecidos.md`.

Configure também **GitHub Environments** (`Settings → Environments`):

- `piloto-dev` (sem required reviewers; auto-apply).
- `piloto-stg` (1 required reviewer).
- `piloto-prod` (2 required reviewers; opcional — só se fez `piloto-prod` na Parte 4).

---

## Tarefa 2 — Pipeline `iac-plan.yml`

`.github/workflows/iac-plan.yml`:

```yaml
name: IaC Plan

on:
  pull_request:
    paths:
      - 'envs/**'
      - 'modules/**'
      - 'policies/**'

permissions:
  contents: read
  pull-requests: write

jobs:
  changes:
    runs-on: ubuntu-latest
    outputs:
      envs: ${{ steps.filter.outputs.envs }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          list-files: json
          filters: |
            envs:
              - 'envs/**'
              - 'modules/**'

  plan:
    needs: changes
    if: needs.changes.outputs.envs == 'true'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        env: [piloto-dev, piloto-stg]
    steps:
      - uses: actions/checkout@v4

      - name: Setup SOPS age key
        run: |
          mkdir -p ~/.config/sops/age
          echo "${{ secrets.SOPS_AGE_KEY }}" > ~/.config/sops/age/keys.txt
          chmod 600 ~/.config/sops/age/keys.txt

      - name: Install sops and yq
        run: |
          SOPS_VERSION=v3.8.1
          curl -fsSLO https://github.com/getsops/sops/releases/download/${SOPS_VERSION}/sops-${SOPS_VERSION}.linux.amd64
          sudo mv sops-${SOPS_VERSION}.linux.amd64 /usr/local/bin/sops
          sudo chmod +x /usr/local/bin/sops
          sudo apt-get install -y yq || pip install yq

      - name: Setup OpenTofu
        uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: 1.8.0

      - name: Fmt
        run: tofu fmt -check -recursive envs/${{ matrix.env }} modules/

      - name: Init
        working-directory: envs/${{ matrix.env }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.MINIO_ACCESS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.MINIO_SECRET_KEY }}
        run: tofu init

      - name: Validate
        working-directory: envs/${{ matrix.env }}
        run: tofu validate

      - name: Checkov
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: envs/${{ matrix.env }}
          framework: terraform
          soft_fail: false

      - name: Policy own (iac_policy_check.py)
        run: |
          python3 scripts/iac_policy_check.py envs/${{ matrix.env }}

      - name: Plan
        id: plan
        working-directory: envs/${{ matrix.env }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.MINIO_ACCESS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.MINIO_SECRET_KEY }}
        run: |
          tofu plan -no-color -out=plan.bin > plan.txt 2>&1 || exit $?
          {
            echo 'plan<<__EOF__'
            cat plan.txt
            echo '__EOF__'
          } >> $GITHUB_OUTPUT

      - name: Upload plan artifact
        uses: actions/upload-artifact@v4
        with:
          name: plan-${{ matrix.env }}
          path: envs/${{ matrix.env }}/plan.bin
          retention-days: 7

      - name: Comment PR
        uses: actions/github-script@v7
        with:
          script: |
            const body = `### OpenTofu Plan — \`${{ matrix.env }}\`\n\n<details><summary>Ver plan</summary>\n\n\`\`\`\n${{ steps.plan.outputs.plan }}\n\`\`\`\n\n</details>`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body,
            });
```

### Testar

1. Crie uma branch: `git checkout -b feat/teste-pipeline`.
2. Faça qualquer mudança inócua em `envs/piloto-dev/main.tf` (ex.: ajuste de comentário que não mude plan).
3. Commit + push.
4. Abra PR.
5. Observe:
   - `fmt`, `validate`, `checkov`, `iac_policy_check.py` rodando.
   - Comentário automático com o plan.
6. **Injete violação** de policy (ex.: `privileged = true` num container) → pipeline deve **falhar** em Checkov ou no script próprio.
7. Reverta; PR volta a ficar verde.

---

## Tarefa 3 — Pipeline `iac-apply.yml`

`.github/workflows/iac-apply.yml`:

```yaml
name: IaC Apply

on:
  push:
    branches: [main]
    paths:
      - 'envs/**'
      - 'modules/**'

permissions:
  contents: read

jobs:
  apply:
    runs-on: ubuntu-latest
    strategy:
      max-parallel: 1
      matrix:
        env: [piloto-dev, piloto-stg]
    environment:
      name: ${{ matrix.env }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup SOPS age key
        run: |
          mkdir -p ~/.config/sops/age
          echo "${{ secrets.SOPS_AGE_KEY }}" > ~/.config/sops/age/keys.txt
          chmod 600 ~/.config/sops/age/keys.txt

      - name: Install sops and yq
        run: |
          SOPS_VERSION=v3.8.1
          curl -fsSLO https://github.com/getsops/sops/releases/download/${SOPS_VERSION}/sops-${SOPS_VERSION}.linux.amd64
          sudo mv sops-${SOPS_VERSION}.linux.amd64 /usr/local/bin/sops
          sudo chmod +x /usr/local/bin/sops
          pip install yq

      - name: Setup OpenTofu
        uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: 1.8.0

      - name: Init
        working-directory: envs/${{ matrix.env }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.MINIO_ACCESS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.MINIO_SECRET_KEY }}
        run: tofu init

      - name: Apply
        working-directory: envs/${{ matrix.env }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.MINIO_ACCESS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.MINIO_SECRET_KEY }}
        run: tofu apply -auto-approve
```

**Ponto crítico:** `environment: piloto-stg` força a aprovação humana **antes** de o apply rodar (se o Environment estiver configurado com `required reviewers`). Em `prod` seria 2 pessoas.

### Testar

1. Merge do PR limpo da Tarefa 2.
2. Vá em **Actions → IaC Apply → Waiting for review**.
3. Aprove `piloto-dev` (auto-aprovado se sem reviewers).
4. Para `piloto-stg`, um reviewer (pode ser você mesmo via PAT) precisa aprovar.
5. Veja o apply rodar e o state ser atualizado no MinIO.

---

## Tarefa 4 — Pipeline de drift detection

`.github/workflows/iac-drift.yml`:

```yaml
name: IaC Drift Detection

on:
  schedule:
    - cron: '0 3 * * *'   # 03:00 UTC
  workflow_dispatch:

jobs:
  detect:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        env: [piloto-dev, piloto-stg]
    steps:
      - uses: actions/checkout@v4

      - name: Setup SOPS age key
        run: |
          mkdir -p ~/.config/sops/age
          echo "${{ secrets.SOPS_AGE_KEY }}" > ~/.config/sops/age/keys.txt
          chmod 600 ~/.config/sops/age/keys.txt

      - name: Install sops and yq
        run: |
          SOPS_VERSION=v3.8.1
          curl -fsSLO https://github.com/getsops/sops/releases/download/${SOPS_VERSION}/sops-${SOPS_VERSION}.linux.amd64
          sudo mv sops-${SOPS_VERSION}.linux.amd64 /usr/local/bin/sops
          sudo chmod +x /usr/local/bin/sops
          pip install yq

      - name: Setup OpenTofu
        uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: 1.8.0

      - name: Init
        working-directory: envs/${{ matrix.env }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.MINIO_ACCESS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.MINIO_SECRET_KEY }}
        run: tofu init

      - name: Plan (detailed exit code)
        id: plan
        working-directory: envs/${{ matrix.env }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.MINIO_ACCESS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.MINIO_SECRET_KEY }}
        run: |
          set +e
          tofu plan -detailed-exitcode -no-color -out=plan.bin > plan.txt 2>&1
          echo "exit=$?" >> $GITHUB_OUTPUT

      - name: Open drift issue
        if: steps.plan.outputs.exit == '2'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const planText = fs.readFileSync('envs/${{ matrix.env }}/plan.txt', 'utf-8').slice(0, 6000);
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Drift detectado em ${{ matrix.env }}`,
              labels: ['drift','iac'],
              body: `Drift detectado em \`${{ matrix.env }}\`.\n\n<details><summary>plan</summary>\n\n\`\`\`\n${planText}\n\`\`\`\n\n</details>\n\n**SLA:** investigar em 3 dias úteis.`,
            });
```

**Teste:** rode manualmente via `workflow_dispatch`. Induza drift (ex.: `docker rm -f piloto-dev-redis`) e dispare o workflow — deve abrir uma issue.

---

## Tarefa 5 — Policies

### Checkov — config

`policies/checkov/.checkov.yml`:

```yaml
framework:
  - terraform
skip-check:
  - CKV_DOCKER_2   # se já sabido que não aplicamos HEALTHCHECK para tudo (justifique!)
soft-fail: false
```

### Policy própria — script `iac_policy_check.py`

Copie o script do Bloco 4 para `scripts/iac_policy_check.py` e integre no workflow (passo "Policy own" já acima).

### Quebre a policy (teste!)

1. Branch nova.
2. Edite `envs/piloto-dev/main.tf` — adicione `privileged = true` num container.
3. Push + PR.
4. Pipeline **falha** em Checkov (CKV_DOCKER_5) E no `iac_policy_check.py` (NIM-001).
5. Reverta.

Documente em `docs/politica-cve.md` (analogia ao Módulo 5):

- O que cada regra verifica.
- Qual a justificativa (regulação? segurança? higiene?).
- Quando skip é aceitável (nunca em prod).

---

## Tarefa 6 — Runbook de onboarding

`docs/runbook-onboarding.md`:

```markdown
# Runbook — Onboarding de novo time na Nimbus IaC

**Tempo esperado:** ≤ 30 min ponta-a-ponta.
**Executor:** SRE da plataforma ou time de produto (depois da onda 2).

## Pré-requisitos

- Acesso de write ao repositório `nimbus-iac` (ou fork + PR).
- Chave age pública cadastrada em `.sops.yaml`.
- Acesso ao MinIO (bucket `nimbus-tfstate`).

## Passo 1 — Criar diretório do ambiente (1 min)

    cp -r envs/piloto-dev envs/<time>-dev
    sed -i 's/piloto/<time>/g' envs/<time>-dev/main.tf
    sed -i 's/piloto\/dev/<time>\/dev/g' envs/<time>-dev/backend.tf

## Passo 2 — Criar segredos (2 min)

    sops envs/<time>-dev/secrets.secret.yaml
    # No editor:
    # postgres_password: <gere com `openssl rand -hex 16`>

## Passo 3 — Escolher porta livre (1 min)

Verifique portas em uso: `grep -R porta_api_externa envs/`.
Edite `main.tf` para uma porta livre (ex.: 8090).

## Passo 4 — PR (5 min)

    git checkout -b feat/onboarding-<time>
    git add envs/<time>-dev
    git commit -m "onboarding: time <time>"
    git push -u origin feat/onboarding-<time>

Abra PR. Pipeline roda: fmt → validate → checkov → policy → plan.

## Passo 5 — Review (variável — meta ≤ 10 min)

Revisor confere:
- Nome do time em kebab-case.
- Porta única.
- Plan "+ 7 to create" (ou similar).

## Passo 6 — Merge + apply (3 min)

Merge em `main` → `iac-apply.yml` dispara.
Para `<time>-dev`, apply é automático; para `<time>-stg`, precisa aprovar no Environment.

## Passo 7 — Smoke test (3 min)

    curl -I http://localhost:<porta>
    # 200 OK

Pronto. Ambiente do time está operando via IaC.

## Passo 8 — Comunicar o time

Envie link do output do apply (URLs, nomes dos containers) pelo canal do time.
Informe que, a partir daqui, qualquer mudança passa por PR.
```

**Teste:** peça a um colega (ou simule) que execute o runbook para um time fictício (ex.: "dados-batch"). Cronometre. Meta: ≤ 30 min.

Anote o tempo em `docs/runbook-onboarding.md#tempo-medido`.

---

## Tarefa 7 — Plano de adoção

`docs/plano-adocao.md`:

```markdown
# Plano de adoção — Nimbus IaC

**Meta:** migrar os 40 times da Nimbus para IaC-first, em 3 ondas, ao longo de 6 meses.

## Onda 1 — Piloto (semanas 1-4) — 1 time

- Time escolhido: Pagamentos Corporate.
- Ambientes: dev + stg (prod continua manual).
- Objetivo: validar que runbook é executável em 30 min.
- **Critério para ir à onda 2:** 4 semanas sem regressão no piloto.

## Onda 2 — Early adopters (semanas 5-12) — 8 times

- Critério de seleção:
  - Times com ≤ 6 meses de idade (menor dívida).
  - Tech leads favoráveis à mudança.
  - Carga de produção baixa (tolerância a ajustes).
- Ambientes: dev + stg.
- **Processo:** cada time abre PR de onboarding; SRE de plataforma pareia nos primeiros PRs.
- **Critério para ir à onda 3:** média de 1 PR de IaC mergado por semana por time.

## Onda 3 — Resto + produção (semanas 13-26) — 31 times + todos os prods

- Times restantes onboarded em batches de 3-5 por semana.
- Migração de ambientes `prod` de todos os times.
- Aprovação de `prod` exige: 2 reviewers, 1 sendo SRE da plataforma.
- Descomissionamento dos fluxos manuais antigos (portais clicáveis fechados para criação de recursos).

## Métricas por onda

| Métrica | Onda 1 | Onda 2 | Onda 3 |
|---------|--------|--------|--------|
| Tempo médio de criação de ambiente | < 30 min | < 30 min | < 30 min |
| % times onboarded | 2.5% | 22.5% | 100% |
| % recursos em IaC | ~5% | ~30% | 100% |
| % mudanças via PR | 90% | 80% | 95% |
| Incidentes de drift / semana | 0-1 | 1-3 | < 1 |

## Riscos e mitigações

| Risco | Probabilidade | Mitigação |
|-------|---------------|-----------|
| Resistência cultural ("eu gosto do portal") | Alta | Workshops, pareamento nas primeiras PRs, métricas visíveis |
| Drift durante migração | Alta | Import incremental; aceita-se drift enquanto migra |
| CI fora do ar trava provisionamento | Média | Procedimento break-glass documentado |
| SOPS keys perdidas | Baixa | Múltiplas chaves age recipients; backup em cofre offline |
| MinIO fora do ar | Média | HA de MinIO na onda 3; backup de state em Postgres |

## Governança

- **Platform team** mantém módulos, policies, pipelines.
- **Times de produto** são responsáveis pelos seus `envs/`.
- **CODEOWNERS**: mudanças em `modules/` e `policies/` exigem aprovação do platform team.
- **Reunião semanal** de stewards: discute drifts abertos, novos pedidos, incidentes.

## Quando abandonar o plano

- Se após 8 semanas da onda 2 tempo médio de criação de ambiente > 1 hora: plano precisa revisão.
- Se a taxa de incidentes causados por IaC ≥ taxa pré-migração: pausa + postmortem.
```

---

## Tarefa 8 — Matriz de "o que IaC resolve / não resolve" na Nimbus

`docs/matriz-responsabilidades.md` — relacione **este módulo** com os **seguintes** (6 → 7 → 8 → 9):

| Problema da Nimbus | Módulo 6 (IaC) | Módulo 7 (K8s) | Módulo 8 (Obs.) | Módulo 9 (DevSecOps) |
|---------------------|-----------------|-----------------|------------------|-----------------------|
| Criação automatizada de ambiente | ✅ resolve | (amplia para K8s) | — | — |
| Rollback de infra | ✅ resolve (`git revert`) | ✅ resolve (rollouts) | — | — |
| Auditoria de mudanças | ✅ resolve (git log) | ✅ complementa | ✅ sinal em traces | ✅ scan em PR |
| Segurança de runtime | parcial (provisiona flags) | ✅ (RBAC, NetworkPolicy) | ✅ (detecção) | ✅ (scan, WAF) |
| Drift | ✅ detecta | ✅ (K8s converge) | — | — |
| Gestão de dados (backup/restore) | ❌ | ❌ | ❌ | ❌ (processo separado) |
| Observabilidade | ❌ | parcial | ✅ resolve | — |
| Compliance | parcial (policy as code) | parcial | ✅ evidências | ✅ auditoria |

Esse documento é parte da **entrega avaliativa**.

---

## Tarefa 9 (bônus) — Apresentação executiva

Monte **10 slides** (ou 5 páginas) em `docs/apresentacao-executiva.md` ou PDF:

1. **Capa** — "Nimbus IaC — Piloto MVP".
2. **Problema** — 10 sintomas, backlog, custo operacional.
3. **Proposta** — IaC + pipeline + policy + secrets.
4. **Tecnologia** — OpenTofu + Docker + MinIO + SOPS + GitHub Actions.
5. **Demonstração** — prints: PR com plan → apply → ambiente up.
6. **Métricas** — antes vs depois (tempo de provisionamento, % em código, etc.).
7. **Plano** — 3 ondas, 6 meses.
8. **Riscos** — top 3 e mitigações.
9. **Orçamento/Recursos** — 1 SRE full-time para onda 2-3; custo de MinIO.
10. **Pedido** — patrocínio executivo + horário dos times para pareamento.

O objetivo é **convencer o VP a autorizar** as ondas 2 e 3.

---

## Entregáveis desta parte

- [ ] `.github/workflows/iac-plan.yml` funcional.
- [ ] `.github/workflows/iac-apply.yml` funcional.
- [ ] `.github/workflows/iac-drift.yml` funcional.
- [ ] Checkov + `iac_policy_check.py` rodando; violação falha o PR.
- [ ] `docs/runbook-onboarding.md` com tempo cronometrado.
- [ ] `docs/plano-adocao.md` com 3 ondas.
- [ ] `docs/matriz-responsabilidades.md`.
- [ ] `docs/politica-cve.md` (ou `docs/politicas-iac.md`) documentando regras ativas.
- [ ] (bônus) `docs/apresentacao-executiva.md` ou PDF.
- [ ] README raiz do repo atualizado com: como clonar, subir MinIO, rodar `make apply`, abrir PR, etc.

---

## Critério de pronto do módulo inteiro

Um avaliador deveria:

1. Clonar seu repositório.
2. Rodar o bootstrap do MinIO.
3. Injetar a chave age privada.
4. Abrir um PR inócuo → ver o plan comentado no PR.
5. Injetar violação de policy → ver o PR falhar.
6. Mergear PR limpo → ver apply rodando.
7. Ler o plano e entender como escalaria para 40 times.

Se responde "sim" a todos os passos, **o módulo está completo**.

---

## Fim do Módulo 6

Você terminou. Se documentou tudo bem, já tem o material da **entrega avaliativa**.

Sinais de que você aprendeu:

- Escreve HCL sem consultar documentação para o básico.
- Lê um `plan` de 200 linhas e pega o essencial em 30 segundos.
- Sabe **quando** IaC é a resposta — e quando **não** é.
- Reconhece que estado é informação crítica; trata backend remoto como inegociável.
- Discute policy as code como prática de **engenharia**, não obstáculo burocrático.

**Próximos passos sugeridos da disciplina:**

- **Módulo 7 — Kubernetes:** substituir o "Docker local" pelo orquestrador real, com deployments, services, ingress, e IaC do próprio cluster.
- **Módulo 8 — Observabilidade:** provisionar, em IaC, a stack de métricas/logs/traces para os ambientes Nimbus.
- **Módulo 9 — DevSecOps:** SAST, DAST, scan de imagens, SBOM, políticas mais ricas.

---

## Reflexão final

A Nimbus hoje: 40 times, click-ops, 3 dias por ambiente.
A Nimbus depois deste plano: 40 times, PR + pipeline, < 30 min por ambiente.

A diferença é de **orgânica** — times deixam de esperar SREs, SREs deixam de ser atendentes, a plataforma passa a ser **produto interno com contrato claro**. IaC é o habilitador técnico; cultura + processo fazem a mudança acontecer.

**É isso que você entrega** na avaliação: não só o código, mas o **plano** de mudança organizacional que o código viabiliza.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 4 — Produção: Multi-ambiente + State Remoto + Secrets](parte-4-producao.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Entrega Avaliativa do Módulo 6](../entrega-avaliativa.md) |

<!-- nav:end -->

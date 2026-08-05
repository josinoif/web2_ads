# Entrega Avaliativa do Módulo 6

**Módulo:** Infraestrutura como Código (5h)
**Cenário:** Nimbus — ver [00-cenario-pbl.md](00-cenario-pbl.md)

---

## Objetivo da entrega

Construir o **MVP** da Nimbus automatizada: um repositório Git que descreve, em código, a infraestrutura de **um time piloto** com ambientes `dev` e `stg`, com pipeline de plan/apply, policy as code, secrets gerenciados, e plano documentado de adoção para os demais 39 times.

---

## O que entregar

### 1. Repositório GitHub com IaC funcional

Estrutura mínima sugerida:

```
nimbus-iac/
├── README.md
├── Makefile
├── .github/workflows/
│   ├── iac-plan.yml              # plan em PR
│   └── iac-apply.yml             # apply em merge
├── modules/
│   ├── ambiente-web/             # reusável
│   │   ├── main.tf (ou __main__.py se Pulumi)
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── banco-postgres/
├── envs/
│   ├── piloto-dev/
│   │   ├── main.tf
│   │   ├── terraform.tfvars
│   │   └── backend.tf
│   └── piloto-stg/
├── policies/
│   ├── opa/                       # rego
│   └── checkov/                   # config
├── scripts/
│   └── bootstrap.sh              # cria backend + state bucket
├── docs/
│   ├── arquitetura.md
│   ├── runbook-onboarding.md
│   ├── adr/                      # ≥ 3 ADRs
│   ├── plano-adocao.md
│   └── limites-reconhecidos.md
├── .gitignore
└── .editorconfig
```

### 2. Ferramenta escolhida (OpenTofu **ou** Pulumi)

Você deve escolher **uma** como ferramenta principal e justificar em ADR. Os conceitos (state, plan, módulos, policy) devem ser aplicados na ferramenta escolhida.

Requisitos comuns:

- **Código versionado** no repositório.
- **Dois ambientes** (`piloto-dev` e `piloto-stg`) subindo **a mesma topologia** com **variáveis diferentes**.
- **Módulos reutilizáveis** — mínimo 2 módulos (`ambiente-web` e `banco-postgres`).
- **State remoto** (self-hosted) — MinIO, HTTP backend ou Pulumi service self-hosted.
- **State com locking** funcional.
- **Outputs** significativos (URL da API, nome do volume, etc.).

### 3. Secrets gerenciados

- **Nenhum segredo em texto plano** no repositório (nem `.env.prod`).
- Uso de **SOPS + age**, **Vault**, ou equivalente self-hosted.
- Pelo menos **1 segredo** referenciado pela IaC (ex.: senha do Postgres).
- `.sops.yaml` (ou equivalente) no repositório, documentando as chaves.

### 4. Policy as Code

Checkov **ou** OPA/Rego:

- Pelo menos **3 regras ativas** bloqueando práticas proibidas. Exemplos:
  - "Nenhum contêiner com `--privileged`."
  - "Toda senha passa por variável sensível, nunca literal."
  - "Nenhum recurso tem tag vazia."
  - "Volume nomeado obrigatório em bancos."
- Pipeline **falha** quando a policy é violada.

### 5. Pipeline CI/CD de IaC

Workflows GitHub Actions (ou equivalente):

**`iac-plan.yml`** (PR):

- `tofu fmt -check` (ou `pulumi` equivalente).
- `tofu validate` (ou `pulumi preview`).
- `tofu plan` com artefato anexado.
- Checkov/OPA nos arquivos.
- Comentário automático no PR com resumo do plan.

**`iac-apply.yml`** (merge em `main` com approval):

- GitHub Environment com `required reviewers`.
- `tofu apply -auto-approve` **apenas após aprovação**.
- Notificação de sucesso/falha.

### 6. Runbook de onboarding

`docs/runbook-onboarding.md` — passo-a-passo para um **novo time** entrar na Nimbus:

1. Criar PR adicionando diretório `envs/<time>-dev/`.
2. Preencher `terraform.tfvars` com nome do time, imagem, porta, recursos.
3. Rodar `make plan TIME=<time>`.
4. Submeter PR, revisar plan, aprovar.
5. Merge → pipeline aplica.
6. Output do pipeline traz URL e credenciais (via secret store).

Meta de tempo do runbook: **≤ 30 minutos** ponta a ponta.

### 7. ADRs (≥ 3)

Em `docs/adr/`:

- **ADR 001 — Escolha da ferramenta** (OpenTofu vs Pulumi + justificativa).
- **ADR 002 — Estratégia de state e backend** (MinIO vs HTTP vs local + locking).
- **ADR 003 — Gestão de secrets** (SOPS vs Vault vs outro + rotação).

Opcionais: ADR 004 (estratégia de módulos), ADR 005 (policy engine).

### 8. Plano de adoção

`docs/plano-adocao.md` — como trazer os **40 times** para dentro da Nimbus automatizada:

- 3 ondas realistas com critério de "pronto para onda seguinte".
- Métricas de sucesso por onda (número de times, lead time de ambiente).
- Riscos e mitigações.

### 9. Limites reconhecidos

`docs/limites-reconhecidos.md`:

- O que este MVP **não** resolve: aplicação, observabilidade, K8s real, rollback de mudança acidental destrutiva (drop de DB etc.), equipe treinada.
- Ponte para Módulos 7 (K8s), 8 (observabilidade), 9 (DevSecOps).

### 10. Evidências

No README do repositório:

- Link de workflow verde.
- Print do comentário automático de plan num PR.
- Print do Checkov/OPA falhando em PR quando violação é injetada.
- Tempo medido do onboarding piloto (seu próprio runbook).
- Output de `tofu state list` (ou `pulumi stack`) dos 2 ambientes.

---

## Critérios de avaliação

| Critério | Peso | O que se espera |
|----------|------|------------------|
| **IaC funcional (2 envs, módulos)** | 20% | Código claro, `plan/apply/destroy` funcionam; módulos reutilizáveis |
| **State remoto + locking** | 10% | Backend self-hosted com locking verificável |
| **Secrets** | 10% | Zero secret literal; mecanismo de criptografia/escopo descrito |
| **Policy as Code** | 15% | ≥ 3 regras ativas; PR falha em violação; exemplos demonstrados |
| **Pipeline IaC** | 15% | plan em PR com comentário, apply em merge com approval |
| **Runbook + tempo medido** | 10% | Onboarding executável por terceiro em ≤ 30 min |
| **ADRs + arquitetura** | 10% | Decisões defensáveis, alternativas consideradas |
| **Plano de adoção + limites** | 10% | Plano realista; admite o que não resolve |

---

## Formato e prazo

- **Formato:** link do repositório GitHub.
- **Prazo:** conforme definido pelo professor. Sugestão: **1 semana após o encerramento do módulo**.
- **Avaliação:** o professor pode **clonar e executar** o pipeline. Certifique-se de que funciona do zero.

---

## Dicas

- **Comece pequeno** — um recurso, um módulo, um ambiente. Depois duplique.
- **Não invente um cluster real** — provider Docker do módulo já dá conta do MVP.
- **Não trate a entrega como "demonstração"** — trate como `main` de equipe real: README, Makefile, scripts de bootstrap, runbook. Outro estudante deveria clonar e executar sem perguntar.
- **`.gitignore`** robusto — nunca commit de `.terraform/`, `*.tfstate`, `*.tfstate.backup`, `.pulumi/`, chaves privadas.
- **Secrets**: se usar SOPS, commite **só o arquivo criptografado**. A chave privada fica fora do repo.

---

## Referência rápida do módulo

- [Cenário PBL — Nimbus](00-cenario-pbl.md)
- [Bloco 1 — Fundamentos de IaC](bloco-1/01-fundamentos-iac.md)
- [Bloco 2 — OpenTofu](bloco-2/02-opentofu-docker.md)
- [Bloco 3 — Pulumi](bloco-3/03-pulumi-python.md)
- [Bloco 4 — Produção](bloco-4/04-iac-producao.md)
- [Exercícios progressivos](exercicios-progressivos/)
- [Referências bibliográficas](referencias.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Pipeline CI/CD + Policy + Plano de Adoção](exercicios-progressivos/parte-5-pipeline-e-plano.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](README.md) | **Próximo →**<br>[Referências Bibliográficas — Módulo 6](referencias.md) |

<!-- nav:end -->

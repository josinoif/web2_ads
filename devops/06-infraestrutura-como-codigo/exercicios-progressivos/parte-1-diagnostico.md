# Parte 1 — Diagnóstico da Nimbus

**Objetivo:** entender o ponto de partida antes de escrever uma linha de código. Ao final, você saberá **o que** vai ser automatizado, **com qual ferramenta**, e **em que ordem**.

---

## Contexto

Releia o [cenário PBL](../00-cenario-pbl.md). Os 10 sintomas, metas da liderança e restrições (self-hosted) são o ponto de partida.

---

## Tarefa 1 — Matriz de sintomas × IaC

Para cada sintoma da Nimbus, responda:

- **(a) IaC resolve?** (sim, parcial, não)
- **(b) Que conceito específico resolve?**
- **(c) Qual o sinal de que foi resolvido?** (métrica observável)

### Entregável

Tabela em `docs/diagnostico.md` no seu repositório:

| # | Sintoma | IaC resolve? | Conceito específico | Sinal de resolução |
|---|---------|--------------|---------------------|---------------------|
| 1 | Click-ops em tudo | Sim | Código declarativo em git, pipeline obrigatório | 0 mudanças via portal em 30 dias |
| 2 | Ambientes floco de neve | Sim | Mesmo código + mesma versão de provider | `tofu plan` de todos os envs retorna "no changes" |
| 3 | Sem histórico | Sim | git log de `envs/<time>/*` | `git log` lista últimos 10 PRs |
| 4 | Rollback manual e lento | Sim | `git revert` + `apply` | Rollback testado em simulação em < 10 min |
| 5 | 3 dias para ambiente novo | Sim | Módulos + pipeline | Novo ambiente em ≤ 30 min |
| 6 | Disparidade dev/stg/prod | Sim | `envs/time-{dev,stg,prod}/` usando o mesmo módulo | Diff entre `tofu show` de envs é só variáveis |
| 7 | Credenciais em planilhas | Parcial | Secret store integrado (SOPS/Vault) | 0 segredos em e-mail/planilha |
| 8 | Onboarding pela sorte | Sim | Runbook executável é PR | Novo SRE aplica primeiro PR em < 1 semana |
| 9 | Desligar pior que criar | Sim | `tofu destroy` é 1 comando | Ambiente descomissionado em ≤ 10 min |
| 10 | Mudanças na madrugada | Parcial | Pipeline automatizado e reversível reduz risco percebido; cultura muda devagar | % de mudanças em horário comercial > 80% |

Note que **sintoma 10** ("mudanças na madrugada") é **parcial**: IaC reduz o risco técnico, mas a **cultura** de "só mexer à noite" precisa ser trabalhada também. Liste isso em `docs/limites-reconhecidos.md`.

---

## Tarefa 2 — Escolha de ferramenta

Você escolherá **uma** das ferramentas para a maior parte da Nimbus (com possibilidade de usar a outra em casos específicos).

### Entregável

Um ADR em `docs/adr/001-escolha-iac.md`:

- **Status:** Aceita / Em deliberação / Substituída.
- **Contexto:** regras da Nimbus, equipe majoritariamente Python, regulação self-hosted.
- **Opções analisadas:** OpenTofu/HCL, Pulumi/Python, Ansible, scripts shell + Docker Compose.
- **Decisão:** (sua escolha).
- **Consequências positivas:** explicite ≥ 3.
- **Consequências negativas:** explicite ≥ 2.
- **Quando revisitar:** evento/data que obrigaria a repensar (ex.: "se a Pulumi descontinuar provider Docker", "após 1 ano do piloto", etc.).

**Sugestão defensável** (e que seguiremos nas partes 2–5):

- **OpenTofu/HCL** como **padrão da plataforma** → maioria dos times, CI padronizado, mercado de profissionais, HCL é linguagem mais fácil de padronizar.
- **Pulumi/Python** disponível para **casos específicos** onde a expressividade de uma linguagem completa agrega (ex.: ferramenta interna que gera configs em lote a partir de um CSV).

Qualquer escolha bem justificada é aceita.

---

## Tarefa 3 — Topologia do repositório

Proponha a topologia de `nimbus-iac/` que usaremos nas Partes 2-5.

### Entregável

`docs/arquitetura.md` com:

- **Árvore de diretórios** anotada.
- **Convenção de nomes** (snake_case? kebab-case? padrão para `<time>-<env>`?).
- **Regras de escopo** — "cada pasta `envs/*` tem seu próprio state; nada de compartilhar"; "módulos são versionados por tag; envs referenciam por caminho relativo em monorepo".

**Exemplo mínimo:**

```
nimbus-iac/
├── README.md                 # instruções de uso
├── Makefile                  # atalhos: make plan ENV=piloto-dev
├── .github/
│   └── workflows/
│       ├── iac-plan.yml
│       ├── iac-apply.yml
│       └── iac-drift.yml
├── modules/                  # reusáveis
│   ├── ambiente-web/
│   └── banco-postgres/
├── envs/                     # um diretório por (time, ambiente)
│   ├── piloto-dev/
│   ├── piloto-stg/
│   └── piloto-prod/
├── policies/                 # policy as code
│   ├── checkov/
│   └── opa/
├── scripts/
│   ├── bootstrap.sh          # cria bucket de state, chave age
│   └── iac_policy_check.py   # lint didático
├── pulumi-alt/               # projeto Pulumi paralelo (Parte 3)
├── docs/
│   ├── adr/
│   ├── arquitetura.md
│   ├── plano-adocao.md
│   ├── limites-reconhecidos.md
│   ├── runbook-onboarding.md
│   └── diagnostico.md
├── .sops.yaml
├── .gitignore
└── .editorconfig
```

---

## Tarefa 4 — Definir o piloto

Defina **qual time** será o piloto da automação, e **quais ambientes** (dev/stg/prod ou só dev+stg).

### Entregável

`docs/piloto.md`:

- **Time escolhido:** (ex.: "Pagamentos Corporate" — novo time, com <6 meses, baixa inércia e liderança tecnicamente simpática).
- **Ambientes a automatizar primeiro:** só `dev` e `stg` no MVP. `prod` só após o piloto comprovar estabilidade por 30 dias.
- **Recursos cobertos:**
  - Rede dedicada.
  - Banco Postgres (com volume).
  - Cache Redis.
  - API (container placeholder; a aplicação real vem dos Módulos 4/5).
- **Recursos excluídos do MVP:**
  - DNS interno (fica manual pra demonstração; automatizar na onda 2).
  - Certificados TLS (Módulo 9).
  - Observabilidade (Módulo 8).

**Critérios de sucesso** do piloto:

1. Ambiente `dev` do piloto é criado e destruído em ≤ 30 min, totalmente por PR.
2. 1 mudança simulada passa por plan em PR, review, merge, apply.
3. Drift induzido é detectado pelo pipeline em até 24h.
4. Outro SRE (não você) consegue criar o ambiente seguindo o runbook, sem ajuda.

---

## Tarefa 5 — Identificar limites de IaC

Liste explicitamente o que **IaC não resolverá** nesta jornada.

### Entregável

`docs/limites-reconhecidos.md`:

Use a tabela do Bloco 4, seção 10, como ponto de partida. Adicione observações específicas para a Nimbus:

- **Cultura** — "Mudança na madrugada" não desaparece só porque existe pipeline; exige trabalho social com a liderança dos times.
- **Dados** — backup/restore de Postgres é **outro** processo; IaC provisiona o volume, não zela pelos dados.
- **Observabilidade** — métricas, traces, logs continuam vindo dos Módulos 8 e 9.
- **Mudanças emergenciais** — break-glass continua existindo; o que muda é que passa a ser **auditado** e seguido de PR de ajuste.

Este documento é parte da **entrega avaliativa**.

---

## Critério de pronto para a Parte 2

Tenha:

- [ ] `docs/diagnostico.md` com a matriz de sintomas.
- [ ] `docs/adr/001-escolha-iac.md` com a decisão de ferramenta.
- [ ] `docs/arquitetura.md` com topologia acordada.
- [ ] `docs/piloto.md` com time e escopo.
- [ ] `docs/limites-reconhecidos.md`.
- [ ] Repositório inicializado: `git init`, `README.md` mínimo, `.gitignore` para `.terraform/`, `terraform.tfstate*`, `.pulumi/`, `.venv/`, `.env*` etc.

---

## Próximo passo

Avance para a **[Parte 2 — IaC v0 com OpenTofu](parte-2-iac-v0-opentofu.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Progressivos — Módulo 6](README.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Parte 2 — IaC v0 com OpenTofu](parte-2-iac-v0-opentofu.md) |

<!-- nav:end -->

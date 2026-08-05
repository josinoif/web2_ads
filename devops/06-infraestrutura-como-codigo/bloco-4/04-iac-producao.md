# Bloco 4 — IaC em Produção

> **Duração estimada:** 80 a 90 minutos. Aborda state compartilhado, multi-ambiente, secrets, Policy as Code, e pipeline CI/CD de IaC. Inclui o script `iac_policy_check.py` — um verificador simples de policies sobre código HCL.

Blocos 2 e 3 mostraram como escrever IaC que **funciona na sua máquina**. Este bloco transforma esse código em algo que **equipe usa em produção**: state compartilhado com segurança, múltiplos ambientes coexistindo, segredos gerenciados, regras automáticas bloqueando o que é proibido, e um pipeline que aplica mudanças com plano e aprovação.

Mesmo que o Módulo 7 (Kubernetes) ou o Módulo 9 (DevSecOps) tragam ferramentas mais sofisticadas, a maior parte do valor **já está aqui** — neste bloco é onde IaC para de ser exercício e vira prática de plataforma.

---

## 1. Backend remoto e locking

No Bloco 2 usamos `backend "local"`. Para equipe, jamais. Opções comuns, todas **self-hostables**:

| Backend | Protocolo | Locking | Uso na Nimbus |
|---------|-----------|---------|---------------|
| **S3 + DynamoDB** | S3 API | DynamoDB Lock Table | Se a empresa já usa AWS para ferramental |
| **MinIO + DynamoDB-compat** | S3 API | Depende (MinIO não tem DynamoDB; usar plugin) | Self-hosted puro, mas locking é mais frágil |
| **HTTP backend** | HTTP/HTTPS | LOCK/UNLOCK via verbos HTTP | Flexível; servidor próprio |
| **`pg` / Postgres backend** | Conexão SQL | Advisory locks | Elegante se já existe Postgres operacional |
| **GitLab Managed State** | HTTP | Nativo | Se a empresa usa GitLab |

Para a Nimbus, dado que **não há nuvem pública**, as duas opções práticas são:

### Opção A — MinIO S3 + advisory file lock

```hcl
# envs/piloto-dev/backend.tf
terraform {
  backend "s3" {
    bucket                      = "nimbus-tfstate"
    key                         = "piloto/dev/terraform.tfstate"
    region                      = "us-east-1"           # ignorado pelo MinIO
    endpoint                    = "https://minio.nimbus.internal:9000"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    force_path_style            = true
    use_lockfile                = true                   # locking via arquivo .tflock no bucket
  }
}
```

**Observação:** `use_lockfile` é nativo do OpenTofu e é preferível ao antigo DynamoDB lock para quem não usa AWS.

### Opção B — Postgres backend

```hcl
terraform {
  backend "pg" {
    conn_str = "postgres://tofu:SENHA@postgres.nimbus.internal/tofu?sslmode=require"
  }
}
```

- Um `schema` por workspace.
- **Advisory locks** nativos do Postgres (muito robustos).
- **Backup** do state entra no mesmo processo de backup do banco.

### Credenciais do backend

Nunca em git. Opções:

- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` em env do CI.
- OIDC do GitHub Actions trocando por credenciais temporárias (melhor).
- `PGPASSWORD` em secret de pipeline.

---

## 2. Multi-ambiente — padrão de diretórios

Pelas razões discutidas no Bloco 2, preferimos **diretório por ambiente** em vez de workspaces:

```
nimbus-iac/
├── modules/
│   ├── ambiente-web/
│   └── banco-postgres/
├── envs/
│   ├── piloto-dev/
│   │   ├── main.tf
│   │   ├── backend.tf
│   │   ├── terraform.tfvars
│   │   └── providers.tf
│   ├── piloto-stg/
│   └── piloto-prod/
└── policies/
```

**Cada env:**

- É um **root module** independente.
- Tem **state próprio** (pasta diferente no S3/MinIO).
- Pode ser aplicado **sozinho** sem tocar nos outros.
- Tem `terraform.tfvars` diferente — apenas **variáveis** mudam entre envs, o **código** é idêntico (via `modules/`).

**Regra de ouro:** **nada** de `if var.ambiente == "prod"` espalhado pelo código. A diferença entre envs é **dados** (variáveis), não **código** (recursos distintos).

Contra-exemplo (ruim):

```hcl
resource "docker_container" "api" {
  env = var.ambiente == "prod" ? ["DEBUG=false"] : ["DEBUG=true"]
}
```

Versão boa:

```hcl
resource "docker_container" "api" {
  env = ["DEBUG=${var.debug}"]
}

# env-dev.tfvars:  debug = "true"
# env-prod.tfvars: debug = "false"
```

O código **não sabe** que existe "prod" ou "dev". Ele sabe que existe uma variável `debug`.

---

## 3. Secrets em IaC — três abordagens

### Abordagem 1 — SOPS + age (recomendada para começar)

**SOPS** (Secrets OPerationS), da Mozilla: criptografa **apenas os valores** de arquivos YAML/JSON/ENV, preservando a estrutura. **age** é um keypair moderno e simples.

**Setup:**

```bash
# Instalar
sudo dnf install -y age sops       # Fedora
brew install age sops              # macOS

# Gerar chave age
age-keygen -o ~/.config/sops/age/keys.txt
# Public key: age1abc...
export SOPS_AGE_RECIPIENTS=age1abc...
```

**Configurar SOPS para a Nimbus:**

`.sops.yaml` (comita no repo):

```yaml
creation_rules:
  - path_regex: envs/.*\.secret\.ya?ml$
    age: age1abc...     # chave pública do time de plataforma
```

**Criar segredo:**

```bash
sops envs/piloto-dev/secrets.secret.yaml
# (abre editor; o arquivo salvo fica cifrado)
```

Conteúdo cifrado (vai para git):

```yaml
postgres_password: ENC[AES256_GCM,data:xyz...,...]
```

**Consumir no OpenTofu via `data` + `external`:**

```hcl
data "external" "secrets" {
  program = ["bash", "-c", "sops -d envs/piloto-dev/secrets.secret.yaml | yq -o=json"]
}

resource "docker_container" "pg" {
  env = ["POSTGRES_PASSWORD=${data.external.secrets.result.postgres_password}"]
}
```

> **Alerta:** o valor **descriptografado** entra no state. SOPS resolve segredo **em repouso no git**; state continua precisando de backend criptografado.

### Abordagem 2 — HashiCorp Vault

Vault self-hosted oferece API para secrets, rotação, policies granulares. Provider `vault` do OpenTofu lê o segredo **no momento do apply**:

```hcl
data "vault_generic_secret" "pg" {
  path = "nimbus/piloto/dev/postgres"
}

resource "docker_container" "pg" {
  env = ["POSTGRES_PASSWORD=${data.vault_generic_secret.pg.data["password"]}"]
}
```

**Vantagens:** rotação, audit log, políticas RBAC. **Custo:** operar Vault em HA.

### Abordagem 3 — Environment variable fixa

Em **último caso** (projetos minúsculos):

```bash
export TF_VAR_postgres_password="..."
tofu apply
```

Útil em emergência. Não é gestão de segredos — é **pular** a gestão.

---

## 4. Drift detection agendado

No Bloco 1 apresentamos o conceito. Em produção, materialize com um job agendado:

`.github/workflows/iac-drift.yml`:

```yaml
name: IaC Drift Detection
on:
  schedule:
    - cron: '0 3 * * *'   # 03:00 UTC todo dia
  workflow_dispatch:

jobs:
  detect:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        env: [piloto-dev, piloto-stg, piloto-prod]
    steps:
      - uses: actions/checkout@v4

      - uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: 1.8.0

      - name: Init
        run: tofu -chdir=envs/${{ matrix.env }} init

      - name: Detect drift
        id: plan
        run: |
          set +e
          tofu -chdir=envs/${{ matrix.env }} plan -detailed-exitcode -out=plan.out
          echo "exit=$?" >> $GITHUB_OUTPUT

      - name: Notify on drift
        if: steps.plan.outputs.exit == '2'
        run: |
          tofu -chdir=envs/${{ matrix.env }} show plan.out > drift.txt
          # enviar para Slack / abrir issue no GitHub
          gh issue create --title "Drift em ${{ matrix.env }}" \
                          --body "$(cat drift.txt | head -200)"
        env:
          GH_TOKEN: ${{ secrets.GH_TOKEN }}
```

**Exit codes de `plan -detailed-exitcode`:**

- `0` = no changes (tudo OK).
- `1` = erro.
- `2` = diff detectado (drift ou mudança não aplicada).

Uma issue aberta automaticamente é **visível**, **discutível** e gera cultura de investigar drift sem pânico.

---

## 5. Policy as Code

Policy as Code = **regras** sobre **seu IaC** expressas em código, executadas automaticamente. Bloqueiam configurações proibidas **antes** de chegarem em produção.

### Ferramentas

| Ferramenta | Linguagem | Onde roda |
|------------|-----------|-----------|
| **Checkov** | Python (regras prontas) | CLI + CI |
| **OPA + Rego** | Rego | CLI (via `conftest`) + CI |
| **Terrascan** | Rego | CLI + CI |
| **tfsec** | Go (regras internas) | CLI + CI |
| **Sentinel** | Sentinel (HashiCorp) | Terraform Cloud (pago) |

Vamos focar em **Checkov** (pronto-para-uso) e **OPA + conftest** (customizável).

### Checkov — out-of-the-box

```bash
pip install checkov
checkov -d envs/piloto-dev/
```

Saída (exemplo):

```
Passed checks: 45
Failed checks: 3
Skipped checks: 0

Check: CKV_DOCKER_2: "Ensure that HEALTHCHECK instructions have been added..."
	FAILED for resource: docker_container.api
	File: /envs/piloto-dev/main.tf:47-65

Check: CKV_DOCKER_3: "Ensure that a user for the container has been created other than root..."
	FAILED for resource: docker_container.api
	File: /envs/piloto-dev/main.tf:47-65
```

**Integração CI** (`.github/workflows/iac-plan.yml`):

```yaml
- name: Checkov
  uses: bridgecrewio/checkov-action@v12
  with:
    directory: envs/piloto-dev
    framework: terraform
    soft_fail: false
```

`soft_fail: false` quebra o pipeline em falha.

### OPA + conftest — regras customizadas

Para regras **próprias da Nimbus**, você escreve Rego:

`policies/opa/nimbus.rego`:

```rego
package nimbus

deny contains msg if {
    resource := input.resource.docker_container[name]
    resource.privileged == true
    msg := sprintf("container %v usa privileged=true (proibido na Nimbus)", [name])
}

deny contains msg if {
    resource := input.resource.docker_container[name]
    not resource.restart
    msg := sprintf("container %v não declara restart policy", [name])
}

deny contains msg if {
    resource := input.resource.docker_container[name]
    env := resource.env[_]
    regex.match(`PASSWORD=[^$]`, env)   # pega literal, não interpolação
    msg := sprintf("container %v tem PASSWORD literal em env", [name])
}
```

Aplicar sobre o plan do OpenTofu:

```bash
tofu -chdir=envs/piloto-dev plan -out=tfplan
tofu -chdir=envs/piloto-dev show -json tfplan > tfplan.json
conftest test --policy policies/opa/ tfplan.json
```

### Script didático — `iac_policy_check.py`

Para **entender** policy as code sem depender de ferramenta externa, um verificador Python minimalista sobre arquivos HCL:

```python
"""iac_policy_check.py — checagem didática de policies sobre código HCL.

Não substitui Checkov/OPA. Serve para entender, com Python puro,
o que uma ferramenta de policy faz:
  1. Ler arquivos .tf
  2. Procurar padrões proibidos (regex)
  3. Emitir violações estruturadas
  4. Sair com código != 0 se houver violações

Uso:
  python iac_policy_check.py caminho/para/envs/piloto-dev/
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Policy:
    id: str
    descricao: str
    padrao: re.Pattern[str]
    deve_casar: bool  # True = policy casa se padrão encontrado; False = falha se NÃO encontrado
    severidade: str   # "high", "medium", "low"


POLICIES: tuple[Policy, ...] = (
    Policy(
        id="NIM-001",
        descricao="docker_container não deve usar privileged=true",
        padrao=re.compile(r"privileged\s*=\s*true", re.IGNORECASE),
        deve_casar=True,
        severidade="high",
    ),
    Policy(
        id="NIM-002",
        descricao="variáveis com 'password' devem declarar sensitive = true",
        # Heurística: variable "xxx_password" seguida de bloco sem "sensitive = true"
        padrao=re.compile(
            r'variable\s+"[^"]*password[^"]*"\s*\{[^}]*?\}',
            re.IGNORECASE | re.DOTALL,
        ),
        deve_casar=True,   # casa o bloco; depois filtramos por ausência de "sensitive"
        severidade="high",
    ),
    Policy(
        id="NIM-003",
        descricao="imagens com tag 'latest' são proibidas (use versão fixa)",
        padrao=re.compile(r':latest"', re.IGNORECASE),
        deve_casar=True,
        severidade="medium",
    ),
    Policy(
        id="NIM-004",
        descricao="docker_container deve declarar restart",
        padrao=re.compile(r'resource\s+"docker_container"\s+"[^"]+"\s*\{(?:[^{}]|\{[^{}]*\})*?\}', re.DOTALL),
        deve_casar=True,
        severidade="low",
    ),
)


@dataclass
class Violacao:
    policy_id: str
    arquivo: str
    trecho: str
    severidade: str

    def __str__(self) -> str:
        preview = self.trecho.replace("\n", " ")[:120]
        return f"[{self.severidade.upper():6s}] {self.policy_id}  {self.arquivo}  {preview}"


def _checar_arquivo(path: Path) -> list[Violacao]:
    texto = path.read_text(encoding="utf-8")
    violacoes: list[Violacao] = []

    # NIM-001
    for m in POLICIES[0].padrao.finditer(texto):
        violacoes.append(Violacao(
            POLICIES[0].id, str(path), m.group(0), POLICIES[0].severidade,
        ))

    # NIM-002: bloco de variable *password* sem 'sensitive = true'
    for m in POLICIES[1].padrao.finditer(texto):
        bloco = m.group(0)
        bloco_normalizado = re.sub(r"\s+", " ", bloco)
        if "sensitive = true" not in bloco_normalizado:
            violacoes.append(Violacao(
                POLICIES[1].id, str(path), bloco, POLICIES[1].severidade,
            ))

    # NIM-003
    for m in POLICIES[2].padrao.finditer(texto):
        violacoes.append(Violacao(
            POLICIES[2].id, str(path), m.group(0), POLICIES[2].severidade,
        ))

    # NIM-004: container sem restart
    for m in POLICIES[3].padrao.finditer(texto):
        bloco = m.group(0)
        if "restart" not in bloco:
            violacoes.append(Violacao(
                POLICIES[3].id, str(path), bloco, POLICIES[3].severidade,
            ))

    return violacoes


def verificar(diretorio: Path) -> list[Violacao]:
    arquivos = list(diretorio.rglob("*.tf"))
    todas: list[Violacao] = []
    for arq in arquivos:
        todas.extend(_checar_arquivo(arq))
    return todas


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("diretorio", type=Path)
    args = p.parse_args(argv)

    if not args.diretorio.is_dir():
        print(f"Diretório não encontrado: {args.diretorio}", file=sys.stderr)
        return 2

    violacoes = verificar(args.diretorio)

    if not violacoes:
        print(f"OK: 0 violações em {args.diretorio}")
        return 0

    print(f"{len(violacoes)} violação(ões) encontrada(s):\n")
    for v in sorted(violacoes, key=lambda x: (x.severidade, x.policy_id)):
        print(f"  {v}")

    high = sum(1 for v in violacoes if v.severidade == "high")
    return 1 if high else 0


if __name__ == "__main__":
    sys.exit(main())
```

**Uso:**

```bash
python iac_policy_check.py envs/piloto-dev/
```

Saída esperada quando alguém introduz uma regressão:

```
3 violação(ões) encontrada(s):

  [HIGH  ] NIM-001  envs/piloto-dev/main.tf  privileged = true
  [HIGH  ] NIM-002  envs/piloto-dev/variables.tf  variable "db_password" { type = string }
  [MEDIUM] NIM-003  envs/piloto-dev/main.tf  "postgres:latest"
```

O script retorna **exit code 1** se houver violação `high`, falhando o pipeline.

---

## 6. Pipeline CI/CD de IaC

### Padrão GitOps

```mermaid
flowchart LR
    DEV[Dev] -->|PR com mudança em envs/xxx/| CI1[iac-plan.yml]
    CI1 -->|checkov + fmt + validate + plan| COMENTARIO[Comentário<br/>automático no PR<br/>com o plan]
    COMENTARIO --> REVIEW[Review humano]
    REVIEW -->|approve + merge| MAIN[main]
    MAIN --> CI2[iac-apply.yml]
    CI2 -->|espera aprovação<br/>Environment| AP[Apply]
    AP --> STATE[(State)]
    AP --> REAL[Infra real]
```

### `iac-plan.yml` — em PR

```yaml
name: IaC Plan
on:
  pull_request:
    paths:
      - 'envs/**'
      - 'modules/**'
      - 'policies/**'

jobs:
  plan:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        env: [piloto-dev, piloto-stg, piloto-prod]
    permissions:
      contents: read
      pull-requests: write
    steps:
      - uses: actions/checkout@v4

      - uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: 1.8.0

      - name: Fmt
        run: tofu fmt -check -recursive envs/${{ matrix.env }} modules/

      - name: Init
        run: tofu -chdir=envs/${{ matrix.env }} init
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.MINIO_ACCESS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.MINIO_SECRET_KEY }}

      - name: Validate
        run: tofu -chdir=envs/${{ matrix.env }} validate

      - name: Checkov
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: envs/${{ matrix.env }}
          framework: terraform
          soft_fail: false

      - name: Plan
        id: plan
        run: |
          tofu -chdir=envs/${{ matrix.env }} plan -no-color -out=plan.out > plan.txt
          echo 'plan<<EOF' >> $GITHUB_OUTPUT
          cat plan.txt >> $GITHUB_OUTPUT
          echo 'EOF'      >> $GITHUB_OUTPUT

      - name: Comment on PR
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

### `iac-apply.yml` — em merge

```yaml
name: IaC Apply
on:
  push:
    branches: [main]
    paths:
      - 'envs/**'
      - 'modules/**'

jobs:
  apply:
    runs-on: ubuntu-latest
    strategy:
      max-parallel: 1
      matrix:
        env: [piloto-dev, piloto-stg, piloto-prod]
    environment:
      name: ${{ matrix.env }}          # GitHub Environment com required reviewers
    steps:
      - uses: actions/checkout@v4

      - uses: opentofu/setup-opentofu@v1
        with:
          tofu_version: 1.8.0

      - name: Init
        run: tofu -chdir=envs/${{ matrix.env }} init
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.MINIO_ACCESS_KEY }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.MINIO_SECRET_KEY }}

      - name: Apply
        run: tofu -chdir=envs/${{ matrix.env }} apply -auto-approve
        env:
          TF_VAR_postgres_password: ${{ secrets.POSTGRES_PASSWORD }}
```

**GitHub Environment** com `required reviewers` força um humano a aprovar **antes** do apply — principalmente para `prod`.

### GitOps puro (opcional)

Ferramentas como **Atlantis** (self-hosted) ou **Flux** levam essa ideia mais longe: o CI virtualmente não existe, o workflow vive **nos comentários do PR** (`atlantis plan`, `atlantis apply`). Útil em grande escala; complexidade inicial justifica só quando há muitas equipes disputando o mesmo repositório.

---

## 7. Separando o "blast radius"

**Blast radius** = alcance do dano se algo der errado.

**Práticas:**

- **Um state por ambiente.** Dev quebrado não toca stg.
- **Um state por componente crítico.** Ex.: `envs/piloto-dev/db` tem state separado de `envs/piloto-dev/app`. Se você "destrói tudo" errado, só destrói o app.
- **Módulo pequeno > módulo gigante.** Módulo que provisiona "metade da nimbus" é alvo de alto risco.
- **Approval rigoroso em prod.** `required reviewers = 2`.
- **Horário de apply.** Em algumas organizações, `apply` em prod é **proibido** sexta à tarde. Regra cultural enforçada no pipeline.

---

## 8. Testes em IaC

Três níveis:

1. **Static tests** — `fmt`, `validate`, Checkov/OPA. Rápidos, pré-plan.
2. **Plan-time tests** — conftest sobre `tfplan.json` (valida **o que** vai ser feito).
3. **Integration tests** — criar ambiente efêmero, aplicar, rodar smoke tests (curl na API), destruir. Cara, mas pega problemas reais.

Em Pulumi, há **testes unitários** nativos (Bloco 3). Em HCL, você tem o `tofu test` (a partir da versão 1.8), que permite escrever casos de teste em HCL.

### Exemplo — `tofu test`

`tests/ambiente-web.tftest.hcl`:

```hcl
variables {
  nome_time         = "teste"
  ambiente          = "test"
  imagem_api        = "nginx:1.27-alpine"
  porta_externa     = 19999
  postgres_password = "test-senha"
}

run "cria_recursos" {
  command = plan

  assert {
    condition     = module.ambiente.rede != ""
    error_message = "Rede deveria ter nome não vazio."
  }

  assert {
    condition     = module.ambiente.api_url == "http://localhost:19999"
    error_message = "api_url deveria refletir a porta."
  }
}
```

Rodar:

```bash
tofu test
```

---

## 9. Guardrails culturais

A infraestrutura mais bem codificada falha se a equipe não respeita o processo. Políticas sociais indispensáveis:

| Guardrail | Como implementar |
|-----------|-------------------|
| **Nada em produção sem PR** | Remover permissão de write no `main`; proteger branch |
| **Plan é lido** | PR não aprovado sem pelo menos um comentário sobre o plan |
| **Apply é feito pelo pipeline** | Remover credenciais do bucket de state da máquina de devs |
| **Drift aberto investigamos** | Issue automática + SLA de 3 dias úteis |
| **Mudança emergencial tem PR posterior** | "Break glass": apply manual sob aviso; PR de ajuste deve vir até 48h depois |
| **Postmortem para acidente em IaC** | Acidente destrutivo → postmortem igual a incidente de produção |

---

## 10. O que IaC NÃO resolve (limites honestos)

Recorrendo ao Morris (2024) e à prática:

| NÃO resolve | Por quê |
|-------------|---------|
| **Bugs na aplicação** | IaC sobe o ambiente; se o código rodando é bugado, é bugado |
| **Falhas operacionais em runtime** | Saturar disco, OOM, vazamento de memória — não são IaC |
| **Falhas humanas em decisão** | IaC executa o que você escreveu; se você escreveu errado, vira apply |
| **Dados** | IaC provisiona o banco; não sabe fazer backup/restore por você |
| **Governança e cultura** | IaC torna *possível* governança; não a substitui |
| **"Tudo em produção"** | IaC garante reprodutibilidade; não elimina diferenças fundamentais de ambiente (latência, volume) |
| **Segurança de runtime** | IaC configura; não monitora exploração |

Esse reconhecimento é parte da **entrega avaliativa**. Um bom plano de plataforma diz claramente o que **está** e o que **não está** no escopo.

---

## 11. Voltando à Nimbus

Como o Bloco 4 responde à pergunta norteadora:

> *"Como redesenhar o provisionamento da Nimbus para que TODO recurso nasça de código versionado, aplicado por pipeline com plano e aprovação, com state compartilhado, secrets seguros e policy enforced?"*

Resposta integrada:

1. **Código**: HCL (ou Pulumi Python) em monorepo `nimbus-iac`, com `modules/` reusáveis.
2. **Versionamento**: git, PR obrigatório, review de 1-2 pessoas.
3. **Pipeline**: `iac-plan.yml` em PR (comenta o plan, roda Checkov/OPA); `iac-apply.yml` em merge, com GitHub Environment + reviewer.
4. **State**: MinIO self-hosted (S3-compatível) com `use_lockfile`.
5. **Secrets**: SOPS + age no curto prazo; Vault no médio prazo.
6. **Policy**: Checkov + `iac_policy_check.py` (ou Rego próprio) bloqueando padrões proibidos.
7. **Drift**: job agendado + issue automática; cultura de "drift é informação".
8. **Multi-ambiente**: diretório por env, state separado, variáveis diferentes.
9. **Adoção**: 3 ondas (piloto, early adopters, resto).
10. **Limites**: reconhecidos em `limites-reconhecidos.md`.

---

## 12. Resumo do bloco

- **Backend remoto + locking** = inegociável para equipe.
- **Diretório por ambiente** > workspace para produção.
- **Segredos**: SOPS+age (simples) ou Vault (robusto); state sempre criptografado no bucket.
- **Drift detection** agendado transforma mudanças silenciosas em issues visíveis.
- **Policy as Code** (Checkov, OPA, `iac_policy_check.py`) fecha a porta para configurações proibidas.
- **Pipeline de IaC**: plan em PR com comentário automático; apply em merge com approval.
- **Blast radius** controlado com states pequenos e módulos pequenos.
- **Limites**: IaC resolve provisionamento; não resolve aplicação, cultura, dados.

---

## Próximo passo

- Faça os **[exercícios resolvidos do Bloco 4](04-exercicios-resolvidos.md)**.
- Inicie os **[exercícios progressivos](../exercicios-progressivos/)**.

---

## Referências deste bloco

- **Morris, K.** *Infrastructure as Code.* Caps. 17 (qualidade), 18 (governança).
- **Brikman, Y.** *Terraform: Up & Running.* Caps. 7-9.
- **HashiCorp** — *Remote state*, *Workspaces*, *State locking*.
- **SOPS** — [github.com/getsops/sops](https://github.com/getsops/sops).
- **Checkov** — [checkov.io](https://www.checkov.io/).
- **Open Policy Agent** — [openpolicyagent.org](https://www.openpolicyagent.org/).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Resolvidos — Bloco 3](../bloco-3/03-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Exercícios Resolvidos — Bloco 4](04-exercicios-resolvidos.md) |

<!-- nav:end -->

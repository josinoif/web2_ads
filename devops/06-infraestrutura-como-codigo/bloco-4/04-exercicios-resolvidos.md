# Exercícios Resolvidos — Bloco 4

Exercícios do Bloco 4 ([IaC em produção](04-iac-producao.md)).

---

## Exercício 1 — Escolher backend

Para a Nimbus (self-hosted, sem nuvem pública, ~40 times, ~400 recursos), avalie as 3 opções de backend e recomende uma, justificando em 5 linhas.

### Solução

**Opção A — MinIO (S3 compatível) + `use_lockfile`:**

- **Pró**: simples, conhecido, separação por "pastas".
- **Contra**: MinIO não oferece locking robusto como DynamoDB; `use_lockfile` do OpenTofu 1.10+ cobre esse gap com arquivo `.tflock` no bucket, mas ainda é lock "advisory".

**Opção B — Backend Postgres nativo:**

- **Pró**: advisory locks robustos, backup integrado, já temos DBAs.
- **Contra**: menos usado, menos material online; cada workspace vira schema.

**Opção C — HTTP backend customizado:**

- **Pró**: controle total.
- **Contra**: **construir e operar** o backend é trabalho adicional; ninguém quer manter mais um microsserviço crítico.

**Recomendação para Nimbus:** **Postgres backend**. Já existe HA de Postgres na fintech; os DBAs sabem escalar/fazer backup; advisory locks do Postgres são provados em décadas; não adiciona nova dependência operacional. MinIO permanece disponível para **artefatos** (binários, SBOMs), mas não para state.

**Veredito alternativo válido:** MinIO + `use_lockfile` se a equipe já opera MinIO em alta disponibilidade e não quer adicionar Postgres como dependência crítica.

---

## Exercício 2 — Migrar state local para remoto

Você está no diretório `envs/piloto-dev/` com `backend "local"` e state já aplicado. Migre para backend S3/MinIO sem perder o state.

### Solução

**Passo 1** — edite `backend.tf`:

```hcl
# antes:
terraform { backend "local" { path = "terraform.tfstate" } }

# depois:
terraform {
  backend "s3" {
    bucket                      = "nimbus-tfstate"
    key                         = "piloto/dev/terraform.tfstate"
    region                      = "us-east-1"
    endpoint                    = "https://minio.nimbus.internal:9000"
    skip_credentials_validation = true
    skip_region_validation      = true
    force_path_style            = true
    use_lockfile                = true
  }
}
```

**Passo 2** — configure credenciais:

```bash
export AWS_ACCESS_KEY_ID="minio-key"
export AWS_SECRET_ACCESS_KEY="minio-secret"
```

**Passo 3** — rode `init -migrate-state`:

```bash
tofu init -migrate-state
# Do you want to copy existing state to the new backend?
# Enter a value: yes
```

OpenTofu:

1. Lê o state local.
2. Cria o objeto `piloto/dev/terraform.tfstate` no bucket.
3. Atualiza `.terraform/terraform.tfstate` (metadata do backend).

**Passo 4** — verifique:

```bash
tofu state list
# Deve listar os mesmos recursos.
```

**Passo 5** — commit de `backend.tf` e remoção do `terraform.tfstate` local do repositório e do disco (para evitar confusão futura):

```bash
git rm --cached terraform.tfstate terraform.tfstate.backup 2>/dev/null
echo "terraform.tfstate*" >> .gitignore
rm terraform.tfstate*
git commit -am "migra backend para MinIO"
```

**Armadilha comum:** `tofu init` **sem** `-migrate-state` em um backend novo pode **apagar** a referência ao state local em favor de um state vazio remoto. Sempre use `-migrate-state` ou `-reconfigure` conscientemente.

---

## Exercício 3 — SOPS em 5 minutos

Configure o SOPS no projeto e crie um `secrets.secret.yaml` com `postgres_password: dev-forte`. Mostre como consumi-lo no HCL.

### Solução

**Passo 1** — gerar chave age:

```bash
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt
# Public key: age1xyz...
```

**Passo 2** — `.sops.yaml` na raiz do repo:

```yaml
creation_rules:
  - path_regex: envs/.*\.secret\.ya?ml$
    age: age1xyz...
```

**Passo 3** — criar o arquivo:

```bash
export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt
sops envs/piloto-dev/secrets.secret.yaml
# Editor abre. Digite:
#   postgres_password: dev-forte
# Salve.
```

O arquivo salvo fica assim (parcial):

```yaml
postgres_password: ENC[AES256_GCM,data:X7f9...,tag:kQ==,type:str]
sops:
    age:
        - recipient: age1xyz...
          enc: |
            -----BEGIN AGE ENCRYPTED FILE-----
            ...
            -----END AGE ENCRYPTED FILE-----
    lastmodified: "2026-..."
    mac: ENC[AES256_GCM,...]
```

**Passo 4** — consumir no HCL via `data "external"`:

```hcl
data "external" "secrets" {
  program = [
    "bash", "-c",
    "sops -d envs/piloto-dev/secrets.secret.yaml | yq -o=json"
  ]
}

resource "docker_container" "pg" {
  # ...
  env = [
    "POSTGRES_PASSWORD=${data.external.secrets.result.postgres_password}",
  ]
}
```

**Passo 5** — `.gitignore` (nunca deixar chaves privadas entrarem no repo):

```
~/.config/sops/age/keys.txt   # na verdade fica fora do repo
```

No CI, injetar a chave private via secret:

```yaml
- name: Setup SOPS age key
  run: |
    mkdir -p ~/.config/sops/age
    echo "${{ secrets.SOPS_AGE_KEY }}" > ~/.config/sops/age/keys.txt
    chmod 600 ~/.config/sops/age/keys.txt
```

**Lição:** SOPS resolve segredo **em repouso no git**. O `state` ainda terá a senha em claro — use backend criptografado + IAM no bucket.

---

## Exercício 4 — Policy own

Escreva 3 policies OPA (Rego) aplicáveis à Nimbus. Uma por severidade (high, medium, low).

### Solução

`policies/opa/nimbus.rego`:

```rego
package nimbus

# HIGH: nada de privileged
deny contains msg if {
    resource := input.resource.docker_container[name]
    resource.privileged == true
    msg := {
        "severity": "high",
        "rule": "no-privileged",
        "message": sprintf("container %v usa privileged=true (proibido)", [name]),
    }
}

# MEDIUM: banco deve ter volume nomeado
deny contains msg if {
    resource := input.resource.docker_container[name]
    contains(resource.image, "postgres")

    # Não tem bloco volumes OU tem mas não é volume nomeado (é bind mount)
    not _tem_volume_nomeado(resource)

    msg := {
        "severity": "medium",
        "rule": "db-volume-nomeado",
        "message": sprintf("container %v (postgres) não usa volume nomeado", [name]),
    }
}

_tem_volume_nomeado(resource) if {
    vol := resource.volumes[_]
    vol.volume_name
    vol.volume_name != ""
}

# LOW: todo recurso deve ter label 'com.nimbus.ambiente'
deny contains msg if {
    resource := input.resource.docker_container[name]
    not _tem_label_ambiente(resource)
    msg := {
        "severity": "low",
        "rule": "label-ambiente",
        "message": sprintf("container %v sem label com.nimbus.ambiente", [name]),
    }
}

_tem_label_ambiente(resource) if {
    lbl := resource.labels[_]
    lbl.label == "com.nimbus.ambiente"
}
```

**Aplicar no pipeline** (`conftest`):

```bash
# gera plan em json
tofu -chdir=envs/piloto-dev plan -out=plan.bin
tofu -chdir=envs/piloto-dev show -json plan.bin > plan.json

# aplica policy
conftest test --policy policies/opa/ plan.json
```

Saída esperada (se violação):

```
FAIL - plan.json - nimbus - container legacy_pg (postgres) não usa volume nomeado
```

---

## Exercício 5 — Pipeline em PR

Desenhe (sem escrever YAML completo) o fluxo de um pipeline `iac-plan.yml` em PR. Liste os **jobs**, em ordem, e o que cada um faz.

### Solução

**Workflow em PR** — `iac-plan.yml`:

1. **checkout** — baixa o repositório.
2. **setup-opentofu** — instala `tofu 1.8.x`.
3. **path-filter** — detecta quais diretórios `envs/*` foram afetados pelo PR (evita rodar em todos desnecessariamente).
4. **fmt** — `tofu fmt -check -recursive` nos diretórios afetados (falha se não formatado).
5. **init** — `tofu init` com credenciais do backend.
6. **validate** — `tofu validate`.
7. **checkov** — varre arquivos `.tf`; falha em severidade ≥ medium.
8. **policy check (OPA)** — gera plan.json e aplica `conftest`.
9. **plan** — `tofu plan -out=plan.bin -no-color > plan.txt`.
10. **upload artifact** — anexa `plan.bin` como artefato do PR (apply subsequente pode usar o mesmo plan).
11. **comment on PR** — usa `actions/github-script` para postar `plan.txt` como comentário Markdown com `<details>`.
12. **summary** — resume no GitHub Step Summary (# adds, # changes, # destroys).

**Gates implícitos:**

- Se **fmt** falha → PR não pode mergear.
- Se **checkov/OPA** falha → PR não pode mergear.
- Se **plan** mostra `destroy` em `prod` → reviewers DEVEM comentar "confirmado" antes de merge (regra cultural, reforçada por `CODEOWNERS` em `envs/*-prod/`).

---

## Exercício 6 — Separando blast radius

A Nimbus tem, para o time de Pagamentos:

- **App** (3 containers, porta, rede).
- **Banco** (1 container + volume persistente + backups).
- **Cache** (1 container Redis).

Você tem hoje **1 state** contendo tudo. Proponha uma reorganização e justifique.

### Solução

**Reorganização para 3 states:**

```
envs/pagamentos-prod/
├── app/        # state A
├── banco/      # state B
└── cache/      # state C
```

Cada diretório é um **root module** próprio com seu `backend.tf` e seu state.

**Dependências cross-state** via **data sources** (`terraform_remote_state`):

```hcl
# envs/pagamentos-prod/app/main.tf
data "terraform_remote_state" "banco" {
  backend = "s3"
  config = {
    bucket = "nimbus-tfstate"
    key    = "pagamentos-prod/banco/terraform.tfstate"
    # ...
  }
}

resource "docker_container" "api" {
  env = [
    "DB_HOST=${data.terraform_remote_state.banco.outputs.db_host}",
  ]
}
```

**Justificativas:**

1. **Blast radius mínimo em "destroy" acidental** — um `tofu destroy` errado no `app/` **não** toca no banco. Banco é **dado**; recriá-lo é catastrófico.
2. **Ritmo de mudança distinto** — app muda diariamente; banco muda raro. Ter states separados permite pipelines e aprovadores diferentes.
3. **Permissões** — time do produto pode mesclar PRs que mexem no `app/`; mas PRs em `banco/` exigem aprovação do DBA + SRE.
4. **Estado menor** — cada state é mais leve; `plan` roda mais rápido.

**Trade-off admitido:**

- Mais complexo para entender; `terraform_remote_state` acopla outputs entre projetos.
- Orquestração de "aplicar tudo ao mesmo tempo" requer script/pipeline coordenador.
- Estudantes iniciantes podem confundir-se — só vale a divisão quando há **risco real** justificando.

---

## Próximo passo

- Inicie os **[exercícios progressivos](../exercicios-progressivos/)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — IaC em Produção](04-iac-producao.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Exercícios Progressivos — Módulo 6](../exercicios-progressivos/README.md) |

<!-- nav:end -->

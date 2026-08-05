# Parte 4 — Produção: Multi-ambiente + State Remoto + Secrets

**Objetivo:** transformar o MVP da Parte 2 numa estrutura **pronta para equipe**. Você fará 3 coisas:

1. Extrair um segundo módulo (`banco-postgres`) e **recompor** o `ambiente-web` em termos dele — demonstra reuso e composição.
2. Migrar o state para **MinIO self-hosted** com locking.
3. Proteger segredos com **SOPS + age**, removendo toda senha em claro.

A escolha de ferramenta a partir daqui é **OpenTofu** (decisão do ADR 001). O `pulumi-alt/` permanece para referência, mas não evolui.

---

## Pré-requisitos

- Parte 2 funcionando.
- Docker, `tofu`, `sops`, `age`, `jq`, `yq` instalados.
- Conhecimento dos Blocos 1 a 4.

**Destrua ambientes pendentes** da Parte 2 antes de começar.

---

## Tarefa 1 — Subir o MinIO (backend de state)

Crie um **arquivo Compose separado** só para o MinIO (infra da própria IaC — bootstrap):

`infra/minio/docker-compose.yml`:

```yaml
services:
  minio:
    image: quay.io/minio/minio:latest
    container_name: nimbus-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minio-admin
      MINIO_ROOT_PASSWORD: minio-admin-forte
    command: server /data --console-address ":9001"
    volumes:
      - minio-data:/data
    restart: unless-stopped

volumes:
  minio-data:
```

Suba:

```bash
cd infra/minio
docker compose up -d
```

Crie o bucket `nimbus-tfstate` via CLI:

```bash
# via `mc` (MinIO Client)
docker run --rm --network host \
  -e MC_HOST_nimbus="http://minio-admin:minio-admin-forte@localhost:9000" \
  minio/mc mb nimbus/nimbus-tfstate

# ou pelo console: http://localhost:9001
```

**Regra importante:** `infra/minio/` é **bootstrap**. NÃO é IaC gerenciada pelo próprio repo. É uma exceção consciente documentada em `docs/adr/002-bootstrap.md`.

---

## Tarefa 2 — Segundo módulo: `banco-postgres`

Hoje, o módulo `ambiente-web` faz **tudo**. Vamos **extrair** o Postgres para um módulo dedicado.

### `modules/banco-postgres/variables.tf`

```hcl
variable "nome" {
  type        = string
  description = "Prefixo do banco (ex: piloto-dev)"
}

variable "rede_name" {
  type        = string
  description = "Nome da rede Docker a conectar"
}

variable "versao" {
  type    = string
  default = "16.3-alpine"
}

variable "db_nome" {
  type    = string
  default = "nimbus"
}

variable "db_usuario" {
  type    = string
  default = "nimbus"
}

variable "db_senha" {
  type      = string
  sensitive = true
}

variable "labels" {
  type    = map(string)
  default = {}
}
```

### `modules/banco-postgres/main.tf`

```hcl
resource "docker_volume" "pgdata" {
  name = "${var.nome}-pgdata"

  dynamic "labels" {
    for_each = var.labels
    content {
      label = labels.key
      value = labels.value
    }
  }
}

resource "docker_image" "postgres" {
  name         = "postgres:${var.versao}"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name  = "${var.nome}-postgres"
  image = docker_image.postgres.image_id

  networks_advanced {
    name = var.rede_name
  }

  volumes {
    volume_name    = docker_volume.pgdata.name
    container_path = "/var/lib/postgresql/data"
  }

  env = [
    "POSTGRES_USER=${var.db_usuario}",
    "POSTGRES_PASSWORD=${var.db_senha}",
    "POSTGRES_DB=${var.db_nome}",
  ]

  restart = "unless-stopped"

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.db_usuario} -d ${var.db_nome}"]
    interval = "10s"
    timeout  = "3s"
    retries  = 5
  }

  dynamic "labels" {
    for_each = var.labels
    content {
      label = labels.key
      value = labels.value
    }
  }
}
```

### `modules/banco-postgres/outputs.tf`

```hcl
output "nome_container" { value = docker_container.postgres.name }
output "nome_volume"    { value = docker_volume.pgdata.name }
output "porta_interna"  { value = 5432 }
```

### Reescreva `modules/ambiente-web/main.tf` usando o novo módulo

```hcl
locals {
  prefixo = "${var.nome_time}-${var.ambiente}"
  labels = {
    "com.nimbus.ambiente"    = var.ambiente
    "com.nimbus.time"        = var.nome_time
    "com.nimbus.gerenciado_por" = "opentofu"
  }
}

resource "docker_network" "net" {
  name   = "${local.prefixo}-net"
  driver = "bridge"

  dynamic "labels" {
    for_each = local.labels
    content {
      label = labels.key
      value = labels.value
    }
  }
}

module "banco" {
  source     = "../banco-postgres"
  nome       = local.prefixo
  rede_name  = docker_network.net.name
  versao     = var.postgres_versao
  db_nome    = var.nome_time
  db_usuario = var.nome_time
  db_senha   = var.postgres_password
  labels     = local.labels
}

# (redis e api continuam como estavam, referenciando
# module.banco.nome_container quando precisarem; por ora,
# só declaram depends_on de module.banco se quiserem ordem)
```

**Ganho:** o módulo `banco-postgres` agora é reutilizável **independentemente** do `ambiente-web`. Um time que precisa **só** de um banco pode usar só esse módulo.

Teste localmente (ainda com backend local):

```bash
make apply ENV=piloto-dev
# deve funcionar como antes
make destroy ENV=piloto-dev
```

---

## Tarefa 3 — Migrar state para MinIO

### Atualize `envs/piloto-dev/backend.tf`

```hcl
terraform {
  backend "s3" {
    bucket                      = "nimbus-tfstate"
    key                         = "piloto/dev/terraform.tfstate"
    region                      = "us-east-1"      # ignorado pelo MinIO
    endpoint                    = "http://localhost:9000"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    force_path_style            = true
    use_lockfile                = true
  }
}
```

### Aplique

```bash
cd envs/piloto-dev

export AWS_ACCESS_KEY_ID="minio-admin"
export AWS_SECRET_ACCESS_KEY="minio-admin-forte"

# Primeiro init migra
tofu init -migrate-state
# Yes (copiar state local para remoto)

# Confirme no MinIO Console (http://localhost:9001)
# deve aparecer: nimbus-tfstate/piloto/dev/terraform.tfstate
```

### Apply normal

```bash
export TF_VAR_postgres_password="senha-temporaria"
tofu apply -auto-approve
```

### Provar locking

Abra dois terminais e rode `tofu apply` simultaneamente em um deles. O segundo terminal deve esperar/falhar com mensagem de lock. Remova o lock apenas **quando** o primeiro terminal concluir.

```
Error: Error acquiring the state lock
Lock Info:
  ID:        ...
  Path:      nimbus-tfstate/piloto/dev/.tflock
  Operation: OperationTypeApply
```

**Isso é o locking funcionando.** Em produção, esse mecanismo protege a Nimbus contra dois SREs aplicando ao mesmo tempo.

### Repita para `envs/piloto-stg`

```hcl
# envs/piloto-stg/backend.tf
terraform {
  backend "s3" {
    bucket                      = "nimbus-tfstate"
    key                         = "piloto/stg/terraform.tfstate"
    # (resto idêntico)
  }
}
```

```bash
cd envs/piloto-stg && tofu init -migrate-state
```

Agora você tem **2 states remotos**, um por ambiente.

---

## Tarefa 4 — Secrets com SOPS + age

### Gerar chave age

```bash
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt
# Public key: age1abc...
```

### `.sops.yaml` na raiz do repo

```yaml
creation_rules:
  - path_regex: envs/.*\.secret\.ya?ml$
    age: age1abc...   # sua chave pública
```

### Criar arquivo de segredos

```bash
export SOPS_AGE_KEY_FILE=~/.config/sops/age/keys.txt

sops envs/piloto-dev/secrets.secret.yaml
# Editor abre. Digite:
```

```yaml
postgres_password: dev-senha-forte-$(openssl rand -hex 6)
```

Ao salvar, o arquivo fica **cifrado** no disco. Cat do arquivo mostra `ENC[AES256_GCM,...]`.

### Consumir no HCL

Adicione em `envs/piloto-dev/main.tf`:

```hcl
data "external" "secrets" {
  program = [
    "bash", "-c",
    "sops -d ${path.module}/secrets.secret.yaml | yq -o=json"
  ]
}

module "ambiente" {
  source = "../../modules/ambiente-web"
  # ...
  postgres_password = data.external.secrets.result.postgres_password
}
```

Remova a `variable "postgres_password"` de `envs/piloto-dev/variables.tf` (e referências). A senha agora vem **só** do SOPS.

### Teste

```bash
unset TF_VAR_postgres_password
tofu plan
# Deve funcionar; plano continua mostrando o diff (senha em claro não aparece — é 'sensitive' via data).
```

Repita para `envs/piloto-stg/`, gerando seu próprio `secrets.secret.yaml` cifrado.

### Criptografar chaves de CI

No GitHub, configure o secret `SOPS_AGE_KEY` com o conteúdo **privado** do arquivo `keys.txt`. No pipeline (Parte 5), decodifique em `~/.config/sops/age/keys.txt` antes de rodar `tofu`.

---

## Tarefa 5 — Inspecionar state depois

Rode de novo o `tfstate_inspect.py`, agora baixando o state do MinIO:

```bash
# Baixar via mc
docker run --rm --network host \
  -e MC_HOST_nimbus="http://minio-admin:minio-admin-forte@localhost:9000" \
  minio/mc cp nimbus/nimbus-tfstate/piloto/dev/terraform.tfstate /tmp/state.json

python3 scripts/tfstate_inspect.py /tmp/state.json
```

Observe:

- O valor **descriptografado** da senha **ainda** aparece no state (SOPS resolve segredo em repouso no git, não no state).
- Em produção, o bucket MinIO deve ter **SSE habilitado** (criptografia no bucket) + **IAM estrito** — documente essa lacuna em `docs/limites-reconhecidos.md`.

**Remova o arquivo baixado imediatamente** — é segredo:

```bash
shred -u /tmp/state.json
```

---

## Tarefa 6 — `piloto-prod` (opcional, recomendado)

Replique `envs/piloto-stg/` em `envs/piloto-prod/` com porta diferente. **Só** adicione após piloto-dev e piloto-stg estáveis. Em produção real, `piloto-prod` teria mais mecanismos (Parte 5: approval reviewers adicionais, ambiente de GitHub com required reviewers).

---

## Tarefa 7 — Atualizar Makefile

```makefile
.PHONY: fmt validate plan apply destroy state init

ENV ?= piloto-dev
DIR := envs/$(ENV)

# Credenciais do MinIO (para init/apply)
export AWS_ACCESS_KEY_ID ?= minio-admin
export AWS_SECRET_ACCESS_KEY ?= minio-admin-forte

init:
	tofu -chdir=$(DIR) init

fmt:
	tofu fmt -recursive modules/ envs/

validate: init
	tofu -chdir=$(DIR) validate

plan: init
	tofu -chdir=$(DIR) plan

apply: init
	tofu -chdir=$(DIR) apply -auto-approve

destroy: init
	tofu -chdir=$(DIR) destroy -auto-approve

state: init
	tofu -chdir=$(DIR) state list

secret-edit:
	sops $(DIR)/secrets.secret.yaml

secret-view:
	sops -d $(DIR)/secrets.secret.yaml
```

---

## Entregáveis desta parte

- [ ] `infra/minio/docker-compose.yml` com MinIO funcional.
- [ ] `modules/banco-postgres/` completo; `modules/ambiente-web/` usa o novo módulo.
- [ ] State remoto funcionando em ≥ 2 ambientes (`piloto-dev`, `piloto-stg`).
- [ ] Locking comprovado (tentativa simultânea falha).
- [ ] `.sops.yaml` + `envs/*/secrets.secret.yaml` (cifrados).
- [ ] Segredo consumido via `data "external"`.
- [ ] `docs/adr/002-backend-state.md` documentando escolha de MinIO.
- [ ] `docs/adr/003-secrets.md` documentando SOPS + age.
- [ ] `docs/limites-reconhecidos.md` atualizado (state ainda vê segredo; SSE pendente).
- [ ] Commit e push.

---

## Critério de pronto

Um colega deveria:

1. Clonar seu repo.
2. Rodar `docker compose -f infra/minio/docker-compose.yml up -d`.
3. Criar `mc mb nimbus/nimbus-tfstate`.
4. Receber **em canal seguro** a chave age privada (fora do repo).
5. Rodar `make apply ENV=piloto-dev` sem nenhum `export TF_VAR_*`.
6. Ver o ambiente subir, o state no MinIO, os segredos **ausentes** do git.

Se funciona, Parte 4 está pronta.

---

## Próximo passo

Avance para a **[Parte 5 — Pipeline CI/CD + plano de adoção](parte-5-pipeline-e-plano.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Mesma Infra em Pulumi (Comparativo)](parte-3-pulumi-paralelo.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Parte 5 — Pipeline CI/CD + Policy + Plano de Adoção](parte-5-pipeline-e-plano.md) |

<!-- nav:end -->

# Parte 2 — IaC v0 com OpenTofu

**Objetivo:** subir o ambiente `piloto-dev` da Nimbus **em código**, localmente, com OpenTofu + provider Docker. É a primeira peça viva: um `tofu apply` deve criar rede, banco, cache e API em até 2 minutos; um `tofu destroy` deve remover tudo em até 30 segundos.

---

## Pré-requisitos

- `tofu --version` (ou `terraform --version`) ≥ 1.6.
- `docker info` funcional.
- Repositório `nimbus-iac` inicializado na Parte 1.

---

## Tarefa 1 — Estrutura mínima

Crie a estrutura:

```
nimbus-iac/
├── modules/
│   └── ambiente-web/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── envs/
    └── piloto-dev/
        ├── main.tf
        ├── providers.tf
        ├── backend.tf
        ├── variables.tf
        ├── outputs.tf
        └── terraform.tfvars
```

### `.gitignore` inicial (raiz do repo)

```gitignore
# OpenTofu / Terraform
.terraform/
.terraform.lock.hcl.bak
*.tfstate
*.tfstate.backup
crash.log
crash.*.log
*.tfplan
plan.out
plan.bin

# Pulumi
.pulumi/
Pulumi.*.secret.yaml.enc

# Python
__pycache__/
*.pyc
.venv/
.python-version

# Segredos
.env
.env.*
!.env.example
*.pem
*.key

# IDE
.vscode/
.idea/
```

> **Importante:** `terraform.tfvars` **NÃO** entra no `.gitignore` — ele deve ir para o repositório, **sem segredos**. Segredos vão para SOPS na Parte 4.

---

## Tarefa 2 — Módulo `ambiente-web`

### `modules/ambiente-web/variables.tf`

```hcl
variable "nome_time" {
  description = "Identificador do time (kebab-case)"
  type        = string
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]*$", var.nome_time))
    error_message = "nome_time deve começar com letra minúscula e conter só a-z0-9-."
  }
}

variable "ambiente" {
  description = "Nome do ambiente: dev, stg, prod"
  type        = string
  validation {
    condition     = contains(["dev", "stg", "prod"], var.ambiente)
    error_message = "ambiente deve ser dev, stg ou prod."
  }
}

variable "imagem_api" {
  description = "Imagem OCI da API (placeholder até a app real)"
  type        = string
  default     = "nginx:1.27-alpine"
}

variable "porta_api_externa" {
  description = "Porta no host para expor a API"
  type        = number
  default     = 8080
}

variable "postgres_versao" {
  type    = string
  default = "16.3-alpine"
}

variable "redis_versao" {
  type    = string
  default = "7.2-alpine"
}

variable "postgres_password" {
  description = "Senha do usuário postgres"
  type        = string
  sensitive   = true
}
```

### `modules/ambiente-web/main.tf`

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

resource "docker_volume" "pgdata" {
  name = "${local.prefixo}-pgdata"

  dynamic "labels" {
    for_each = local.labels
    content {
      label = labels.key
      value = labels.value
    }
  }
}

resource "docker_image" "postgres" {
  name         = "postgres:${var.postgres_versao}"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name  = "${local.prefixo}-postgres"
  image = docker_image.postgres.image_id

  networks_advanced {
    name = docker_network.net.name
  }

  volumes {
    volume_name    = docker_volume.pgdata.name
    container_path = "/var/lib/postgresql/data"
  }

  env = [
    "POSTGRES_USER=${var.nome_time}",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=${var.nome_time}",
  ]

  restart = "unless-stopped"

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U ${var.nome_time} -d ${var.nome_time}"]
    interval = "10s"
    timeout  = "3s"
    retries  = 5
  }

  dynamic "labels" {
    for_each = local.labels
    content {
      label = labels.key
      value = labels.value
    }
  }
}

resource "docker_image" "redis" {
  name         = "redis:${var.redis_versao}"
  keep_locally = true
}

resource "docker_container" "redis" {
  name  = "${local.prefixo}-redis"
  image = docker_image.redis.image_id

  networks_advanced {
    name = docker_network.net.name
  }

  restart = "unless-stopped"

  healthcheck {
    test     = ["CMD", "redis-cli", "ping"]
    interval = "10s"
    timeout  = "3s"
    retries  = 5
  }

  dynamic "labels" {
    for_each = local.labels
    content {
      label = labels.key
      value = labels.value
    }
  }
}

resource "docker_image" "api" {
  name         = var.imagem_api
  keep_locally = true
}

resource "docker_container" "api" {
  name  = "${local.prefixo}-api"
  image = docker_image.api.image_id

  networks_advanced {
    name = docker_network.net.name
  }

  ports {
    internal = 80
    external = var.porta_api_externa
  }

  restart = "unless-stopped"

  depends_on = [
    docker_container.postgres,
    docker_container.redis,
  ]

  dynamic "labels" {
    for_each = local.labels
    content {
      label = labels.key
      value = labels.value
    }
  }
}
```

### `modules/ambiente-web/outputs.tf`

```hcl
output "api_url" {
  description = "URL pública local da API"
  value       = "http://localhost:${var.porta_api_externa}"
}

output "rede" {
  description = "Nome da rede Docker"
  value       = docker_network.net.name
}

output "postgres_container" {
  value = docker_container.postgres.name
}

output "redis_container" {
  value = docker_container.redis.name
}
```

---

## Tarefa 3 — Root module `envs/piloto-dev/`

### `envs/piloto-dev/providers.tf`

```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}
```

### `envs/piloto-dev/backend.tf`

```hcl
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
```

*(Na Parte 4 migraremos para backend remoto.)*

### `envs/piloto-dev/variables.tf`

```hcl
variable "postgres_password" {
  type      = string
  sensitive = true
}
```

### `envs/piloto-dev/main.tf`

```hcl
module "ambiente" {
  source = "../../modules/ambiente-web"

  nome_time         = "piloto"
  ambiente          = "dev"
  imagem_api        = "nginx:1.27-alpine"
  porta_api_externa = 8080
  postgres_versao   = "16.3-alpine"
  redis_versao      = "7.2-alpine"
  postgres_password = var.postgres_password
}
```

### `envs/piloto-dev/outputs.tf`

```hcl
output "api_url"            { value = module.ambiente.api_url }
output "rede"               { value = module.ambiente.rede }
output "postgres_container" { value = module.ambiente.postgres_container }
```

### `envs/piloto-dev/terraform.tfvars`

(**sem** a senha!)

```hcl
# Variáveis públicas do ambiente piloto-dev.
# Segredos (postgres_password) vêm via TF_VAR_* no ambiente ou SOPS (Parte 4).
```

---

## Tarefa 4 — Primeiro apply

```bash
cd envs/piloto-dev

# 1. Senha via env (temporário — vira SOPS na Parte 4)
export TF_VAR_postgres_password="dev-$(openssl rand -hex 8)"

# 2. Init
tofu init
# Initializing the backend...
# Initializing modules...
# Initializing provider plugins...
# - Finding kreuzwerker/docker versions matching "~> 3.0"...

# 3. Formatar
tofu fmt -recursive ../..

# 4. Validate
tofu validate

# 5. Plan
tofu plan
# Plan: 7 to add, 0 to change, 0 to destroy.
# Changes to Outputs:
#   + api_url            = "http://localhost:8080"
#   + postgres_container = (known after apply)
#   + rede               = "piloto-dev-net"

# 6. Apply
time tofu apply -auto-approve
# Apply complete! Resources: 7 added, 0 changed, 0 destroyed.

# Meça: deve ser < 60s.

# 7. Verificar
docker ps --filter "label=com.nimbus.ambiente=dev" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
# NAMES                  IMAGE                  STATUS
# piloto-dev-api         nginx:1.27-alpine      Up (healthy)
# piloto-dev-redis       redis:7.2-alpine       Up (healthy)
# piloto-dev-postgres    postgres:16.3-alpine   Up (healthy)

curl -I http://localhost:8080
# HTTP/1.1 200 OK
# Server: nginx/1.27.x
```

---

## Tarefa 5 — Mudança simulada

Edite `envs/piloto-dev/main.tf` trocando a versão do Redis:

```hcl
redis_versao = "7.4-alpine"
```

Rode `tofu plan`:

```
Plan: 1 to add, 0 to change, 2 to destroy.
```

Entenda o diff: como o `docker_container.redis` referencia `docker_image.redis.image_id`, e a imagem muda → **replace** do container.

Apply:

```bash
tofu apply -auto-approve
```

Confira:

```bash
docker ps --filter "name=piloto-dev-redis" --format "{{.Image}}"
# redis:7.4-alpine
```

Tempo da mudança: **segundos**. Compare mentalmente com os **3 dias** do cenário manual.

---

## Tarefa 6 — Drift induzido

Simule o cenário PBL "alguém clica em algo":

```bash
# Alguém mata o redis à mão
docker rm -f piloto-dev-redis

# Rode plan
tofu plan
# Plan: 1 to add, 0 to change, 0 to destroy.
#   # module.ambiente.docker_container.redis will be created
#   + resource "docker_container" "redis" { ... }
```

Apply reconcilia:

```bash
tofu apply -auto-approve
# Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

**Em produção**, isso seria detectado pelo job agendado de drift (Bloco 4 seção 4).

---

## Tarefa 7 — Destroy

```bash
tofu destroy -auto-approve
# Destroy complete! Resources: 7 destroyed.

docker ps -a --filter "label=com.nimbus.ambiente=dev"
# (vazio)

docker volume ls --filter "name=piloto-dev-"
# (vazio — volume destruído; dados perdidos)
```

Tempo: segundos.

**Anote em `docs/runbook-onboarding.md`:**

- Criação: `tofu apply` após ≤ 2 min.
- Destruição: `tofu destroy` após ≤ 30 s.
- Mudança: `tofu apply` após ≤ 1 min (depende do tipo de mudança).

---

## Tarefa 8 — Inspecionar o state

Use o script `tfstate_inspect.py` do Bloco 2 (copie para `scripts/tfstate_inspect.py`):

```bash
# (reaplique antes de destruir)
tofu apply -auto-approve
python3 ../../scripts/tfstate_inspect.py terraform.tfstate
```

Saída esperada:

```
State version:   4
OpenTofu/Terraform: 1.8.x
Lineage:         ...
Serial:          1
Total recursos:  7

Por tipo:
    3 × docker_container
    3 × docker_image
    1 × docker_network

[ALERTA] 1 possível(is) segredo(s) em claro:
  - docker_container.postgres.env[1] = POSTGRES_PASSWORD=dev-...
```

**Objetivo pedagógico:** sentir, com os próprios olhos, que o state **vê o segredo**. Isso motiva a Parte 4 (SOPS + backend criptografado).

---

## Tarefa 9 — Criar `piloto-stg`

Copie `envs/piloto-dev/` para `envs/piloto-stg/` e ajuste:

- `porta_api_externa = 8081` (evitar colisão com dev).
- `nome_time = "piloto"`, `ambiente = "stg"`.

**Questão reflexiva:** você teve que **editar 2 arquivos**. Se criasse `piloto-prod`, seriam mais 2. O que fica repetido? O que vira **convenção** nas próximas partes?

Resposta esperada (anote em `docs/arquitetura.md`):

- `providers.tf` e `backend.tf` são **boilerplate** repetido. Na Parte 4, extrairemos para templates.
- O módulo `ambiente-web` é reusado — a menos repetição é proporcional à qualidade do módulo.

---

## Tarefa 10 — Makefile inicial

Na raiz do repo:

```makefile
# Makefile — atalhos para IaC
.PHONY: fmt validate plan apply destroy state

ENV ?= piloto-dev
DIR := envs/$(ENV)

fmt:
	tofu fmt -recursive modules/ envs/

validate:
	tofu -chdir=$(DIR) init -backend=false
	tofu -chdir=$(DIR) validate

plan:
	tofu -chdir=$(DIR) init
	tofu -chdir=$(DIR) plan

apply:
	tofu -chdir=$(DIR) apply -auto-approve

destroy:
	tofu -chdir=$(DIR) destroy -auto-approve

state:
	tofu -chdir=$(DIR) state list
```

Uso:

```bash
make plan ENV=piloto-dev
make apply ENV=piloto-stg
make destroy ENV=piloto-dev
```

---

## Entregáveis desta parte

- [ ] `modules/ambiente-web/` completo.
- [ ] `envs/piloto-dev/` funcional (apply/destroy).
- [ ] `envs/piloto-stg/` funcional.
- [ ] `Makefile` raiz.
- [ ] `docs/runbook-onboarding.md` com tempos medidos.
- [ ] `scripts/tfstate_inspect.py` incluído.
- [ ] Observações de drift documentadas em `docs/diagnostico.md` (apêndice).
- [ ] Commit e push para GitHub.

---

## Critério de pronto

Outro estudante deveria conseguir clonar o seu repo e rodar:

```bash
export TF_VAR_postgres_password="teste"
make apply ENV=piloto-dev
curl -I http://localhost:8080   # 200 OK
make destroy ENV=piloto-dev
```

Se isso funciona **sem perguntas**, a Parte 2 está pronta.

---

## Próximo passo

Avance para a **[Parte 3 — Mesma infra em Pulumi](parte-3-pulumi-paralelo.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — Diagnóstico da Nimbus](parte-1-diagnostico.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Parte 3 — Mesma Infra em Pulumi (Comparativo)](parte-3-pulumi-paralelo.md) |

<!-- nav:end -->

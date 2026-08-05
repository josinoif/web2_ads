# Exercícios Resolvidos — Bloco 2

Exercícios do Bloco 2 ([OpenTofu com Provider Docker](02-opentofu-docker.md)).

---

## Exercício 1 — HCL básico

Escreva o HCL mínimo para criar:

- Uma rede Docker chamada `estudo-net` (driver `bridge`).
- Um volume `estudo-data`.
- Um container `estudo-redis` usando imagem `redis:7.2-alpine`, conectado à rede, montando o volume em `/data`.

### Solução

```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    docker = { source = "kreuzwerker/docker", version = "~> 3.0" }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_network" "estudo" {
  name   = "estudo-net"
  driver = "bridge"
}

resource "docker_volume" "dados" {
  name = "estudo-data"
}

resource "docker_image" "redis" {
  name         = "redis:7.2-alpine"
  keep_locally = true
}

resource "docker_container" "redis" {
  name  = "estudo-redis"
  image = docker_image.redis.image_id

  networks_advanced {
    name = docker_network.estudo.name
  }

  volumes {
    volume_name    = docker_volume.dados.name
    container_path = "/data"
  }

  restart = "unless-stopped"
}
```

**Pontos:**

- O OpenTofu deduz a ordem `image → volume/network → container`.
- `keep_locally = true` evita que `destroy` remova a imagem (útil em estudo offline).
- `image = docker_image.redis.image_id` cria **dependência implícita**.

---

## Exercício 2 — Parametrizando

Transforme o HCL do Exercício 1 para aceitar:

- `ambiente` (dev/stg/prod) como prefixo dos nomes.
- `redis_versao` (default 7.2-alpine).
- `habilitar_persistencia` (bool, default true) — se false, não cria volume e não monta.

### Solução

```hcl
variable "ambiente" {
  type = string
  validation {
    condition     = contains(["dev", "stg", "prod"], var.ambiente)
    error_message = "ambiente deve ser dev, stg ou prod."
  }
}

variable "redis_versao" {
  type    = string
  default = "7.2-alpine"
}

variable "habilitar_persistencia" {
  type    = bool
  default = true
}

locals {
  prefixo = "estudo-${var.ambiente}"
}

resource "docker_network" "estudo" {
  name   = "${local.prefixo}-net"
  driver = "bridge"
}

resource "docker_volume" "dados" {
  count = var.habilitar_persistencia ? 1 : 0
  name  = "${local.prefixo}-data"
}

resource "docker_image" "redis" {
  name         = "redis:${var.redis_versao}"
  keep_locally = true
}

resource "docker_container" "redis" {
  name  = "${local.prefixo}-redis"
  image = docker_image.redis.image_id

  networks_advanced {
    name = docker_network.estudo.name
  }

  dynamic "volumes" {
    for_each = var.habilitar_persistencia ? [1] : []
    content {
      volume_name    = docker_volume.dados[0].name
      container_path = "/data"
    }
  }

  restart = "unless-stopped"
}
```

**Pontos:**

- `count = condição ? 1 : 0` materializa zero ou um recurso condicionalmente.
- `dynamic "volumes"` gera o bloco **só se** `habilitar_persistencia = true`.
- Se desligar persistência depois, `plan` mostrará **remoção** do volume e **recreation** do container. Atenção a dados!

---

## Exercício 3 — Modularizando

Transforme o HCL do Exercício 2 em um **módulo** em `modules/redis/` e consuma-o a partir de dois root modules: `envs/dev/` e `envs/stg/`, cada um com ambiente/versão diferentes.

### Solução

Estrutura:

```
modules/redis/
├── main.tf
├── variables.tf
└── outputs.tf

envs/
├── dev/
│   ├── main.tf
│   └── terraform.tfvars
└── stg/
    ├── main.tf
    └── terraform.tfvars
```

**`modules/redis/variables.tf`:**

```hcl
variable "ambiente"              { type = string }
variable "redis_versao"          { type = string, default = "7.2-alpine" }
variable "habilitar_persistencia" { type = bool,   default = true }
```

**`modules/redis/main.tf`:** (igual ao Exercício 2, sem o provider — o provider é configurado pelo root module).

**`modules/redis/outputs.tf`:**

```hcl
output "container_name" { value = docker_container.redis.name }
output "rede_name"      { value = docker_network.estudo.name }
```

**`envs/dev/main.tf`:**

```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    docker = { source = "kreuzwerker/docker", version = "~> 3.0" }
  }
  backend "local" { path = "terraform.tfstate" }
}

provider "docker" { host = "unix:///var/run/docker.sock" }

module "redis" {
  source       = "../../modules/redis"
  ambiente     = "dev"
  redis_versao = "7.2-alpine"
}

output "container" { value = module.redis.container_name }
```

**`envs/stg/main.tf`:**

```hcl
terraform {
  required_version = ">= 1.6"
  required_providers {
    docker = { source = "kreuzwerker/docker", version = "~> 3.0" }
  }
  backend "local" { path = "terraform.tfstate" }
}

provider "docker" { host = "unix:///var/run/docker.sock" }

module "redis" {
  source                 = "../../modules/redis"
  ambiente               = "stg"
  redis_versao           = "7.0-alpine"  # versão ligeiramente diferente
  habilitar_persistencia = false         # stg sem persistência, pra testes
}

output "container" { value = module.redis.container_name }
```

**Executando:**

```bash
cd envs/dev && tofu init && tofu apply -auto-approve
cd ../stg  && tofu init && tofu apply -auto-approve

docker ps --format '{{.Names}} {{.Image}}'
# estudo-dev-redis redis:7.2-alpine
# estudo-stg-redis redis:7.0-alpine
```

**Ganho:** adicionar um terceiro ambiente (`prod`) custa 6 linhas de HCL.

---

## Exercício 4 — Drift intencional

No ambiente `dev` do Exercício 3:

1. Pare o container à mão (`docker stop`).
2. Rode `tofu plan`. O que o plano mostra?
3. Rode `tofu apply`. O que acontece?
4. Remova o volume à mão (`docker volume rm`). Rode plan + apply.

### Solução

**Passo 1:** `docker stop estudo-dev-redis` — container fica em `Exited`.

**Passo 2:** `tofu plan`:

- Na maioria das versões do provider Docker, o state armazena o **ID do container**. O container parado **ainda existe** (só não está running), portanto o state continua consistente. O plan mostra **"no changes"**.
- Para provocar drift visível, remova em vez de parar: `docker rm -f estudo-dev-redis`. Aí o plan mostrará:
  ```
    # docker_container.redis will be created
    + resource "docker_container" "redis" { ... }
  ```

**Passo 3:** `tofu apply` recria o container com a mesma configuração. **O dado em `/data` persistiu**, porque o volume nomeado é separado.

**Passo 4:** `docker volume rm estudo-dev-data` (após desmontar/remover container). Agora o state diz "volume existe", mas o mundo diz que não. `tofu plan`:

```
  # docker_volume.dados[0] will be created
  + resource "docker_volume" "dados" { ... }
```

`tofu apply` recria o volume. **Os dados perdidos não voltam** — IaC gerencia **existência**, não estado interno de dados. Esse é um limite importante: IaC não substitui backup.

---

## Exercício 5 — `tfstate_inspect.py`

Aplique o Exercício 2 com `redis_versao = "7.2-alpine"` e `habilitar_persistencia = true`. Rode o script `tfstate_inspect.py terraform.tfstate`. Responda:

a) Quantos recursos o state registra?
b) Aparece algum "possível segredo"? Justifique.
c) Acrescente uma variável `redis_password` e uma `env = ["REDIS_PASSWORD=${var.redis_password}"]` no container. Apply + re-inspeção. Agora aparece segredo? Como mitigar **sem** deixar de usar a variável?

### Solução

**a)** 4 recursos: `docker_network.estudo`, `docker_volume.dados[0]`, `docker_image.redis`, `docker_container.redis`.

**b)** **Não**. Redis alpine padrão não define senha; nenhuma string de atributo casa com o padrão `password|token|secret`.

**c)** Após adicionar `REDIS_PASSWORD=<valor>` em `env`, o state passará a conter essa string. O `tfstate_inspect.py` alertará:

```
[ALERTA] 1 possível(is) segredo(s) em claro:
  - docker_container.redis.env[0] = REDIS_PASSWORD=secreto...
```

**Mitigações** (Bloco 4 aprofunda):

1. **Backend remoto criptografado** (MinIO com SSE, S3 com KMS): o state continua contendo o segredo, mas **em repouso** está cifrado. IAM restringe leitura.
2. **Secret fora do state**: em vez de passar a senha como variável para o `env`, pedir ao container que **leia** de um **arquivo montado** (e o arquivo vem de um secret manager externo). IaC só aponta para o caminho — o valor nunca entra no state.
3. **Ephemeral values** (OpenTofu 1.10+): valores marcados como *ephemeral* não são persistidos no state.

O importante: **marcar `sensitive = true` NÃO remove o valor do state**. Apenas oculta da saída de CLI.

---

## Exercício 6 — Importando click-ops

Simule o cenário Nimbus: alguém criou manualmente `docker run -d --name legado-cache redis:6.2-alpine`. Traga para IaC **sem destruir**.

### Solução

**Passo 1** — crie o recurso HCL correspondente:

```hcl
resource "docker_container" "legado" {
  name  = "legado-cache"
  image = "redis:6.2-alpine"
}
```

**Passo 2** — import:

```bash
tofu import docker_container.legado legado-cache
```

**Passo 3** — `tofu plan`. Provavelmente aparecerá um diff porque o container real tem muitos atributos **default** que o seu HCL não declarou. Exemplo:

```
  ~ resource "docker_container" "legado" {
        name    = "legado-cache"
      - restart = null -> "no"
      ...
    }
```

**Passo 4** — iterar no HCL até o plan ficar limpo:

```hcl
resource "docker_container" "legado" {
  name    = "legado-cache"
  image   = "redis:6.2-alpine"
  restart = "no"

  lifecycle {
    ignore_changes = [env, logs]
  }
}
```

O bloco `lifecycle { ignore_changes = [...] }` é escape válido para atributos que **variam** e não interessam à gestão.

**Passo 5** — a partir daqui, qualquer mudança passa por HCL, PR e `apply`. A dívida técnica (imagem antiga) fica **visível** no código, pressionando para modernização.

**Lição operacional:** na Nimbus, import vira **rotina**. Cada time que entra no programa de adoção faz um "sprint de import" — todos os recursos clicados entram no repositório. Drift sobre recursos importados **cai para zero** assim que a equipe adota o fluxo PR + apply.

---

## Próximo passo

- Avance para o **[Bloco 3 — Pulumi com Python](../bloco-3/03-pulumi-python.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — OpenTofu com Provider Docker](02-opentofu-docker.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Bloco 3 — Pulumi com Python](../bloco-3/03-pulumi-python.md) |

<!-- nav:end -->

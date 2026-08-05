# Bloco 2 — OpenTofu com Provider Docker

> **Duração estimada:** 80 a 90 minutos. Inclui HCL completo para subir um ambiente Nimbus local, uso de `plan/apply/destroy`, módulos, variáveis, e o script `tfstate_inspect.py` que analisa o arquivo de estado.

Você já entendeu o **porquê** (Bloco 1). Agora vamos ao **como**. O mundo DevOps converge, há anos, em torno de **HCL** — a linguagem originada no Terraform e adotada também pelo **OpenTofu** (o fork aberto da comunidade após a mudança de licença para BSL em agosto de 2023). Para a Nimbus, escolheremos **OpenTofu** porque é software livre e totalmente compatível. Todo o conteúdo deste bloco funciona sem mudanças com `terraform` no lugar de `tofu`.

---

## 1. OpenTofu em 3 minutos

**Instalação** (Linux):

```bash
# Fedora/RHEL:
sudo dnf install -y opentofu
# Debian/Ubuntu:
curl --proto '=https' --tlsv1.2 -fsSL https://get.opentofu.org/install-opentofu.sh | sh
# macOS:
brew install opentofu
```

Verificar:

```bash
tofu --version
# OpenTofu v1.8.x
```

**Fluxo de trabalho canônico:**

```mermaid
flowchart LR
    INIT[tofu init<br/>baixa providers] --> FMT[tofu fmt<br/>formata HCL]
    FMT --> VALIDATE[tofu validate<br/>sintaxe e tipos]
    VALIDATE --> PLAN[tofu plan<br/>diff vs state]
    PLAN --> APPLY[tofu apply<br/>aplica plan]
    APPLY -.-> DESTROY[tofu destroy<br/>remove tudo]
```

---

## 2. Anatomia de um projeto OpenTofu

Um **root module** é qualquer diretório com arquivos `.tf`. Convenções amplamente aceitas:

| Arquivo | Conteúdo típico |
|---------|-----------------|
| `main.tf` | `resource`s principais |
| `variables.tf` | `variable`s (inputs) |
| `outputs.tf` | `output`s (o que expor pra fora) |
| `providers.tf` | blocos `terraform { required_providers { ... } }` e `provider "..."` |
| `backend.tf` | backend de state (local, S3, HTTP, etc.) |
| `versions.tf` | pin de versão de OpenTofu e providers |
| `locals.tf` | valores derivados |
| `data.tf` | `data` sources (leituras) |

A separação é **convencional**, não obrigatória — o OpenTofu concatena todos os `.tf` do diretório em um só grafo.

---

## 3. Provider

**Provider** = plugin que sabe falar com uma API (AWS, Azure, Docker, GitHub, etc.).

Para a Nimbus local, usaremos o **provider Docker** (kreuzwerker/docker), que chama a API do Docker daemon:

```hcl
# providers.tf
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

**`required_version`**: versão mínima de OpenTofu/Terraform. Congela atualizações que quebrem.
**`required_providers`**: pinagem de **provider + versão** usando `~> 3.0` (equivalente a `>=3.0, <4.0`).

Ao rodar `tofu init`, OpenTofu:

1. Lê `required_providers`.
2. Baixa o binário do provider para `.terraform/providers/`.
3. Cria o `.terraform.lock.hcl` (versões exatas — **deve ir para git**).

---

## 4. Resource — o cérebro do HCL

```hcl
resource "<tipo>" "<nome_local>" {
  <argumentos>
}
```

- **`<tipo>`**: identificador do recurso no provider (`docker_container`, `docker_network`, `docker_image`).
- **`<nome_local>`**: identificador **seu** dentro do módulo. Referenciável como `docker_container.app.id`.

Exemplo mínimo — uma rede Docker:

```hcl
resource "docker_network" "nimbus" {
  name   = "nimbus-net"
  driver = "bridge"
}
```

### Atributos vs argumentos

- **Argumento** = você fornece (`name`, `driver`).
- **Atributo** = o provider preenche após criar (`id`, `ipam_config`).

Referenciar atributos de outros recursos cria **dependências implícitas**, resolvidas em ordem topológica pelo OpenTofu.

---

## 5. Variables

```hcl
# variables.tf
variable "ambiente" {
  description = "Nome do ambiente: dev, stg, prod"
  type        = string
  validation {
    condition     = contains(["dev", "stg", "prod"], var.ambiente)
    error_message = "ambiente deve ser dev, stg ou prod."
  }
}

variable "postgres_versao" {
  description = "Tag da imagem Postgres"
  type        = string
  default     = "16.3-alpine"
}

variable "postgres_password" {
  description = "Senha do usuário postgres"
  type        = string
  sensitive   = true
}

variable "recursos" {
  description = "Limites de CPU/mem por serviço"
  type = object({
    cpu_api      = string
    mem_api      = string
    cpu_postgres = string
    mem_postgres = string
  })
  default = {
    cpu_api      = "0.5"
    mem_api      = "256m"
    cpu_postgres = "1.0"
    mem_postgres = "512m"
  }
}
```

**Tipos**: `string`, `number`, `bool`, `list(...)`, `map(...)`, `object({...})`, `tuple([...])`.

**`sensitive = true`**: a variável não aparece na saída de `plan`/`apply`.

**`validation`**: bloqueia valores inválidos **antes** de aplicar.

### Como fornecer valores

Em ordem de precedência (maior vence):

1. CLI: `-var="ambiente=dev"` ou `-var-file="dev.tfvars"`.
2. Arquivo `terraform.tfvars` (auto-carregado).
3. Arquivos `*.auto.tfvars` (auto-carregados em ordem alfabética).
4. Variável de ambiente: `TF_VAR_ambiente=dev`.
5. Default da variável.

**Exemplo — `terraform.tfvars`:**

```hcl
ambiente          = "dev"
postgres_versao   = "16.3-alpine"
# postgres_password — NUNCA em git; use TF_VAR_postgres_password ou secret store
```

---

## 6. Outputs

```hcl
# outputs.tf
output "api_url" {
  description = "URL interna da API nimbus"
  value       = "http://localhost:${docker_container.api.ports[0].external}"
}

output "postgres_conn" {
  description = "String de conexão Postgres"
  value       = "postgresql://nimbus:***@localhost:${docker_container.postgres.ports[0].external}/nimbus"
  sensitive   = true
}
```

Outputs são:

- Lidos por módulos pais.
- Exibidos após `apply`.
- Consultáveis: `tofu output api_url`.
- Serializáveis: `tofu output -json`.

---

## 7. Locals

Valores derivados, para não repetir expressões:

```hcl
locals {
  prefixo = "nimbus-${var.ambiente}"

  labels_comuns = {
    "com.nimbus.ambiente" = var.ambiente
    "com.nimbus.gerenciado_por" = "opentofu"
  }
}

resource "docker_network" "nimbus" {
  name = "${local.prefixo}-net"
  labels {
    label = "ambiente"
    value = var.ambiente
  }
}
```

---

## 8. Data sources

Leem informação **sem criar**. Exemplo — verificar que uma imagem existe no daemon local:

```hcl
data "docker_registry_image" "postgres" {
  name = "postgres:${var.postgres_versao}"
}

resource "docker_image" "postgres" {
  name          = data.docker_registry_image.postgres.name
  pull_triggers = [data.docker_registry_image.postgres.sha256_digest]
}
```

O `pull_triggers` garante que, se a **tag** aponta para um **digest** diferente no futuro, o recurso será atualizado — é como "pin por digest" via SHA.

---

## 9. Projeto completo — Nimbus piloto local

Estrutura:

```
nimbus-iac-mvp/
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── backend.tf
└── terraform.tfvars
```

### `providers.tf`

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

### `backend.tf`

```hcl
# Para estudo local — backend local. Em produção, use remoto (Bloco 4).
terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
```

### `variables.tf`

```hcl
variable "ambiente" {
  description = "Nome do ambiente: dev, stg, prod"
  type        = string
}

variable "postgres_versao" {
  type    = string
  default = "16.3-alpine"
}

variable "postgres_password" {
  type      = string
  sensitive = true
}

variable "api_porta_externa" {
  type    = number
  default = 8080
}
```

### `main.tf`

```hcl
locals {
  prefixo = "nimbus-${var.ambiente}"
}

resource "docker_network" "nimbus" {
  name   = "${local.prefixo}-net"
  driver = "bridge"
}

resource "docker_volume" "pgdata" {
  name = "${local.prefixo}-pgdata"
}

resource "docker_image" "postgres" {
  name         = "postgres:${var.postgres_versao}"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name  = "${local.prefixo}-postgres"
  image = docker_image.postgres.image_id

  networks_advanced {
    name = docker_network.nimbus.name
  }

  volumes {
    volume_name    = docker_volume.pgdata.name
    container_path = "/var/lib/postgresql/data"
  }

  env = [
    "POSTGRES_USER=nimbus",
    "POSTGRES_PASSWORD=${var.postgres_password}",
    "POSTGRES_DB=nimbus",
  ]

  restart = "unless-stopped"

  healthcheck {
    test     = ["CMD-SHELL", "pg_isready -U nimbus -d nimbus"]
    interval = "10s"
    timeout  = "3s"
    retries  = 5
  }
}

resource "docker_image" "api" {
  name         = "nginx:1.27-alpine"  # placeholder: API real vem dos Módulos 4/5
  keep_locally = true
}

resource "docker_container" "api" {
  name  = "${local.prefixo}-api"
  image = docker_image.api.image_id

  networks_advanced {
    name = docker_network.nimbus.name
  }

  ports {
    internal = 80
    external = var.api_porta_externa
  }

  restart = "unless-stopped"

  depends_on = [docker_container.postgres]
}
```

### `outputs.tf`

```hcl
output "api_url" {
  value = "http://localhost:${var.api_porta_externa}"
}

output "rede" {
  value = docker_network.nimbus.name
}

output "postgres_container" {
  value = docker_container.postgres.name
}
```

### `terraform.tfvars`

```hcl
ambiente = "dev"
# postgres_password vem via env: export TF_VAR_postgres_password="dev-senha"
```

### Executando

```bash
# 1. Init
tofu init
# Initializing the backend...
# Initializing provider plugins...
# - Installing kreuzwerker/docker v3.x...

# 2. Formatar
tofu fmt

# 3. Validar
tofu validate
# Success! The configuration is valid.

# 4. Exportar secret
export TF_VAR_postgres_password="dev-senha-forte"

# 5. Plan (NÃO aplica)
tofu plan
# Plan: 5 to add, 0 to change, 0 to destroy.

# 6. Apply
tofu apply -auto-approve

# 7. Verificar
docker ps --filter "label=ambiente=dev"
curl -I http://localhost:8080

# 8. Inspecionar state
tofu state list
# docker_container.api
# docker_container.postgres
# docker_image.api
# docker_image.postgres
# docker_network.nimbus
# docker_volume.pgdata

# 9. Destruir (no fim do estudo)
tofu destroy -auto-approve
```

---

## 10. Módulos

**Módulo** = diretório com HCL, **consumível** por outros módulos. Em grande escala, módulos são a unidade de reuso — na Nimbus, um único módulo `ambiente-web` pode servir aos 40 times.

### Estrutura típica

```
modules/ambiente-web/
├── main.tf
├── variables.tf
└── outputs.tf
```

### `modules/ambiente-web/variables.tf`

```hcl
variable "nome_time" {
  type = string
}

variable "ambiente" {
  type = string
}

variable "imagem_api" {
  type = string
}

variable "porta_externa" {
  type = number
}

variable "postgres_password" {
  type      = string
  sensitive = true
}
```

### `modules/ambiente-web/main.tf`

```hcl
locals {
  prefixo = "${var.nome_time}-${var.ambiente}"
}

resource "docker_network" "net" {
  name   = "${local.prefixo}-net"
  driver = "bridge"
}

resource "docker_volume" "pgdata" {
  name = "${local.prefixo}-pgdata"
}

resource "docker_image" "postgres" {
  name         = "postgres:16.3-alpine"
  keep_locally = true
}

resource "docker_container" "postgres" {
  name  = "${local.prefixo}-postgres"
  image = docker_image.postgres.image_id

  networks_advanced { name = docker_network.net.name }
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
}

resource "docker_image" "api" {
  name         = var.imagem_api
  keep_locally = true
}

resource "docker_container" "api" {
  name  = "${local.prefixo}-api"
  image = docker_image.api.image_id

  networks_advanced { name = docker_network.net.name }
  ports {
    internal = 80
    external = var.porta_externa
  }

  restart    = "unless-stopped"
  depends_on = [docker_container.postgres]
}
```

### `modules/ambiente-web/outputs.tf`

```hcl
output "api_url"   { value = "http://localhost:${var.porta_externa}" }
output "postgres"  { value = docker_container.postgres.name }
output "rede"      { value = docker_network.net.name }
```

### Consumindo no root module

```hcl
# envs/pagamentos-dev/main.tf
module "ambiente" {
  source = "../../modules/ambiente-web"

  nome_time         = "pagamentos"
  ambiente          = "dev"
  imagem_api        = "nginx:1.27-alpine"
  porta_externa     = 8081
  postgres_password = var.postgres_password
}

output "api_url" { value = module.ambiente.api_url }
```

### `for_each` e `count`

Quando uma mesma "forma" precisa de N instâncias:

```hcl
resource "docker_container" "workers" {
  for_each = toset(["worker-a", "worker-b", "worker-c"])

  name  = "${local.prefixo}-${each.key}"
  image = docker_image.worker.image_id
  networks_advanced { name = docker_network.net.name }
}
```

**Regra prática:** use `for_each` (map/set) em vez de `count` (list), porque adicionar/remover um elemento do meio de uma lista **desloca índices** e faz o OpenTofu destruir/recriar recursos não relacionados.

---

## 11. O arquivo `.tfstate` na prática

Após `apply`, abra `terraform.tfstate`:

```json
{
  "version": 4,
  "terraform_version": "1.8.0",
  "serial": 5,
  "lineage": "abc123...",
  "outputs": { "api_url": { "value": "http://localhost:8080", "type": "string" } },
  "resources": [
    {
      "mode": "managed",
      "type": "docker_container",
      "name": "postgres",
      "provider": "provider[\"registry.terraform.io/kreuzwerker/docker\"]",
      "instances": [
        {
          "schema_version": 2,
          "attributes": {
            "id": "sha256:...",
            "name": "nimbus-dev-postgres",
            "image": "sha256:...",
            "env": ["POSTGRES_USER=nimbus", "POSTGRES_PASSWORD=dev-senha-forte", "..."]
          }
        }
      ]
    }
  ]
}
```

**Observações:**

- `lineage` — UUID único do state; evita apply com state errado.
- `serial` — incrementa a cada apply; útil para detectar conflitos.
- `attributes` — **pode conter segredos em claro** (veja o `POSTGRES_PASSWORD` acima!). Por isso, em produção, state vai para backend **criptografado** com **controle de acesso**.

### `tfstate_inspect.py` — analisador didático

Script Python para extrair info do state JSON:

```python
"""tfstate_inspect.py — leitor didático de terraform.tfstate.

Mostra:
  - Versão do state, provider, lineage.
  - Lista de recursos agrupados por tipo.
  - Presença de possíveis segredos em claro (heurística).

Uso:
  python tfstate_inspect.py terraform.tfstate
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


SEGREDO_PATTERNS = [
    re.compile(r"password", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"_key$", re.IGNORECASE),
]


@dataclass
class Relatorio:
    versao: int
    tf_version: str
    lineage: str
    serial: int
    total_recursos: int
    por_tipo: Counter
    possiveis_segredos: list[str]


def analisar(tfstate: dict) -> Relatorio:
    versao = tfstate.get("version", 0)
    tf_version = tfstate.get("terraform_version", "?")
    lineage = tfstate.get("lineage", "?")
    serial = tfstate.get("serial", 0)

    recursos = tfstate.get("resources", [])
    por_tipo: Counter = Counter()
    possiveis_segredos: list[str] = []

    for r in recursos:
        t = r.get("type", "?")
        por_tipo[t] += 1
        for inst in r.get("instances", []):
            attrs = inst.get("attributes", {}) or {}
            for chave, valor in _achatar(attrs).items():
                if _parece_segredo(chave) and valor and isinstance(valor, str):
                    tag = f"{t}.{r.get('name')}.{chave} = {_truncar(valor)}"
                    possiveis_segredos.append(tag)

    return Relatorio(
        versao=versao,
        tf_version=tf_version,
        lineage=lineage,
        serial=serial,
        total_recursos=len(recursos),
        por_tipo=por_tipo,
        possiveis_segredos=possiveis_segredos,
    )


def _achatar(d: dict, prefixo: str = "") -> dict:
    saida: dict = {}
    for k, v in d.items():
        chave = f"{prefixo}.{k}" if prefixo else k
        if isinstance(v, dict):
            saida.update(_achatar(v, chave))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    saida.update(_achatar(item, f"{chave}[{i}]"))
                else:
                    saida[f"{chave}[{i}]"] = item
        else:
            saida[chave] = v
    return saida


def _parece_segredo(chave: str) -> bool:
    return any(p.search(chave) for p in SEGREDO_PATTERNS)


def _truncar(v: str, n: int = 30) -> str:
    return v if len(v) <= n else v[:n] + "..."


def imprimir(r: Relatorio) -> None:
    print(f"State version:   {r.versao}")
    print(f"OpenTofu/Terraform: {r.tf_version}")
    print(f"Lineage:         {r.lineage}")
    print(f"Serial:          {r.serial}")
    print(f"Total recursos:  {r.total_recursos}")
    print("\nPor tipo:")
    for tipo, n in r.por_tipo.most_common():
        print(f"  {n:3d} × {tipo}")

    if r.possiveis_segredos:
        print(f"\n[ALERTA] {len(r.possiveis_segredos)} possível(is) segredo(s) em claro:")
        for s in r.possiveis_segredos:
            print(f"  - {s}")
        print("\n  Mitigações: backend remoto com criptografia, uso de `sensitive = true`,")
        print("  secret store externo (Vault, SOPS) em vez de variáveis literais.")
    else:
        print("\nNenhum segredo evidente detectado (heurística simples).")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("tfstate", type=Path)
    args = p.parse_args(argv)

    try:
        data = json.loads(args.tfstate.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {args.tfstate}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"JSON inválido: {e}", file=sys.stderr)
        return 2

    relatorio = analisar(data)
    imprimir(relatorio)
    return 1 if relatorio.possiveis_segredos else 0


if __name__ == "__main__":
    sys.exit(main())
```

**Uso:**

```bash
python tfstate_inspect.py terraform.tfstate
```

Saída típica após apply do exemplo:

```
State version:   4
OpenTofu/Terraform: 1.8.0
Lineage:         abc...
Serial:          1
Total recursos:  6

Por tipo:
    2 × docker_container
    2 × docker_image
    1 × docker_network
    1 × docker_volume

[ALERTA] 1 possível(is) segredo(s) em claro:
  - docker_container.postgres.env[1] = POSTGRES_PASSWORD=dev-senha...

  Mitigações: backend remoto com criptografia, uso de `sensitive = true`,
  secret store externo (Vault, SOPS) em vez de variáveis literais.
```

**Lição transformadora:** o state **vê** o segredo. Mesmo marcando a variável como `sensitive = true`, ela chega ao state. Por isso, em produção, **backend criptografado + IAM estrito** é inegociável.

---

## 12. `import` — trazer para IaC o que foi criado à mão

Na Nimbus, uma parte significativa da infraestrutura **já existe** sem IaC. Recriar do zero é arriscado (dados, DNS, clientes). A ferramenta `tofu import` resolve:

```bash
# Passo 1: escreva o recurso HCL (sem aplicar ainda)
cat > main.tf <<'EOF'
resource "docker_container" "legacy_pg" {
  name  = "pg-legado"
  image = "postgres:14"
}
EOF

# Passo 2: import
tofu import docker_container.legacy_pg pg-legado

# Passo 3: rode plan — deve mostrar diffs menores de campos que faltam no HCL
tofu plan

# Passo 4: ajuste o HCL até que `plan` retorne "no changes"
```

**A partir do OpenTofu 1.5+ e Terraform 1.5+**, existe o bloco `import` declarativo:

```hcl
import {
  to = docker_container.legacy_pg
  id = "pg-legado"
}

resource "docker_container" "legacy_pg" {
  # ...
}
```

**Trade-off:** migração incremental é mais lenta mas **segura**. Na Nimbus, import + ajuste iterativo será o padrão de onboarding dos 40 times (Bloco 4 e exercícios progressivos).

---

## 13. Workspaces — nota curta

`tofu workspace new dev` cria um espaço separado dentro do **mesmo** root module, com **state próprio**. Útil em testes. **Não** usaremos workspaces para separar ambientes de produção — preferimos **diretórios por ambiente** (Bloco 4), porque:

- Risco de `apply` no workspace errado.
- Difícil diferenciar permissões por env.
- Código fica com muitos `var.ambiente == "prod" ? ...` — ruído.

---

## 14. Resumo do bloco

- **OpenTofu** é o fork aberto do Terraform; mesma HCL, binário `tofu`.
- Ciclo: `init → fmt → validate → plan → apply → destroy`.
- **Resource** declara o quê; **variable** parametriza; **output** expõe; **module** reusa.
- State é JSON: contém **segredos em claro** — proteja o backend.
- `for_each` > `count`.
- `import` permite trazer recursos pré-existentes para IaC sem recriar.
- Script `tfstate_inspect.py` revela, sem ferramenta extra, a estrutura e os riscos do state.

---

## Próximo passo

- Faça os **[exercícios resolvidos do Bloco 2](02-exercicios-resolvidos.md)**.
- Avance para o **[Bloco 3 — Pulumi com Python](../bloco-3/03-pulumi-python.md)**.

---

## Referências deste bloco

- **Brikman, Y.** *Terraform: Up & Running.* 3ª ed., O'Reilly, 2022. Caps. 2-5.
- **OpenTofu docs** — [opentofu.org/docs/language/](https://opentofu.org/docs/language/).
- **Kreuzwerker Docker provider** — [registry.terraform.io/providers/kreuzwerker/docker](https://registry.terraform.io/providers/kreuzwerker/docker/latest/docs).
- **Morris, K.** *Infrastructure as Code.* Cap. 6 ("Building Environments").

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Resolvidos — Bloco 1](../bloco-1/01-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Exercícios Resolvidos — Bloco 2](02-exercicios-resolvidos.md) |

<!-- nav:end -->

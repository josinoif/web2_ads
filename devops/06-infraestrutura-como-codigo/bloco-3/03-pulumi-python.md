# Bloco 3 — Pulumi com Python

> **Duração estimada:** 60 a 70 minutos. Implementa a **mesma** topologia Nimbus do Bloco 2, agora em **Python**, e discute trade-offs.

O Bloco 2 apresentou **OpenTofu + HCL**, que hoje é o padrão mais disseminado de IaC. Pulumi é a alternativa principal — faz o mesmo trabalho (provisionar recursos, gerenciar state, planejar mudanças), mas usa **linguagens de propósito geral** (Python, TypeScript, Go, .NET, Java). Como a disciplina escolheu **stack Python**, é razoável mostrar essa alternativa em detalhe: você terá duas ferramentas no cinto e saberá **quando** cada uma compensa.

---

## 1. Por que Pulumi?

| Aspecto | OpenTofu/HCL | Pulumi + Python |
|---------|--------------|-----------------|
| **Linguagem** | DSL própria (HCL) | Python (ou TS/Go/.NET/Java) |
| **Loops e condicionais** | `for_each`, `count`, funções do HCL | `for`, `if`, compreensões, classes |
| **Testes unitários** | Terratest (Go), limitado | `pytest`, mocking nativo, fácil |
| **IDE** | Extensões para HCL | Autocomplete Python completo + tipos |
| **Curva de aprendizado** | Menor (DSL mais restrita) | Maior (abstrações da linguagem) |
| **Maturidade do ecossistema** | Gigante (milhares de módulos) | Crescente (providers portados de TF) |
| **Portabilidade** | HCL é quase padrão do setor | Requer Pulumi CLI; menor adoção |
| **Multi-linguagem** | Só HCL | Equipes podem usar idioma nativo |

**Resumo:** Pulumi brilha quando o código de IaC se beneficia de **abstrações de programa** (loops complexos, classes, biblioteca própria da empresa, testes unitários). HCL vence em **padronização** e **disciplina imposta** — o que é um **feature** em equipes grandes.

**Para a Nimbus**, ambas funcionam. Os exercícios progressivos usarão OpenTofu (padrão do setor); este bloco ensina Pulumi para você ter conhecimento comparativo.

---

## 2. Setup

**Instalação do Pulumi CLI:**

```bash
curl -fsSL https://get.pulumi.com | sh
# adicionar ~/.pulumi/bin ao PATH
pulumi version
# v3.120.x
```

**Login em backend local** (sem nuvem, self-hosted):

```bash
# backend local no filesystem (padrão se não logar em lugar nenhum)
pulumi login --local

# ou aponte para um diretório:
pulumi login file:///var/lib/pulumi-state

# ou MinIO self-hosted (S3-compatível):
pulumi login s3://nimbus-pulumi-state?region=us-east-1&endpoint=minio.nimbus.internal:9000
```

> **Observação:** por padrão, Pulumi sugere `pulumi login` sem argumentos, que usa o **Pulumi Service** (cloud, fora do seu perímetro). Na Nimbus, **self-hosted** impõe usar `--local` ou backend S3 com MinIO.

**Projeto Python:**

```bash
mkdir nimbus-pulumi && cd nimbus-pulumi
python3 -m venv .venv && source .venv/bin/activate
pip install pulumi pulumi-docker

pulumi new python --name nimbus-piloto --stack dev --generate-only
```

O CLI cria:

```
nimbus-pulumi/
├── Pulumi.yaml        # metadata do projeto
├── Pulumi.dev.yaml    # config do stack "dev" (variáveis)
├── __main__.py        # programa Pulumi
├── requirements.txt
└── venv/...
```

**`Pulumi.yaml` típico:**

```yaml
name: nimbus-piloto
runtime:
  name: python
  options:
    virtualenv: .venv
description: Infraestrutura Nimbus — time piloto
```

---

## 3. Conceitos Pulumi

| Conceito | Equivalente OpenTofu | Função |
|----------|----------------------|---------|
| **Project** | Root module + backend | Unidade de código Python |
| **Stack** | Workspace | Instância parametrizada (dev/stg/prod) |
| **Resource** | `resource` HCL | Objeto Python instanciado |
| **Input** | Variable | `config.get(...)` do stack |
| **Output** | Output | `pulumi.export("nome", valor)` |
| **Outputs (type)** | Atributos computados | `Output[T]` — valores **assíncronos** |
| **Provider** | Provider | Pacote pip (`pulumi-docker`, etc.) |

### Stack

Uma pilha (stack) é uma **instância** do programa com config própria. Cada stack tem **state separado**.

```bash
pulumi stack init dev
pulumi stack init stg
pulumi stack init prod

pulumi stack ls
# NAME  LAST UPDATE
# dev   n/a
# stg   n/a
# prod  n/a
```

Config por stack:

```bash
pulumi stack select dev
pulumi config set redisVersao 7.2-alpine
pulumi config set ambiente dev
pulumi config set --secret postgresPassword dev-senha-forte
# ↑ --secret: criptografa no Pulumi.dev.yaml usando chave local (~/.pulumi)
```

Resultado em `Pulumi.dev.yaml`:

```yaml
config:
  nimbus-piloto:ambiente: dev
  nimbus-piloto:redisVersao: 7.2-alpine
  nimbus-piloto:postgresPassword:
    secure: v1:abc123...  # cifrado
```

O arquivo vai para git — **seguro**, pois o valor está criptografado. A chave fica no Pulumi local ou em KMS/Vault em produção.

### Outputs são futuros

Em Python, `resource.id` não é uma string comum; é um `Output[str]` — **valor que só será conhecido depois do apply**. Isso impede hacks imperativos:

```python
# ERRADO: string concatenation direta não funciona com Output
nome = "nimbus-" + container.id   # TypeError-like — Output não é string

# CERTO: Output.concat ou apply
nome = pulumi.Output.concat("nimbus-", container.id)
nome = container.id.apply(lambda i: f"nimbus-{i}")
```

`apply` é o equivalente a `.then()` de uma Promise: corre **quando** o valor real chega.

---

## 4. Programa Pulumi completo — Nimbus piloto

Este é o **equivalente** do projeto OpenTofu do Bloco 2.

### `requirements.txt`

```
pulumi>=3.120
pulumi-docker>=4.5
```

### `__main__.py`

```python
"""Programa Pulumi — ambiente Nimbus piloto (Postgres + API placeholder).

Stack config esperada (Pulumi.<stack>.yaml):
  nimbus-piloto:ambiente         (dev|stg|prod)
  nimbus-piloto:postgresVersao   (ex.: 16.3-alpine)
  nimbus-piloto:apiPortaExterna  (ex.: 8080)
  nimbus-piloto:postgresPassword (secret)
"""
from __future__ import annotations

import pulumi
import pulumi_docker as docker

config = pulumi.Config()
ambiente = config.require("ambiente")
postgres_versao = config.get("postgresVersao") or "16.3-alpine"
api_porta_externa = int(config.get("apiPortaExterna") or "8080")
postgres_password = config.require_secret("postgresPassword")

prefixo = f"nimbus-{ambiente}"
tags = {
    "com.nimbus.ambiente": ambiente,
    "com.nimbus.gerenciado_por": "pulumi",
}


rede = docker.Network(
    "rede-nimbus",
    name=f"{prefixo}-net",
    driver="bridge",
)

pgdata = docker.Volume(
    "pgdata",
    name=f"{prefixo}-pgdata",
)

imagem_pg = docker.RemoteImage(
    "imagem-postgres",
    name=f"postgres:{postgres_versao}",
    keep_locally=True,
)

postgres = docker.Container(
    "postgres",
    name=f"{prefixo}-postgres",
    image=imagem_pg.image_id,
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=rede.name)],
    volumes=[docker.ContainerVolumeArgs(
        volume_name=pgdata.name,
        container_path="/var/lib/postgresql/data",
    )],
    envs=[
        "POSTGRES_USER=nimbus",
        postgres_password.apply(lambda s: f"POSTGRES_PASSWORD={s}"),
        "POSTGRES_DB=nimbus",
    ],
    restart="unless-stopped",
    healthcheck=docker.ContainerHealthcheckArgs(
        tests=["CMD-SHELL", "pg_isready -U nimbus -d nimbus"],
        interval="10s",
        timeout="3s",
        retries=5,
    ),
)

imagem_api = docker.RemoteImage(
    "imagem-api",
    name="nginx:1.27-alpine",
    keep_locally=True,
)

api = docker.Container(
    "api",
    name=f"{prefixo}-api",
    image=imagem_api.image_id,
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=rede.name)],
    ports=[docker.ContainerPortArgs(internal=80, external=api_porta_externa)],
    restart="unless-stopped",
    opts=pulumi.ResourceOptions(depends_on=[postgres]),
)


pulumi.export("api_url", f"http://localhost:{api_porta_externa}")
pulumi.export("rede", rede.name)
pulumi.export("postgres_container", postgres.name)
```

### Execução

```bash
cd nimbus-pulumi
source .venv/bin/activate

# Configurar stack dev
pulumi stack select dev
pulumi config set ambiente dev
pulumi config set postgresVersao 16.3-alpine
pulumi config set apiPortaExterna 8080
pulumi config set --secret postgresPassword dev-senha-forte

# Preview (equivale a `tofu plan`)
pulumi preview
# Previewing update (dev):
#      Type                          Name             Plan
#  +   pulumi:pulumi:Stack           nimbus-piloto-dev  create
#  +   ├─ docker:index:Network       rede-nimbus      create
#  +   ├─ docker:index:Volume        pgdata           create
#  +   ├─ docker:index:RemoteImage   imagem-postgres  create
#  +   ├─ docker:index:Container     postgres         create
#  +   ├─ docker:index:RemoteImage   imagem-api       create
#  +   └─ docker:index:Container     api              create
#
# Outputs:
#     api_url: "http://localhost:8080"

# Apply (equivale a `tofu apply`)
pulumi up --yes

# Ver outputs
pulumi stack output
#    OUTPUT              VALUE
#    api_url             http://localhost:8080
#    rede                nimbus-dev-net
#    postgres_container  nimbus-dev-postgres

# Destruir
pulumi destroy --yes
```

---

## 5. Componentes — a unidade de reuso do Pulumi

Análogo a módulo do HCL, mas em Python:

```python
"""modules/ambiente_web.py"""
from __future__ import annotations
from dataclasses import dataclass

import pulumi
import pulumi_docker as docker


@dataclass
class AmbienteWebArgs:
    nome_time: str
    ambiente: str
    imagem_api: str
    porta_externa: int
    postgres_password: pulumi.Input[str]


class AmbienteWeb(pulumi.ComponentResource):
    """Componente reutilizável: rede + volume + postgres + api placeholder."""

    def __init__(
        self,
        name: str,
        args: AmbienteWebArgs,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__("nimbus:web:AmbienteWeb", name, {}, opts)

        prefixo = f"{args.nome_time}-{args.ambiente}"
        child = pulumi.ResourceOptions(parent=self)

        self.rede = docker.Network(
            f"{name}-rede",
            name=f"{prefixo}-net",
            driver="bridge",
            opts=child,
        )

        self.pgdata = docker.Volume(
            f"{name}-pgdata",
            name=f"{prefixo}-pgdata",
            opts=child,
        )

        self.postgres_img = docker.RemoteImage(
            f"{name}-pg-img",
            name="postgres:16.3-alpine",
            keep_locally=True,
            opts=child,
        )

        self.postgres = docker.Container(
            f"{name}-postgres",
            name=f"{prefixo}-postgres",
            image=self.postgres_img.image_id,
            networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=self.rede.name)],
            volumes=[docker.ContainerVolumeArgs(
                volume_name=self.pgdata.name,
                container_path="/var/lib/postgresql/data",
            )],
            envs=[
                f"POSTGRES_USER={args.nome_time}",
                pulumi.Output.concat("POSTGRES_PASSWORD=", args.postgres_password),
                f"POSTGRES_DB={args.nome_time}",
            ],
            restart="unless-stopped",
            opts=child,
        )

        self.api_img = docker.RemoteImage(
            f"{name}-api-img",
            name=args.imagem_api,
            keep_locally=True,
            opts=child,
        )

        self.api = docker.Container(
            f"{name}-api",
            name=f"{prefixo}-api",
            image=self.api_img.image_id,
            networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=self.rede.name)],
            ports=[docker.ContainerPortArgs(internal=80, external=args.porta_externa)],
            restart="unless-stopped",
            opts=pulumi.ResourceOptions(parent=self, depends_on=[self.postgres]),
        )

        self.register_outputs({
            "api_url": f"http://localhost:{args.porta_externa}",
            "rede":    self.rede.name,
        })
```

### Consumindo o componente

```python
# __main__.py
import pulumi
from modules.ambiente_web import AmbienteWeb, AmbienteWebArgs

cfg = pulumi.Config()

amb = AmbienteWeb(
    "pagamentos",
    AmbienteWebArgs(
        nome_time="pagamentos",
        ambiente=cfg.require("ambiente"),
        imagem_api="nginx:1.27-alpine",
        porta_externa=int(cfg.require("portaExterna")),
        postgres_password=cfg.require_secret("postgresPassword"),
    ),
)

pulumi.export("api_url", amb.api.name)
```

**Vantagens** dessa abordagem em Python:

- Tipagem: `AmbienteWebArgs` é `dataclass` → IDE mostra os argumentos válidos.
- `parent=self` cria hierarquia visível no preview (árvore).
- Classe permite **métodos**, **validações**, **defaults com lógica**.

---

## 6. Testes unitários — vantagem real do Python

Pulumi permite testar **sem** chamar o Docker de verdade, via `pulumi.runtime.set_mocks`. Exemplo:

```python
"""test_ambiente_web.py"""
from __future__ import annotations
import pulumi
import pulumi.runtime


class Mocks(pulumi.runtime.Mocks):
    def new_resource(self, args):
        # Retorna um ID e os inputs como estado "simulado"
        return [args.name + "_id", args.inputs]

    def call(self, args):
        return {}


pulumi.runtime.set_mocks(Mocks())

# Importa SÓ DEPOIS de setar os mocks
from modules.ambiente_web import AmbienteWeb, AmbienteWebArgs


def test_prefixo_usa_nome_e_ambiente():
    amb = AmbienteWeb(
        "teste",
        AmbienteWebArgs(
            nome_time="pag",
            ambiente="dev",
            imagem_api="nginx:1.27-alpine",
            porta_externa=9999,
            postgres_password="fake",
        ),
    )

    caixa = {"nome_rede": None}

    def capturar(valor):
        caixa["nome_rede"] = valor

    amb.rede.name.apply(capturar)
    assert caixa["nome_rede"] == "pag-dev-net"


def test_porta_externa_propagada():
    amb = AmbienteWeb(
        "teste2",
        AmbienteWebArgs(
            nome_time="car",
            ambiente="stg",
            imagem_api="nginx:1.27-alpine",
            porta_externa=7777,
            postgres_password="fake",
        ),
    )

    caixa = {"port": None}

    def capturar(p):
        caixa["port"] = p[0].external if p else None

    amb.api.ports.apply(capturar)
    assert caixa["port"] == 7777
```

Executar:

```bash
pytest test_ambiente_web.py
```

Em HCL equivalente, testes dessa profundidade exigem **Terratest** (Go) com ciclo de apply real — mais caro, mais lento.

---

## 7. Secrets em Pulumi

Pulumi tem **criptografia de config nativa** por stack:

```bash
pulumi config set --secret dbPassword minha-senha
```

Isso cifra com uma **chave** que, por padrão, é gerada e guardada no backend (no Pulumi Service, por padrão; no self-hosted, no diretório do backend). Para produção séria, configurar um **secrets provider** explícito (passphrase, KMS, Vault):

```bash
# Passphrase (para estudo):
pulumi stack init dev --secrets-provider passphrase
# Ele pede uma passphrase; salva cifrado no estado.

# Em produção real, preferir KMS/HSM:
pulumi stack init prod --secrets-provider awskms:///alias/pulumi
# (funciona também com HashiCorp Vault etc.)
```

No código:

```python
senha = config.require_secret("dbPassword")   # Output[str], redacted em logs
# Para usar em string, .apply:
envs = [senha.apply(lambda s: f"DB_PASSWORD={s}")]
```

**Ao exportar**, mark secrets para não vazarem:

```python
pulumi.export("db_password", pulumi.Output.secret(senha))
```

> **State em repouso:** ao contrário do HCL onde o `tfstate.json` guarda valores em claro, o Pulumi cifra **secrets** no state. O arquivo de state é um JSON **com segredos cifrados** ao lado de atributos normais. Ainda assim, **backend com IAM estrito** é obrigatório — criptografia protege contra leitura acidental, não substitui controle de acesso.

---

## 8. Conversão mental HCL ↔ Pulumi

| HCL | Python/Pulumi |
|-----|---------------|
| `variable "x" { type = string }` | `cfg.require("x")` |
| `output "y" { value = z }` | `pulumi.export("y", z)` |
| `locals { a = "b-${var.c}" }` | `a = f"b-{var_c}"` |
| `for_each = toset([...])` | `for name in lista: Resource(name, ...)` |
| `depends_on = [X]` | `opts=pulumi.ResourceOptions(depends_on=[X])` |
| `sensitive = true` | `cfg.require_secret("...")` |
| `module "foo" { source = "..." }` | `AmbienteWeb(...)` instância de `ComponentResource` |
| `resource.attr` (dependência implícita) | `resource.attr` (também, mas é `Output[T]`) |
| `lifecycle { ignore_changes = [...] }` | `opts=pulumi.ResourceOptions(ignore_changes=[...])` |

---

## 9. Quando escolher qual

**Use OpenTofu/HCL quando:**

- A equipe é grande e variada (padronização é valiosa).
- O objetivo é **legibilidade** direta por qualquer engenheiro.
- Você vive em ambientes onde **terraform** é o de facto (maioria).
- O código de IaC é em grande parte **declarativo plano** — não precisa de loops sofisticados.

**Use Pulumi quando:**

- A equipe já é forte numa linguagem (Python, TS).
- IaC se beneficiará de **abstração** (classes, módulos compartilhados na empresa).
- **Testes unitários** de IaC são uma meta explícita.
- Você quer **unificar** aplicação + infra na mesma linguagem.

Em empresa grande, é comum encontrar **ambos** coexistindo. O que **não** se recomenda é misturar as duas ferramentas dentro do **mesmo** projeto — duplicidade de state é receita para drift.

---

## 10. Resumo do bloco

- **Pulumi** usa linguagens de programação reais; com **Python**, dialoga direto com o stack da disciplina.
- **Stack** é a instância com config; equivalente a workspace do HCL.
- **ComponentResource** é a unidade de reuso; classe Python com hierarquia de recursos.
- **Output[T]** é valor **assíncrono**; use `apply`/`Output.concat` para compor.
- **Secrets** são cifrados por stack; secret provider configurável (passphrase/KMS/Vault).
- **Testes unitários** com `runtime.set_mocks` — vantagem concreta sobre HCL.
- Em **grande parte dos cenários**, a escolha é cultural e de equipe; ambas entregam o mesmo conceito.

---

## Próximo passo

- Faça os **[exercícios resolvidos do Bloco 3](03-exercicios-resolvidos.md)**.
- Avance para o **[Bloco 4 — IaC em produção](../bloco-4/04-iac-producao.md)**.

---

## Referências deste bloco

- **Pulumi docs Python** — [pulumi.com/docs/languages-sdks/python/](https://www.pulumi.com/docs/languages-sdks/python/).
- **Pulumi Docker provider** — [pulumi.com/registry/packages/docker/](https://www.pulumi.com/registry/packages/docker/).
- **Pulumi unit testing** — [pulumi.com/docs/using-pulumi/testing/unit/](https://www.pulumi.com/docs/using-pulumi/testing/unit/).
- **Morris, K.** *Infrastructure as Code.* Cap. 7 (Configuração), Cap. 9 (Testes).

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Resolvidos — Bloco 2](../bloco-2/02-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Exercícios Resolvidos — Bloco 3](03-exercicios-resolvidos.md) |

<!-- nav:end -->

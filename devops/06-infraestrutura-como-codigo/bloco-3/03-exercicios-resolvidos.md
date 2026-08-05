# Exercícios Resolvidos — Bloco 3

Exercícios do Bloco 3 ([Pulumi com Python](03-pulumi-python.md)).

---

## Exercício 1 — Do HCL para Python

Traduza para Pulumi/Python o HCL abaixo:

```hcl
resource "docker_network" "net" {
  name   = "teste-net"
  driver = "bridge"
}

resource "docker_volume" "data" {
  name = "teste-data"
}

resource "docker_image" "redis" {
  name         = "redis:7.2-alpine"
  keep_locally = true
}

resource "docker_container" "redis" {
  name  = "teste-redis"
  image = docker_image.redis.image_id

  networks_advanced {
    name = docker_network.net.name
  }

  volumes {
    volume_name    = docker_volume.data.name
    container_path = "/data"
  }
}
```

### Solução

```python
import pulumi_docker as docker

net = docker.Network("net", name="teste-net", driver="bridge")

data = docker.Volume("data", name="teste-data")

redis_img = docker.RemoteImage(
    "redis-img",
    name="redis:7.2-alpine",
    keep_locally=True,
)

redis_container = docker.Container(
    "redis",
    name="teste-redis",
    image=redis_img.image_id,
    networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=net.name)],
    volumes=[docker.ContainerVolumeArgs(
        volume_name=data.name,
        container_path="/data",
    )],
)
```

**Pontos:**

- `docker_image` virou `RemoteImage` (Pulumi) — mais preciso quanto ao nome do objeto.
- Atributos `networks_advanced` e `volumes` passam a ser **listas** de `*Args`.
- Dependências implícitas continuam via **referência de atributo** (`net.name`, `redis_img.image_id`).

---

## Exercício 2 — Stacks com config diferente

Crie 2 stacks (`dev` e `stg`) do projeto Redis, com config:

- **dev**: versão `7.2-alpine`, porta externa 6379.
- **stg**: versão `7.0-alpine`, porta externa 6380.

Mostre os comandos e o arquivo `Pulumi.dev.yaml` resultante.

### Solução

```bash
pulumi stack init dev
pulumi config set redisVersao 7.2-alpine
pulumi config set portaExterna 6379

pulumi stack init stg
pulumi config set redisVersao 7.0-alpine
pulumi config set portaExterna 6380
```

**`Pulumi.dev.yaml`:**

```yaml
config:
  meu-projeto:redisVersao: 7.2-alpine
  meu-projeto:portaExterna: "6379"
```

**`Pulumi.stg.yaml`:**

```yaml
config:
  meu-projeto:redisVersao: 7.0-alpine
  meu-projeto:portaExterna: "6380"
```

No código:

```python
cfg = pulumi.Config()
versao = cfg.require("redisVersao")
porta = int(cfg.require("portaExterna"))

container = docker.Container(
    "redis",
    name=f"teste-redis",
    image=docker.RemoteImage("img", name=f"redis:{versao}").image_id,
    ports=[docker.ContainerPortArgs(internal=6379, external=porta)],
)
```

Alternar entre stacks:

```bash
pulumi stack select dev
pulumi up        # sobe dev

pulumi stack select stg
pulumi up        # sobe stg — estado e recursos separados
```

---

## Exercício 3 — Componente (ComponentResource)

Empacote o Redis parametrizado do Exercício 2 em um **`ComponentResource`** chamado `CacheRedis`. Inputs: `nome`, `ambiente`, `versao`, `porta_externa`. Outputs: `endpoint`.

### Solução

```python
from dataclasses import dataclass
import pulumi
import pulumi_docker as docker


@dataclass
class CacheRedisArgs:
    nome: str
    ambiente: str
    versao: str = "7.2-alpine"
    porta_externa: int = 6379


class CacheRedis(pulumi.ComponentResource):
    def __init__(self, name: str, args: CacheRedisArgs, opts=None):
        super().__init__("nimbus:cache:Redis", name, {}, opts)
        child = pulumi.ResourceOptions(parent=self)

        prefixo = f"{args.nome}-{args.ambiente}"

        self.net = docker.Network(
            f"{name}-net", name=f"{prefixo}-net", driver="bridge", opts=child,
        )

        self.img = docker.RemoteImage(
            f"{name}-img", name=f"redis:{args.versao}", keep_locally=True, opts=child,
        )

        self.container = docker.Container(
            f"{name}-ct",
            name=f"{prefixo}-redis",
            image=self.img.image_id,
            networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=self.net.name)],
            ports=[docker.ContainerPortArgs(internal=6379, external=args.porta_externa)],
            restart="unless-stopped",
            opts=child,
        )

        self.endpoint = f"redis://localhost:{args.porta_externa}"

        self.register_outputs({"endpoint": self.endpoint})
```

**Consumindo:**

```python
import pulumi
from componentes.cache_redis import CacheRedis, CacheRedisArgs

cfg = pulumi.Config()

cache = CacheRedis(
    "cache-pagamentos",
    CacheRedisArgs(
        nome="pagamentos",
        ambiente=cfg.require("ambiente"),
        versao=cfg.get("redisVersao") or "7.2-alpine",
        porta_externa=int(cfg.get("portaExterna") or "6379"),
    ),
)

pulumi.export("cache_endpoint", cache.endpoint)
```

**Ganhos:**

- Em tempo de `preview`, a árvore do componente fica visível:
  ```
  pulumi:pulumi:Stack nimbus-dev
  └─ nimbus:cache:Redis cache-pagamentos
     ├─ docker:index:Network    cache-pagamentos-net
     ├─ docker:index:RemoteImage cache-pagamentos-img
     └─ docker:index:Container   cache-pagamentos-ct
  ```
- Adicionar um 2º cache é uma linha de código.

---

## Exercício 4 — Teste unitário

Escreva um teste **sem** chamar o Docker que garanta que o nome do container do `CacheRedis` respeita o padrão `<nome>-<ambiente>-redis`.

### Solução

```python
"""test_cache_redis.py"""
import pulumi
import pulumi.runtime


class Mocks(pulumi.runtime.Mocks):
    def new_resource(self, args):
        return [args.name + "_id", args.inputs]

    def call(self, args):
        return {}


pulumi.runtime.set_mocks(Mocks())

from componentes.cache_redis import CacheRedis, CacheRedisArgs


def _get(output, timeout=1):
    """Helper para resolver Output em teste (bloqueante)."""
    caixa = {"v": None}
    output.apply(lambda v: caixa.__setitem__("v", v))
    return caixa["v"]


def test_nome_container_segue_padrao():
    cache = CacheRedis(
        "x",
        CacheRedisArgs(nome="pag", ambiente="dev"),
    )
    assert _get(cache.container.name) == "pag-dev-redis"


def test_endpoint_reflete_porta_customizada():
    cache = CacheRedis(
        "y",
        CacheRedisArgs(nome="car", ambiente="stg", porta_externa=7777),
    )
    assert cache.endpoint == "redis://localhost:7777"
```

**Executar:**

```bash
pytest test_cache_redis.py -v
```

**Observação:** `_get` acima é simplificado (vazio ≠ Output resolvido). Em testes reais, considere `pulumi.Output.all(...).apply(...)` com `pytest-asyncio` ou o utilitário oficial. Mas a **ideia** do teste é a correta.

---

## Exercício 5 — Migração HCL → Pulumi

Argumente, em 5 bullets, por que sua equipe **deveria** (ou **não deveria**) migrar um projeto OpenTofu/HCL maduro para Pulumi+Python. Use o contexto da Nimbus.

### Solução (exemplo de argumentação)

**A favor de migrar:**

- A equipe central da plataforma é majoritariamente Python → reuso de conhecimento, mesma linguagem que aplicações.
- Testes unitários de módulos compartilhados são objetivo estratégico do próximo trimestre; Pulumi entrega isso nativamente.
- Módulos complexos (ex.: geração de 40 configurações por time) seriam mais legíveis com classes/loops Python do que com `for_each` aninhado em HCL.

**Contra migrar:**

- HCL já é padrão na fintech; CI, linters, módulos internos e playbooks operacionais estão baseados em HCL. Trocar duplica custo operacional por meses.
- Mercado maior de profissionais em Terraform/HCL; contratar e onboarding são mais rápidos.

**Veredito para a Nimbus (caso real):** **não migrar** todo o parque. **Padronizar em OpenTofu** para os 40 times. **Usar Pulumi** apenas em **bolsões específicos** onde a abstração Python é comprovadamente vantajosa (ex.: ferramenta interna de auto-provisionamento que precisa ler um CSV e gerar dezenas de ambientes).

> Esta é a resposta de engenharia realista: ferramenta certa para problema certo, padrão para a massa.

---

## Exercício 6 — Outputs assíncronos

Complete o código:

```python
import pulumi
import pulumi_docker as docker

rede = docker.Network("r", name="teste-net")
volume = docker.Volume("v", name="teste-vol")

# Queremos exportar um valor único que junte rede.name e volume.name
# no formato: "rede=<nome>;volume=<nome>"
resumo = ...   # COMPLETE AQUI

pulumi.export("resumo", resumo)
```

### Solução

**Opção 1 — `Output.all` + `apply`:**

```python
resumo = pulumi.Output.all(rede.name, volume.name).apply(
    lambda valores: f"rede={valores[0]};volume={valores[1]}"
)
```

**Opção 2 — `Output.concat` (só strings):**

```python
resumo = pulumi.Output.concat(
    "rede=", rede.name, ";volume=", volume.name
)
```

**Por que não funciona o óbvio (`f"rede={rede.name};volume={volume.name}"`):**

- Em tempo de execução do programa, `rede.name` e `volume.name` são **`Output[str]`**, não strings.
- A f-string os converte com `str(output)` → algo como `<pulumi.Output object at 0x...>` — **não** é o nome real.
- Saber **quando** o valor chega (após o resource ser criado) é o ponto de `apply`/`concat`.

**Lição:** programar IaC em linguagem de propósito geral **parece** que é programar normal, mas **não é**. Respeitar a natureza assíncrona dos outputs é o item #1 em "armadilhas Pulumi".

---

## Próximo passo

- Avance para o **[Bloco 4 — IaC em produção](../bloco-4/04-iac-producao.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Pulumi com Python](03-pulumi-python.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Bloco 4 — IaC em Produção](../bloco-4/04-iac-producao.md) |

<!-- nav:end -->

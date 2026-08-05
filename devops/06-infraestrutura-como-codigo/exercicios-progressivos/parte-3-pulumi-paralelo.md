# Parte 3 — Mesma Infra em Pulumi (Comparativo)

**Objetivo:** reproduzir o ambiente `piloto-dev` da Parte 2 em **Pulumi + Python**. Ao final, você terá **dois** projetos funcionalmente equivalentes e uma **análise comparativa defensável**. Essa parte é mais curta e serve para **consolidar** a comparação feita no Bloco 3.

> **Importante:** Pulumi e OpenTofu **não devem compartilhar state**. O projeto Pulumi vai em `pulumi-alt/` como **exploração paralela**. Você escolherá **uma** ferramenta como padrão na Parte 4.

---

## Pré-requisitos

- Parte 2 concluída e funcionando.
- `pulumi --version` instalado.
- `python3` ≥ 3.12 disponível.

**Destrua o ambiente da Parte 2** antes de começar (para evitar colisão de portas e nomes):

```bash
make destroy ENV=piloto-dev
```

---

## Tarefa 1 — Estrutura do projeto Pulumi

```
pulumi-alt/
├── Pulumi.yaml
├── Pulumi.dev.yaml
├── __main__.py
├── requirements.txt
├── componentes/
│   ├── __init__.py
│   └── ambiente_web.py
└── .venv/           # não commitar
```

### Inicializar

```bash
mkdir -p pulumi-alt && cd pulumi-alt
python3 -m venv .venv && source .venv/bin/activate
pip install pulumi pulumi-docker

pulumi login --local        # backend local, sem cloud service

pulumi new python --name nimbus-piloto --stack dev --generate-only
# Edite Pulumi.yaml, veja abaixo.
```

### `requirements.txt`

```
pulumi>=3.120
pulumi-docker>=4.5
```

### `Pulumi.yaml`

```yaml
name: nimbus-piloto
runtime:
  name: python
  options:
    virtualenv: .venv
description: IaC da Nimbus — MVP Pulumi paralelo (Parte 3)
```

---

## Tarefa 2 — `ComponentResource` equivalente ao módulo HCL

### `componentes/ambiente_web.py`

```python
"""ComponentResource equivalente ao modules/ambiente-web do OpenTofu."""
from __future__ import annotations

from dataclasses import dataclass

import pulumi
import pulumi_docker as docker


@dataclass
class AmbienteWebArgs:
    nome_time: str
    ambiente: str
    imagem_api: str = "nginx:1.27-alpine"
    porta_api_externa: int = 8080
    postgres_versao: str = "16.3-alpine"
    redis_versao: str = "7.2-alpine"
    postgres_password: pulumi.Input[str] = ""


class AmbienteWeb(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        args: AmbienteWebArgs,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__("nimbus:web:AmbienteWeb", name, {}, opts)
        child = pulumi.ResourceOptions(parent=self)

        prefixo = f"{args.nome_time}-{args.ambiente}"

        labels = [
            docker.ContainerLabelArgs(label="com.nimbus.ambiente", value=args.ambiente),
            docker.ContainerLabelArgs(label="com.nimbus.time", value=args.nome_time),
            docker.ContainerLabelArgs(label="com.nimbus.gerenciado_por", value="pulumi"),
        ]

        self.rede = docker.Network(
            f"{name}-net",
            name=f"{prefixo}-net",
            driver="bridge",
            opts=child,
        )

        self.pgdata = docker.Volume(
            f"{name}-pgdata",
            name=f"{prefixo}-pgdata",
            opts=child,
        )

        self.img_postgres = docker.RemoteImage(
            f"{name}-img-pg",
            name=f"postgres:{args.postgres_versao}",
            keep_locally=True,
            opts=child,
        )

        self.postgres = docker.Container(
            f"{name}-postgres",
            name=f"{prefixo}-postgres",
            image=self.img_postgres.image_id,
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
            healthcheck=docker.ContainerHealthcheckArgs(
                tests=["CMD-SHELL", f"pg_isready -U {args.nome_time} -d {args.nome_time}"],
                interval="10s",
                timeout="3s",
                retries=5,
            ),
            labels=labels,
            opts=child,
        )

        self.img_redis = docker.RemoteImage(
            f"{name}-img-redis",
            name=f"redis:{args.redis_versao}",
            keep_locally=True,
            opts=child,
        )

        self.redis = docker.Container(
            f"{name}-redis",
            name=f"{prefixo}-redis",
            image=self.img_redis.image_id,
            networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=self.rede.name)],
            restart="unless-stopped",
            healthcheck=docker.ContainerHealthcheckArgs(
                tests=["CMD", "redis-cli", "ping"],
                interval="10s",
                timeout="3s",
                retries=5,
            ),
            labels=labels,
            opts=child,
        )

        self.img_api = docker.RemoteImage(
            f"{name}-img-api",
            name=args.imagem_api,
            keep_locally=True,
            opts=child,
        )

        self.api = docker.Container(
            f"{name}-api",
            name=f"{prefixo}-api",
            image=self.img_api.image_id,
            networks_advanced=[docker.ContainerNetworksAdvancedArgs(name=self.rede.name)],
            ports=[docker.ContainerPortArgs(internal=80, external=args.porta_api_externa)],
            restart="unless-stopped",
            labels=labels,
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self.postgres, self.redis],
            ),
        )

        self.api_url = f"http://localhost:{args.porta_api_externa}"

        self.register_outputs({
            "api_url":  self.api_url,
            "rede":     self.rede.name,
        })
```

---

## Tarefa 3 — Programa principal

### `__main__.py`

```python
"""Programa Pulumi — ambiente piloto-dev da Nimbus."""
import pulumi

from componentes.ambiente_web import AmbienteWeb, AmbienteWebArgs

cfg = pulumi.Config()

amb = AmbienteWeb(
    "piloto",
    AmbienteWebArgs(
        nome_time="piloto",
        ambiente=cfg.require("ambiente"),
        imagem_api=cfg.get("imagemApi") or "nginx:1.27-alpine",
        porta_api_externa=int(cfg.get("portaApiExterna") or "8080"),
        postgres_versao=cfg.get("postgresVersao") or "16.3-alpine",
        redis_versao=cfg.get("redisVersao") or "7.2-alpine",
        postgres_password=cfg.require_secret("postgresPassword"),
    ),
)

pulumi.export("api_url",            amb.api_url)
pulumi.export("rede",               amb.rede.name)
pulumi.export("postgres_container", amb.postgres.name)
pulumi.export("redis_container",    amb.redis.name)
```

---

## Tarefa 4 — Configurar stack dev

```bash
pulumi stack init dev --secrets-provider passphrase
# Enter your passphrase to protect config/secrets:
# (use uma passphrase qualquer de estudo; salve em um gerenciador pessoal)

pulumi config set ambiente dev
pulumi config set portaApiExterna 8080
pulumi config set --secret postgresPassword "dev-$(openssl rand -hex 8)"
```

Verifique `Pulumi.dev.yaml` — a senha aparece como `secure: v1:...`.

---

## Tarefa 5 — Preview + Up

```bash
pulumi preview
# Previewing update (dev):
# ...
# Resources:
#   + 9 to create

time pulumi up --yes
# Resources:
#   + 9 created
# Duration: ~30-60s

# Verificar
docker ps --filter "label=com.nimbus.ambiente=dev" --format "table {{.Names}}\t{{.Image}}"
curl -I http://localhost:8080
```

---

## Tarefa 6 — Mudança e destroy

Altere em `Pulumi.dev.yaml` (ou por CLI) `redisVersao: 7.4-alpine` e rode:

```bash
pulumi up --yes
# Mostra "replace" do container redis (e manutenção dos demais)
```

Destrua:

```bash
pulumi destroy --yes
```

---

## Tarefa 7 — Comparativo estruturado

Escreva em `docs/adr/001-escolha-iac.md` (expansão do ADR criado na Parte 1) a **análise comparativa factual** das duas implementações.

### Entregável — tabela

Preencha os "..." com seus **números medidos** e **observações reais**:

| Dimensão | OpenTofu (Parte 2) | Pulumi (Parte 3) |
|----------|---------------------|------------------|
| Linhas de HCL/Python (módulo) | ... | ... |
| Linhas de HCL/Python (root) | ... | ... |
| Tempo de `plan`/`preview` | ... | ... |
| Tempo de `apply`/`up` (primeiro) | ... | ... |
| Tempo de destroy | ... | ... |
| Dependências instaladas | só tofu + provider | tofu + python + pip packages |
| Estado onde fica | `terraform.tfstate` local | `~/.pulumi/stacks/...` |
| Segredo em state | texto claro | cifrado |
| Readability para não-dev | Alta (HCL é DSL limpa) | Média (Python exige conhecer Output, apply, etc.) |
| Testabilidade | Baixa (`tofu test`, básico) | Alta (pytest + mocks) |
| Autocomplete IDE | Moderado (plugins) | Excelente (tipos Python) |

### Entregável — 3 parágrafos

1. **Quando HCL ganha?** (Quando o código é **declarativo plano**, a equipe é diversa, e padronização importa — a maioria dos casos da Nimbus.)
2. **Quando Pulumi ganha?** (Quando precisa de lógica não-trivial — ex.: gerar 40 configs por CSV —, quando testes unitários são estratégicos, quando a linguagem-alvo da equipe é Python/TS.)
3. **Recomendação final para a Nimbus** e justificativa de **por que não misturar os dois** dentro do mesmo recurso.

---

## Tarefa 8 — Testes unitários em Pulumi

Escreva pelo menos **1 teste** unitário para o `AmbienteWeb` (à moda do Bloco 3, Exercício 4).

### `test_ambiente_web.py`

```python
"""Teste unitário do AmbienteWeb sem chamar Docker."""
import pulumi
import pulumi.runtime


class Mocks(pulumi.runtime.Mocks):
    def new_resource(self, args):
        return [args.name + "_id", args.inputs]

    def call(self, args):
        return {}


pulumi.runtime.set_mocks(Mocks())

from componentes.ambiente_web import AmbienteWeb, AmbienteWebArgs


def _colher(output):
    caixa = {"v": None}
    output.apply(lambda v: caixa.__setitem__("v", v))
    return caixa["v"]


def test_nome_container_segue_padrao():
    amb = AmbienteWeb(
        "piloto-test",
        AmbienteWebArgs(
            nome_time="piloto",
            ambiente="test",
            postgres_password="fake",
        ),
    )
    assert _colher(amb.postgres.name) == "piloto-test-postgres"
    assert _colher(amb.redis.name)    == "piloto-test-redis"
    assert _colher(amb.api.name)      == "piloto-test-api"


def test_porta_customizada_aparece_no_url():
    amb = AmbienteWeb(
        "x",
        AmbienteWebArgs(
            nome_time="x",
            ambiente="dev",
            porta_api_externa=9999,
            postgres_password="fake",
        ),
    )
    assert amb.api_url == "http://localhost:9999"
```

Executar:

```bash
pip install pytest
pytest test_ambiente_web.py -v
```

**Reflexão:** em HCL equivalente, esses testes exigiriam Terratest (Go) com apply real, ou `tofu test` — mais trabalhoso. **Essa é a vantagem concreta do Pulumi em Python.**

---

## Entregáveis desta parte

- [ ] `pulumi-alt/` com programa completo.
- [ ] Teste unitário passando.
- [ ] ADR 001 atualizado com a comparação factual.
- [ ] Commit e push.

---

## Critério de pronto

```bash
cd pulumi-alt
source .venv/bin/activate
pulumi stack select dev
pulumi up --yes
curl -I http://localhost:8080   # 200 OK
pulumi destroy --yes
pytest
```

Funcionou sem erro? Parte 3 completa.

---

## Próximo passo

Avance para a **[Parte 4 — Produção (multi-env + state remoto + secrets)](parte-4-producao.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — IaC v0 com OpenTofu](parte-2-iac-v0-opentofu.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Parte 4 — Produção: Multi-ambiente + State Remoto + Secrets](parte-4-producao.md) |

<!-- nav:end -->

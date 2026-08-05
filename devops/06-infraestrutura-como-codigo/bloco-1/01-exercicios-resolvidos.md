# Exercícios Resolvidos — Bloco 1

Exercícios do Bloco 1 ([Fundamentos de IaC](01-fundamentos-iac.md)).

---

## Exercício 1 — Classificação

Classifique cada prática em **(a) IaC moderna**, **(b) Config management**, **(c) Imperativo ad-hoc**, ou **(d) Nada disso**.

1. `ansible-playbook -i inventory site.yml` que ajusta `/etc/nginx/nginx.conf` em 12 servidores.
2. `terraform apply` que cria 5 VMs, 1 LB e 3 regras de firewall.
3. Script bash que clona um repo, roda `make build` e `scp` o binário para 3 servidores.
4. `docker run ...` com 20 flags, salvo num `~/notes.md`.
5. Pulumi program em Python descrevendo Kubernetes namespaces, deployments e services.
6. Ansible criando VMs no Proxmox e depois configurando-as.

### Solução

| # | Categoria | Justificativa |
|---|-----------|---------------|
| 1 | **(b)** Config management | Ajusta servidor existente; idempotente; declarativo mas centrado em host. |
| 2 | **(a)** IaC moderna | Provisiona infra; declarativo; com state e plan. |
| 3 | **(c)** Imperativo | Sequência de comandos sem estado e sem plano. |
| 4 | **(c)** Imperativo | Um notebook, sem idempotência, sem versionamento operacional. |
| 5 | **(a)** IaC moderna | Descreve recursos; linguagem geral; provider gerencia estado. |
| 6 | **Misto — (a) + (b)** | Módulo `proxmox_kvm` é IaC; módulo `apt` / `template` que configura é CM. Comum, mas acumula complexidade. |

**Insight:** a fronteira não é linguagem (Ansible faz os dois); é **propósito**. "Criar o recurso" = IaC. "Configurar o recurso existente" = CM.

---

## Exercício 2 — Declarativo vs Imperativo

Reescreva o script bash abaixo em **pseudocódigo declarativo** (estilo HCL, sem sintaxe rigorosa):

```bash
#!/usr/bin/env bash
set -e
if ! docker network ls | grep -q nimbus-net; then
  docker network create nimbus-net
fi
if ! docker volume ls | grep -q pgdata; then
  docker volume create pgdata
fi
CID=$(docker ps -aqf "name=^pg$")
if [ -z "$CID" ]; then
  docker run -d --name pg --network nimbus-net \
    -v pgdata:/var/lib/postgresql/data \
    -e POSTGRES_PASSWORD=dev postgres:16.3-alpine
else
  IMG=$(docker inspect -f '{{.Config.Image}}' "$CID")
  if [ "$IMG" != "postgres:16.3-alpine" ]; then
    docker rm -f "$CID"
    docker run -d --name pg --network nimbus-net \
      -v pgdata:/var/lib/postgresql/data \
      -e POSTGRES_PASSWORD=dev postgres:16.3-alpine
  fi
fi
```

### Solução

Equivalente **declarativo**:

```hcl
resource "docker_network" "nimbus" {
  name = "nimbus-net"
}

resource "docker_volume" "pgdata" {
  name = "pgdata"
}

resource "docker_image" "pg" {
  name = "postgres:16.3-alpine"
}

resource "docker_container" "pg" {
  name  = "pg"
  image = docker_image.pg.image_id

  networks_advanced {
    name = docker_network.nimbus.name
  }

  volumes {
    volume_name    = docker_volume.pgdata.name
    container_path = "/var/lib/postgresql/data"
  }

  env = ["POSTGRES_PASSWORD=dev"]
}
```

**Linhas de código**: 30 imperativas → 17 declarativas. Mais importante:

- **Zero condicionais** — a ferramenta cuida de "existe? cria. difere? atualiza. igual? no-op."
- **Ordem** é resolvida pela ferramenta a partir de **dependências implícitas** (`docker_container.pg` depende de `docker_network.nimbus` porque referencia seus atributos).
- **Rodar 10 vezes** = mesmo estado final.
- **Muda para `postgres:17`**? Edita 1 linha; `plan` mostra "replace"; `apply` cuida.

---

## Exercício 3 — Drift em ação

Você aplicou IaC que declara 2 containers: `pg` (postgres:16.3-alpine) e `redis` (redis:7.2-alpine). Alguém, sem você saber:

1. Parou o `redis`.
2. Criou um container `adminer` pelo portal.
3. Recriou o `pg` com imagem `postgres:16.5-alpine` (minor mais recente).

Você roda `detect_drift.py` (script do bloco). Classifique cada caso:

### Solução

| Mudança | Categoria | Ação recomendada |
|---------|-----------|-------------------|
| `redis` parado | **DIVERGENTE** (status real=stopped esperado=running) | `apply` reconcilia (sobe de novo) OU investigar por que alguém parou |
| `adminer` criado | **EXTRA** | Remover **ou** importar para IaC se é legítimo (ex.: ferramenta temporária de debug vira permanente) |
| `pg` com imagem 16.5 | **DIVERGENTE** (imagem diferente) | Duas opções: (i) atualizar código para 16.5 (absorver) — se houve upgrade autorizado; (ii) reverter via `apply` — se foi acidente |

**Lições:**

- Drift **não é bug** — é informação sobre realidade.
- A ação depende de **por que** a mudança aconteceu. Pergunte antes de apertar botão.
- Um comentário no PR do "ajuste de absorção" deve referenciar o Slack/ticket onde a mudança manual foi discutida.

---

## Exercício 4 — Quando imperativo é razoável

Liste **3 situações concretas** onde usar um **script imperativo** é mais adequado do que IaC declarativa. Justifique cada uma.

### Solução

**Situações:**

1. **Bootstrap da IaC propriamente dita.** Para criar o **bucket de state** e as **credenciais de admin** do próprio Terraform, você ainda não tem Terraform rodando. Um script `bootstrap.sh` executado uma vez na vida resolve. Depois disso, tudo é IaC.
2. **Operações de "comando único" em infraestrutura efêmera.** Ex.: "preciso rodar um SQL de migração de dados **agora**, manual, com DBA assistindo". Um script é mais apropriado — IaC não é modelo de runtime.
3. **Investigação de incidente.** Durante firefighting, você pode precisar `kubectl delete pod` ou `docker restart` para voltar serviço. Registre a ação; depois, codifique a causa em IaC para evitar repetição.

**Princípio:** imperativo é **legítimo** para operações **pontuais**, **não-repetitivas**, **de emergência** ou que **sustentam** a IaC. Sai do legítimo quando vira **substituto permanente** de IaC.

---

## Exercício 5 — Topologia do repositório

A Nimbus terá, no longo prazo, ~400 recursos gerenciados em dev/stg/prod × 40 times. Proponha uma estrutura de repositório, justificando.

### Solução

**Estrutura proposta (`nimbus-iac/`):**

```
modules/
├── base/              # recursos compartilhados: rede, DNS zona
├── ambiente-web/      # app + banco + redis padronizado
├── banco-postgres/    # só DB, parametrizável
├── fila-kafka/
└── observabilidade/   # exportadores, labels, coletores

envs/
├── shared/            # DNS, IAM global, compartilhado entre todos
│   ├── dev.tf / stg.tf / prod.tf
├── time-pagamentos/
│   ├── dev/
│   ├── stg/
│   └── prod/
├── time-cartoes/
│   ├── dev/ ...
└── time-<N>/

policies/
├── opa/ (rego)
└── checkov/
```

**Razões:**

- **`modules/`** — DRY. Módulo `ambiente-web` usado por **todos** os 40 times.
- **`envs/<time>/<env>/`** — WET (repetição controlada). Cada ambiente é um `root module` com state próprio, minimizando blast radius.
- **`envs/shared/`** — recursos verdadeiramente globais (DNS, políticas). Apply raro, approval rigoroso.
- **`policies/`** — policy as code central, aplicada a **todos** os PRs.
- Alternativa **workspaces por ambiente** dentro de um root único: rejeitada porque `apply` no workspace errado é trivial em escala.
- **Multi-repo** (um por time): rejeitado porque a Nimbus é plataforma central; fragmentar dificulta governança e padronização.

**Trade-off admitido:** monorepo cresce; PR de um time pode disparar pipeline em todos. Mitigação: pipeline com **change detection** por diretório (só planeja/aplica o que mudou).

---

## Exercício 6 — Estado, por quê e como

Responda em 4 linhas cada:

a) Por que ferramentas IaC modernas **precisam** de estado?
b) Quais 3 riscos do estado **local** na máquina de um dev?
c) Como "state encryption" protege segredos?

### Solução

**a)** A ferramenta precisa mapear cada recurso do **código** para o recurso real no **mundo** (o ID na nuvem, o container no Docker). Sem essa ponte, mudanças no código tornam-se impossíveis de aplicar incrementalmente — só "destruir tudo e criar tudo", perdendo dados, causando downtime e dificultando rollback. O estado também permite **plan** (simular o diff) e **drift detection** (comparar código, estado e mundo).

**b)** **1.** Se a máquina morre, o estado morre junto — ninguém mais consegue aplicar sem reconstruir do zero. **2.** Colaboração impossível: dois devs não podem aplicar concorrentemente; corridas corrompem o arquivo. **3.** Estado pode conter **segredos em claro** (senhas geradas, tokens); máquina do dev geralmente não tem criptografia de disco gerenciada pela organização — risco de vazamento.

**c)** State encryption criptografa o arquivo no **repositório remoto** (S3 com SSE, MinIO com KMS, etc.). Mesmo que alguém baixe o blob sem autorização, não consegue ler. Complementa o `sensitive = true` em variáveis (que apenas oculta da **saída** de `plan`, não do conteúdo do arquivo state). Em prática, combinar **state encryption** + **least privilege** na IAM do bucket + **acesso humano via auditoria** é o padrão.

---

## Próximo passo

- Avance para o **[Bloco 2 — OpenTofu com provider Docker](../bloco-2/02-opentofu-docker.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — Fundamentos de IaC](01-fundamentos-iac.md) | **↑ Índice**<br>[Módulo 6 — Infraestrutura como código](../README.md) | **Próximo →**<br>[Bloco 2 — OpenTofu com Provider Docker](../bloco-2/02-opentofu-docker.md) |

<!-- nav:end -->

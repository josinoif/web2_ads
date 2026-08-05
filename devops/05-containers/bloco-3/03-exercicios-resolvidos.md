# Exercícios Resolvidos — Bloco 3

Exercícios do Bloco 3 ([Docker Compose e Ambientes Multi-Serviço](03-compose-multi-servico.md)).

---

## Exercício 1 — Identificar os defeitos do Compose

Analise o arquivo abaixo e aponte todos os problemas.

```yaml
version: "3.8"

services:
  db:
    image: postgres:latest
    environment:
      POSTGRES_PASSWORD: 123
    ports:
      - "5432:5432"

  api:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:123@localhost:5432/app
    ports:
      - "8000:8000"
    depends_on:
      - db
```

### Solução

| # | Problema | Correção |
|---|----------|----------|
| 1 | `version: "3.8"` obsoleto | remover |
| 2 | `postgres:latest` | pinar (ex.: `postgres:16.3-alpine`) |
| 3 | Senha `123` **hardcoded** | `${POSTGRES_PASSWORD}` + `.env` com valor, `.env.example` sem |
| 4 | Banco exposto na porta 5432 em produção | não publicar em produção; apenas em `override` de dev |
| 5 | `DATABASE_URL` aponta para `localhost` — **dentro** do container, localhost é o próprio container | usar nome do serviço: `@db:5432` |
| 6 | `depends_on` sem `condition: service_healthy` | adicionar healthcheck em db + condition |
| 7 | Sem healthcheck em lugar nenhum | acrescentar em db e api |
| 8 | Sem rede customizada — vai pro `default` | ok, mas considerar separar front/back |
| 9 | Sem volume para dados do Postgres — perde tudo a cada `down` | adicionar volume nomeado |
| 10 | `build: .` sem `dockerfile:` — usa `./Dockerfile` implícito. Pode ser intencional, mas explicitar é mais claro |

**Versão corrigida:**

```yaml
services:

  db:
    image: postgres:16.3-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: app
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app"]
      interval: 5s
      retries: 10
    networks: [backend]

  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://app:${POSTGRES_PASSWORD}@db:5432/app
    ports:
      - "8000:8000"
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://localhost:8000/health || exit 1"]
      interval: 10s
      retries: 5
    networks: [backend]

volumes:
  pgdata:

networks:
  backend:
```

---

## Exercício 2 — Ordem de inicialização correta

A CodeLab tem estes componentes com dependências:

- **Postgres** — sem dependência.
- **Redis** — sem dependência.
- **Migrate** (one-shot) — precisa Postgres healthy.
- **API** — precisa Postgres healthy, Redis healthy, Migrate concluído com sucesso.
- **Worker** — precisa Postgres healthy, Redis healthy, Migrate concluído com sucesso.
- **Adminer** (opcional, perfil `tools`) — precisa Postgres healthy.

Escreva o trecho de `depends_on` de cada serviço.

### Solução

```yaml
services:
  postgres:
    # (sem depends_on)
    healthcheck: ...

  redis:
    # (sem depends_on)
    healthcheck: ...

  migrate:
    depends_on:
      postgres: { condition: service_healthy }

  api:
    depends_on:
      postgres: { condition: service_healthy }
      redis:    { condition: service_healthy }
      migrate:  { condition: service_completed_successfully }

  worker:
    depends_on:
      postgres: { condition: service_healthy }
      redis:    { condition: service_healthy }
      migrate:  { condition: service_completed_successfully }

  adminer:
    profiles: ["tools"]
    depends_on:
      postgres: { condition: service_healthy }
```

**Observação:** `migrate` é um container one-shot com `restart: "no"`. Se ele falhar, **API e Worker não sobem** — comportamento correto.

---

## Exercício 3 — Override para ambiente de integração (CI)

Você quer três arquivos:

- `docker-compose.yml` — base (produção-like).
- `docker-compose.override.yml` — dev local (hot reload, DB exposto).
- `docker-compose.test.yml` — CI (sem portas expostas, DB ephemeral, fixture pré-carregada).

Escreva o `docker-compose.test.yml` mínimo (focado em `postgres` e `api`).

### Solução

```yaml
# docker-compose.test.yml
services:

  postgres:
    environment:
      POSTGRES_PASSWORD: test
    tmpfs:
      - /var/lib/postgresql/data     # RAM — mais rápido, dispensa volume
    ports: []                         # não expor

  api:
    environment:
      DATABASE_URL: postgresql://codelab:test@postgres:5432/codelab
      ENVIRONMENT: test
    ports: []                         # não expor; CI usa exec para falar com o container
    volumes:
      - ./tests/fixtures:/fixtures:ro
```

Uso no CI (override do override explícito — CI **não** herda `docker-compose.override.yml` automaticamente se você passar `-f` explicitamente):

```bash
docker compose -f docker-compose.yml -f docker-compose.test.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.test.yml exec -T api pytest tests/integration
docker compose -f docker-compose.yml -f docker-compose.test.yml down --volumes
```

> Dica: o `tmpfs` do Postgres em teste deixa a suíte **30-50% mais rápida**. Aceitável porque CI descarta tudo.

---

## Exercício 4 — Runners da CodeLab no Compose?

O worker da CodeLab precisa **lançar** runners (Python, JS, C) sob demanda — um container por submissão. Três propostas:

**a)** Declarar cada runner como serviço em `docker-compose.yml` e deixar sempre no ar.

**b)** Deixar o worker lançar runners via API Docker (`docker.sock` montado).

**c)** Não usar Compose para runners: cada submissão cria um processo do próprio worker, com `subprocess`.

Qual você escolhe e por quê?

### Solução

**A resposta correta é (b).**

**Por que não (a):**

- Runner precisa ser **efêmero por submissão** — `--rm --network=none --read-only`, limites, FS dedicado. Serviço permanente no Compose não dá isso.
- Você não sabe **quantos runners** vai precisar em paralelo. Declarar 10 e deixar rodando é **desperdício** e ainda assim **limitado**.
- Isolação: cada container serve **uma** submissão e é destruído. Serviço permanente serviria múltiplas — tropeço.

**Por que não (c):**

- `subprocess` dentro do worker **compartilha** FS, rede, PIDs, UIDs. Anula o motivo de containerizar.
- Isolação zero. Volta ao Sintoma 3 da CodeLab.

**Por que (b):**

- Dá isolação por submissão.
- Controle fino via API Docker (flags de segurança, limites).
- **Porém há risco**: `docker.sock` no worker = controle total do Docker = escalada para host. Mitigações:
  - Usar **docker-socket-proxy** (ex.: [tecnativa/docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy)) com allowlist de endpoints.
  - **Rootless Docker** no host.
  - Em produção real, **migrar para Kubernetes** e usar Jobs com RBAC — é **exatamente** o caso de uso do K8s (Módulo 7). O worker vira um **controller** que cria `Job` por submissão.

**Esboço do Compose atual:**

```yaml
worker:
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro   # pelo menos ro
  # Em produção: substituir por socket-proxy
```

**Runner lançado pelo worker (pseudocódigo Python, só para visualizar):**

```python
import docker
client = docker.from_env()
result = client.containers.run(
    image="ghcr.io/codelab/runner-python:0.5.0",
    command=["python", "/submissao/main.py"],
    volumes={f"/tmp/sub-{sub_id}": {"bind": "/submissao", "mode": "ro"}},
    network_mode="none",
    read_only=True,
    tmpfs={"/tmp": "size=64m,mode=1777"},
    mem_limit="256m",
    nano_cpus=1_000_000_000,
    pids_limit=30,
    user="10001:10001",
    cap_drop=["ALL"],
    security_opt=["no-new-privileges:true"],
    remove=True,
    detach=False,
    stdout=True, stderr=True,
    stdin_open=False,
)
```

---

## Exercício 5 — Healthcheck frágil

Revise o healthcheck abaixo e diga o que há de errado:

```yaml
api:
  healthcheck:
    test: ["CMD", "curl", "http://localhost:8000/"]
```

### Solução

Problemas:

1. **`curl` sem `-f`** — `curl` retorna exit 0 mesmo com HTTP 500. O healthcheck passa com a API quebrada.
2. **`-s` ausente** — ruído no log.
3. **Endpoint `/`** — pode renderizar muita coisa; melhor `/health` dedicado, leve.
4. **Sem `interval`, `retries`, `timeout`, `start_period`** — usa defaults, que podem ser lentos (30s interval) — startup fica lento.
5. **Depende de `curl` na imagem** — imagens slim/distroless não têm curl.

**Correção:**

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -fsS http://localhost:8000/health || exit 1"]
  interval: 10s
  timeout: 3s
  retries: 5
  start_period: 5s
```

Ou, independente de curl:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request,sys; \
    sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health').status==200 else 1)"]
```

E obviamente, **a aplicação precisa de `/health`** — endpoint rápido, sem dependência de DB/rede externa. Dependências externas ficam para um `/ready` separado (padrão K8s).

---

## Exercício 6 — Reproduzir produção localmente

Um dev relata: "O bug só aparece em produção". Investigando, você descobre que a equipe usa `docker-compose.override.yml` agressivo em dev — com bind mount, hot reload e `DEBUG=true` — e **nunca** roda a versão "produção-like".

Liste 3 comandos de Compose para que a dev rode **exatamente** a versão produção-like em sua máquina, e 3 boas práticas para evitar o problema.

### Solução

**Comandos (um basta, outros variam):**

```bash
# 1. Ignorar o override automático
docker compose -f docker-compose.yml up -d

# 2. Nomeando o projeto, evita colisão com o dev rodando
docker compose -f docker-compose.yml --project-name codelab-prod up -d

# 3. Setando env equivalente ao de prod
ENVIRONMENT=production docker compose -f docker-compose.yml up -d
```

**Boas práticas:**

1. **CI **sempre** sobe `-f docker-compose.yml` sem override** — assim bugs só-em-produção aparecem cedo.
2. **Makefile expõe dois alvos**:
   ```makefile
   up:       docker compose up -d
   up-prod:  docker compose -f docker-compose.yml up -d
   ```
   Dev roda `make up-prod` para reproduzir prod na máquina.
3. **Ambiente de `staging`** — subir o mesmo Compose num servidor separado com dados reais sintéticos, sem override. Bug só-em-prod vira bug-só-em-staging (mais cedo).
4. **Revisão do override**: limitar a diffs "dev-only" pequenos (bind mount, DEBUG, portas). Nunca mudar imagem, comando, segredos.

---

## Próximo passo

- Siga para o **[Bloco 4 — Produção e Segurança](../bloco-4/04-producao-seguranca.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Docker Compose e Ambientes Multi-Serviço](03-compose-multi-servico.md) | **↑ Índice**<br>[Módulo 5 — Containers e orquestração](../README.md) | **Próximo →**<br>[Bloco 4 — Produção, Segurança, Registries e SBOM](../bloco-4/04-producao-seguranca.md) |

<!-- nav:end -->

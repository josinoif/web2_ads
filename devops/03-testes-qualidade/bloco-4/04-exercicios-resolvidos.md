# Exercícios Resolvidos — Bloco 4

**Tempo estimado:** 25 a 40 minutos.

---

## Exercício 1 — Escolhendo o nível certo para cada caso

**Enunciado:**

Para cada cenário da MediQuick, diga se o teste mais adequado é **unit**, **integração com Testcontainers**, **E2E HTTP** ou **E2E de navegador (Playwright)**:

1. Verificar se `calcular_valor_consulta(plano, cupom)` retorna o valor correto.
2. Verificar se `ConsultaRepo.listar_entre(data_ini, data_fim)` gera a query SQL correta com `BETWEEN`.
3. Verificar se a API `POST /consultas` retorna 409 quando há conflito de horário.
4. Verificar se o **calendário visual** da UI destaca corretamente as datas ocupadas.
5. Verificar se `Paciente.deve_cobrar()` retorna `True` após a segunda consulta no mês.
6. Verificar se, ao agendar, **um e-mail é enfileirado** no Redis.

### Resolução

| # | Nível | Justificativa |
|---|-------|----------------|
| 1 | **Unit** | Função pura, sem I/O. Teste de milissegundos. |
| 2 | **Integração (Testcontainers + Postgres)** | Precisa do banco **real** para pegar bugs de SQL. |
| 3 | **E2E HTTP** (com `TestClient` e Postgres) | Envolve rota, validação, repo, banco. |
| 4 | **E2E de navegador (Playwright)** | Rendering visual — só navegador reproduz. **Poucos testes assim.** |
| 5 | **Unit** | Lógica de domínio. Testcontainers seria overkill. |
| 6 | **Integração (Testcontainers + Redis)** | Precisa do Redis real para verificar que o item foi enfileirado. |

---

## Exercício 2 — Refatorando um E2E flaky

**Enunciado:**

Abaixo, um teste E2E do repositório da MediQuick que falha 1 em 4 execuções. Identifique **no mínimo 4 causas de flakiness** e reescreva.

```python
import time, requests, random

def test_agendamento_via_api():
    # cria paciente com email aleatório... mas talvez repita
    email = f"paciente{random.randint(1, 100)}@ex.com"
    requests.post("http://staging/pacientes", json={"email": email})
    time.sleep(3)  # espera o serviço assimilar

    data = "2026-06-15T10:00"  # sem timezone!
    r = requests.post(
        "http://staging/consultas",
        json={"paciente": email, "data": data}
    )
    assert r.status_code == 201

    time.sleep(2)
    r2 = requests.get(f"http://staging/consultas?paciente={email}")
    assert len(r2.json()) == 1  # mas pode haver consulta de rodada anterior
```

### Resolução

**Causas de flakiness identificadas:**

1. **`random.randint(1,100)`** — espaço pequeno, colisões frequentes. Use `uuid.uuid4()`.
2. **`time.sleep(3)` e `time.sleep(2)`** — espera arbitrária. Devagar em ambiente lento, rápido demais em ambiente rápido. Use **polling com timeout**.
3. **Ambiente compartilhado (`staging`)** — outro teste pode estar criando dados com mesmo email. Use **ambiente efêmero** (testcontainers) ou **namespace por teste**.
4. **Data sem timezone** — comportamento varia com fuso. **Sempre use ISO 8601 com timezone**.
5. **`len(...) == 1`** — o banco não é limpo entre rodadas; pode haver registros prévios. **Isole estado**.
6. **Sem `raise_for_status`** — se POST retornar 500 com body estranho, o assert pode passar por acidente.
7. **Nome genérico** — `test_agendamento_via_api` não diz qual comportamento.

**Versão corrigida** (usando TestClient + fixture de banco limpo):

```python
import uuid
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from mediquick.api import app, set_repo


def test_post_consulta_retorna_201_e_torna_buscavel(repo):
    set_repo(repo)
    client = TestClient(app)
    email = f"paciente-{uuid.uuid4()}@ex.com"
    data_hora = datetime(2026, 6, 15, 10, 0, tzinfo=timezone.utc).isoformat()

    r = client.post(
        "/consultas",
        json={"paciente_email": email, "data_hora": data_hora},
    )
    assert r.status_code == 201
    criada = r.json()

    r2 = client.get(f"/consultas/{criada['id']}")
    assert r2.status_code == 200
    assert r2.json()["paciente_email"] == email
```

**Melhorias aplicadas:**

- **Banco efêmero e limpo** via fixture `repo` (truncate antes do teste).
- **`uuid.uuid4()`** — zero colisão.
- **ISO 8601 com timezone** explícito.
- **Sem `sleep`** — `TestClient` é síncrono; não há latência de rede.
- **Assert sobre ID retornado**, não count geral.
- **Nome descritivo** do comportamento testado.

---

## Exercício 3 — Construindo um fixture de Testcontainers

**Enunciado:**

Você precisa testar integração com **Redis** na MediQuick (fila de notificações). Escreva:

1. O fixture que sobe um Redis efêmero.
2. Um teste mínimo que verifica `LPUSH` + `LRANGE`.

### Resolução

**`conftest.py`:**

```python
import pytest
import redis
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:7-alpine") as rc:
        yield rc


@pytest.fixture
def redis_client(redis_container):
    """Client com banco LIMPO a cada teste."""
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    client = redis.Redis(host=host, port=int(port), decode_responses=True)
    client.flushdb()
    return client
```

**`test_notificacoes_queue.py`:**

```python
def test_lpush_e_lrange_mantem_ordem(redis_client):
    redis_client.lpush("fila:notif", "msg1")
    redis_client.lpush("fila:notif", "msg2")
    redis_client.lpush("fila:notif", "msg3")

    # LPUSH coloca no início — última fica em índice 0
    itens = redis_client.lrange("fila:notif", 0, -1)
    assert itens == ["msg3", "msg2", "msg1"]


def test_flushdb_isola_testes(redis_client):
    # teste anterior não contamina este
    itens = redis_client.lrange("fila:notif", 0, -1)
    assert itens == []
```

**Por que `flushdb` na fixture:** garante isolamento sem custo de subir contêiner novo por teste.

---

## Exercício 4 — Aposentando E2E redundantes

**Enunciado:**

A MediQuick tem 450 testes E2E. O líder técnico listou os 5 primeiros:

1. `test_login_com_credenciais_validas` — verifica que o login OK redireciona pra home.
2. `test_login_com_senha_errada_mostra_erro_generico` — verifica texto de erro.
3. `test_login_com_email_invalido_mostra_erro_de_validacao` — formato inválido.
4. `test_login_sql_injection_bloqueado` — passa `' OR 1=1 --` como email.
5. `test_fluxo_completo_agendamento_ate_dashboard` — login + agendar + ver no dashboard.

Para cada um, proponha **manter como E2E** ou **migrar para outro nível** (unit/integração). Justifique.

### Resolução

| # | Proposta | Nível alvo | Justificativa |
|---|----------|------------|----------------|
| 1 | **Manter como E2E** (mas reduzir a 1) | E2E | Fluxo crítico visual — prova que login redireciona. **Um** suficiente. |
| 2 | **Migrar para unit da view/controller** | Unit | Testar `view_login(invalid)` retorna erro. E2E de navegador é desproporcional. |
| 3 | **Migrar para unit do validator** | Unit | Validação de formato é lógica pura — teste unit cobre em milissegundos. |
| 4 | **Migrar para integração** | Integração | SQL injection exige **banco real**. Não precisa navegador. |
| 5 | **Manter como E2E** (fluxo de negócio real) | E2E | Fluxo crítico de ponta a ponta. **Um** E2E desse tipo por feature crítica. |

**Saldo:** 5 E2E → 2 E2E. Se você fizer isso para todos os 450, provavelmente ficam entre **20 e 40 E2E reais**. É o tamanho certo.

---

## Exercício 5 — Organizando jobs no CI

**Enunciado:**

Considere que a MediQuick tem:

- 1500 testes unitários (rodam em 90s).
- 60 testes de integração com Postgres (rodam em 3 min).
- 15 testes E2E HTTP (rodam em 4 min).
- 3 testes E2E Playwright (rodam em 8 min).

Proponha uma **configuração de jobs GitHub Actions** que minimize feedback ao dev sem sacrificar cobertura de PR.

### Resolução

**Estratégia:** pipeline em 3 jobs paralelos onde possível; E2E Playwright só após merge (nightly ou merge-queue).

```yaml
name: CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  # Job 1 — Fast lane: lint + unit (~2 min total)
  fast:
    name: Fast (lint + unit)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: "pip" }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: ruff check .
      - run: pytest tests/unit --cov=src --cov-branch --cov-fail-under=70

  # Job 2 — Integração (~3 min), em paralelo ao fast
  integration:
    name: Integration (Postgres)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: "pip" }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/integration -v

  # Job 3 — E2E HTTP rápidos (~4 min), em paralelo
  e2e-http:
    name: E2E (HTTP)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: "pip" }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/e2e/http -v

  # Job 4 — Playwright só em push para main (não em PR) — evita gargalar
  e2e-playwright:
    name: E2E (Playwright) — main only
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: "pip" }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: playwright install chromium --with-deps
      - run: pytest tests/e2e/browser -v
```

**Por quê:**

- **Jobs paralelos** — os 3 primeiros rodam simultaneamente; **feedback total** do PR em ~4 min, não 10.
- **Playwright só em `main`** — se quebrar no merge para main, o time conserta como hotfix. No dia a dia, **não** trava PR por 8 min adicionais.
- **Cache `pip`** — pull reaproveita dependências.
- Alternativa robusta: **merge queue** do GitHub (se o plano permite) — rodaria Playwright automaticamente antes do merge final.

---

## Exercício 6 — Trade-off: E2E vs. Contract

**Enunciado:**

Os serviços **Agendamento** e **Notificação** da MediQuick comunicam via Redis. Hoje, cada mudança em **Agendamento** quebra o deploy porque um **E2E** atravessa os dois.

O arquiteto propõe: "**vamos fazer E2E mais robustos**". Você discorda. Proponha **contract tests** e explique o trade-off.

### Resolução

**Diagnóstico:**

O E2E "Agendamento → fila → Notificação" está fazendo 2 trabalhos:

- Verificar que **Agendamento** publica corretamente.
- Verificar que **Notificação** consome corretamente.
- E ainda: subir **ambos os serviços + Redis** + coordenar tempo.

**Proposta de Contract testing:**

Dividir em 2 contratos independentes:

1. **Provider test (Agendamento):** após agendar, **verifica que publicou** a mensagem no formato esperado.

```python
def test_agendar_publica_evento_no_formato_esperado(repo, redis_client):
    set_repo(repo)
    client = TestClient(app_agendamento)

    client.post("/consultas", json={...})

    msg = redis_client.rpop("eventos:consulta_agendada")
    evento = json.loads(msg)
    assert evento["schema_version"] == 1
    assert "consulta_id" in evento
    assert "paciente_email" in evento
    assert "data_hora" in evento
```

2. **Consumer test (Notificação):** dado um evento no formato esperado, **verifica que consumiu e agiu corretamente** — sem rodar Agendamento.

```python
def test_notificacao_consome_evento_e_envia_email(redis_client, notificador_fake):
    evento = {
        "schema_version": 1,
        "consulta_id": 42,
        "paciente_email": "ana@ex.com",
        "data_hora": "2026-06-15T10:00:00+00:00",
    }
    redis_client.lpush("eventos:consulta_agendada", json.dumps(evento))

    consumir_uma_mensagem()  # função do serviço Notificação

    assert notificador_fake.enviados == [{"to": "ana@ex.com", "template": "confirmacao"}]
```

**Trade-off:**

| Dimensão | E2E Integrado | Contract tests |
|----------|---------------|----------------|
| Infraestrutura | Sobe 2 serviços + Redis + banco | Cada um sobe o seu |
| Velocidade | Lento (~1 min) | Rápido (~10s cada) |
| Falha diagnóstica | "Falhou — onde?" | "Agendamento falha aqui" vs. "Notificação falha aqui" |
| Deploy independente | Não permite — precisa testar tudo junto | **Permite** — mudanças em um serviço testam contra o contrato |
| Custo de escrever | Médio | Médio (e cresce menos com N serviços) |

**Risco único do contract testing:** você precisa **garantir que o contrato está em sincronia**. Se um lado muda sem atualizar o contrato, o bug vaza.

Ferramentas como **Pact** automatizam isso: provider publica o que cumpre, consumer publica o que espera, e um **broker** detecta divergência.

---

## Próximo passo

Você concluiu os 4 blocos teóricos. Siga para os **[exercícios progressivos](../exercicios-progressivos/)** — onde você aplica tudo ao cenário da MediQuick em 5 partes práticas.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Testes de Integração, E2E e Estratégias](04-integracao-e2e.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Exercícios Progressivos — Módulo 3](../exercicios-progressivos/README.md) |

<!-- nav:end -->

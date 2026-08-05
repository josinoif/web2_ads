# Parte 3 — Integração com Testcontainers (Postgres real)

**Tempo:** ~1h
**Pré-requisitos:** Parte 2 concluída, **Docker instalado** e **Bloco 4**.
**Entregável:** pasta `tests/integration/` com `conftest.py` + testes + implementação `repo.py`.

---

## Objetivo

Adicionar a camada de **persistência** ao seu serviço de Agendamento e escrever **testes de integração** que rodam contra **Postgres real** via Testcontainers.

Ao final:

- Existe um `ConsultaRepo` que persiste em Postgres.
- Testes de integração **sobem Postgres efêmero** automaticamente.
- O teste de integração **reproduz bugs de SQL** que testes unit jamais detectariam.

---

## Dependências adicionais

```bash
pip install 'testcontainers[postgres]' psycopg2-binary
```

Adicione também em um novo `requirements-dev.txt`:

```
pytest>=8.0
pytest-cov>=4.1
ruff>=0.4
testcontainers[postgres]>=4.4
psycopg2-binary>=2.9
```

E em `requirements.txt`:

```
psycopg2-binary>=2.9
```

---

## Estrutura alvo

```
mediquick-agendamento/
├── src/agendamento/
│   ├── __init__.py
│   ├── agenda.py           (já existe, da Parte 2)
│   └── repo.py             (novo)
├── tests/
│   ├── unit/
│   │   └── test_agenda.py
│   └── integration/
│       ├── __init__.py
│       ├── conftest.py
│       └── test_consulta_repo.py
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

---

## Passo 1 — Escrever `src/agendamento/repo.py`

```python
"""Repositório de Consulta — persistência em Postgres."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS consultas (
    id             SERIAL PRIMARY KEY,
    paciente_email VARCHAR(200) NOT NULL,
    data_hora      TIMESTAMPTZ NOT NULL,
    cancelada      BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_paciente_data UNIQUE (paciente_email, data_hora)
);
"""


@dataclass
class ConsultaRow:
    id: int
    paciente_email: str
    data_hora: datetime
    cancelada: bool


class ConsultaRepo:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn

    def _conn(self):
        return psycopg2.connect(self.dsn)

    def criar_schema(self) -> None:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)

    def salvar(self, paciente_email: str, data_hora: datetime) -> int:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO consultas (paciente_email, data_hora) "
                "VALUES (%s, %s) RETURNING id",
                (paciente_email, data_hora),
            )
            return cur.fetchone()[0]

    def buscar(self, consulta_id: int) -> ConsultaRow | None:
        with self._conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM consultas WHERE id = %s", (consulta_id,))
            row = cur.fetchone()
            return ConsultaRow(**row) if row else None

    def listar_futuras_do_paciente(
        self, paciente_email: str, agora: datetime
    ) -> list[ConsultaRow]:
        sql = (
            "SELECT * FROM consultas "
            "WHERE paciente_email = %s AND data_hora > %s AND cancelada = FALSE "
            "ORDER BY data_hora ASC"
        )
        with self._conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (paciente_email, agora))
            return [ConsultaRow(**r) for r in cur.fetchall()]

    def marcar_cancelada(self, consulta_id: int) -> bool:
        with self._conn() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE consultas SET cancelada = TRUE WHERE id = %s",
                (consulta_id,),
            )
            return cur.rowcount == 1
```

**Commit:**

```bash
git add src/agendamento/repo.py requirements.txt requirements-dev.txt
git commit -m "feat(repo): adiciona ConsultaRepo com persistência em Postgres"
```

---

## Passo 2 — `tests/integration/conftest.py`

```python
"""Fixtures para testes de integração — Postgres efêmero."""
from __future__ import annotations

import psycopg2
import pytest
from testcontainers.postgres import PostgresContainer

from agendamento.repo import ConsultaRepo


@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest.fixture(scope="session")
def dsn(postgres_container) -> str:
    url = postgres_container.get_connection_url()
    # testcontainers devolve URL SQLAlchemy; psycopg2 quer "postgresql://"
    return url.replace("postgresql+psycopg2://", "postgresql://")


@pytest.fixture(scope="session")
def repo_com_schema(dsn) -> ConsultaRepo:
    r = ConsultaRepo(dsn)
    r.criar_schema()
    return r


@pytest.fixture
def repo(repo_com_schema, dsn) -> ConsultaRepo:
    """A cada teste, limpa a tabela."""
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE consultas RESTART IDENTITY")
    return repo_com_schema
```

**Commit:**

```bash
git add tests/integration/
git commit -m "test(integration): conftest com Testcontainers Postgres"
```

---

## Passo 3 — `tests/integration/test_consulta_repo.py`

Escreva **ao menos 4 testes de integração**:

```python
from datetime import datetime, timedelta, timezone

import psycopg2
import pytest


UTC = timezone.utc


def test_salvar_e_buscar_recupera_todos_os_campos(repo):
    dt = datetime(2026, 3, 10, 14, 30, tzinfo=UTC)

    id_ = repo.salvar("ana@ex.com", dt)
    row = repo.buscar(id_)

    assert row is not None
    assert row.paciente_email == "ana@ex.com"
    assert row.data_hora == dt
    assert row.cancelada is False


def test_restricao_unica_impede_paciente_marcar_duas_vezes_no_mesmo_horario(repo):
    dt = datetime(2026, 3, 10, 14, 30, tzinfo=UTC)
    repo.salvar("ana@ex.com", dt)

    with pytest.raises(psycopg2.errors.UniqueViolation):
        repo.salvar("ana@ex.com", dt)


def test_listar_futuras_retorna_somente_nao_canceladas_e_futuras(repo):
    agora = datetime(2026, 3, 1, 9, 0, tzinfo=UTC)
    # futura - deve aparecer
    id_futura = repo.salvar("ana@ex.com", agora + timedelta(days=5))
    # passada - não deve aparecer
    repo.salvar("ana@ex.com", agora - timedelta(days=1))
    # futura cancelada - não deve aparecer
    id_cancelada = repo.salvar("ana@ex.com", agora + timedelta(days=10))
    assert repo.marcar_cancelada(id_cancelada) is True
    # outro paciente - não deve aparecer
    repo.salvar("outro@ex.com", agora + timedelta(days=7))

    futuras = repo.listar_futuras_do_paciente("ana@ex.com", agora)

    assert len(futuras) == 1
    assert futuras[0].id == id_futura


def test_marcar_cancelada_retorna_false_se_id_nao_existe(repo):
    assert repo.marcar_cancelada(99999) is False


def test_buscar_id_inexistente_retorna_none(repo):
    assert repo.buscar(42) is None
```

**Rodar:**

```bash
pytest tests/integration -v
```

Na primeira rodada, o Docker baixa `postgres:16-alpine` (~90 MB). Depois, cada rodada sobe em segundos.

**Saída esperada:**

```
tests/integration/test_consulta_repo.py::test_salvar_e_buscar_recupera_todos_os_campos PASSED
tests/integration/test_consulta_repo.py::test_restricao_unica_impede_paciente_marcar_duas_vezes_no_mesmo_horario PASSED
tests/integration/test_consulta_repo.py::test_listar_futuras_retorna_somente_nao_canceladas_e_futuras PASSED
tests/integration/test_consulta_repo.py::test_marcar_cancelada_retorna_false_se_id_nao_existe PASSED
tests/integration/test_consulta_repo.py::test_buscar_id_inexistente_retorna_none PASSED
```

**Commit:**

```bash
git add tests/integration/test_consulta_repo.py
git commit -m "test(integration): ConsultaRepo com Postgres real via Testcontainers"
```

---

## Passo 4 — Separar execução de unit vs. integração no `pyproject.toml`

Unit **não** pode depender de Docker. Adicione marcadores para facilitar:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
markers = [
    "integration: marcar teste que precisa de Docker/Testcontainers",
]
addopts = "-ra --strict-markers"
```

No topo de `tests/integration/conftest.py`, marque automaticamente todo teste da pasta:

```python
def pytest_collection_modifyitems(config, items):
    import pathlib
    integration_dir = pathlib.Path(__file__).parent
    for item in items:
        if integration_dir in pathlib.Path(item.fspath).parents or \
           pathlib.Path(item.fspath) == integration_dir / item.fspath.basename:
            item.add_marker("integration")
```

(Alternativa mais simples: rodar apenas `pytest tests/unit` para unit e `pytest tests/integration` para integração.)

---

## Passo 5 — Documentar no README

No `README.md` do seu projeto, adicione:

```markdown
## Como rodar os testes

### Testes unitários (rápidos, sem Docker)
```bash
pytest tests/unit
```

### Testes de integração (exigem Docker)
```bash
pytest tests/integration
```

### Suíte completa com cobertura
```bash
pytest --cov=src --cov-branch --cov-report=term-missing
```
```

**Commit final da Parte 3:**

```bash
git add README.md pyproject.toml tests/integration/conftest.py
git commit -m "docs: documenta execução de testes e separa unit/integration"
```

---

## Critérios de "pronto"

- [ ] `ConsultaRepo` implementado com `salvar`, `buscar`, `listar_futuras_do_paciente`, `marcar_cancelada`.
- [ ] `conftest.py` com Postgres efêmero e fixture `repo` que limpa tabela.
- [ ] **Mínimo 4 testes de integração** passando.
- [ ] Testes **unit** (da Parte 2) continuam passando **sem Docker**.
- [ ] README atualizado.

---

## Dicas e armadilhas

- **Erro mais comum:** Docker não está rodando. Teste com `docker ps`. Se der "cannot connect", suba o daemon ou use Docker Desktop.
- **Lento na primeira rodada?** Normal (pull da imagem). Nas próximas, cache local acelera.
- **Testcontainers em WSL2**: pode exigir `DOCKER_HOST=unix:///var/run/docker.sock`. Veja [docs](https://testcontainers.com/guides/getting-started-with-testcontainers-for-python/).
- **Usar `scope="session"` no contêiner** — sobe UMA vez por rodada. `scope="function"` sobe por teste (segundos x teste = minutos de overhead).
- **Sempre `TRUNCATE`** — `DELETE FROM` também zera dados, mas `TRUNCATE RESTART IDENTITY` resetam sequências (`id`).
- **Use `postgres:16-alpine`** (ou a versão que você usa em produção). **Não** use `:latest` — vira flaky ao longo do tempo com atualizações.

---

## Próximo passo

Siga para a **[Parte 4 — Quality Gates no pipeline CI](parte-4-quality-gates-ci.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — TDD do Serviço de Agendamento](parte-2-tdd-agendamento.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Parte 4 — Quality Gates no Pipeline CI](parte-4-quality-gates-ci.md) |

<!-- nav:end -->

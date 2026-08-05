# Parte 2 — TDD do Serviço de Agendamento

**Tempo:** ~1h 30min
**Pré-requisitos:** Bloco 2 — TDD, BDD e Red-Green-Refactor.
**Entregável:** repositório Git com código + testes + **commits mostrando o ciclo Red-Green-Refactor**.

---

## Objetivo

Construir o **esqueleto do serviço de Agendamento** da MediQuick usando **TDD**. Ao final, você terá:

- Código de domínio (`Consulta`, `Agenda`) com regras de negócio.
- Suíte de testes unitários na proporção correta da pirâmide.
- Histórico git que **prova** TDD (3 commits por feature).

Este é o **núcleo do repositório** que você entrega na avaliação.

---

## Setup inicial

### 1. Criar o projeto

```bash
mkdir mediquick-agendamento
cd mediquick-agendamento
git init
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pytest pytest-cov ruff
```

### 2. Estrutura mínima

```bash
mkdir -p src/agendamento tests/unit
touch src/agendamento/__init__.py tests/__init__.py tests/unit/__init__.py
```

### 3. `pyproject.toml`

```toml
[project]
name = "mediquick-agendamento"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = "-ra --strict-markers"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 80

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "W", "B", "N", "UP"]
```

### 4. `.gitignore`

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.coverage
coverage.xml
htmlcov/
```

### 5. Primeiro commit

```bash
git add .
git commit -m "chore: esqueleto do projeto mediquick-agendamento"
```

---

## Feature 1 — Agendar uma consulta

**Regra de negócio:**

> Um paciente pode agendar uma consulta com **pelo menos 24h de antecedência** em **horário comercial (8h às 18h)**.

### Ciclo 1 — Agendamento válido

#### 🔴 RED

Arquivo `tests/unit/test_agenda.py`:

```python
from datetime import datetime

from agendamento.agenda import Agenda


def test_agendar_cria_consulta_no_futuro_em_horario_comercial():
    agora = datetime(2026, 1, 15, 9, 0, 0)
    data_consulta = datetime(2026, 1, 20, 10, 0, 0)
    agenda = Agenda()

    consulta = agenda.agendar(
        paciente_email="ana@example.com",
        data_hora=data_consulta,
        agora=agora,
    )

    assert consulta.paciente_email == "ana@example.com"
    assert consulta.data_hora == data_consulta
    assert consulta.cancelada is False
```

Rode: `pytest`. Falha por `ImportError`. **RED**.

**Commit:**

```bash
git add tests/
git commit -m "test(agenda): RED - agendamento válido cria consulta"
```

#### 🟢 GREEN

Arquivo `src/agendamento/agenda.py`:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Consulta:
    paciente_email: str
    data_hora: datetime
    cancelada: bool = False


class Agenda:
    def agendar(
        self,
        paciente_email: str,
        data_hora: datetime,
        agora: datetime,
    ) -> Consulta:
        return Consulta(paciente_email=paciente_email, data_hora=data_hora)
```

Rode: `pytest`. **1 passed**. GREEN.

**Commit:**

```bash
git add src/
git commit -m "feat(agenda): GREEN - agendamento retorna consulta"
```

### Ciclo 2 — Bloqueia se faltar < 24h

#### 🔴 RED

Adicione ao `test_agenda.py`:

```python
import pytest

from agendamento.agenda import Agenda, AgendamentoInvalido


def test_nao_permite_agendar_com_menos_de_24h():
    agora = datetime(2026, 1, 15, 10, 0, 0)
    data_consulta = datetime(2026, 1, 15, 15, 0, 0)  # 5h depois, hoje
    agenda = Agenda()

    with pytest.raises(AgendamentoInvalido):
        agenda.agendar(
            paciente_email="ana@example.com",
            data_hora=data_consulta,
            agora=agora,
        )
```

Rode. Falha. **RED**.

```bash
git add tests/
git commit -m "test(agenda): RED - bloqueia agendamento com menos de 24h"
```

#### 🟢 GREEN

Adicione ao `agenda.py`:

```python
from datetime import datetime, timedelta


class AgendamentoInvalido(Exception):
    pass


class Agenda:
    def agendar(self, paciente_email, data_hora, agora) -> Consulta:
        if data_hora - agora < timedelta(hours=24):
            raise AgendamentoInvalido(
                "Agendamento requer 24h de antecedência mínima."
            )
        return Consulta(paciente_email=paciente_email, data_hora=data_hora)
```

Rode: **2 passed**. GREEN.

```bash
git add src/
git commit -m "feat(agenda): GREEN - bloqueia agendamento com menos de 24h"
```

### Ciclo 3 — Bloqueia fora do horário comercial

#### 🔴 RED

```python
def test_nao_permite_agendar_fora_do_horario_comercial():
    agora = datetime(2026, 1, 15, 9, 0, 0)
    data_consulta = datetime(2026, 1, 20, 22, 0, 0)  # 22h
    agenda = Agenda()

    with pytest.raises(AgendamentoInvalido):
        agenda.agendar(
            paciente_email="ana@example.com",
            data_hora=data_consulta,
            agora=agora,
        )
```

```bash
git add tests/
git commit -m "test(agenda): RED - bloqueia horário não comercial"
```

#### 🟢 GREEN

```python
HORA_INICIO_COMERCIAL = 8
HORA_FIM_COMERCIAL = 18  # 18h exclusivo (última consulta inicia às 17h)


class Agenda:
    def agendar(self, paciente_email, data_hora, agora) -> Consulta:
        if data_hora - agora < timedelta(hours=24):
            raise AgendamentoInvalido("Agendamento requer 24h de antecedência mínima.")
        if not (HORA_INICIO_COMERCIAL <= data_hora.hour < HORA_FIM_COMERCIAL):
            raise AgendamentoInvalido(
                f"Horário fora do comercial ({HORA_INICIO_COMERCIAL}h-{HORA_FIM_COMERCIAL}h)."
            )
        return Consulta(paciente_email=paciente_email, data_hora=data_hora)
```

```bash
git add src/
git commit -m "feat(agenda): GREEN - bloqueia fora do horário comercial"
```

#### 🔵 REFACTOR

Agora há 2 validações misturadas. Extrair:

```python
from dataclasses import dataclass
from datetime import datetime, timedelta


ANTECEDENCIA_MIN = timedelta(hours=24)
HORA_INICIO_COMERCIAL = 8
HORA_FIM_COMERCIAL = 18


class AgendamentoInvalido(Exception):
    pass


@dataclass
class Consulta:
    paciente_email: str
    data_hora: datetime
    cancelada: bool = False


class Agenda:
    def agendar(self, paciente_email, data_hora, agora) -> Consulta:
        self._validar(data_hora, agora)
        return Consulta(paciente_email=paciente_email, data_hora=data_hora)

    def _validar(self, data_hora: datetime, agora: datetime) -> None:
        self._exigir_antecedencia(data_hora, agora)
        self._exigir_horario_comercial(data_hora)

    @staticmethod
    def _exigir_antecedencia(data_hora: datetime, agora: datetime) -> None:
        if data_hora - agora < ANTECEDENCIA_MIN:
            raise AgendamentoInvalido("Agendamento requer 24h de antecedência mínima.")

    @staticmethod
    def _exigir_horario_comercial(data_hora: datetime) -> None:
        if not (HORA_INICIO_COMERCIAL <= data_hora.hour < HORA_FIM_COMERCIAL):
            raise AgendamentoInvalido(
                f"Horário fora do comercial "
                f"({HORA_INICIO_COMERCIAL}h-{HORA_FIM_COMERCIAL}h)."
            )
```

Rode: **3 passed**. Refactor não quebrou.

```bash
git add src/
git commit -m "refactor(agenda): extrai validações em métodos dedicados"
```

---

## Feature 2 — Cancelamento (TDD completo, com menos orientação)

**Regra:**

> Pode cancelar consulta se faltar **2h ou mais** de antecedência.

**Sua tarefa:** implementar por TDD seguindo o mesmo padrão:

1. 🔴 RED: `test_cancelar_com_antecedencia_marca_cancelada` (commit de teste vermelho).
2. 🟢 GREEN: implementação mínima (commit GREEN).
3. 🔴 RED: `test_nao_permite_cancelar_com_menos_de_2h` (commit vermelho).
4. 🟢 GREEN: implementação mínima (commit GREEN).
5. 🔵 REFACTOR (se fizer sentido): commit de refactor.

**Minimo:** 4 commits (2 ciclos). **Ideal:** 6 (com refactor).

---

## Feature 3 — Listagem de consultas futuras (bonus)

**Regra:**

> `agenda.listar_futuras(paciente_email, agora)` retorna consultas **não canceladas** e **com data_hora > agora**, ordenadas.

Você precisa primeiro adicionar **armazenamento** à `Agenda` (lista em memória serve nessa etapa — o banco real vem na Parte 3).

TDD no ritmo que você já pegou. Não está medido no tempo, mas **será exigido** mais adiante (Parte 3).

---

## Mínimo esperado ao final da Parte 2

- [ ] Commits sequenciais com padrão `test: RED → feat: GREEN → refactor:`.
- [ ] **Pelo menos 7 testes passando** em `tests/unit/` (3 agendamento + 2 a 3 cancelamento + opcional listagem).
- [ ] Cobertura **≥ 80%** em `src/agendamento/agenda.py` (checar com `pytest --cov=src --cov-report=term-missing`).
- [ ] `ruff check .` sem erros.
- [ ] Código commitado em repositório Git.

Exemplo de histórico esperado:

```
* refactor(agenda): consolida política de cancelamento
* feat(agenda): GREEN - bloqueia cancelamento com menos de 2h
* test(agenda): RED - bloqueia cancelamento com menos de 2h
* feat(agenda): GREEN - cancelamento simples
* test(agenda): RED - cancelar marca consulta como cancelada
* refactor(agenda): extrai validações em métodos dedicados
* feat(agenda): GREEN - bloqueia fora do horário comercial
* test(agenda): RED - bloqueia horário não comercial
* feat(agenda): GREEN - bloqueia agendamento com menos de 24h
* test(agenda): RED - bloqueia agendamento com menos de 24h
* feat(agenda): GREEN - agendamento retorna consulta
* test(agenda): RED - agendamento válido cria consulta
* chore: esqueleto do projeto mediquick-agendamento
```

---

## Dicas

- **Não adiante commits.** Commit logo após RED; commit logo após GREEN. É tentador fazer tudo junto, mas **o histórico importa**.
- **Se errar de commit** (esqueceu `git add`, mensagem errada), use `git commit --amend` **antes** de pushear.
- **Mantenha o ciclo curto.** Cada ciclo RED→GREEN deveria durar **5 a 20 minutos**. Mais que isso, algo está grande demais — divida o teste.
- **Não mocke nada ainda.** As validações são pura lógica; teste direto. A injeção de `agora` é o que você precisa para ser determinístico.

---

## Próximo passo

Com o domínio pronto e testado, siga para a **[Parte 3 — Integração com Testcontainers](parte-3-integracao-testcontainers.md)** — você vai adicionar **persistência real em Postgres** e escrever os testes de integração.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — Diagnóstico da Pirâmide Atual da MediQuick](parte-1-diagnostico-piramide.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Parte 3 — Integração com Testcontainers (Postgres real)](parte-3-integracao-testcontainers.md) |

<!-- nav:end -->

# Exercícios Resolvidos — Bloco 2

**Tempo estimado:** 30 a 45 minutos. O exercício 3 exige digitar código.

---

## Exercício 1 — Identificando quem é RED, GREEN ou REFACTOR

**Enunciado:**

Classifique cada situação como **RED**, **GREEN**, **REFACTOR** ou **não é TDD**:

1. Dev adiciona `test_calcular_desconto_vip()` que falha com `AttributeError: 'Paciente' object has no attribute 'desconto_vip'`.
2. Dev adiciona `if paciente.plano == "VIP": return 0.1` até o teste passar.
3. Dev renomeia a variável `d` para `percentual_desconto`, sem alterar lógica; todos os testes continuam passando.
4. Dev implementa toda a regra de desconto do sistema (4 tipos de plano) e depois escreve testes para ver se está certo.
5. Dev adiciona um teste, e para fazer passar, implementa **duas** regras diferentes de uma vez.

### Resolução

| # | Classificação | Comentário |
|---|---------------|------------|
| 1 | **RED** | Teste falha por razão específica (atributo ausente). ✅ |
| 2 | **GREEN** | Mínimo que faz passar. ✅ |
| 3 | **REFACTOR** | Melhora o design (legibilidade) mantendo comportamento. ✅ |
| 4 | **Não é TDD** | Teste depois. Pode ser código testado, mas **não** é TDD. Perde efeito de design. |
| 5 | **Violação de GREEN** | GREEN é **mínimo**. Implementar 2 regras de uma vez gera código sem teste que cobre. Quebra disciplina do ciclo. |

---

## Exercício 2 — O que seu histórico git conta sobre você?

**Enunciado:**

O histórico abaixo é de um dev afirmando praticar TDD. Analise e identifique sinais de que o processo foi **mesmo TDD** ou **teste adicionado depois**:

```
* 4f2a9 feat: implementa politica de cancelamento de consulta
* a7be1 feat: implementa agendamento + validações
* 3d5c8 feat: tipos de paciente + relacionamento com consulta
* 9e2f4 test: cobertura de agendamento, cancelamento e paciente
```

### Resolução

**Sinais claros de que NÃO é TDD:**

- Os 3 commits de **feat vieram antes** do commit de teste.
- O commit de **teste** é **um só**, grande, "cobre tudo" — padrão típico de quem adicionou teste depois.
- Não há ciclo `test → feat → refactor` por feature.

**Um histórico coerente com TDD** seria:

```
* 7b2a1 refactor(paciente): extrai tipo Plano como enum
* c4e9f feat(paciente): implementa relacionamento com consulta
* 1d3a7 test(paciente): paciente tem consultas associadas
* 8a92b refactor(consulta): extrai politica de cancelamento
* 5bc44 feat(consulta): bloqueia cancelamento com menos de 2h
* e7a2c test(consulta): cancelamento com menos de 2h falha
* 0ff33 feat(consulta): agendar consulta
* 3d18e test(consulta): agendar consulta cria registro
```

Cada **feat** é precedido por um **test** correspondente. Refatorações aparecem **depois** de GREEN, não misturadas.

---

## Exercício 3 — Pratique TDD (hands-on)

**Enunciado:**

Siga o ciclo **Red-Green-Refactor** para implementar a seguinte regra:

> Na MediQuick, um **Paciente** tem direito a **1 consulta gratuita por mês** se for do plano **Básico**. A segunda consulta no mesmo mês é cobrada.
>
> Implemente o método `deve_cobrar(data: datetime) -> bool` em uma classe `Paciente`.

Faça **3 ciclos RED-GREEN** no mínimo. Não precisa fazer REFACTOR se não houver o que refatorar.

### Resolução

#### Setup

```bash
mkdir -p mediquick-ex3/src/mediquick mediquick-ex3/tests
cd mediquick-ex3
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
touch src/mediquick/__init__.py tests/__init__.py
```

`pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

#### Ciclo 1 — Primeira consulta do mês é gratuita

**🔴 RED** — `tests/test_paciente.py`:

```python
from datetime import datetime

from mediquick.paciente import Paciente


def test_primeira_consulta_do_mes_nao_e_cobrada():
    paciente = Paciente(id=1, nome="Ana", plano="BASICO")

    assert paciente.deve_cobrar(datetime(2026, 1, 15)) is False
```

**🟢 GREEN** — `src/mediquick/paciente.py`:

```python
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Paciente:
    id: int
    nome: str
    plano: str

    def deve_cobrar(self, data: datetime) -> bool:
        return False
```

Passou. Seguimos.

#### Ciclo 2 — Segunda consulta no mesmo mês é cobrada

**🔴 RED**:

```python
def test_segunda_consulta_no_mesmo_mes_e_cobrada():
    paciente = Paciente(id=1, nome="Ana", plano="BASICO")
    paciente.registrar_consulta(datetime(2026, 1, 10))

    assert paciente.deve_cobrar(datetime(2026, 1, 15)) is True
```

Falha com `AttributeError: 'Paciente' has no attribute 'registrar_consulta'`.

**🟢 GREEN**:

```python
@dataclass
class Paciente:
    id: int
    nome: str
    plano: str
    consultas_do_mes: list = None

    def __post_init__(self):
        if self.consultas_do_mes is None:
            self.consultas_do_mes = []

    def registrar_consulta(self, data: datetime) -> None:
        self.consultas_do_mes.append(data)

    def deve_cobrar(self, data: datetime) -> bool:
        do_mesmo_mes = [
            d for d in self.consultas_do_mes
            if d.year == data.year and d.month == data.month
        ]
        return len(do_mesmo_mes) >= 1
```

Passou.

#### Ciclo 3 — Consultas de mês diferente não contam

**🔴 RED**:

```python
def test_consulta_de_mes_anterior_nao_conta():
    paciente = Paciente(id=1, nome="Ana", plano="BASICO")
    paciente.registrar_consulta(datetime(2025, 12, 10))

    assert paciente.deve_cobrar(datetime(2026, 1, 15)) is False
```

**Já passa** com a implementação atual — mas é um teste de **regressão** valioso. Adicione ao conjunto.

#### Ciclo 4 — Plano não-básico sempre cobra? (escolha de design)

O enunciado diz "se for do plano Básico". E os outros? Vamos assumir **sempre cobra** (cenário real pode ter outras regras).

**🔴 RED**:

```python
def test_plano_premium_sempre_e_cobrado_mesmo_na_primeira_consulta():
    paciente = Paciente(id=1, nome="Ana", plano="PREMIUM")

    assert paciente.deve_cobrar(datetime(2026, 1, 15)) is True
```

**🟢 GREEN**:

```python
    def deve_cobrar(self, data: datetime) -> bool:
        if self.plano != "BASICO":
            return True
        do_mesmo_mes = [
            d for d in self.consultas_do_mes
            if d.year == data.year and d.month == data.month
        ]
        return len(do_mesmo_mes) >= 1
```

#### 🔵 REFACTOR final

Agora o método começa a ter **duas responsabilidades**: regra de plano e contagem mensal. Podemos extrair:

```python
from collections.abc import Iterable


def _consultas_no_mes(consultas: Iterable[datetime], referencia: datetime) -> list[datetime]:
    return [d for d in consultas if (d.year, d.month) == (referencia.year, referencia.month)]


@dataclass
class Paciente:
    id: int
    nome: str
    plano: str
    consultas_do_mes: list = None

    def __post_init__(self):
        if self.consultas_do_mes is None:
            self.consultas_do_mes = []

    def registrar_consulta(self, data: datetime) -> None:
        self.consultas_do_mes.append(data)

    def deve_cobrar(self, data: datetime) -> bool:
        if self.plano != "BASICO":
            return True
        return len(_consultas_no_mes(self.consultas_do_mes, data)) >= 1
```

Testes continuam passando — refactor válido.

---

## Exercício 4 — Convertendo teste tradicional para BDD

**Enunciado:**

Dado o teste pytest puro abaixo, reescreva como **cenário Gherkin**:

```python
def test_agendar_consulta_em_horario_comercial_cria_consulta_pendente():
    agora = datetime(2026, 1, 15, 14, 0, 0)
    paciente = Paciente(id=1, nome="Ana", plano="BASICO")
    medico = Medico(id=10, nome="Dr. Silva", especialidade="Cardiologia")
    horario = datetime(2026, 1, 20, 10, 0, 0)

    consulta = AgendamentoService().agendar(paciente, medico, horario, agora)

    assert consulta.status == "PENDENTE"
    assert consulta.paciente_id == 1
    assert consulta.medico_id == 10
```

### Resolução

```gherkin
Feature: Agendamento de consulta
  Como paciente
  Quero agendar uma consulta com um médico
  Para ser atendido

  Scenario: Agendamento em horário comercial cria consulta pendente
    Given um paciente "Ana" do plano "BASICO"
    And um médico "Dr. Silva" da especialidade "Cardiologia"
    When eu agendo uma consulta para o dia 20/01/2026 às 10:00
    Then a consulta é criada com status "PENDENTE"
    And a consulta está vinculada ao paciente
    And a consulta está vinculada ao médico
```

**Observação pedagógica:**

A versão Gherkin é **melhor para conversar com negócio**; a versão pytest é **melhor para executar em massa**. **Não** traduza toda a suíte unitária para Gherkin — o custo supera o benefício. Reserve Gherkin para **cenários de aceitação de alto valor**.

---

## Exercício 5 — Quando NÃO fazer TDD?

**Enunciado:**

Liste **3 situações** onde TDD **não** é a melhor ferramenta, e explique por quê.

### Resolução

1. **Spikes e prototipação descartável.** Quando o código existe para você **aprender** se uma abordagem funciona — uma POC, um spike de 2 horas — o objetivo é **velocidade de descoberta**, não qualidade estrutural. TDD aqui atrapalha. Regra: **spike, jogue fora, depois reescreva com TDD**.

2. **UI visual / experiência do usuário.** Testar que "o botão azul está no lugar certo" via TDD é caro e frágil. Testes de componente têm valor, mas **não** dirigem design. Use teste visual (snapshot) ou inspeção manual para UI pura.

3. **Bibliotecas de thin wrapper / plumbing trivial.** Um adapter que só traduz `dict` para dataclass, sem lógica, tem **baixíssimo risco** e alto custo relativo de TDD. Teste com um ou dois casos e pare.

**Adicionalmente:**

- Em **bugs de infraestrutura** (configuração de SO, Kubernetes) TDD não se aplica — embora o caso de reproduzir o bug em um teste de integração antes de consertar seja ouro.

> **Pragmatismo:** TDD é **ferramenta**, não religião. Use onde agrega; reconheça quando não agrega. **Mas o default deve ser TDD em lógica de domínio**, porque é exatamente ali que os bugs caros da MediQuick moram.

---

## Exercício 6 — Diagnóstico aplicado à MediQuick

**Enunciado:**

A CTO da MediQuick pergunta: *"TDD resolve meu problema de cobertura de 15%?"*. Responda em **4 a 5 frases**, com nuance.

### Resolução (exemplo de resposta)

> TDD **aumenta naturalmente a cobertura** porque cada comportamento novo começa como teste — mas sozinho **não resolve** o problema de 15% porque **seu passivo atual** (código já escrito sem teste) continua sem cobertura. A estratégia precisa combinar **TDD para código novo** + **caracterização** (escrever testes pós-hoc para módulos críticos legados, priorizando por risco: agendamento e prescrição primeiro) + **quality gate no CI** que barre PRs que **diminuam** a cobertura. Adicionalmente, TDD ataca um problema mais grave que cobertura: a cultura do **mockismo selvagem** (sintoma 9) — TDD feito corretamente **expõe acoplamento alto** e força refatoração, gerando código mais testável a médio prazo. Em 3 meses, com TDD + caracterização + quality gate, é realista chegar de 15% para 50 a 60% nos módulos críticos; os 80% da meta são objetivo de 6 a 9 meses.

Essa resposta:

- Reconhece o valor do TDD **sem ser dogmática**.
- Diferencia **código novo** de **legado**.
- Cita **combinação de estratégias**, não solução única.
- Aponta uma meta **realista no tempo**, não "TDD resolve tudo".

---

## Próximo passo

Siga para o **[Bloco 3 — Quality Gates, cobertura e shift-left](../bloco-3/03-quality-gates.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — TDD, BDD e o Ciclo Red-Green-Refactor](02-tdd-bdd.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Bloco 3 — Quality Gates, Cobertura e Shift-Left](../bloco-3/03-quality-gates.md) |

<!-- nav:end -->

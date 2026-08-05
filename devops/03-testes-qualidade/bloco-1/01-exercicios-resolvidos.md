# Exercícios Resolvidos — Bloco 1

**Tempo estimado:** 25 a 35 minutos.

Estes exercícios exigem leitura prévia do [Bloco 1 — Pirâmide de testes](01-piramide-testes.md). Tente responder antes de ler a resolução.

---

## Exercício 1 — Classificando níveis de teste

**Enunciado:**

Para cada descrição, indique o **nível de teste** (Unit / Integration / E2E / Contract / Smoke / Teste manual) mais apropriado:

1. Verifica se a função `calcular_valor_consulta(plano, convenio)` retorna o preço correto.
2. Abre o navegador, faz login como paciente, agenda uma consulta e confirma que ela aparece no dashboard.
3. Verifica se o `AgendamentoRepo` grava a consulta no banco Postgres e lê de volta corretamente.
4. Após um deploy em staging, roda 5 requisições contra a raiz do serviço para ver se responde 200.
5. Dois serviços (Agendamento e Notificação) concordam sobre o formato do evento `consulta_agendada` que trafega via fila.
6. Um QA executa manualmente um fluxo que envolve fax, telefone e impressora médica.

### Resolução

| # | Descrição | Nível | Justificativa |
|---|-----------|-------|---------------|
| 1 | `calcular_valor_consulta` isolada | **Unit** | Função pura, sem I/O. Rápida, determinística. |
| 2 | Login + agendamento via navegador | **E2E** | Atravessa todo o sistema (UI, API, banco). |
| 3 | Repo gravando no Postgres real | **Integração** | Código + dependência externa (banco). |
| 4 | Health check 5 requisições pós-deploy | **Smoke** | Conjunto mínimo para validar "serviço sobe". |
| 5 | Evento entre 2 serviços (formato) | **Contract** | Testa o contrato de integração (Pact, etc.). |
| 6 | Fluxo envolvendo hardware físico não-automável | **Teste manual** | Quando automação é impossível ou desproporcional, teste manual **ainda é legítimo** — mas escolhido por necessidade, não por omissão. |

---

## Exercício 2 — Identificando o anti-padrão

**Enunciado:**

Três times descreveram suas suítes:

- **Time A:** 1000 testes unitários (rodam em 30s), 120 de integração (rodam em 3 min), 15 E2E (rodam em 5 min).
- **Time B:** 80 testes unitários, 30 de integração, 450 E2E que rodam em 1h15min; QA revisa manualmente mais 20 cenários.
- **Time C:** 600 testes unitários, 20 de integração, 200 E2E.

Para cada time, identifique o padrão/anti-padrão.

### Resolução

| Time | Diagnóstico | Análise |
|------|-------------|---------|
| **A** | **Pirâmide saudável** | Base larga rápida, meio razoável, topo estreito. Total roda em < 10 min — aceitável para CI. |
| **B** | **Ice Cream Cone** | Topo gigante + camada manual em cima. Suíte lenta (mais de 1h), flaky provável. **É o padrão MediQuick.** |
| **C** | **Hourglass** | Base boa, **meio crítico** (apenas 20 de integração). Risco: bugs de integração passam despercebidos. Preocupação específica se os serviços têm várias integrações (banco, filas, APIs). |

---

## Exercício 3 — F.I.R.S.T. na prática

**Enunciado:**

O teste abaixo falha aleatoriamente. Identifique **quais princípios F.I.R.S.T.** ele viola e reescreva corrigindo.

```python
def test_consulta_esta_no_futuro():
    consulta = Consulta(
        id=1,
        paciente_email="a@x.com",
        data_hora=datetime.now() + timedelta(hours=1),
    )
    time.sleep(2)
    assert consulta.data_hora > datetime.now()
```

### Resolução

**Violações:**

- **F (Fast):** `time.sleep(2)` — adiciona 2s gratuitos a cada rodada.
- **R (Repeatable):** depende de `datetime.now()` em dois pontos com intervalo entre eles. Comportamento varia com latência de execução.
- **S (Self-validating):** o assert passa/falha, ok — não viola aqui.
- **I, T:** não aplicáveis diretamente.

**Versão corrigida:**

```python
def test_consulta_mantem_data_hora_futura_em_relacao_a_agora_injetado():
    agora = datetime(2026, 1, 15, 9, 0, 0)
    uma_hora_depois = agora + timedelta(hours=1)

    consulta = Consulta(id=1, paciente_email="a@x.com", data_hora=uma_hora_depois)

    assert consulta.data_hora > agora
```

**Princípios aplicados:**

- **Injeção de tempo** — `agora` vira parâmetro explícito (ou atributo da classe). Zero dependência de `datetime.now()`.
- **Sem `sleep`** — teste roda instantâneo.
- **Determinístico** — roda igual em qualquer máquina, a qualquer hora, offline.

---

## Exercício 4 — Escolhendo o test double certo

**Enunciado:**

Dado o código abaixo:

```python
class CobrancaService:
    def __init__(self, gateway_pagamento, logger, repo_consulta):
        self.gateway = gateway_pagamento
        self.logger = logger
        self.repo = repo_consulta

    def cobrar(self, consulta_id: int, valor: float) -> bool:
        consulta = self.repo.buscar(consulta_id)
        sucesso = self.gateway.processar(consulta.paciente_cartao, valor)
        self.logger.info(f"Cobrança id={consulta_id} sucesso={sucesso}")
        return sucesso
```

Para cada dependência, indique o **test double mais apropriado** e justifique:

1. `gateway_pagamento` (API externa paga, ~200 ms por chamada).
2. `logger` (stdout, muito simples).
3. `repo_consulta` (acesso a Postgres em produção).

### Resolução

| Dep. | Test double | Justificativa |
|------|-------------|----------------|
| `gateway_pagamento` | **Stub** (ou Mock, se quiser verificar interação) | Forçar caminho "sucesso" e "falha" sem chamar API real. Mock seria usado **se** você quisesse assegurar que `processar()` foi chamado com o cartão certo. |
| `logger` | **Dummy** (ou nem teste double) | O teste não liga para log; passe um `Mock()` sem configurar. Se `None` fosse aceito, seria dummy. |
| `repo_consulta` | **Stub** ou **Fake** | Stub retorna uma `consulta` fixa. Fake seria um `RepoEmMemoria` (mais reutilizável se vários testes precisam). |

**Exemplo com pytest-mock:**

```python
def test_cobrar_delega_valor_ao_gateway(mocker):
    gateway = mocker.Mock()
    gateway.processar.return_value = True
    repo = mocker.Mock()
    repo.buscar.return_value = Consulta(id=1, paciente_cartao="4111...", paciente_email="a@b")
    logger = mocker.Mock()

    service = CobrancaService(gateway, logger, repo)
    resultado = service.cobrar(consulta_id=1, valor=120.0)

    assert resultado is True
    gateway.processar.assert_called_once_with("4111...", 120.0)
```

### Anti-padrão a evitar

**Não mockar** `CobrancaService` em si — é o **SUT** (System Under Test). Se você mockasse `self.gateway.processar` **de dentro do próprio service**, o teste passaria sempre e não provaria nada.

---

## Exercício 5 — Reescrevendo um teste ruim

**Enunciado:**

O teste abaixo foi extraído do repositório da MediQuick (versão simplificada). Liste **pelo menos 4 problemas** e reescreva.

```python
import requests, json, datetime

def test_tudo():
    # primeiro cria paciente
    r = requests.post("http://staging/api/pacientes", json={"nome":"Ana"})
    assert r.status_code == 201
    pid = r.json()["id"]
    # agora agenda
    r = requests.post("http://staging/api/agendamento", json={"paciente":pid,"data":str(datetime.datetime.now()+datetime.timedelta(days=1))})
    assert r.status_code in (200, 201)
    # cancela
    aid = r.json()["id"]
    r = requests.delete(f"http://staging/api/agendamento/{aid}")
    # verifica
    r = requests.get(f"http://staging/api/agendamento/{aid}")
    assert "cancelada" in r.text
```

### Resolução

**Problemas identificados:**

1. **Depende de ambiente externo** (`http://staging`) — viola **Repeatable**. Teste não roda offline; quebra se staging cair.
2. **Um teste fazendo tudo** ("test_tudo") — se falhar, você não sabe onde. Viola boa prática de "um teste, um comportamento".
3. **Não limpa estado** — cada rodada cria paciente novo, polui banco de staging.
4. **Usa `datetime.now()`** — tempo real em staging; viola Repeatable.
5. **Assert frágil** — `assert "cancelada" in r.text` pega qualquer ocorrência dessa string, mesmo em mensagem de erro.
6. **Nome ruim** — `test_tudo` não explica o comportamento testado.
7. **Sem `response.raise_for_status()`** — se DELETE retornar 500, o teste continua.
8. **Acoplamento a campos internos** (`id`, `paciente`) — se API mudar o nome, todos os testes quebram.

**Versão corrigida** (teste unitário de regra de negócio, não E2E):

```python
from datetime import datetime, timedelta

import pytest


def test_cancelar_consulta_com_24h_de_antecedencia_marca_como_cancelada():
    agora = datetime(2026, 1, 15, 9, 0, 0)
    amanha = agora + timedelta(days=1)
    consulta = Consulta(id=1, paciente_email="a@b.com", data_hora=amanha)

    consulta.cancelar(agora=agora)

    assert consulta.cancelada is True
```

Se **precisar** testar o fluxo de ponta a ponta, isso vira **um** teste E2E dedicado (topo da pirâmide) — com ambiente efêmero, setup/teardown e **poucas** interações.

---

## Exercício 6 — Desafiador (opcional)

**Enunciado:**

Um engenheiro argumenta: *"100% de cobertura garante que o software funciona."* Avalie a afirmação.

### Resolução

A afirmação é **falsa** em duas dimensões:

1. **Cobertura mede linhas executadas, não comportamento validado.** Um teste que **executa** todo o código mas **não verifica nada** (sem asserts significativos) dá 100% de cobertura e não garante nada. Exemplo:

```python
def test_parece_testar_mas_nao_testa(mocker):
    service = CobrancaService(mocker.Mock(), mocker.Mock(), mocker.Mock())
    service.cobrar(1, 100)
    assert True  # roda tudo, verifica nada
```

2. **Cobertura não mede qualidade do oracle de teste.** Mesmo com asserts, você pode estar verificando apenas caminhos triviais. A métrica complementar é **mutation testing** — modifica o código e verifica se o teste detecta.

Além disso, **100%** é caro. Para código crítico (checkout, agendamento da MediQuick), **sim**. Para código de plumbing (adapters simples), o custo supera o benefício. **70 a 85% bem distribuído nos caminhos críticos** supera 100% superficial.

> **Referência:** Fowler, em "Test Coverage" ([martinfowler.com/bliki/TestCoverage.html](https://martinfowler.com/bliki/TestCoverage.html)): *"coverage analysis is useful to find untested parts of code, but says little about the quality of your testing."*

---

## Próximo passo

Siga para o **[Bloco 2 — TDD, BDD e ciclo Red-Green-Refactor](../bloco-2/02-tdd-bdd.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — Pirâmide de Testes e Fundamentos](01-piramide-testes.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Bloco 2 — TDD, BDD e o Ciclo Red-Green-Refactor](../bloco-2/02-tdd-bdd.md) |

<!-- nav:end -->

# Entrega Avaliativa do Módulo 3

**Módulo:** Testes Automatizados e Qualidade de Software (5h)
**Cenário:** MediQuick — ver [00-cenario-pbl.md](00-cenario-pbl.md)

---

## Objetivo da entrega

Produzir um **repositório GitHub** contendo uma **pequena aplicação Python** (já fornecida nos exercícios progressivos — o serviço de **Agendamento** da MediQuick) com uma **suíte de testes completa e um pipeline CI com quality gates**.

Diferente do Módulo 1 (relatório conceitual) e do Módulo 2 (pipeline + estratégia), o Módulo 3 entrega **código funcionando**: testes reais, cobertura medida, pipeline barrando código de baixa qualidade.

---

## O que entregar

### 1. Repositório GitHub com a aplicação + testes

Repositório (público ou privado com acesso ao professor) contendo:

```
mediquick-agendamento/
├── src/
│   └── agendamento/
│       ├── __init__.py
│       ├── model.py            # entidades de domínio
│       ├── repo.py             # acesso a dados
│       └── service.py          # regras de negócio
├── tests/
│   ├── unit/                   # testes unitários (rápidos, isolados)
│   ├── integration/            # testes de integração (com Postgres real)
│   └── e2e/                    # 1 a 3 testes E2E de fluxo crítico
├── .github/workflows/
│   └── ci.yml                  # pipeline com quality gates
├── pyproject.toml ou setup.cfg
├── requirements.txt
├── requirements-dev.txt
├── ruff.toml ou pyproject [tool.ruff]
└── README.md                   # instruções de setup e execução
```

### 2. Suíte de testes com proporção de pirâmide

Seus testes **precisam seguir a pirâmide**:

- **≥ 20 testes unitários** — rápidos (< 1s cada), sem rede, sem banco.
- **4 a 8 testes de integração** — com Postgres real via Testcontainers.
- **1 a 3 testes E2E** — fluxo crítico de ponta a ponta (pode ser via cliente HTTP `httpx`).

Pelo menos **2 dos testes unitários devem ter sido escritos em TDD** (commits mostrando o ciclo Red-Green-Refactor — ver seção "Como comprovar TDD" abaixo).

### 3. Quality gates no pipeline CI

O arquivo `.github/workflows/ci.yml` deve ter **todos** os gates abaixo:

| Gate | Falha se... | Ferramenta |
|------|-------------|------------|
| **Linter** | Existe warning/erro de lint | `ruff` |
| **Formatação** | Código não está formatado | `ruff format --check` |
| **Testes unitários** | Algum teste unit falha | `pytest tests/unit` |
| **Cobertura** | Cobertura global abaixo do mínimo estabelecido (ex.: 70%) | `pytest-cov` com `--cov-fail-under` |
| **Testes de integração** | Algum teste de integração falha | `pytest tests/integration` (em job separado com serviço de Postgres) |
| **Complexidade** | Alguma função com complexidade ciclomática > limiar (ex.: 10) | `radon cc` |

### 4. Documento curto (1 a 2 páginas)

`docs/estrategia-de-testes.md` explicando:

1. **Proporções escolhidas** (quantos testes em cada camada) e **por quê**.
2. **Escolha do threshold de cobertura** (por que 70%, 80%, etc.) e argumentação sobre os **riscos da métrica** (Lei de Goodhart).
3. **Estratégia de test double** — onde usou mock, stub, fake; e **o que evitou mockar** e por quê.
4. **Como o time atacaria os sintomas da MediQuick** — quais dos 10 sintomas seu repositório resolve e quais ficam para outros módulos.
5. **Referências** — pelo menos 2 obras da pasta `books/` + Fowler (TestPyramid) obrigatoriamente.

---

## Critérios de avaliação

| Critério | Peso | O que se espera |
|----------|------|------------------|
| **Pirâmide respeitada** | 15% | Proporção correta, justificada no documento. |
| **Qualidade dos testes unitários** | 20% | F.I.R.S.T.: rápidos, independentes, repetíveis, auto-verificáveis, com oracle claro. |
| **Testes de integração reais** | 15% | Usam Testcontainers ou similar; exercitam o Postgres de verdade. |
| **Pipeline com gates funcionais** | 20% | Todos os gates listados; pipeline falha corretamente quando qualquer gate reprova (inclua um commit com falha proposital e link para o run falho no README). |
| **Uso correto de test doubles** | 10% | Mock onde fazia sentido; não mockou o SUT; sem over-mocking. |
| **Evidência de TDD** | 10% | Pelo menos 2 features com commits mostrando ciclo Red → Green → Refactor. |
| **Documento de estratégia** | 10% | Argumentação consistente, cita referências, reconhece limites. |

---

## Como comprovar TDD

TDD é um processo, não um resultado — o código final parece igual a código sem TDD. Por isso, a comprovação vem do **histórico git**:

**Sugestão:** para pelo menos **2 features**, crie **3 commits sequenciais**:

1. `test(agendamento): RED — adiciona teste de cancelamento com menos de 2h de antecedência` — commit que **apenas adiciona o teste** e **não faz ele passar**.
2. `feat(agendamento): GREEN — bloqueia cancelamento com menos de 2h de antecedência` — mínimo código que faz o teste passar.
3. `refactor(agendamento): extrai política de cancelamento em classe dedicada` — melhora do design sem mudar comportamento; teste continua passando.

Inclua no README do projeto um **link para esses 3 commits** como prova.

---

## Formato e prazo

- **Formato:** link do repositório GitHub + arquivo `docs/estrategia-de-testes.md` dentro dele.
- **README** deve conter:
  - Instruções de setup (venv, pip install).
  - Como rodar cada tipo de teste.
  - Link para os commits de TDD.
  - Link para um run do pipeline que **passou** e outro que **falhou** (pode ser um branch propositalmente quebrado).
- **Prazo:** conforme definido pelo professor — sugestão: **1 semana após o encerramento do módulo**.

---

## Dicas

- **Comece do exercício progressivo Parte 2** — ele já entrega um esqueleto de aplicação da MediQuick. Você evolui a partir dele.
- **Use `pytest-cov` com `--cov-branch`** — cobertura de branch é mais reveladora que só de linhas.
- **Rode `ruff` antes de commitar** (configure um pre-commit hook se conseguir).
- **Não persiga cobertura de 100%** — vai levar você a testar o trivial e ignorar o difícil. **70 a 85%** bem distribuído é melhor que 100% superficial.
- **Teste os caminhos críticos primeiro** — na MediQuick, "agendamento duplicado" é catastrófico; "tela de perfil" não.
- **Admita limites no documento** — se o Playwright E2E não coube no tempo, explique.

---

## Referência rápida do módulo

- [Cenário PBL — MediQuick](00-cenario-pbl.md)
- [Bloco 1 — Pirâmide de testes](bloco-1/01-piramide-testes.md)
- [Bloco 2 — TDD, BDD e Red-Green-Refactor](bloco-2/02-tdd-bdd.md)
- [Bloco 3 — Quality Gates](bloco-3/03-quality-gates.md)
- [Bloco 4 — Integração e E2E](bloco-4/04-integracao-e2e.md)
- [Exercícios progressivos](exercicios-progressivos/)
- [Referências bibliográficas](referencias.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Reflexão e Plano MediQuick](exercicios-progressivos/parte-5-reflexao-plano.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](README.md) | **Próximo →**<br>[Referências Bibliográficas — Módulo 3](referencias.md) |

<!-- nav:end -->

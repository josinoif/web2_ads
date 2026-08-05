# Exercícios Resolvidos — Bloco 3

**Tempo estimado:** 30 a 40 minutos.

---

## Exercício 1 — Shift-left na MediQuick

**Enunciado:**

Um time da MediQuick adota o seguinte fluxo:

1. Dev escreve código.
2. Dev commita direto em `main`.
3. CI roda lint.
4. QA testa manualmente em staging (3 dias).
5. Vai para produção.

Identifique **em que estágio o bug é detectado** em cada caso e estime o **custo relativo** de corrigir:

- (a) Erro de estilo/import não usado (`import os` que não é usado).
- (b) Função quebrada por typo (`return Non` em vez de `return None`).
- (c) Bug de regra de negócio (cancelamento permitido após 1h em vez de 2h).
- (d) Erro de integração (query SQL inválida no banco real).

### Resolução

| Caso | Onde é detectado (hoje) | Custo relativo | Para onde poderíamos mover? |
|------|--------------------------|----------------|------------------------------|
| (a) Import não usado | CI (lint) | **10x** | Editor (IDE com `ruff`) → **1x** |
| (b) Typo `Non` | **Staging manual** (se tiver sorte) ou **produção** | **15–30x+** | Unit test ou lint (mypy) → **1–10x** |
| (c) Bug de regra | **Produção** (paciente reclama) | **100–1000x** | Unit test com TDD → **1x** |
| (d) SQL inválido | **Produção** (erro de banco) | **100x** | Teste de integração → **10x** |

**Ação prática:** deslocar detecção via **pre-commit** (lint + unit rápido) e **CI** (unit + integração). Staging manual deixa de ser primeira linha.

---

## Exercício 2 — Construindo a configuração de quality gates

**Enunciado:**

A MediQuick quer um pipeline "starter pack" com gates **leves** (para introduzir sem trauma). Escreva o que entra em cada arquivo:

- `pyproject.toml` — configuração do ruff com regras E, F, I; e pytest-cov com fail_under começando em 20.
- `.github/workflows/ci.yml` — 3 gates: lint, teste unitário, cobertura mínima.

### Resolução

**`pyproject.toml`:**

```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 20
show_missing = true
```

**`.github/workflows/ci.yml`:**

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - run: pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint
        run: ruff check .

      - name: Unit tests + coverage
        run: |
          pytest tests/unit \
            --cov=src --cov-branch \
            --cov-report=term-missing \
            --cov-fail-under=20
```

**Por que começar leve:**

- `fail_under=20` é um **ponto de partida real** dado os 15% da MediQuick. Qualquer PR que não diminua **já é vitória**.
- Só 3 gates — o time não é sobrecarregado. Gates adicionais (format, radon, bandit) entram em ondas.

---

## Exercício 3 — Interpretando relatório de cobertura

**Enunciado:**

Dado o relatório abaixo, responda:

```
Name                         Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/agendamento/consulta.py     50      5   90%    45-49
src/agendamento/paciente.py     30     15   50%    22-27, 35-42
src/agendamento/notif.py         8      0  100%
src/agendamento/billing.py      80     40   50%    50-89
------------------------------------------------------------
TOTAL                          168     60   64%
```

1. A cobertura global é 64%. Passa em um gate com `--cov-fail-under=70`?
2. Onde priorizar esforço?
3. `notif.py` tem 100%. Isso garante que não tem bug?

### Resolução

1. **Não passa.** `--cov-fail-under=70` é global; 64% < 70%. Pipeline falha.

2. **Prioridade:**
   - **`consulta.py` — 90% e faltam 45-49**: ver o que há nessas linhas. Se for path de erro raro, aceitável. Se for lógica de negócio, **testar**.
   - **`paciente.py` e `billing.py` — 50%**: candidatos óbvios. Entre eles, **qual é mais crítico**? Se a MediQuick tem incidentes em cobrança (sintoma 7 — cobrança dupla), `billing.py` vem **primeiro**.
   - Estratégia: atacar `billing.py` primeiro via **caracterização** (criar testes que documentam o comportamento atual, antes de mudar); depois `paciente.py`.

3. **Não garante.** `notif.py` tem 100% **line coverage**, mas:
   - Pode não ter **branch coverage** — `if/else` onde só um ramo é testado.
   - Pode ter testes **sem asserts reais** (ver Exercício 4 abaixo).
   - **Mutation testing** em `notif.py` provavelmente revelaria mutações sobreviventes.

---

## Exercício 4 — Detectando teste cosmético

**Enunciado:**

Dado o código e teste abaixo, qual a cobertura resultante? E o que está errado?

```python
# src/desconto.py
def calcular_desconto(plano: str, cupom: str | None = None) -> float:
    if plano == "BASICO":
        desc = 0.0
    elif plano == "PREMIUM":
        desc = 0.10
    else:
        desc = 0.05

    if cupom == "BEMVINDO":
        desc += 0.05

    return min(desc, 0.30)
```

```python
# tests/test_desconto.py
from desconto import calcular_desconto

def test_cobre_tudo():
    calcular_desconto("BASICO")
    calcular_desconto("PREMIUM")
    calcular_desconto("OUTRO")
    calcular_desconto("PREMIUM", "BEMVINDO")
    assert True  # pra parecer teste
```

### Resolução

- **Cobertura:** ~100% de linhas (`cov`) e ~100% de branches. Todas as linhas executam.
- **Problema fundamental:** o teste **não valida** o resultado. `assert True` sempre passa. Se você trocar `desc = 0.10` por `desc = 999.0`, **nenhum teste falha**.

**Diagnóstico por mutation testing:** rodando `mutmut` nesta função:
- Trocar `0.10` por `-0.10` — **mutação sobrevive** (nenhum teste morre).
- Trocar `min` por `max` — **mutação sobrevive**.
- Remover `+= 0.05` — **mutação sobrevive**.

**Mutation score ≈ 0%** — a cobertura era **cosmética**.

**Teste corrigido:**

```python
from desconto import calcular_desconto


def test_plano_basico_nao_tem_desconto():
    assert calcular_desconto("BASICO") == 0.0


def test_plano_premium_tem_10_por_cento():
    assert calcular_desconto("PREMIUM") == 0.10


def test_plano_desconhecido_tem_5_por_cento():
    assert calcular_desconto("OUTRO") == 0.05


def test_cupom_bemvindo_soma_5_por_cento_ao_plano():
    assert calcular_desconto("PREMIUM", cupom="BEMVINDO") == 0.15


def test_desconto_maximo_e_30_por_cento():
    # forçando cenário hipotético: se tivessemos regra somando > 30%
    assert calcular_desconto("PREMIUM", cupom="BEMVINDO") <= 0.30
```

> **Moral:** cobertura alta **sem asserts fortes** é **pior** do que cobertura baixa — dá falsa sensação de segurança.

---

## Exercício 5 — Complexidade ciclomática

**Enunciado:**

Calcule a CC (aproximada) do seguinte código e discuta o que fazer:

```python
def processar_cancelamento(consulta, agora, usuario, motivo):
    if consulta.cancelada:
        return "ja cancelada"
    if consulta.data_hora - agora < timedelta(hours=2):
        if usuario.tipo == "admin":
            pass  # admin pode forçar
        else:
            return "antecedencia insuficiente"
    if usuario.plano == "BASICO" and motivo == "arrependimento":
        if consulta.paga:
            return "nao e reembolsavel"
    if consulta.telemedicina and consulta.iniciada:
        if usuario.tipo != "admin":
            return "ja iniciada"
    consulta.cancelada = True
    return "ok"
```

### Resolução

**Cálculo de CC** — conta decisões + 1:

- `if consulta.cancelada` → +1
- `if consulta.data_hora - agora < ...` → +1
- `if usuario.tipo == "admin":` → +1
- `if usuario.plano == "BASICO" and motivo == "arrependimento":` → +2 (o `and` conta)
- `if consulta.paga:` → +1
- `if consulta.telemedicina and consulta.iniciada:` → +2
- `if usuario.tipo != "admin":` → +1

**Total CC ≈ 10** — "razoável" no limite, já preocupante.

**Verificação com `radon`:**

```bash
radon cc -s processar_cancelamento.py
```

**O que fazer:**

1. **Extrair políticas** — a função tem 3 responsabilidades: antecedência, reembolso, estado. Uma função por política.
2. **Usar padrão de "early return"** para clareza.
3. **Exceções** em vez de strings: `AntecedenciaInsuficiente`, `NaoReembolsavel`, etc.

**Versão refatorada:**

```python
def processar_cancelamento(consulta, agora, usuario, motivo):
    if consulta.cancelada:
        return "ja cancelada"
    _verificar_antecedencia(consulta, agora, usuario)
    _verificar_reembolso(consulta, usuario, motivo)
    _verificar_estado(consulta, usuario)
    consulta.cancelada = True
    return "ok"


def _verificar_antecedencia(consulta, agora, usuario):
    if consulta.data_hora - agora >= timedelta(hours=2):
        return
    if usuario.tipo != "admin":
        raise AntecedenciaInsuficiente()


def _verificar_reembolso(consulta, usuario, motivo):
    cenario_de_arrependimento = (
        usuario.plano == "BASICO" and motivo == "arrependimento"
    )
    if cenario_de_arrependimento and consulta.paga:
        raise NaoReembolsavel()


def _verificar_estado(consulta, usuario):
    if consulta.telemedicina and consulta.iniciada and usuario.tipo != "admin":
        raise ConsultaJaIniciada()
```

Cada função tem **CC ≤ 4**. Total ainda é **10 no módulo**, mas **cada função é testável isoladamente** — e é isso que importa para o gate.

---

## Exercício 6 — Elaborando um plano de ratchet

**Enunciado:**

A MediQuick quer subir a cobertura de **15% para 70% em 9 meses** via ratchet. Proponha:

- Uma **curva de subida** mês a mês.
- Uma **justificativa** para o ritmo escolhido.
- **Uma alternativa** caso a curva linear não caiba no ritmo da equipe.

### Resolução

**Curva proposta (sugestão):**

| Mês | Threshold | Delta | Comentário |
|-----|-----------|-------|------------|
| 1 | 15% | — | Estabelece o **baseline**. Só não pode descer. |
| 2 | 20% | +5 | Começa ratchet. Fácil: alguns testes rápidos levam de 15 → 20. |
| 3 | 28% | +8 | Foco em testes unit de caminhos críticos. |
| 4 | 36% | +8 | Cobertura dos serviços de agendamento e prescrição. |
| 5 | 44% | +8 | Testes de integração entram. |
| 6 | 52% | +8 | Primeira auditoria de mutation testing nos módulos críticos. |
| 7 | 58% | +6 | Ritmo diminui — código legado crítico já coberto. |
| 8 | 64% | +6 | |
| 9 | 70% | +6 | Meta alcançada. |

**Justificativa do ritmo:**

- **Acelera no meio** (+8/mês nos meses 3–6) porque os **quick wins** (caminhos críticos, código recente) estão aí.
- **Desacelera perto da meta** (+6/mês nos meses 7–9) — cobrir os últimos 10 a 15% é sempre o mais difícil (código de erro, casos raros).
- **Respeita a capacidade do time** — 2 a 3 dias de sprint para testes é realista; mais vira opressão e a qualidade dos testes cai (Goodhart).

**Alternativa se o ritmo for insustentável:**

- **Métrica segmentada**: exigir 80% **só em diretórios críticos** (`/domain/agendamento/`, `/domain/prescricao/`), sem threshold no restante. Isso foca o esforço **onde importa**.
- **Ratchet por módulo**: cada módulo tem o próprio threshold, sobe no seu ritmo.
- **Freezing de legado**: código existente fica no nível atual; **código novo** obrigatoriamente 80%. Em 12–18 meses, o legado é substituído ou coberto oportunisticamente.

> **Princípio central:** ratchet **funciona** porque é **gradual e negociado**. Ratchet imposto ("80% amanhã!") leva a **gaming**: testes vazios, mocks que cobrem tudo, asserts `== True`. A Lei de Goodhart pune.

---

## Próximo passo

Siga para o **[Bloco 4 — Integração, E2E e estratégias](../bloco-4/04-integracao-e2e.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Quality Gates, Cobertura e Shift-Left](03-quality-gates.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Bloco 4 — Testes de Integração, E2E e Estratégias](../bloco-4/04-integracao-e2e.md) |

<!-- nav:end -->

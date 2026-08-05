# Exercícios Resolvidos — Bloco 3

Exercícios do Bloco 3 ([Estratégias de Release: Blue-Green, Canary, Rolling e Feature Flags](03-estrategias-release.md)).

---

## Exercício 1 — Escolher a estratégia certa

Para cada serviço, proponha **estratégia principal** e **justifique em 2 linhas**.

| # | Serviço | Características |
|---|---------|-----------------|
| a | Microserviço stateless de consulta, 500 req/s | — |
| b | Serviço que mantém **sessão de usuário** em memória | — |
| c | Serviço financeiro com compliance (SOX) | — |
| d | Worker que processa fila (consumer de RabbitMQ) | — |
| e | Serviço com ML — queremos validar acurácia nova contra antiga com 5% tráfego | — |

### Solução

| # | Estratégia | Justificativa |
|---|-----------|---------------|
| a | **Rolling** | Stateless, retrocompat fácil, baixo custo. Rolling do Kubernetes cobre bem. |
| b | **Blue-Green** + sticky sessions ou cache externo (Redis) | Durante rolling, sessões podem ir para pod novo e perder estado. Blue-Green permite **drenar** antes de chavear. |
| c | **Blue-Green** + aprovação manual | Compliance exige trilha de aprovação. Rollback instantâneo de Blue-Green protege cálculos financeiros. |
| d | **Canary por consumer group** ou **Rolling** | Worker não tem tráfego HTTP; chaveia quantos consumers da fila rodam nova versão. Combina bem com flag operacional para desligar nova versão. |
| e | **Canary** "de verdade" ou **Feature Flag percentual** com métrica customizada | Quer **dados estatísticos** com fração real de usuários — clássico caso de canary. |

---

## Exercício 2 — Debate: Blue-Green vs. Canary

Um colega argumenta: *"Blue-Green é sempre melhor que Canary porque o rollback é mais rápido"*. Responda em 4 a 6 linhas, usando argumentos técnicos do bloco.

### Solução

A afirmação é **parcialmente verdadeira** mas simplista. Blue-Green de fato tem **rollback em segundos** (rechaveia roteador), enquanto Canary leva alguns minutos para reverter. Porém:

1. Blue-Green **não detecta** bugs que só aparecem com **tráfego real e dataset real** — a versão Green é validada apenas com smoke test, então bugs estatísticos (0,3% dos requests) chegam a 100% dos usuários quando chavear.
2. Canary expõe **5-10% de usuários reais** à nova versão: isso **revela** bugs estatísticos antes de afetar todos.
3. Blue-Green custa **2× infra** enquanto ambos ambientes convivem. Canary custa ~1,05×.
4. Em sistemas grandes (milhares de instâncias), **Blue-Green é inviável** financeiramente. Canary é o padrão de fato.

Conclusão: Blue-Green é melhor **para rollback de emergência**; Canary é melhor **para detectar o problema antes**. Em produção madura, **combina-se** ambos: Rolling/Blue-Green para o deploy + Feature Flag percentual para a release.

---

## Exercício 3 — Implementar uma flag nova

A LogiTrack quer introduzir uma feature nova: **"Roteamento otimizado por IA"** que recalcula rotas em tempo real. Deve ser:

- Desligada por padrão.
- Liberável progressivamente por `transportadora_id`.
- Permitir **kill switch** imediato se algo sair do controle.

Adicione ao `features.py` do bloco.

### Solução

```python
# features.py (trecho — adicionar)

ROTEAMENTO_IA = FeatureFlag(
    name="roteamento_ia",
    default=False,
    tipo=FlagType.RELEASE,
    descricao="Recalcula rotas em tempo real usando modelo IA.",
    expira_em="2026-12-31",
)


def catalogo() -> list[FeatureFlag]:
    return [
        ESTIMATIVA_ML,
        CIRCUIT_BREAKER_BILLING,
        NOVA_UI_RASTREAMENTO,
        BETA_TRANSPORTADORA_PREMIUM,
        ROTEAMENTO_IA,
    ]
```

**Uso no código:**

```python
from features import ROTEAMENTO_IA, is_enabled


def calcular_rota(transportadora_id: int, origem: str, destino: str) -> Rota:
    subject = f"transportadora:{transportadora_id}"
    if is_enabled(ROTEAMENTO_IA, subject=subject):
        return rota_ia(origem, destino)
    return rota_heuristica(origem, destino)
```

**Liberação progressiva (operação):**

```bash
# 10% das transportadoras
export LOGITRACK_FLAG_ROTEAMENTO_IA_PERCENT=10

# crescer se OK
export LOGITRACK_FLAG_ROTEAMENTO_IA_PERCENT=30
export LOGITRACK_FLAG_ROTEAMENTO_IA_PERCENT=60
export LOGITRACK_FLAG_ROTEAMENTO_IA_PERCENT=100

# kill switch imediato (voltar para 0)
export LOGITRACK_FLAG_ROTEAMENTO_IA_PERCENT=0
```

**Por que `subject = "transportadora:X"`?** Porque liberação "por usuário" (package, request, etc.) mudaria **durante** a sessão da transportadora — experiência inconsistente. Usando `transportadora_id` como subject, toda a frota da **mesma transportadora** recebe o **mesmo tratamento**.

---

## Exercício 4 — Rolling com migration incompatível

Seu time está prestes a fazer **rolling update** de v1.0 para v1.1. A v1.1 introduz uma migration que **dropa a coluna `endereco_completo`** e divide em 3 colunas (`rua`, `numero`, `cidade`).

Durante o rolling, 2 pods rodam v1.0 (que ainda usa `endereco_completo`) e 2 pods rodam v1.1. **O que vai acontecer?** Como evitar?

### Solução

**O que vai acontecer:**

- Pods v1.1 aplicam a migration → `endereco_completo` não existe mais.
- Pods v1.0 seguem rodando e tentam **SELECT endereco_completo** → **500 Internal Server Error** em metade dos pods.
- Users reclamam. Ninguém sabe por quê.

**Como evitar: padrão Expand/Contract (Bloco 4 em detalhes).**

1. **Expand** (deploy N, mesma versão de código): adiciona as 3 novas colunas **mantendo** `endereco_completo`. Popula as novas a partir da velha. Versão antiga segue funcionando.
2. **Migrate** (deploy N+1): novo código **escreve** nas 3 novas E na velha. Lê das novas (com fallback).
3. **Contract** (deploy N+2): novo código só usa novas colunas. Migration dropa a velha.

A regra geral: **cada deploy individual é retrocompatível** com o imediatamente anterior. Migrations destrutivas só **depois** de confirmar que nenhuma versão ativa depende do que será destruído.

**Resposta curta:** migrations destrutivas **não podem** coincidir com deploy do código que as torna obsoletas. **Sempre 2 deploys separados** (expand, contract).

---

## Exercício 5 — Critérios de promoção canary

Você precisa escrever **critérios objetivos** para promover um canary automaticamente de 10% para 100% no serviço Tracking API. Proponha 4 critérios **quantitativos**.

Depois, escreva o **script** (pseudocódigo Python) que avalia e retorna True/False.

### Solução

**Critérios propostos:**

| # | Critério | Limite |
|---|----------|--------|
| 1 | Taxa de erros 5xx do canary | ≤ 1.2× da taxa do baseline (mesma janela) |
| 2 | Latência p95 do canary | ≤ 1.3× do p95 do baseline |
| 3 | Erro de negócio (ex.: "pacote recusado por schema") | ≤ baseline + 0.5% absoluto |
| 4 | Duração mínima da observação | ≥ 10 min e ≥ 10 000 requisições no canary |

**Pseudo-script:**

```python
from dataclasses import dataclass


@dataclass
class MetricasJanela:
    total_requests: int
    erro_5xx_taxa: float        # 0.0 - 1.0
    latencia_p95_ms: float
    erro_negocio_taxa: float    # 0.0 - 1.0


def canary_saudavel(
    canary: MetricasJanela,
    baseline: MetricasJanela,
    janela_segundos: int,
    limite_5xx: float = 1.2,
    limite_p95: float = 1.3,
    limite_negocio_abs: float = 0.005,  # +0.5%
    min_janela: int = 600,              # 10 min
    min_requests: int = 10_000,
) -> tuple[bool, list[str]]:
    motivos: list[str] = []

    if janela_segundos < min_janela:
        motivos.append(f"janela {janela_segundos}s < {min_janela}s")
    if canary.total_requests < min_requests:
        motivos.append(f"requests {canary.total_requests} < {min_requests}")

    if canary.erro_5xx_taxa > baseline.erro_5xx_taxa * limite_5xx:
        motivos.append(
            f"5xx {canary.erro_5xx_taxa:.4f} > {limite_5xx}× baseline {baseline.erro_5xx_taxa:.4f}"
        )
    if canary.latencia_p95_ms > baseline.latencia_p95_ms * limite_p95:
        motivos.append(
            f"p95 {canary.latencia_p95_ms:.1f} > {limite_p95}× baseline {baseline.latencia_p95_ms:.1f}"
        )
    if canary.erro_negocio_taxa > baseline.erro_negocio_taxa + limite_negocio_abs:
        motivos.append(
            f"erro_negocio {canary.erro_negocio_taxa:.4f} > baseline + {limite_negocio_abs:.4f}"
        )

    return (not motivos), motivos
```

**Uso no pipeline:**

```bash
python monitor_canary.py --canary=canary.json --baseline=baseline.json --janela=900
# exit 0 = promover; exit 1 = não promover, com motivos no stderr
```

**Nota importante:** em produção real, a coleta vem do Prometheus / Datadog. Aqui é a **lógica de decisão** — a coleta varia com o stack. O contratualmente importante: **decisão é automatizada**, não subjetiva.

---

## Exercício 6 — Limpar débito de flags

Ao vasculhar a LogiTrack, você encontra 14 feature flags. Descobre:

- **3 flags de release** com `expira_em` vencido há mais de 6 meses. Todas estão ligadas 100%.
- **2 flags de experimento** que ninguém lembra o que testam. Uma está ligada para 73% dos usuários.
- **5 flags operacionais** legítimas (kill switches).
- **2 flags de permissão** que na verdade são regras de negócio ("beta para premium").
- **2 flags novas** (< 1 mês).

Proponha um **plano em 4 passos** para limpar o débito.

### Solução

**Passo 1 — Remover as 3 flags de release vencidas (quick win)**

Se estão ligadas 100% há 6+ meses sem incidente, a feature estabilizou. Remoção é **mecânica**:

- Delete a flag do catálogo.
- Delete o `if is_enabled(...)` do código, mantendo o ramo "novo".
- Teste. Deploy.
- 1 PR por flag.

**Passo 2 — Decidir sobre as 2 flags de experimento**

- Se o experimento **concluiu**: tratar como flag de release vencida (Passo 1).
- Se **ninguém lembra**: o experimento está morto. Escolher o ramo preferido pela métrica de produto e remover.
- Uma flag em 73%? Quase certamente escolher o ramo novo (se estava ganhando) ou o antigo (se não) — **não deixar em 73%**.

**Passo 3 — Recategorizar as flags de "permissão"**

Flags que são **regras de negócio permanentes** ("transportadora premium vê X") **não deveriam** estar no mecanismo de feature flags — deveriam ser **modeladas** como feature/role no domínio.

- Mova para o modelo (ex.: `Transportadora.plano == 'premium'`).
- Remova da tabela de flags.

**Passo 4 — Instrumentar governança**

Para **evitar** o débito voltar:

- Toda flag nova **obrigatoriamente** tem `expira_em`.
- Job agendado no CI alerta quando `expira_em` passa.
- Retrospectiva mensal: "quais flags podem morrer?"
- Limite duro: nunca mais de **20 flags ativas** na plataforma.

**Resultado esperado após 4 semanas:**

- 14 flags → 7 flags (5 ops legítimas + 2 novas).
- Código mais simples.
- Complexidade cognitiva (ramos combinatórios) despenca.

---

## Próximo passo

- Revise o **[Bloco 3](03-estrategias-release.md)** se necessário.
- Avance para o **[Bloco 4 — Release Engineering, versionamento e rollback](../bloco-4/04-release-engineering.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Estratégias de Release: Blue-Green, Canary, Rolling e Feature Flags](03-estrategias-release.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](../README.md) | **Próximo →**<br>[Bloco 4 — Release Engineering: Versionamento, Migrations e Rollback](../bloco-4/04-release-engineering.md) |

<!-- nav:end -->

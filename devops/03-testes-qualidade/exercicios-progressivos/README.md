# Exercícios Progressivos — Módulo 3

Os exercícios progressivos são a **oficina** do módulo. Diferente dos exercícios de cada bloco (conceituais, curtos), aqui você **constrói software real** da MediQuick em **5 partes encadeadas**. Ao final, você terá um repositório pronto para a [entrega avaliativa](../entrega-avaliativa.md).

---

## Visão geral

```mermaid
flowchart LR
    P1[Parte 1<br/>Diagnóstico<br/>da pirâmide] --> P2[Parte 2<br/>TDD de feature<br/>de agendamento]
    P2 --> P3[Parte 3<br/>Integração<br/>Testcontainers]
    P3 --> P4[Parte 4<br/>Quality Gates<br/>no CI]
    P4 --> P5[Parte 5<br/>Reflexão +<br/>plano MediQuick]

    style P1 fill:#e3f2fd
    style P2 fill:#c8e6c9
    style P3 fill:#fff9c4
    style P4 fill:#bbdefb
    style P5 fill:#ffe0b2
```

| # | Título | Tempo | Entregável |
|---|--------|-------|------------|
| 1 | [Diagnóstico da pirâmide atual](parte-1-diagnostico-piramide.md) | 30 min | Análise escrita + diagrama |
| 2 | [TDD do serviço de Agendamento](parte-2-tdd-agendamento.md) | 1h 30min | Código + testes + 3 commits (Red-Green-Refactor) |
| 3 | [Integração com Testcontainers](parte-3-integracao-testcontainers.md) | 1h | Testes + conftest |
| 4 | [Quality Gates no pipeline CI](parte-4-quality-gates-ci.md) | 1h | `.github/workflows/ci.yml` + 1 PR falhando, 1 PR passando |
| 5 | [Reflexão e plano MediQuick](parte-5-reflexao-plano.md) | 30 min | Documento de estratégia (1 a 2 páginas) |

**Tempo total estimado:** ~4h 30min (dentro da carga do módulo de 5h).

---

## Pré-requisitos técnicos

- **Python 3.11+**
- **Git**
- **Docker** (para Parte 3 — Testcontainers)
- **GitHub** (para Parte 4 — Actions)
- Ambiente virtual Python configurado (ver [README principal](../README.md#setup-do-ambiente-uma-vez-por-máquina))

---

## Filosofia

Estes exercícios **não são avaliados isoladamente**; eles **constituem a entrega**:

- O **diagnóstico** (Parte 1) vira a seção "Análise da pirâmide atual" do documento de estratégia.
- O **código TDD** (Parte 2) é a base do repositório da entrega.
- Os **testes de integração** (Parte 3) compõem a camada de integração da suíte.
- O **pipeline** (Parte 4) é o `.github/workflows/ci.yml` da entrega.
- A **reflexão** (Parte 5) vira o corpo do documento de estratégia.

Você **pode** fazer as partes fora de ordem, mas a ordem apresentada **minimiza retrabalho**.

---

## Como usar este material

- Cada parte tem: **objetivo**, **passos detalhados**, **critérios de pronto** e **dicas/armadilhas comuns**.
- Há **espaço para exploração** — o tempo sugerido assume uma primeira tentativa; faça mais se quiser.
- **Commite frequentemente** — para a Parte 2, seus commits **são prova** do processo TDD.

---

## Próximo passo

Comece pela **[Parte 1 — Diagnóstico da pirâmide atual](parte-1-diagnostico-piramide.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios Resolvidos — Bloco 4](../bloco-4/04-exercicios-resolvidos.md) | **↑ Índice**<br>[Módulo 3 — Testes e qualidade de software](../README.md) | **Próximo →**<br>[Parte 1 — Diagnóstico da Pirâmide Atual da MediQuick](parte-1-diagnostico-piramide.md) |

<!-- nav:end -->

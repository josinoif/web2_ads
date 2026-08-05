# Parte 5 — Reflexão Final e Plano de Transformação em Ondas

**Duração:** 1 hora
**Pré-requisito:** Partes 1, 2, 3 e 4 concluídas. Todo o conteúdo dos 4 blocos lido.

---

## Objetivo

Consolidar todo o aprendizado do módulo em um **plano de transformação em ondas** para a CloudStore, e refletir criticamente sobre limites, riscos e trade-offs. Esta é a parte que **amarra o relatório** e prepara as seções 4 e 5 da entrega avaliativa.

---

## Atividades

### Atividade 1 — Plano de transformação em 3 ondas (35 min)

Elabore um **plano em 3 ondas** de transformação para a CloudStore, com horizontes:

- **Onda 1: 0 a 2 meses** — quick wins. Mudanças culturais e de processo **sem investimento alto**.
- **Onda 2: 2 a 4 meses** — automação básica e ferramental compartilhado. Liga ao Módulo 2 (CI) e Módulo 4 (CD).
- **Onda 3: 4 a 6 meses** — cultura madura + métricas DORA + observabilidade. Liga aos Módulos 8 e 10.

Para **cada onda**, preencha a tabela:

| Intervenção | O que muda (concreto) | Por que muda (qual sintoma ataca + qual princípio embasa) | Como medir sucesso | Custo estimado (baixo/médio/alto) |
|-------------|------------------------|------------------------------------------------------------|--------------------|-----------------------------------|
| (exemplo Onda 1) Daily Dev/Ops | Daily de 15 min às 9h30, terças e quintas, 2 de cada lado | Ataca sintomas 1 e 2 (silos). Princípio: Sharing (CALMS) e 2º Caminho (feedback). | Reduzir pelo menos 30% de tickets de "dúvida" entre times em 60 dias. | Baixo |
| ... | ... | ... | ... | ... |

**Requisitos do plano:**

- **Pelo menos 3 intervenções por onda** (9 no total).
- **Cada intervenção** deve citar **pelo menos 1 sintoma** da CloudStore e **1 princípio** (CALMS, Três Caminhos ou DORA).
- **Pelo menos 2 intervenções** citam **uma referência** da pasta `books/` (ex.: "seguindo o padrão de *blameless postmortem* descrito em Beyer et al., 2016, cap. 15").
- **Custo estimado** claro — a CTO vai perguntar.
- **Métrica de sucesso concreta** — não "melhorar a cultura", mas "aumentar Deployment Frequency de 2/mês para 5/mês".

### Atividade 2 — Ligação com os próximos módulos (10 min)

Marque, em sua tabela, quais intervenções da Onda 2 e 3 dependem explicitamente de **conceitos de módulos futuros** da disciplina:

| Intervenção | Módulo correspondente |
|-------------|-----------------------|
| Pipeline CI | Módulo 2 |
| Testes automatizados | Módulo 3 |
| Deploy automatizado / blue-green | Módulo 4 |
| Containers | Módulo 5 |
| Kubernetes | Módulo 6 |
| IaC | Módulo 7 |
| Observabilidade | Módulo 8 |
| DevSecOps | Módulo 9 |
| Métricas DORA maduras | Módulo 10 |

Mostre que você entende que o **Módulo 1 estabelece a cultura**, mas a **transformação técnica** vem nos módulos seguintes.

### Atividade 3 — Riscos, trade-offs e limites (15 min)

Escreva 3 parágrafos (um para cada pergunta):

1. **Risco cultural:** qual é o **maior risco** para o sucesso desse plano — mesmo se tecnicamente tudo for feito certo? (Dica comum: resistência de média gerência, medo de responsabilidade compartilhada, pressão por resultado imediato da diretoria.)

2. **Trade-off:** em **quais situações** a transformação DevOps pode **não valer a pena** para a CloudStore? (Dica comum: se o domínio de negócio mudar para algo altamente regulado, ou se a empresa entrar em modo "survival" sem espaço para investimento.)

3. **Limite:** há algum **problema** da CloudStore que **DevOps NÃO resolve**? Cite e explique. (Dica: problemas de produto/negócio, arquitetura mal dimensionada, débito técnico estrutural profundo — DevOps amplifica mas não cria valor de negócio.)

---

## Entregáveis desta parte

1. **Tabela do plano de 3 ondas** com pelo menos 9 intervenções.
2. **Tabela de ligação com módulos futuros**.
3. **Texto de riscos, trade-offs e limites** (3 parágrafos).

Esses artefatos formam as **seções 4 e 5** do relatório avaliativo.

---

## Rubrica de autoavaliação

- [ ] Cada intervenção cita **sintoma da CloudStore** + **princípio teórico**.
- [ ] Pelo menos **2 intervenções** citam **livro da pasta `books/`**.
- [ ] Cada intervenção tem **métrica de sucesso mensurável**.
- [ ] Reconheço **pelo menos um risco cultural** sério e proponho mitigação.
- [ ] Admito **pelo menos uma limitação** de DevOps — não vendi "bala de prata".

---

## Consolidação

Com as 5 partes prontas, você tem o material bruto completo do **Relatório de Transformação DevOps da CloudStore**. O próximo passo é **formatar o relatório final** seguindo a estrutura da [entrega-avaliativa.md](../entrega-avaliativa.md).

Sugestão de organização do relatório final:

- **Seção 1:** incorpore diretamente o diagrama de causas da Parte 1.
- **Seção 2:** incorpore a tabela CALMS + radar da Parte 2.
- **Seção 3:** incorpore os VSMs (atual e futuro) + análise da Parte 3.
- **Seção 4:** use o plano de ondas da Parte 5.
- **Seção 5:** use os riscos/trade-offs da Parte 5.
- **Anexos:** template de postmortem + postmortem preenchido (Parte 4).

---

## Palavra final do módulo

Você começou este módulo com **10 sintomas da CloudStore** e termina com um **plano concreto, fundamentado e realista** para transformá-la.

O próximo módulo — **[Módulo 2 — Versionamento, Automação e CI](../../02-versionamento-automacao-ci/)** — é onde parte do plano vira código. Mas guarde o aprendizado principal:

> **Pipeline, contêiner, Kubernetes e métrica DORA são *consequências* da cultura certa.**
> **Sem a cultura, as ferramentas ficam paradas na garagem.**

Bom trabalho.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 4 — Template de Postmortem Blameless](parte-4-postmortem-blameless.md) | **↑ Índice**<br>[Módulo 1 — Fundamentos e cultura DevOps](../README.md) | **Próximo →**<br>[Entrega Avaliativa do Módulo 1](../entrega-avaliativa.md) |

<!-- nav:end -->

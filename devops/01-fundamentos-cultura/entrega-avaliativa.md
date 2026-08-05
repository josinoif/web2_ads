# Entrega Avaliativa do Módulo 1

**Módulo:** Fundamentos de DevOps e Cultura (5h)
**Cenário:** CloudStore — ver [00-cenario-pbl.md](00-cenario-pbl.md)

---

## Objetivo da entrega

Produzir um **Relatório de Transformação DevOps para a CloudStore**, consolidando as análises feitas nos exercícios progressivos em um documento coeso que uma CTO real poderia ler e tomar decisões com base.

Diferente do Módulo 2 (que entrega artefatos técnicos — pipeline `.yml`), o Módulo 1 entrega um **artefato conceitual**: um relatório que demonstra que você **entende o problema** e sabe **justificar tecnicamente** uma proposta de mudança.

---

## O que entregar

### 1. Relatório de Transformação DevOps (artefato principal)

Documento em **Markdown** ou **PDF**, de 6 a 10 páginas, com a seguinte estrutura mínima:

#### Seção 1 — Diagnóstico da CloudStore (1 a 2 páginas)

- Identifique as **causas sistêmicas** (não individuais) dos 10 sintomas apresentados no cenário.
- Agrupe os sintomas em **categorias** (ex.: silos, falta de automação, falta de feedback, falta de métricas, cultura de culpa).
- Use um **diagrama Mermaid** (fluxograma ou mapa mental) para visualizar as relações entre causas e sintomas.

#### Seção 2 — Análise pelo modelo CALMS (1 a 2 páginas)

- Classifique cada um dos 10 sintomas em uma ou mais dimensões **CALMS** (Culture, Automation, Lean, Measurement, Sharing).
- Apresente uma **tabela** com: sintoma → dimensão(ões) afetada(s) → justificativa breve.
- Aponte em qual dimensão a CloudStore está **pior** e por quê.

#### Seção 3 — Análise pelos Três Caminhos (1 a 2 páginas)

- Identifique problemas de **Primeiro Caminho (Fluxo)**, **Segundo Caminho (Feedback)** e **Terceiro Caminho (Aprendizado)**.
- Inclua o **Value Stream Map** produzido na Parte 3 dos exercícios progressivos (imagem ou diagrama textual) com a identificação de gargalos.
- Calcule e apresente métricas de fluxo: **Lead Time estimado**, **% Activity Ratio** (tempo de trabalho efetivo / lead time total).

#### Seção 4 — Plano de Transformação (2 a 3 páginas)

Apresente um **plano em ondas de 3 a 6 meses**, com pelo menos **três ondas**:

- **Onda 1 (0 a 2 meses):** "Quick wins" — mudanças culturais e de processo de baixo custo (ex.: instituir postmortem blameless, criar Slack compartilhado Dev/Ops, instituir on-call rotativo com devs).
- **Onda 2 (2 a 4 meses):** Automação básica (conectar com Módulos 2 a 4 que virão — CI, testes, deploy).
- **Onda 3 (4 a 6 meses):** Métricas DORA + cultura madura (conectar com Módulo 10).

Para cada onda, especifique:

- **O que muda** (processo, ferramenta, ritual, métrica).
- **Por que muda** (qual sintoma da CloudStore isso resolve e qual princípio embasa — cite autor).
- **Como medir sucesso** (métrica quantitativa ou qualitativa).

#### Seção 5 — Riscos, Trade-offs e Limites (1 página)

- Quais são os **riscos culturais** da transformação? (ex.: resistência de Ops que perde "poder", medo de Dev em ser responsabilizado por produção).
- **Onde DevOps não é bala de prata?** (ex.: problema de domínio, arquitetura monolítica, regulação externa).
- O que você **não se comprometeu** a resolver neste plano e por quê?

#### Seção 6 — Referências

- Cite ao menos **3 obras** da pasta `books/` (ver [referencias.md](referencias.md)).
- Use o formato autor + obra + capítulo/seção.

---

### 2. Template de Postmortem Blameless (anexo)

Anexo ao relatório (pode ser arquivo separado): o **template de postmortem** produzido na Parte 4 dos exercícios progressivos, pronto para uso na CloudStore.

---

### 3. Value Stream Map (anexo)

Anexo ao relatório: o **VSM** produzido na Parte 3, com gargalos identificados.

---

## Critérios de avaliação

| Critério | Peso | O que se espera |
|----------|------|------------------|
| **Diagnóstico sistêmico** | 20% | Análise identifica causas estruturais, não culpa indivíduos. Diagrama Mermaid coerente. |
| **Aplicação correta de CALMS** | 15% | Cada sintoma corretamente classificado com justificativa. |
| **Aplicação dos Três Caminhos** | 15% | Problemas de fluxo, feedback e aprendizado identificados corretamente. VSM presente. |
| **Plano de transformação** | 25% | Plano em ondas, realista, com métricas de sucesso. Liga cada intervenção a um princípio teórico citado. |
| **Riscos e trade-offs** | 10% | Demonstra maturidade — reconhece limites e dificuldades. |
| **Qualidade da argumentação** | 10% | Texto claro, coeso, com citações corretas das obras. |
| **Anexos (postmortem + VSM)** | 5% | Completude e qualidade dos anexos. |

---

## Formato e prazo

- **Formato:** Markdown (`.md`) ou PDF. Se Markdown, pode ser entregue em repositório GitHub (o mesmo do módulo 2 ou um novo).
- **Nome do arquivo:** `relatorio-transformacao-cloudstore.md` (ou `.pdf`).
- **Prazo:** conforme definido pelo professor — sugestão: **1 semana após encerramento do módulo**.

---

## Dicas para uma boa entrega

- **Seja específico**: em vez de "melhorar comunicação", escreva "instituir daily de 15 min compartilhado entre tech leads de Dev e Ops nas quartas e sextas".
- **Conecte teoria e prática**: toda recomendação deve vir amarrada a um conceito do módulo (CALMS, Três Caminhos) e a um autor.
- **Evite "DevOps genérico"**: seu plano deve responder à **CloudStore**, não a uma empresa imaginária.
- **Diagramas contam pontos**: use Mermaid para causas → efeitos, VSM, fluxo antes/depois.
- **Não tenha medo de discordar**: se em algum ponto você acha que "DevOps puro" não cabe no contexto da CloudStore, argumente.

---

## Referência rápida do módulo

- [Cenário PBL — CloudStore](00-cenario-pbl.md)
- [Bloco 1 — O que é DevOps](bloco-1/01-o-que-e-devops.md)
- [Bloco 2 — Modelo CALMS](bloco-2/02-modelo-calms.md)
- [Bloco 3 — Os Três Caminhos](bloco-3/03-tres-caminhos.md)
- [Bloco 4 — Cultura em prática](bloco-4/04-cultura-pratica-antipadroes.md)
- [Exercícios progressivos](exercicios-progressivos/)
- [Referências bibliográficas](referencias.md)

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 5 — Reflexão Final e Plano de Transformação em Ondas](exercicios-progressivos/parte-5-reflexao-plano.md) | **↑ Índice**<br>[Módulo 1 — Fundamentos e cultura DevOps](README.md) | **Próximo →**<br>[Referências Bibliográficas — Módulo 1](referencias.md) |

<!-- nav:end -->

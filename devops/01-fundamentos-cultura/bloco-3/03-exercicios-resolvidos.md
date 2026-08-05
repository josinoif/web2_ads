# Exercícios Resolvidos — Bloco 3

**Tempo estimado:** 25 a 35 minutos.

Estes exercícios exigem leitura prévia do [Bloco 3 — Os Três Caminhos](03-tres-caminhos.md).

---

## Exercício 1 — Identificando o caminho afetado

**Enunciado:**

Para cada problema abaixo, identifique **qual dos Três Caminhos** ele mais afeta (Fluxo, Feedback ou Aprendizado) e justifique em uma linha:

1. Um bug que estava em produção há 3 semanas foi descoberto por um cliente.
2. Uma equipe tem 25 tickets simultaneamente em andamento.
3. Após um incidente grave, o postmortem focou em descobrir "quem fez o merge".
4. O deploy é feito numa janela fixa de sexta à noite, agrupando todas as mudanças da semana.
5. Dev não sabe que uma feature que escreveu está derrubando a API de pagamento em produção.
6. Um aprendizado importante foi documentado no Confluence de um time, mas os outros times desconhecem.

### Resolução

| # | Problema | Caminho | Justificativa |
|---|----------|---------|---------------|
| 1 | Bug descoberto por cliente 3 sem depois | **2º — Feedback** | Feedback lento e fraco; deveria ter vindo de monitoramento/alertas muito antes. |
| 2 | 25 tickets em paralelo | **1º — Fluxo** | WIP alto prejudica throughput (Lei de Little). |
| 3 | "Quem fez o merge?" | **3º — Aprendizado** | Cultura de culpa impede blameless postmortem → impede aprendizado. |
| 4 | Janela fixa de sexta | **1º — Fluxo** | Lote grande, fluxo bloqueado fora da janela; handoffs. |
| 5 | Dev não sabe de bug em prod | **2º — Feedback** | Informação de produção não volta a quem a produziu. |
| 6 | Aprendizado isolado em um time | **3º — Aprendizado** | Falha em converter aprendizado local em global (Sharing no CALMS). |

---

## Exercício 2 — Simulação prática do WIP

**Enunciado:**

Rode o script `simula_fluxo.py` do Bloco 3. Em seguida, **modifique o script** para:

(a) Acrescentar um cenário `Cenario("WIP ideal (WIP=1)", wip=1, capacidade_dia=2.0, overhead_switch=0.08)`.
(b) Mudar `SWITCH` para `0.0` (sem context switch) e rodar de novo. O que muda?
(c) Mantendo `SWITCH = 0.08`, qual WIP faz o throughput cair à metade?

### Resolução

(a) **WIP=1:**
- penalty = 0.08 × 0 = 0
- throughput = 2.0 × 1.0 = 2.0 tarefas/dia
- lead time = 1 / 2.0 = **0.5 dias**

(b) **Sem context switch (SWITCH=0):** throughput é sempre 2.0 para qualquer WIP. Ou seja, no modelo "ideal" sem custo de troca, o **throughput não cai**. O que ainda cresce é o **lead time** — pela Lei de Little, W = L/λ. Mesmo com throughput constante, **lead time cresce linear com WIP**. Esse é o argumento **puramente matemático** — mesmo sem o custo de troca de contexto, WIP alto = lead time alto.

(c) Queremos throughput = 1.0 (metade de 2.0).
- 2.0 × (1 - 0.08 × (WIP - 1)) = 1.0
- 1 - 0.08 × (WIP - 1) = 0.5
- 0.08 × (WIP - 1) = 0.5
- WIP - 1 = 6.25
- **WIP ≈ 7.25** (na prática, com 7 tarefas simultâneas o throughput já caiu pela metade)

### Lição aprendida

A simulação mostra que **mesmo sem context switch**, lead time cresce linear com WIP (Lei de Little). Com context switch, é **pior ainda** — não é linear, é **agravado**. Na CloudStore, reduzir o WIP é uma das intervenções de **baixo custo** e **alto impacto** imediato no fluxo.

---

## Exercício 3 — Andon Cord em software

**Enunciado:**

O conceito do **Andon Cord** em Toyota é que **qualquer operário** pode parar a linha de produção ao notar um defeito. Traduza este conceito para o contexto de uma equipe de software — **dê 3 exemplos** práticos do "Andon Cord digital".

### Resolução

Exemplos possíveis de "Andon Cord" em software:

1. **CI que bloqueia merges quando o build/teste está vermelho** — ninguém pode fazer merge até o build voltar a verde. Literalmente "parar a linha".

2. **Feature flag kill switch** — qualquer engenheiro pode desligar uma feature em produção em segundos se notar que ela está causando problemas, sem precisar de deploy de hotfix.

3. **Política de "qualquer um pode parar a release"** — se alguém do time (inclusive QA, dev júnior, SRE) tem **sinal amarelo**, a release é pausada até investigar. Sem hierarquia de veto.

4. **(bônus) Pipeline que recusa deploy com SLO abaixo do limiar** — se a métrica de disponibilidade do serviço está caindo, o próprio pipeline recusa novos deploys até estabilizar.

**Essência comum:** o poder de **interromper o fluxo** está distribuído, não concentrado em poucos. E a expectativa cultural é que, **quando alguém puxa a corda, isso é celebrado** — não punido.

---

## Exercício 4 — Diagnóstico da CloudStore pelos Três Caminhos

**Enunciado:**

Volte ao [cenário da CloudStore](../00-cenario-pbl.md). Identifique **2 sintomas** claramente relacionados a cada um dos Três Caminhos:

### Resolução

**Primeiro Caminho — Fluxo:**

- **Sintoma 3** — Deploys manuais em janela de sexta: lote grande + janela fixa bloqueia fluxo.
- **Sintoma 5** — "Releases agrupadas, semanas entre uma e outra": tamanho de lote grande + baixa frequência de deploy.

**Segundo Caminho — Feedback:**

- **Sintoma 4** — "Bugs aparecem em homologação": feedback tardio; deveria ter sido no CI.
- **Sintoma 7** — "Dev não tem acesso a log de produção": realimentação produção → dev cortada.
- (alternativa: Sintoma 9 — on-call só de Ops — dev não sente o impacto do que produz.)

**Terceiro Caminho — Aprendizado:**

- **Sintoma 6** — "Postmortem vira caça às bruxas": impede aprendizado organizacional.
- **Sintoma 10** — "O Roberto" (conhecimento concentrado): impede compartilhamento; sem sharing, aprendizado não escala.

**Observação:** alguns sintomas **cruzam** os três caminhos. Isso é esperado — **os caminhos são complementares**, não disjuntos.

---

## Exercício 5 — Segurança psicológica na prática

**Enunciado:**

Segurança psicológica é o fator #1 para o Terceiro Caminho (aprendizado). Liste **3 práticas concretas** (não declarações) que uma liderança pode adotar para **construir** segurança psicológica em um time.

### Resolução (exemplos)

1. **Reconhecer publicamente a própria falha primeiro.** A liderança admite que errou em uma decisão específica, em reunião aberta. Isso dá permissão para o resto do time fazer o mesmo.

2. **Separar a discussão de "o que aconteceu" da discussão de "quem foi".** No postmortem, **proibir** referências nominais na reconstrução de fatos ("o merge de X introduziu"). Usar "a alteração de config no arquivo Y" em vez de "João alterou isto".

3. **Celebrar falhas que geraram aprendizado.** Newsletter interna ou ritual de time onde se apresenta um aprendizado vindo de um erro, **sem punir** quem cometeu. Algumas empresas têm o "Failure of the Month" (Pivotal) ou "award do melhor aprendizado".

4. **(bônus) Ter um canal `#incident-learning` público** no Slack/Teams onde incidentes são discutidos abertos, em vez de em DMs privados entre gestores. A **transparência** desmonta medo de exposição.

5. **(bônus) Promover pessoas que **admitem não saber** e buscam ajuda.** Quando o modelo de promoção recompensa o "superman solitário", segurança psicológica morre.

---

## Exercício 6 — Desafiador (opcional)

**Enunciado:**

Uma empresa afirma: *"Não precisamos de Chaos Engineering — nosso sistema já sofre falhas reais o suficiente em produção."* Avalie criticamente.

### Resolução

A afirmação mistura dois conceitos distintos:

- **Falhas reais (não planejadas)** — aparecem nos piores momentos, sob pressão, com equipe despreparada. **Produzem medo, não aprendizado estruturado.**
- **Chaos Engineering (falhas controladas)** — injetadas em **momento escolhido**, em **ambiente preparado**, com a equipe observando como hipóteses. **Produz aprendizado com baixo custo.**

Ou seja: sofrer falhas reais **sem método** não substitui Chaos Engineering. Sofrer falha real ensina **pouco por muito** (alto custo, baixo aprendizado). Chaos Engineering ensina **muito por pouco** (custo controlado, aprendizado alto).

Além disso, Chaos Engineering permite **testar hipóteses específicas**: "o que acontece se a zona us-east-1 cair?". Uma falha real raramente te dá o **escopo exato** que você quer testar.

> **Leitura:** *Chaos Engineering* (Rosenthal & Jones, O'Reilly, 2020). Netflix introduziu Chaos Monkey em 2011 como ferramenta didática — hoje é padrão em empresas de alta maturidade.

---

## Próximo passo

Siga para o **[Bloco 4 — Cultura em prática e anti-padrões](../bloco-4/04-cultura-pratica-antipadroes.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Os Três Caminhos (The Three Ways)](03-tres-caminhos.md) | **↑ Índice**<br>[Módulo 1 — Fundamentos e cultura DevOps](../README.md) | **Próximo →**<br>[Bloco 4 — Cultura em Prática, Anti-padrões e Introdução às Métricas DORA](../bloco-4/04-cultura-pratica-antipadroes.md) |

<!-- nav:end -->

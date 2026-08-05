# Exercícios Resolvidos — Bloco 2

**Tempo estimado:** 25 a 35 minutos.

Estes exercícios exigem leitura prévia do [Bloco 2 — Modelo CALMS](02-modelo-calms.md).

---

## Exercício 1 — Classificação CALMS

**Enunciado:**

Classifique cada situação abaixo na(s) dimensão(ões) CALMS mais afetada(s):

1. Um time usa Jenkins para rodar testes automaticamente a cada commit.
2. A empresa não sabe quantos deploys fez no mês passado.
3. Todo bug descoberto em produção gera uma reunião onde se busca "o responsável".
4. Só um engenheiro da empresa conhece o schema do banco de dados legado.
5. Um deploy leva 4 horas porque tem 40 passos manuais.
6. Features terminadas ficam "prontas" por 3 semanas até serem agrupadas em release.
7. Dev e QA são times separados que se comunicam só por ticket.
8. Cada time escolhe sua ferramenta de CI; há 5 diferentes na empresa.

### Resolução

| # | Situação | Dimensão CALMS | Justificativa |
|---|----------|----------------|---------------|
| 1 | Jenkins rodando testes automáticos | **A** | Automação de processo repetitivo. |
| 2 | Não sabe quantos deploys fez | **M** | Ausência de medição; não pode melhorar o que não mede. |
| 3 | Reunião de "busca de culpado" | **C** | Cultura de culpa, fere segurança psicológica. |
| 4 | Só um conhece o banco legado | **S** | Concentração de conhecimento; falta compartilhamento. |
| 5 | Deploy de 4h em 40 passos | **A** + **L** | Toil (automação) e desperdício no fluxo (Lean). |
| 6 | Features "prontas" paradas 3 semanas | **L** | Muda tipo "estoque" (inventory) — acúmulo de risco. |
| 7 | Dev e QA por ticket | **C** + **S** | Silos e falta de colaboração. |
| 8 | 5 ferramentas de CI | **S** | Falta compartilhamento de ferramental; retrabalho e silos tecnológicos. |

> **Observação:** muitas situações afetam **mais de uma dimensão**. CALMS não é taxonomia rígida — é lente. A mesma situação pode ser vista por duas lentes e ambos os diagnósticos serem corretos.

---

## Exercício 2 — Toil vs trabalho duro

**Enunciado:**

Marque **Toil (T)** ou **Não-Toil (NT)** em cada item, justificando:

1. Reiniciar um serviço manualmente todo dia porque ele vaza memória.
2. Refatorar um módulo grande para reduzir acoplamento.
3. Responder tickets de acesso no Jira toda segunda-feira.
4. Projetar a arquitetura de um novo microsserviço.
5. Rodar manualmente um script de backup todo fim de semana.
6. Ajudar um colega a entender um bug complexo em produção.
7. Copiar arquivos de configuração entre ambientes manualmente a cada release.
8. Escrever um runbook para o on-call.

### Resolução

| # | Situação | Tipo | Justificativa |
|---|----------|------|----------------|
| 1 | Reiniciar serviço com vazamento | **T** | Manual, repetitivo, automatizável (corrigir o vazamento é a solução **estrutural**), não agrega valor duradouro. |
| 2 | Refatorar módulo | **NT** | Agrega valor duradouro; é trabalho de engenharia. Pode ser difícil, mas não é toil. |
| 3 | Responder tickets de acesso | **T** | Clássico candidato a automação (IAM self-service, IaC). |
| 4 | Projetar nova arquitetura | **NT** | Trabalho criativo de engenharia; não repetitivo. |
| 5 | Backup manual fim de semana | **T** | Automatizável, repetitivo, reativo. |
| 6 | Ajudar colega a debugar | **NT** (ou parcial) | Ajuda pontual é aprendizado/compartilhamento; se virar "só eu sei debugar isso e todo dia alguém me chama", aí é sintoma de **S** ruim. |
| 7 | Copiar configs entre ambientes | **T** | Óbvio candidato a IaC ou pipeline. |
| 8 | Escrever runbook | **NT** | Agrega valor duradouro; aprendizado **compartilhado** (alimenta S). |

**Regra mnemônica:** pergunte-se — *"se eu automatizar isso, nunca mais precisarei fazer manualmente, certo?"*. Se sim, é candidato a toil. Se a tarefa **sempre exigirá julgamento humano ou criatividade**, não é toil.

---

## Exercício 3 — Cálculo de custo de toil

**Enunciado:**

Use o script `custo_toil.py` apresentado no Bloco 2. Modifique os parâmetros para simular **3 cenários** e anote os custos anuais:

- **Cenário A (CloudStore hoje):** 40 passos, 5 min/passo, 2 deploys/mês, taxa falha 15%.
- **Cenário B (semi-automatizado):** 10 passos, 3 min/passo, 8 deploys/mês, taxa falha 5%.
- **Cenário C (automatizado):** 0 passos manuais, 10 deploys/dia úteis (~200/mês), taxa falha 3%.

Calcule e compare.

### Resolução

Modificando e rodando o script:

**Cenário A:**

- tempo_por_deploy ≈ 3.48h
- custo_mensal ≈ R$ 1.045
- **custo_anual ≈ R$ 12.540**

**Cenário B:**

- tempo = (10 × 3 / 60) × (1 + 0.05 × 0.30) = 0.5 × 1.015 = 0.508h
- custo_mensal = 0.508 × 8 × 150 ≈ R$ 609
- **custo_anual ≈ R$ 7.308**

**Cenário C:**

- tempo_direto_humano = 0 (deploy fully automated)
- **custo_anual de toil humano ≈ R$ 0**

(Haveria custo de infraestrutura de CI/CD, mas já não é mais toil.)

### Leitura do resultado

Note que o Cenário C **entrega muito mais** (200 deploys/mês vs 2 do Cenário A — **100x mais**) e ainda assim custa **menos em toil**. Esse é o ganho combinado de Lean + Automation: **mais fluxo com menos esforço humano repetitivo**.

O script também deixa ver que, à medida que a **frequência aumenta**, o toil manual fica **insustentável**. Se a CloudStore quisesse dobrar a frequência sem automatizar, precisaria dobrar o custo de Ops — isso é a definição de **escala linear** do toil, citada pelo livro SRE.

---

## Exercício 4 — Value Stream Mapping básico

**Enunciado:**

Considere um ticket na CloudStore que levou **22 dias** do pedido até ir a produção, assim distribuídos:

- 2 dias esperando priorização.
- 5 dias de Dev trabalhando.
- 3 dias parado esperando code review.
- 1 dia em ajustes pós-review.
- 4 dias esperando QA pegar.
- 2 dias de QA testando.
- 2 dias esperando agendamento de release.
- 3 dias esperando janela de sexta.

Calcule:

(a) **Lead Time** total.
(b) **Tempo de trabalho efetivo** (quando alguém estava realmente trabalhando).
(c) **Activity Ratio** (% de trabalho efetivo sobre lead time).
(d) Em qual dimensão CALMS você atacaria primeiro e por quê?

### Resolução

(a) **Lead Time** = 2 + 5 + 3 + 1 + 4 + 2 + 2 + 3 = **22 dias**.

(b) **Trabalho efetivo** = 5 (Dev) + 1 (ajustes) + 2 (QA) = **8 dias**.

(Observação: code review e homologação também exigem trabalho humano, mas em boa parte do tempo o ticket está **parado na fila** — nesse exercício consideramos só o tempo de execução ativa.)

(c) **Activity Ratio** = 8 / 22 ≈ **36%**.

(d) A principal dimensão é **L — Lean**. O problema não é que as pessoas trabalhem devagar — é que existe **14 dias de espera** entre atividades (desperdício tipo "espera" + "estoque"). Atacaria:

- **Espera de review (3d):** instituir SLA de review (ex.: máximo 1 dia útil), PRs pequenos, pair programming.
- **Espera de QA (4d):** shift-left — Dev e QA trabalham juntos desde o início, testes automatizados no CI.
- **Espera de janela de release (3d):** eliminar janela fixa por meio de deploy automatizado contínuo (Módulo 4).

Cada uma dessas mudanças também envolve **A (automação)** e **C (cultura de colaboração)**, mas o **diagnóstico** é prioritariamente Lean.

---

## Exercício 5 — Armadilha da métrica como meta (Lei de Goodhart)

**Enunciado:**

Um gestor da CloudStore, ao começar a medir, propõe: *"Vou pagar bônus ao time de Dev com base em **número de commits por semana**."* Avalie essa ideia.

### Resolução

É uma **ideia ruim**, e exemplifica a **Lei de Goodhart**: *"Quando uma métrica vira meta, deixa de ser uma boa métrica."*

O que pode acontecer:

- **Commits gigantes são quebrados** artificialmente em vários pequenos.
- **Mudanças triviais** (alterar espaço em branco, trocar comentário) são feitas para inflar número.
- **Refatorações e trabalho de manutenção** caem — dão poucos commits, mas são essenciais.
- **Documentação** despencada — muito esforço para zero commits no repo de código.
- **Pair programming** morre — dois commitam como um; prejudica a métrica individual.

A métrica mede **atividade**, não **valor**. E pior: ao vinculá-la a bônus, você garante que ela vai ser gamificada.

**Melhor abordagem** (alinhada a DORA, Módulo 10):

- Medir **throughput do time** (não individual) — tarefas/user-stories entregues por período.
- Combinar com **qualidade** — change failure rate, defeitos em produção.
- Medir **fluxo** (lead time) e **satisfação** da equipe periodicamente (pesquisa).
- **Nunca** atrelar bônus individual a métricas de saída técnica.

> **Referência:** Forsgren, Humble & Kim. *Accelerate.* IT Revolution, 2018 — mostra que os melhores times olham métricas de **fluxo e qualidade combinadas**, sem gamificação.

---

## Exercício 6 — Desafiador (opcional)

**Enunciado:**

Uma empresa implementou Kubernetes, GitHub Actions e está com 100% dos deploys automatizados. Porém, os postmortems continuam sendo uma **caça às bruxas** e os times de Dev e Ops continuam separados. Pela lente CALMS, diagnostique: essa empresa está madura em DevOps?

### Resolução

**Não.** Essa empresa é um caso clássico de **maturidade em "A" com deficit em "C" e "S"**.

- **A — Automation:** forte. Pipelines, K8s, deploys automáticos.
- **L — Lean:** parcial. Automação ajuda no fluxo, mas se o trabalho ainda espera entre silos, há desperdício.
- **M — Measurement:** talvez razoável (K8s traz métricas "de graça").
- **C — Culture:** **crítico**. Postmortem de culpa destrói segurança psicológica.
- **S — Sharing:** **crítico**. Silos persistem; responsabilidade não é compartilhada.

**Consequências previsíveis:** engenheiros começarão a **esconder erros** e evitar riscos. A velocidade potencial criada pela automação **não vai se materializar**, porque ninguém vai se arriscar a usá-la. A empresa terá um **pipeline excelente parado**.

**Lição:** DevOps é sistema; **o pilar mais fraco define o teto**. Pode-se ter tudo em ferramentas e falhar em DevOps por falhar em cultura.

> *"You can't buy DevOps."* — ditado comum do movimento. Ferramenta não substitui transformação organizacional.

---

## Próximo passo

Siga para o **[Bloco 3 — Os Três Caminhos](../bloco-3/03-tres-caminhos.md)**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Modelo CALMS](02-modelo-calms.md) | **↑ Índice**<br>[Módulo 1 — Fundamentos e cultura DevOps](../README.md) | **Próximo →**<br>[Bloco 3 — Os Três Caminhos (The Three Ways)](../bloco-3/03-tres-caminhos.md) |

<!-- nav:end -->

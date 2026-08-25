# Workshop de decisões — Qual camada escalar?

**Módulo:** [05 — Escalabilidade](README.md)  
**Faça depois** da [teoria](teoria.md) e, de preferência, do [lab aplicação](tutorial-escala-aplicacao.md).  
**Objetivo:** escolher **camada + técnica** — sem gabarito único.  
Termos: [glossario.md](glossario.md).

---

## Como usar

Para cada cenário:

1. Nomeie a **camada** (aplicação, dados, ambas, cache/07).  
2. Nomeie a **técnica** (N APIs, réplica leitura, partição, fila…).  
3. Liste **2 ganhos** e **2 custos**.  
4. Diga **como mediria** (RPS, p99, conexões DB, tamanho por shard).

| Critério | Pergunta rápida |
|----------|-----------------|
| Onde dói? | CPU da API, conexões DB, uma chave quente? |
| Leitura ou escrita? | Boletim ≠ matrícula |
| Consistência | Stale aceitável? ([03](../03-consistencia-cap/)) |
| Coordenação | Lock global no caminho? ([04](../04-coordenacao-locks/)) |

---

## Cenário 1 — Dia do boletim

08h: milhares de `GET` de notas. Professores **não** lançam nota nesse horário.

**Perguntas**

1. Primeiro: mais APIs, réplica de leitura ([02](../02-replicacao/)), ou cache ([07](../07-cache-distribuido/))?  
2. Depois do [lab aplicação](tutorial-escala-aplicacao.md) / `aproximar-teto`: o que limitaria se só subisse API?  
3. CAP: leitura na réplica — o que o aluno pode ver de stale?
4. Este cenário é **leitura** — partição de avisos resolve o boletim?

---

## Cenário 2 — p99 alto com 3 APIs

RPS médio ok; alguns alunos reclamam de lentidão. Um pod está com GC/delay.

**Perguntas**

1. Isso é falha de **escala** ou de **balanceamento/saúde**?  
2. Depois do Exp. worker lento: p50 vs p99.  
3. O que o módulo [06](../06-falhas-timeout/) acrescenta (timeout, tirar o nó do LB)?

---

## Cenário 3 — Avisos por campus no mesmo segundo

Campi A e B publicam dezenas de avisos. Um único Mongo vira gargalo de escrita.

**Perguntas**

1. Particionar por `campus_id` resolve? Quando **não**?  
2. Depois do [lab dados](tutorial-escala-dados.md): hot vs spread.  
3. Relatório “todos os campi” — o que o fan-out custa?

---

## Cenário 4 — Matrícula na última vaga sob pico

SD-101 com 1 vaga; fila enorme de cliques.

**Perguntas**

1. Escalar APIs resolve overbooking?  
2. Lock global ([04](../04-coordenacao-locks/)) vs shard por disciplina?  
3. Qual camada é o teto real aqui?

---

## Cenário 5 — “Escalamos no Kubernetes, problema resolvido”

Time só aumentou `replicas: 10` da API. Banco continua um.

**Perguntas**

1. Qual camada de fato ganhou capacidade?  
2. Que métricas pediria antes de celebrar?  
3. Como explicaria gargalo móvel à coordenação?

---

## Cenário 6 — Vertical primeiro?

Startup com 200 alunos: VM maior vs já partir em shards.

**Perguntas**

1. Quando vertical é a escolha certa?  
2. Quando horizontal na app basta?  
3. Quando partição de dados é prematura?

---

## Rubrica

| Nível | Esperado |
|-------|----------|
| **Insuficiente** | Só “sobe mais pod” sem camada nem métrica. |
| **Básico** | Nomeia app ou dados. |
| **Bom** | Camada + técnica + um trade-off; cita lab. |
| **Ótimo** | Gargalo móvel; CAP/locks; sequência de evolução. |

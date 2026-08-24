# Glossário — Consistência e CAP

**Módulo:** [03 — Consistência/CAP](README.md)

| Termo | Definição curta |
|-------|-----------------|
| **CAP** | Modelo didático: sob **partição**, trade-off entre **consistência forte** e **disponibilidade** de resposta. |
| **Consistência (C no CAP)** | Todas as réplicas expõem a **mesma** versão lógica dos dados no mesmo instante (visão simplificada). |
| **Disponibilidade (A no CAP)** | Toda requisição a um nó **não caído** recebe resposta **sem** erro de indisponibilidade. |
| **Partition tolerance (P)** | Sistema continua operando quando a **rede** divide os nós em grupos que não se comunicam. |
| **CP** | Sob partição, **prioriza consistência** — pode recusar/bloquear operações. |
| **AP** | Sob partição, **prioriza disponibilidade** — responde mesmo com risco de stale/divergência. |
| **Partição de rede** | Falha em que nós permanecem vivos mas **não trocam mensagens** entre grupos. |
| **Quórum / majority** | Maioria dos nós do cluster (ex.: 2 de 3) deve confirmar operação. |
| **Strong consistency** | Leitura retorna o valor mais recente confirmado globalmente. |
| **Eventual consistency** | Réplicas **convergem** com o tempo, se pararem de escrever. |
| **Stale read** | Leitura de valor **antigo** (módulo 02) — caso especial de eventual. |
| **writeConcern** | MongoDB: quantos nós devem confirmar escrita (`w:1`, `majority`, …). |
| **readConcern** | MongoDB: quais dados podem ser lidos (`local`, `majority`, …). |
| **synchronous_commit** | Postgres: commit espera réplica síncrona antes de retornar ao cliente. |
| **PACELC** | Sem partição: trade-off **latência vs consistência** (extensão do CAP). |
| **Overbooking** | Matricular mais alunos do que vagas — bug clássico sem exclusão mútua + CP. |
| **Linearizabilidade** | Strong consistency formal: operações parecem executar em sequência global (visão avançada). |
| **Split-brain** | Dois nós acreditam ser primary ao mesmo tempo — risco em partição mal gerenciada. |
| **RPO / RTO** | Perda máxima de dados / tempo para voltar — módulo 02; partição afeta RPO se async. |

Ver também: [glossário do módulo 02](../02-replicacao/glossario.md) (lag, primary, WAL, …).

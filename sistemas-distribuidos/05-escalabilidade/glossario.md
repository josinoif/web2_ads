# Glossário — Escalabilidade

**Módulo:** [05 — Escalabilidade](README.md)

| Termo | Definição curta |
|-------|-----------------|
| **Escalabilidade** | Capacidade de manter desempenho aceitável sob **mais carga** (ou crescimento). |
| **Escala vertical** | Aumentar recursos de **uma** máquina. |
| **Escala horizontal** | Adicionar **mais nós**/instâncias. |
| **Camada de aplicação** | Serviços que processam requests (API, workers) — tipicamente atrás de LB. |
| **Camada de dados** | Bancos / stores — réplicas, partições, shards. |
| **Throughput / RPS** | Operações (ou requests) por segundo. |
| **p50 / p99** | Latência na mediana / no percentil 99 (cauda). |
| **Balanceador (LB)** | Distribui requests entre instâncias (ex.: nginx). |
| **Stateless** | Instância não guarda sessão crítica local — qualquer réplica atende. |
| **Gargalo móvel** | Ao escalar uma camada, outra passa a limitar. |
| **SPOF** | Single Point of Failure — um componente cuja queda derruba o serviço. |
| **Amdahl (intuição)** | A fração **serial** do trabalho limita o ganho ao adicionar nós. |
| **Pool de conexões** | Limite de conexões reutilizadas app↔banco; teto comum antes de “mais API”. |
| **Réplica de leitura** | Cópia para servir **leituras** (módulo 02). |
| **Particionamento / shard** | Dividir dados por chave (campus, usuário…) em stores distintos. |
| **Shard key** | Atributo que decide **qual** partição recebe o dado. |
| **Hot key / hot shard** | Chave/partição que recebe carga desproporcional. |
| **Fan-out** | Uma operação que consulta **vários** shards (ex.: relatório global). |
| **Worker lento** | Instância com delay alto — piora p99 sob round-robin. |
| **CPU / custo sintético** | `WORK_MS` (busy-wait), `WRITE_MS`, `READ_SHARD_MS`, `DB_SLOTS`+`STORE_HOLD_MS` — carga artificial rotulada para o efeito aparecer no lab. |

Ver também: [glossário 02](../02-replicacao/glossario.md) · [03](../03-consistencia-cap/glossario.md) · [04](../04-coordenacao-locks/glossario.md).

# Glossário — Replicação (módulo 02)

| Termo | Significado curto |
|-------|-------------------|
| **Async replication** | Primary confirma antes da réplica aplicar — lag e stale possíveis — [teoria §3](teoria.md) |
| **Base backup** | Cópia inicial do disco do primary para criar standby — demora no primeiro boot |
| **Failover** | Troca do nó ativo (primary) para outro membro — [tutorial-mongodb](tutorial-mongodb.md) |
| **Hot standby** | Réplica Postgres pronta para leitura e promoção — [tutorial-postgres](tutorial-postgres.md) |
| **Lag** | Atraso entre primary e réplica — [teoria §4](teoria.md) |
| **Oplog** | Log de operações no MongoDB; base da replicação |
| **Primary** | Nó que aceita escritas (líder) |
| **Quorum** | Maioria de votos no replica set (ex.: 2 de 3) — [tutorial-mongodb Exp. 3](tutorial-mongodb.md) |
| **Read preference** | Driver Mongo escolhe primary ou secondary — [lab-mongodb](lab-mongodb/) `?dest=` |
| **Read replica** | Cópia usada principalmente para leitura |
| **Replica set** | Conjunto MongoDB com eleição de primary — [tutorial-mongodb Parte A](tutorial-mongodb.md) |
| **Replication** | Cópia contínua de dados entre nós |
| **RPO** | *Recovery Point Objective* — quanto dado se aceita perder após desastre |
| **RTO** | *Recovery Time Objective* — tempo máximo para voltar ao ar |
| **Secondary** | Membro MongoDB que replica o primary |
| **Stale read** | Leitura de valor desatualizado na réplica |
| **Standby** | Réplica Postgres em recovery (`pg_is_in_recovery()`) |
| **Sticky read after write** | Após gravar, mesma sessão lê no primary — [tecnologias §6](tecnologias-e-escolhas.md) |
| **Streaming replication** | Postgres envia WAL ao standby em tempo quase real |
| **Sync replication** | Escrita só confirma após réplica ack — [tutorial-sync-async](tutorial-sync-async.md) |
| **sync_state** | Campo Postgres (`async` / `sync`) — [lab-sync-async](lab-sync-async/) `/replicacao/status` |
| **WAL** | *Write-Ahead Log* — journal do Postgres |

Ver também: [teoria.md](teoria.md) · [troubleshooting.md](troubleshooting.md).

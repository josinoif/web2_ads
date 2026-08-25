# Gabarito enxuto — Decisões (09)

**Abra só depois** de tentar [decisoes.md](decisoes.md). Não é a única resposta certa — é um espelho.

| Cenário | Direção razoável | Risco se errar |
|---------|------------------|----------------|
| **1** Portal no prazo | `docker logs` em 3 containers na pressa falha. JSON + `trace_id` + Loki: um filtro remonta. Sem propagação = três histórias (Exp. 2). | Tempo perdido no pico; aluno sem recibo e time sem evidência |
| **2** Startup | SaaS se o time não quer operar stack e precisa retenção/alerta rápido. Grafana+OTel no lab cobre o *modelo*; faltam on-call, retenção longa, RBAC. OTel facilita trocar backend. | Travado em vendor **ou** afogado em ops prematura |
| **3** CPU vs negócio | Acordar por **erro/latência do POST** (RED/SLI). CPU é capacidade — útil, secundário. SLO = meta sobre a experiência. Health mentiroso (Exp. 3) reforça. | Fadiga de alarme; incidente de negócio sem página |
| **4** Sampling | 100% ok em QPS baixo/lab. Em produção, amostrar e manter logs com `trace_id` para casos quentes. | Fatura absurda **ou** zero evidência no incidente raro |
| **5** `aluno_id` em métrica | Cardinalidade explode. Por aluno → log/trace; métrica agrega por rota/serviço/status (quiz lab B). | Prometheus lento/cai; custo de cardinality |
| **6** Campus B | Agregado global mascara. Dimensão `campus` (baixa cardinalidade) ou eventos/traces filtrados — unknown unknowns. | “Tudo verde” enquanto um segmento sofre |
| **7** Fronteira | 09: instrumentar + correlacionar + diagnosticar. DevOps: operar stack no cluster. App deve expor `/metrics`, logs JSON e contexto de trace **sempre**. | Cada time reinventa stack; ou app “cega” na plataforma boa |

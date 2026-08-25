# Tecnologias e escolhas — Arquitetura

**Módulo:** [10 — Arquitetura](README.md)  
**Pré-leitura:** [teoria.md](teoria.md)

Este módulo **não** introduz stack nova de produção. A tabela liga cada estilo ao que você **já usou** na trilha.

> **01 = mecanismo · 10 = escolha de estilo** com o mecanismo já conhecido.

---

## 1. Estilo → evidência no curso

| Estilo | O que já apareceu | Onde |
|--------|-------------------|------|
| Cliente–servidor / n-tier | HTTP na borda, API + store | Quase todos os labs |
| Monólito layered (modular) | Um processo / módulos nomeados | Lab A (`monolito`) |
| Pipeline de serviços (≠ MS completo) | Gateway → análise → store | Lab A; [09](../09-observabilidade/) |
| Microsserviços (conceito) | Deploy/dados independentes | Teoria §5 + workshop — **não** o lab A sozinho |
| EDA / filas | Redis lista, Kafka | [01](../01-comunicacao/); Lab B eventos |
| Pub-sub / fan-out | Tópico Kafka; notificador Redis | [01](../01-comunicacao/); Lab B (limite: pub/sub) |
| Escala por camadas | N APIs, partição | [05](../05-escalabilidade/) |
| Resiliência | Timeout, retry, CB | [06](../06-falhas-timeout/) |
| Observabilidade | Logs, métricas, traces | [09](../09-observabilidade/) |
| SOA / legado / ACL | Conceito (workshop) | Sem lab — integração institucional |
| P2P | Contraste (teoria §7) | Sem lab — Tanenbaum Ch. 2 |

---

## 2. Lab A — o que cada peça faz

| Peça | Papel didático |
|------|----------------|
| `monolito` (:8120) | Arquivos `app.py` + `analise_mod.py` + `store_mod.py` **no mesmo processo** |
| `gateway` (:8121) | Borda HTTP do pipeline |
| `analise` (:8122 admin) | Hop do meio (delay / pode ser parado) |
| `store` | Persistência em memória |

**Não é** microsserviço de produção. Serve para **ver isolamento de processo**.

---

## 3. Lab B — o que cada peça faz

| Peça | Papel didático |
|------|----------------|
| Gateway sync (:8130) | Cadeia síncrona até o store |
| Gateway eventos (:8131) | Aceita e **enfileira** (Redis lista) |
| Redis (:6381) | Fila + status + pub/sub (fan-out) |
| Worker | Consome fila, “analisa”, atualiza status |
| Notificador | Segundo consumidor via pub/sub — deve estar up **antes** do evento |

---

## 4. Matriz de decisão rápida

| Se você precisa… | Incline para… | Evite… |
|------------------|---------------|--------|
| Entregar MVP com 1 time | Monólito (+ fila se o pico doer) | Microsserviços “porque sim” |
| Times com ritmo de deploy diferente | MS ou service-based (+ dados por contexto) | Monólito sem módulos; “MS” com DB único |
| Aceitar no prazo e analisar depois | EDA / fila ([01](../01-comunicacao/)) | Sync longo na borda |
| Integrar ERP + secretaria + portal | SOA / integração + ACL | N chamadas ad hoc sem contrato |
| Autoridade central de notas | Cliente–servidor | P2P como núcleo |
| Diagnosticar hop lento | Instrumentação ([09](../09-observabilidade/)) | Mais processos sem traces |

---

## 5. Cloud vs lab

| Produção | Lab 10 |
|----------|--------|
| Serviços com DB/schema próprios | Store em memória / Redis status |
| Service mesh / K8s | Compose + `stop` de container |
| Kafka / SQS maduro (retenção) | Redis lista + pub/sub (didático; pub/sub pode perder evento) |
| Saga / outbox | Fora de escopo — Hard Parts na teoria |

---

## Fora deste módulo

Kubernetes, service mesh, data mesh completo e “quebra o monólito em 40 serviços” — aprofundar em DevOps / projetos maiores. Aqui: **critério de escolha** + dois experimentos observáveis + síntese no workshop.

# Sistemas Distribuídos — Mini-projetos práticos

**Público:** Ensino superior (ADS)  
**Objetivo:** Exercitar na prática os conceitos de sistemas distribuídos com **mini-projetos pequenos**, focados em **demonstrar um conceito por vez**, com o menor atrito possível de setup.

**Stack padrão:** **Python 3** (biblioteca padrão sempre que der) + **Docker / Compose** como ambiente de experimentação (vários nós, serviços de apoio, falhas simuladas).

---

## Princípios do material

1. **Um conceito por tutorial** — cada pasta isola uma ideia.
2. **Simplicidade primeiro** — poucos arquivos, poucas dependências.
3. **Ver o efeito, não só ler a teoria** — cada mini-projeto tem um experimento observável (logs, lag, inconsistência, throughput, traces).
4. **Lab reproduzível** — Docker Compose para subir N nós e serviços de apoio; Python para a lógica do experimento.
5. **Progressão** — ambiente Docker → comunicação e estado → escala e resiliência → armazenamento e observabilidade.

> Cliente–servidor HTTP básico **não** entra nesta trilha: os alunos já praticam isso em outras disciplinas. Aqui o foco é o que muda quando há **vários nós, falhas parciais e estado compartilhado**.

---

## Pré-requisitos sugeridos

- Python 3 (`python3 --version`)
- Docker Engine + Docker Compose (`docker compose version`)
- Terminal básico
- Noções de HTTP/APIs (já vistas no curso)

Comece obrigatoriamente pelo tutorial **00** se ainda não usa Docker no dia a dia.

**Imagens Postgres na trilha:** labs “simples” (04, 05 app) usam `postgres:16-alpine`. Labs com **replicação Bitnami** (02, 03) usam `bitnamilegacy/postgresql:16.6.0-debian-12-r2` **com digest pin** — a tag `bitnami/postgresql:16` deixou de existir no Docker Hub. No lab 03, rode `./scripts/ativar-sync.sh` após o `up` (sync no boot deadlocks o init).

---

## Mapa dos tutoriais

| # | Pasta | Conceito central | Mini-projeto (ideia) |
|---|-------|------------------|----------------------|
| 0 | [00-ambiente-docker](00-ambiente-docker/) | Docker como bancada de experimentação | Compose com 3 nós + Redis; folha de comandos |
| 1 | [01-comunicacao](01-comunicacao/) | Comunicação: filas, Kafka, gRPC | Teoria + 3 labs (A/B/C) + decisões; ver caminho mínimo no README do módulo |
| 2 | [02-replicacao](02-replicacao/) | Replicação, líder/seguidores, lag, sync/async | Postgres + sync/async + MongoDB; portal de notas |
| 3 | [03-consistencia-cap](03-consistencia-cap/) | Consistência vs disponibilidade (intuição do CAP) | Postgres partição + matrícula CP; Mongo concerns + feed avisos |
| 4 | [04-coordenacao-locks](04-coordenacao-locks/) | Exclusão mútua, locks distribuídos | Postgres multi-API + Mongo/Redis reserva |
| 5 | [05-escalabilidade](05-escalabilidade/) | Escala por camadas (app + dados) | N APIs+Postgres (RPS); Mongo partição por campus |
| 6 | [06-falhas-timeout](06-falhas-timeout/) | Timeouts, retries, idempotência, circuit breaker | Postgres matrícula + Mongo avisos |
| 7 | [07-cache-distribuido](07-cache-distribuido/) | Cache, invalidação, stale reads (CAP na leitura) | Postgres boletim + Mongo avisos + Redis |
| 8 | [08-armazenamento-arquivos](08-armazenamento-arquivos/) | Object storage + metadado (não DFS clássico); dedup, falha parcial, RPO | MinIO + Postgres/Mongo (entrega / catálogo) |
| 9 | [09-observabilidade](09-observabilidade/) | Logs agregados, APM, tracing | App instrumentada + visualizar correlação de requests |

Cada pasta terá, no mínimo:

- `README.md` — objetivo, conceito, passos do experimento e o que observar
- código mínimo do mini-projeto (quando o tutorial estiver pronto)

---

## Como usar em sala

1. **Aula 0:** ambiente Docker ([00-ambiente-docker](00-ambiente-docker/)) — toda a turma sobe o mesmo lab.
2. Nos demais módulos: **teoria** (leitura ou 15–25 min em sala) + experimento do lab + **decisão/trade-off** quando o módulo tiver workshop.  
3. **Experimento coletivo** — comparar resultados (“quem viu inconsistência?”, “quanto ganhou de RPS com 3 workers?”).  
4. **Perguntas-guia** / cenários de decisão no final — o aluno deve **justificar** escolhas, não só reproduzir comandos.

Ordem recomendada: **00** → **01–04** (fundamentos) → **05–07** (escala e resiliência) → **08–09** (dados e operação).

---

## Stack e ferramentas

| Situação | Escolha |
|----------|---------|
| Ambiente multi-nó / falhas | Docker Compose (tutorial 00) |
| Processos HTTP / workers | Python 3 (`http.server`, `urllib`, scripts curtos) |
| Fila / cache / lock | Redis via Docker |
| Arquivos distribuídos | MinIO (API S3) via Docker — módulo [08](08-armazenamento-arquivos/) |
| Observabilidade | Stack mínima via Compose (definida no tutorial 09) |

---

## Relação com outros materiais do repositório

- Containers / Compose (visão geral): [`infra/docker/`](../infra/docker/)
- Containers em profundidade (DevOps): [`devops/05-containers/`](../devops/05-containers/)
- Object storage (MinIO/S3): [`infra/storage/`](../infra/storage/)
- Observabilidade em DevOps: [`devops/08-observabilidade/`](../devops/08-observabilidade/) — aqui o foco é **o que o sistema distribuído precisa expor**; lá o foco é operar a plataforma

O tutorial **00** desta pasta é a **folha de referência de comandos** para os labs da disciplina; os materiais acima aprofundam Dockerfile, produção e operação.

---

## Status

| Tutorial | Status |
|----------|--------|
| 00-ambiente-docker | pronto (referência + lab) |
| 01-comunicacao | pronto (teoria, glossário, 3 labs, decisões; caminho mínimo + completo) |
| 02-replicacao | pronto (teoria, glossário, 3 labs Postgres/sync-async/Mongo, decisões) |
| 03-consistencia-cap | pronto (teoria, glossário, 2 labs Postgres/Mongo, decisões) |
| 04-coordenacao-locks | pronto (teoria, glossário, 2 labs Postgres/Mongo+Redis, decisões) |
| 05-escalabilidade | pronto (teoria, glossário, 2 labs app/dados, decisões) |
| 06-falhas-timeout | pronto (teoria, glossário, 2 labs Postgres/Mongo, decisões) |
| 07-cache-distribuido | pronto (teoria, glossário, 2 labs Postgres/Mongo+Redis, decisões) |
| 08-armazenamento-arquivos | pronto (teoria, glossário, 2 labs Postgres/Mongo+MinIO, decisões) |
| 09-observabilidade | planejado |

---

## Próximos passos (material)

- [ ] Alinhar 09 com `devops/08-observabilidade/`
- [ ] Cruzar com a ementa oficial (obrigatório vs. opcional)

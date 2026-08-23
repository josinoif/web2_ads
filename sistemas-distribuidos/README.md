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

---

## Mapa dos tutoriais

| # | Pasta | Conceito central | Mini-projeto (ideia) |
|---|-------|------------------|----------------------|
| 0 | [00-ambiente-docker](00-ambiente-docker/) | Docker como bancada de experimentação | Compose com 3 nós + Redis; folha de comandos |
| 1 | [01-comunicacao](01-comunicacao/) | Comunicação entre nós: filas e gRPC | Correção de provas em lote (fila) + gRPC de status |
| 2 | [02-replicacao](02-replicacao/) | Replicação, líder/seguidores, lag | “Banco” em memória replicado para N nós |
| 3 | [03-consistencia-cap](03-consistencia-cap/) | Consistência vs disponibilidade (intuição do CAP) | Dois nós com partição simulada |
| 4 | [04-coordenacao-locks](04-coordenacao-locks/) | Exclusão mútua, locks distribuídos | Contador compartilhado com e sem lock |
| 5 | [05-escalabilidade](05-escalabilidade/) | Escala horizontal, balanceamento, medição | Gateway + N workers; medir throughput ao adicionar nós |
| 6 | [06-falhas-timeout](06-falhas-timeout/) | Timeouts, retries, circuit breaker mínimo | Cliente que sobrevive quando um nó falha |
| 7 | [07-cache-distribuido](07-cache-distribuido/) | Cache, invalidação, stale reads | API + cache compartilhado |
| 8 | [08-armazenamento-arquivos](08-armazenamento-arquivos/) | Object storage / arquivos distribuídos | Upload/download via API S3-compatível (MinIO) |
| 9 | [09-observabilidade](09-observabilidade/) | Logs agregados, APM, tracing | App instrumentada + visualizar correlação de requests |

Cada pasta terá, no mínimo:

- `README.md` — objetivo, conceito, passos do experimento e o que observar
- código mínimo do mini-projeto (quando o tutorial estiver pronto)

---

## Como usar em sala

1. **Aula 0:** ambiente Docker ([00-ambiente-docker](00-ambiente-docker/)) — toda a turma sobe o mesmo lab.
2. Nos demais módulos: **teoria curta** (10–15 min) + experimento do README.
3. **Experimento coletivo** — comparar resultados (“quem viu inconsistência?”, “quanto ganhou de RPS com 3 workers?”).
4. **Perguntas-guia** no final de cada README.

Ordem recomendada: **00** → **01–04** (fundamentos) → **05–07** (escala e resiliência) → **08–09** (dados e operação).

---

## Stack e ferramentas

| Situação | Escolha |
|----------|---------|
| Ambiente multi-nó / falhas | Docker Compose (tutorial 00) |
| Processos HTTP / workers | Python 3 (`http.server`, `urllib`, scripts curtos) |
| Fila / cache / lock | Redis via Docker |
| Arquivos distribuídos | MinIO (API S3) via Docker |
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
| 01-comunicacao | bloco filas pronto (tutorial + lab); gRPC a fazer |
| 02-replicacao | planejado |
| 03-consistencia-cap | planejado |
| 04-coordenacao-locks | planejado |
| 05-escalabilidade | planejado |
| 06-falhas-timeout | planejado |
| 07-cache-distribuido | planejado |
| 08-armazenamento-arquivos | planejado |
| 09-observabilidade | planejado |

---

## Próximos passos (para o professor)

- [ ] Bloco gRPC do módulo 01 (mesmo domínio da correção)
- [ ] Reutilizar o padrão Compose do 00/01 nos labs seguintes
- [ ] Alinhar 08 e 09 com `infra/storage/` e `devops/08-observabilidade/`
- [ ] Cruzar com a ementa oficial (obrigatório vs. opcional)

# Tutorial — Correção de provas com fila de mensagens

**Módulo:** [01 — Comunicação](README.md)  
**Nível:** iniciante em sistemas distribuídos  
**Tempo sugerido:** 1 aula + experimentos (≈ 90–120 min)  
**Pré-requisito:** [00 — Ambiente Docker](../00-ambiente-docker/)

Neste tutorial você vai montar um **portal de correção de provas em escala reduzida**. O professor envia várias provas; a análise (lenta) roda **depois**, em outro processo. No caminho, você vai ver na prática o que significa **comunicação assíncrona** e **fila de mensagens**.

---

## 0. O problema (por que isso importa)

Imagine o fim da unidade: o professor precisa enviar **80 PDFs**. Para cada um, o sistema deveria:

1. aceitar o arquivo  
2. extrair texto  
3. calcular similaridade (checagem de plágio)  
4. gerar um parecer  

Os passos 2–4 demoram. Se a tela de upload **só liberar** quando a análise acabar, o navegador trava, o servidor satura e na sexta às 23h59 ninguém consegue entregar.

**Pergunta-guia:** nos próximos 3 segundos após o “Enviar”, o que o professor precisa garantir — e o que pode ficar para daqui a alguns minutos?

O desenho abaixo resume a dor do caminho **síncrono** no dia da entrega:

```mermaid
sequenceDiagram
    autonumber
    actor Prof as Professor
    participant API
    participant Analise as Análise (lenta)

    Prof->>API: Enviar prova 1
    API->>Analise: extrair + similaridade
    Note over Analise: demora vários segundos
    Analise-->>API: relatório
    API-->>Prof: ok (só agora)
    Prof->>API: Enviar prova 2...
    Note over Prof,API: Com 80 provas, a tela "trava"
```

> **Conceito: trabalho síncrono vs assíncrono**  
> - **Síncrono:** quem pede espera o resultado na mesma conversa (“fica na linha”).  
> - **Assíncrono:** quem pede registra o pedido e segue; o resultado chega depois (status, e-mail, painel).  
> Filas de mensagens são uma forma clássica de organizar o trabalho assíncrono entre processos.

```mermaid
flowchart LR
    subgraph sync["Síncrono"]
        A1[Pedido] --> B1[Espera]
        B1 --> C1[Resultado]
    end
    subgraph async["Assíncrono"]
        A2[Pedido] --> B2[Ack rápido]
        B2 --> C2[Trabalho depois]
        C2 --> D2[Resultado / status]
    end
```

---

## 1. O que vamos construir

Três peças:

| Peça | Papel no mundo real | No lab |
|------|---------------------|--------|
| **API** | Portal que recebe o upload | Serviço `api` na porta `8080` |
| **Fila** | “Banco de trabalhos pendentes” | Redis (lista `prova:fila`) |
| **Worker** | Analisador de plágio / correção | Serviço `worker` (pode ter mais de um) |

Arquitetura do lab:

```mermaid
flowchart TB
    Prof[Professor / curl]

    subgraph compose["Docker Compose"]
        API[API - produtor<br/>porta 8080]
        Redis[(Redis<br/>fila + status)]
        W1[Worker - consumidor]
    end

    Prof -->|POST /provas| API
    Prof -->|GET /provas/id| API
    API -->|LPUSH mensagem| Redis
    API -->|lê/grava status| Redis
    W1 -->|BRPOP job| Redis
    W1 -->|atualiza status| Redis
```

Fluxo no tempo (ack rápido + trabalho depois):

```mermaid
sequenceDiagram
    autonumber
    actor Prof as Professor
    participant API
    participant Fila as Redis fila
    participant Status as Redis status
    participant Worker

    Prof->>API: POST /provas
    API->>Status: status = na_fila
    API->>Fila: enfileira mensagem
    API-->>Prof: 202 Accepted
    Note over Prof: já pode fechar a tela
    Worker->>Fila: BRPOP
    Worker->>Status: status = processando
    Note over Worker: sleep = análise simulada
    Worker->>Status: status = concluido
    Prof->>API: GET /provas/id
    API->>Status: consulta
    API-->>Prof: relatório pronto
```

Neste lab o PDF é **simulado** (não precisamos de arquivo de verdade). O worker só “dorme” alguns segundos para imitar a análise pesada. O importante é a **forma** do sistema, não o OCR.

Código pronto em [`lab/`](lab/).

---

## 2. Subir o ambiente

No terminal:

```bash
cd sistemas-distribuidos/01-comunicacao/lab
docker compose up -d --build
docker compose ps
```

Espere os três serviços (`redis`, `api`, `worker`) ficarem `running`. Teste:

```bash
curl -s http://localhost:8080/health
```

Resposta esperada: `{"ok": true}`.

Se algo falhar: `docker compose logs -f api` e `docker compose logs -f worker`.

> **Conceito: vários processos = sistema distribuído em miniatura**  
> API e worker são **processos diferentes** (containers diferentes). Eles não compartilham memória da aplicação: combinam através da **fila** e do **status** no Redis. Essa indirection é o coração do desenho.

```mermaid
flowchart LR
    subgraph host["Seu notebook"]
        subgraph c1["container api"]
            P1[processo Python API]
        end
        subgraph c2["container worker"]
            P2[processo Python worker]
        end
        subgraph c3["container redis"]
            P3[(Redis)]
        end
        P1 <--> P3
        P2 <--> P3
    end
```

Não há memória compartilhada entre API e worker: o Redis é o **ponto de encontro**.

---

## 3. Caminho feliz — uma prova

### 3.1 Enviar (enfileirar)

```bash
curl -s -X POST http://localhost:8080/provas \
  -H "Content-Type: application/json" \
  -d '{"aluno":"maria","arquivo":"maria.pdf"}' | python3 -m json.tool
```

Você deve ver algo como:

- HTTP implícito **202** (Accepted) — “aceitei, ainda não terminei”  
- `"status": "na_fila"`  
- um `submission_id` (guarde esse valor)

Cronometre mentalmente: a resposta veio em **fração de segundo**, não em 3 segundos.

> **Conceito: produtor**  
> A API é o **produtor**: quem **cria** a mensagem e a coloca na fila. O produtor não precisa conhecer *quem* vai analisar — só o formato da mensagem.

### 3.2 Acompanhar o status

Substitua `SEU_ID` pelo `submission_id` retornado:

```bash
./scripts/acompanhar.sh SEU_ID
```

Ou manualmente:

```bash
curl -s http://localhost:8080/provas/SEU_ID | python3 -m json.tool
```

Em poucos segundos o status passa por:

1. `na_fila`  
2. `processando`  
3. `concluido` (com um `relatorio` fictício)

```mermaid
stateDiagram-v2
    [*] --> na_fila: POST /provas
    na_fila --> processando: worker pega o job
    processando --> concluido: análise ok
    processando --> erro: falha simulada
    concluido --> [*]
    erro --> [*]
```

Olhe também o log do worker:

```bash
docker compose logs -f worker
```

> **Conceito: consumidor (worker)**  
> O worker é o **consumidor**: fica esperando mensagens (`BRPOP`), processa uma, depois a próxima. Quem envia a prova e quem analisa estão **desacoplados no tempo**: a API já respondeu quando o worker ainda nem começou.

> **Conceito: fila de mensagens**  
> A fila é um buffer ordenado de trabalhos. Quem produz pode ser mais rápido (ou estar disponível em outro horário) do que quem consome. A fila **segura** o que ainda não foi feito.

---

## 4. Comparar com a versão síncrona (teoria na pele)

A API também tem um endpoint que **faz a análise dentro do próprio request** — o anti-padrão que queremos evitar no dia da entrega:

```bash
time curl -s -X POST http://localhost:8080/provas/sincrono \
  -H "Content-Type: application/json" \
  -d '{"aluno":"joao","arquivo":"joao.pdf"}' | python3 -m json.tool
```

Observe:

- a resposta demora ≈ `ANALISE_SEGUNDOS` (padrão: 3s)  
- o campo `latencia_api_segundos` confirma isso  
- o professor só recebe “ok” quando a análise acabou

Agora compare com o assíncrono:

```bash
time curl -s -X POST http://localhost:8080/provas \
  -H "Content-Type: application/json" \
  -d '{"aluno":"ana","arquivo":"ana.pdf"}' | python3 -m json.tool
```

| | `POST /provas/sincrono` | `POST /provas` (fila) |
|--|-------------------------|----------------------|
| Tempo até a resposta | ≈ tempo da análise | curto |
| Análise pronta na resposta? | sim | ainda não |
| Se o analisador estiver sobrecarregado | o upload “trava” | o upload ainda aceita |

Lado a lado no tempo:

```mermaid
sequenceDiagram
    autonumber
    actor Prof as Professor
    participant API
    participant Fila as Fila
    participant Worker

    rect rgb(255, 230, 230)
        Note over Prof,Worker: Caminho síncrono POST /provas/sincrono
        Prof->>API: enviar
        API->>API: analisa aqui dentro
        API-->>Prof: 200 só no fim
    end

    rect rgb(230, 255, 230)
        Note over Prof,Worker: Caminho assíncrono POST /provas
        Prof->>API: enviar
        API->>Fila: mensagem
        API-->>Prof: 202 na hora
        Worker->>Fila: pega job
        Worker->>Worker: analisa depois
    end
```

> **Conceito: acoplamento temporal**  
> No síncrono, cliente e analisador precisam estar disponíveis **ao mesmo tempo** e o cliente paga a latência do trabalho pesado.  
> No assíncrono com fila, o cliente e o worker podem viver em ritmos diferentes. O preço é outro: você precisa de **status** (“já enviei” ≠ “já tenho relatório”).

Anote em uma frase: *o que o professor ganha e o que ele deixa de ter na hora do upload?*

---

## 5. Entender a mensagem (o “contrato” da fila)

Quando a API enfileira, ela grava um JSON parecido com:

```json
{
  "submission_id": "prova-a1b2c3d4",
  "aluno": "maria",
  "arquivo": "maria.pdf",
  "enqueued_at": "2026-08-23T02:10:00Z"
}
```

Pontos importantes:

- A mensagem carrega **dados suficientes** para o worker trabalhar sem ligar de volta para a API.  
- O `submission_id` identifica a prova de forma estável (vamos usar isso nos testes de falha).

> **Conceito: contrato de mensagem**  
> Em sistemas assíncronos, o “contrato” entre serviços muitas vezes é o **formato da mensagem**, não uma URL de API. Mudar esse JSON sem cuidado quebra produtores e consumidores — mesmo que eles nunca se falem por HTTP.

Inspecione a fila (tamanho):

```bash
curl -s http://localhost:8080/fila | python3 -m json.tool
```

Ou direto no Redis:

```bash
docker compose exec redis redis-cli LLEN prova:fila
```

---

## 6. Experimentos — evidenciar características de sistemas distribuídos

A partir daqui o objetivo não é “fazer funcionar”. É **provocar o sistema** e anotar o que acontece. Use uma folha (ou o final desta seção) para registrar tempos e impressões.

Antes de cada experimento, se a fila estiver suja:

```bash
docker compose restart worker
# esvaziar fila (cuidado: apaga jobs pendentes)
docker compose exec redis redis-cli DEL prova:fila
```

---

### Experimento 1 — Pico de entrega (a fila como amortecedor)

**Hipótese:** a API continua rápida mesmo quando há muitas provas; o atraso aparece no *término* da análise, não no upload.

```mermaid
flowchart LR
    subgraph chegada["Chegada rápida"]
        P1[prova]
        P2[prova]
        P3[prova]
        P4[prova]
        P5[prova]
    end
    Fila[(Fila<br/>amortecedor)]
    W[Worker<br/>devagar]

    P1 --> Fila
    P2 --> Fila
    P3 --> Fila
    P4 --> Fila
    P5 --> Fila
    Fila --> W
```

```bash
./scripts/enviar-lote.sh 15
curl -s http://localhost:8080/fila | python3 -m json.tool
docker compose logs --tail=30 worker
```

**O que anotar**

- Quanto tempo o `enviar-lote` levou?  
- Qual o `tamanho` da fila logo após o lote?  
- Os statuses das primeiras provas já viraram `processando`/`concluido` enquanto as últimas ainda estão `na_fila`?

> **Conceito: buffer / absorção de pico**  
> A fila acumula trabalho quando a chegada é mais rápida que o consumo. Isso protege a API e espalha a carga no tempo. Em troca, aparece **lag** (atraso até `concluido`).

---

### Experimento 2 — Worker desligado (desacoplamento temporal)

**Hipótese:** com o analisador fora do ar, o professor **ainda consegue enviar**; as provas esperam.

```mermaid
sequenceDiagram
    autonumber
    actor Prof as Professor
    participant API
    participant Fila as Fila Redis
    participant Worker

    Note over Worker: parado (stop)
    Prof->>API: POST lote
    API->>Fila: mensagens acumulam
    API-->>Prof: 202 ok
    Note over Fila: LLEN > 0
    Note over Worker: start
    Worker->>Fila: drena a fila
```

```bash
docker compose stop worker
./scripts/enviar-lote.sh 10
curl -s http://localhost:8080/fila | python3 -m json.tool
```

Escolha um `submission_id` do lote e consulte:

```bash
curl -s http://localhost:8080/provas/SEU_ID | python3 -m json.tool
```

Status esperado: `na_fila`. A fila não deve estar vazia.

Agora religue:

```bash
docker compose start worker
docker compose logs -f worker
```

A fila deve **drenar** e os statuses irem para `concluido`.

**O que anotar**

- O `POST` falhou com o worker parado? (não deve)  
- Quanto tempo até a fila voltar a zero depois do `start`?

> **Conceito: desacoplamento temporal**  
> Produtor e consumidor não precisam estar no ar no mesmo instante. A fila “segura o bastão”. Isso é o oposto do `POST /provas/sincrono`, que falharia ou travaria se a análise não pudesse rodar na hora.

---

### Experimento 3 — Escalar consumidores (paralelismo)

**Hipótese:** dois workers processam o backlog mais rápido que um.

```mermaid
flowchart TB
    Fila[(prova:fila)]
    W1[Worker 1]
    W2[Worker 2]
    Fila -->|job A| W1
    Fila -->|job B| W2
    Fila -->|job C| W1
    Fila -->|job D| W2
```

Vários consumidores **competem** pela mesma fila: cada mensagem vai para **um** worker (não para todos).

Garanta um worker só, esvazie a fila, pare o worker, enfileire 12 provas, meça o tempo para drenar com 1 worker; repita com 2.

**Com 1 worker**

```bash
docker compose stop worker
docker compose exec redis redis-cli DEL prova:fila
./scripts/enviar-lote.sh 12

# anote a hora e suba 1 worker
time (
  docker compose start worker
  while [ "$(curl -s http://localhost:8080/fila | python3 -c 'import sys,json; print(json.load(sys.stdin)["tamanho"])')" != "0" ]; do
    sleep 1
  done
)
```

**Com 2 workers**

No `docker-compose.yml` o serviço se chama `worker`. Suba uma segunda réplica:

```bash
docker compose stop worker
docker compose exec redis redis-cli DEL prova:fila
./scripts/enviar-lote.sh 12

time (
  docker compose up -d --scale worker=2 worker
  while [ "$(curl -s http://localhost:8080/fila | python3 -c 'import sys,json; print(json.load(sys.stdin)["tamanho"])')" != "0" ]; do
    sleep 1
  done
)
```

Veja nos logs hostnames diferentes dos containers — cada réplica do worker se identifica sozinha. O essencial é confirmar **dois consumidores** competindo pela mesma fila.

**O que anotar**

- Tempo com 1 vs 2 workers  
- O ganho foi próximo de 2×? Se não, por quê? (overhead, Redis, sleep fixo…)

> **Conceito: escala horizontal do consumidor**  
> Em filas do tipo *compete consumers*, vários workers pegam mensagens diferentes da mesma fila. Você escala o **trabalho pesado** sem mudar a API. Isso é uma característica clássica de arquiteturas baseadas em mensagens.

Para voltar ao padrão:

```bash
docker compose up -d --scale worker=1 worker
```

---

### Experimento 4 — Queda no meio do job (falha parcial)

**Hipótese:** se o worker morrer durante a análise, o sistema pode ficar em um estado estranho (status `processando` para sempre, ou trabalho perdido) — evidência de que “assíncrono” exige cuidado com falhas.

```mermaid
sequenceDiagram
    autonumber
    participant Fila
    participant Worker
    participant Status

    Fila->>Worker: BRPOP remove a mensagem
    Worker->>Status: processando
    Note over Worker: kill no meio do sleep
    Worker--xWorker: processo morre
    Note over Fila: mensagem já saiu da fila
    Note over Status: preso em processando?
```

Neste lab simples o `BRPOP` tira a mensagem **antes** do fim do trabalho. Se o worker cair no meio, a prova pode “sumir” da fila e ficar com status inconsistente — exatamente o tipo de bug que sistemas reais tentam evitar com ack, timeout e retry.

```bash
# limpe e envie uma prova
docker compose exec redis redis-cli DEL prova:fila
ID=$(curl -s -X POST http://localhost:8080/provas \
  -H "Content-Type: application/json" \
  -d '{"aluno":"teste-kill","arquivo":"kill.pdf"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['submission_id'])")
echo "ID=$ID"

# quando aparecer "processando" nos logs, mate o worker na hora
docker compose logs -f worker &
sleep 1
docker kill "$(docker compose ps -q worker)"
curl -s "http://localhost:8080/provas/$ID" | python3 -m json.tool
curl -s http://localhost:8080/fila | python3 -m json.tool
```

**O que anotar**

- O status ficou em `processando`?  
- A mensagem ainda está na fila? (neste lab simples, o `BRPOP` **já removeu** a mensagem — ela pode ter “sumido”)  
- O que um sistema de produção faria? (ack só no fim, retry, timeout de status, fila de dead letter…)

Suba o worker de novo:

```bash
docker compose up -d worker
```

> **Conceito: falha parcial e at-least-once**  
> Em sistemas distribuídos, um nó pode morrer no meio do caminho. Brokers maduros só consideram a mensagem “entregue” depois de um **ack**. Muitos sistemas garantem **pelo menos uma vez** (*at-least-once*): a mensagem pode ser processada de novo. Por isso jobs precisam ser **idempotentes** (processar a mesma `submission_id` duas vezes não cria dois relatórios conflitantes).

> **Conceito: consistência eventual**  
> Por um tempo, a verdade do sistema é “a prova foi recebida, mas o relatório ainda não existe” (ou “parece processando, mas o worker morreu”). Usuários e outras partes do sistema precisam ser desenhados para esse atraso — painéis de status, não uma única resposta HTTP mágica.

---

### Experimento 5 — O que a fila *não* esconde

**Hipótese:** fila não acelera a análise; só muda *quando* o custo aparece.

Com 1 worker e `ANALISE_SEGUNDOS=3`, 10 provas precisam de ≈ 30s de trabalho total (em série). Enfileirar em 1s não faz a turma ficar pronta em 1s.

Calcule:

```text
tempo_mínimo_aproximado ≈ (número de provas × ANALISE_SEGUNDOS) / número_de_workers
```

Confira com um lote e o relógio.

> **Conceito: a fila não é milagre de performance**  
> Ela melhora **latência do ack**, **resiliência** e **escala do consumidor**. O trabalho total continua existindo. Sem mais workers (ou análise mais rápida), o backlog só espera.

---

## 7. Tabela de fechamento (preencha com o grupo)

| Característica observada | Onde viu no lab | Vantagem? | Custo / risco? |
|--------------------------|-----------------|-----------|----------------|
| Desacoplamento temporal | Experimento 2 | | |
| Absorção de pico | Experimento 1 | | |
| Escala de workers | Experimento 3 | | |
| Falha parcial | Experimento 4 | | |
| Consistência eventual (status) | Experimento 1–2 | | |
| Acoplamento do caminho síncrono | Seção 4 | | |

**Perguntas finais**

1. Em qual tela do portal a comunicação **precisa** ser síncrona?  
2. O que você mudaria no worker após o experimento 4 para não perder prova?  
3. O `submission_id` ajuda em quê se a mesma mensagem for processada duas vezes?  
4. Onde entraria o armazenamento de arquivos (MinIO) neste desenho — a mensagem carregaria o PDF ou só um caminho?

---

## 8. Mapa rápido dos comandos

```bash
# subir / ver / logs
docker compose up -d --build
docker compose ps
docker compose logs -f api worker

# usar
curl -s http://localhost:8080/health
curl -s -X POST http://localhost:8080/provas -H "Content-Type: application/json" \
  -d '{"aluno":"maria","arquivo":"maria.pdf"}'
./scripts/enviar-lote.sh 15
./scripts/acompanhar.sh SEU_ID
curl -s http://localhost:8080/fila

# provocar
docker compose stop worker
docker compose start worker
docker compose up -d --scale worker=2 worker
docker kill "$(docker compose ps -q worker)"

# encerrar
docker compose down -v
```

---

## 9. O que olhar no código (depois de rodar)

| Arquivo | O que ele ensina |
|---------|------------------|
| [`lab/api/app.py`](lab/api/app.py) | produtor; `202`; status; contraste `/provas/sincrono` |
| [`lab/worker/worker.py`](lab/worker/worker.py) | consumidor; `BRPOP`; atualização de status |
| [`lab/docker-compose.yml`](lab/docker-compose.yml) | três processos no mesmo “cluster” local |

Leia com calma a função `enfileirar` na API e o loop `while rodando` no worker: ali está o desenho inteiro.

---

## 10. Próximos passos na disciplina

- **gRPC (bloco B do módulo):** consulta tipada de status (“qual a situação da prova 042 agora?”).  
- **05 Escalabilidade:** medir drenagem com 1/2/4 workers de forma mais sistemática.  
- **06 Falhas:** retry + timeout + dead letter de verdade.  
- **08 Arquivos:** PDF no MinIO; mensagem só com `object_key`.  
- **09 Observabilidade:** propagar `submission_id` em logs/traces.

---

## Encerrar o lab

```bash
docker compose down -v
```

Se você conseguiu: (1) sentir a diferença síncrono vs fila, (2) enviar com worker parado, (3) acelerar com mais um worker e (4) ver o estrago de um `kill` no meio do job — você experimentou, na prática, o essencial de **comunicação assíncrona com fila** em sistemas distribuídos.

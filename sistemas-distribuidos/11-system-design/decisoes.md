# Workshop de decisões — System design no quadro

**Módulo:** [11 — System Design](README.md)  
**Faça depois** da [teoria](teoria.md) e, de preferência, dos labs **A → C → B → D**.  
**Objetivo:** praticar os **4 passos** — sem gabarito único.  
Termos: [glossario.md](glossario.md) · fichas: [casos-entrevista.md](casos-entrevista.md).  
**Gabarito:** [decisoes-gabarito.md](decisoes-gabarito.md) — só depois de tentar.

---

## Como usar

Para cada cenário, responda no **modelo dos 4 passos** (não “nomeie o estilo” como no 10):

1. **Escopo** — 3 perguntas que você faria + o que fica de fora.  
2. **High-level** — caixas + sync/async + 1–2 números de envelope.  
3. **Deep dive** — 1 gargalo e o trade-off.  
4. **Wrap-up** — SPOF ou falha + 10× + o que medir ([09](../09-observabilidade/)).

| Critério | Pergunta rápida |
|----------|-----------------|
| Carga | Reads ≫ writes? Pico 2×? |
| Tempo na borda | O cliente precisa da resposta *agora*? ([10](../10-arquitetura/)) |
| Consistência | Pode atrasar 1 s? ([03](../03-consistencia-cap/)) |
| Evidência | Qual lab/módulo sustenta a escolha? |
| Moda | “Kafka + K8s” passa no cenário 6? |

### Modelo de resposta (exemplo fictício — não é um cenário abaixo)

> **Cenário X — “contador de likes de um post”**  
> 1. Escopo: só incrementar/ler contador; anti-fraude fora. QPS leitura 10× escrita.  
> 2. High-level: API → Redis (hot) → flush eventual ao SQL.  
> 3. Deep dive: perda no crash do Redis vs p99 — aceito eventual ([03](../03-consistencia-cap/)).  
> 4. Wrap-up: Redis SPOF → réplica; 10× = shard da chave; métrica: lag do flush.

---

## Cenário 1 — URL shortener (leitura pesada)

Produto público de encurtar links. Premissa sugerida (pode mudar): 100 M URLs novas/mês; leitura:escrita ≈ 100:1 (teoria §3).

**Perguntas (para você praticar o passo 1 — e depois *responder*)**

1. Onde está o gargalo — POST ou GET?  
2. Contador, hash ou ticket? O que o lab A mostrou sobre colisão?  
3. 301 ou 302 — o que muda no QPS da origem?  
4. Alguém dispara 1 M de `POST /encurtar` (spam): o que entra no wrap-up — **rate limit** na criação, captcha, ou só “mais pods”?

---

## Cenário 2 — Rate limiter na borda

API pública de matrícula/consulta. Há pico no prazo. Alguém propõe “só aumentar pods”.

**Perguntas**

1. Por IP, por aluno ou por rota?  
2. Redis caiu: fail-open ou fail-closed — e *por quê* neste domínio? (lab C: **503** vs **200**; cota = **429**)  
3. Isso substitui escala de app ([05](../05-escalabilidade/)) ou **protege** a camada de baixo?  
4. O lab usou **janela fixa** — o que você diria se pedissem token bucket?

---

## Cenário 3 — Notification (push + e-mail; um canal cai)

Evento de negócio (“pedido confirmado” / analogia: prova recebida). Push ao usuário + e-mail à operação. O gateway de e-mail está lento/fora.

**Perguntas**

1. A borda deve esperar o SMTP? Evidência do [10](../10-arquitetura/) lab B e lab D (202).  
2. Filas separadas por canal — por quê? Evidência: `provar-isolamento.sh` (lab D).  
3. Retry cria dois e-mails — como evita? (idempotência — **quadro**/[06](../06-falhas-timeout/); o lab D não simula reenvio)

> Prepara o **Mock 1**. Modelo falado **depois** do mock: [exemplo-notificacao.md](exemplo-notificacao.md).

---

## Cenário 4 — News feed (celebridade)

App de following. 1% dos autores tem 1000× mais seguidores. Leitura do feed é o caminho quente.

**Perguntas**

1. Fan-out on write, on read ou híbrido? Evidência do lab B (N≈40 no Compose; multiplique na oral).  
2. O que você mede para decidir o híbrido (seguidores? QPS do autor?)?  
3. Worker de fan-out parado: o que o wrap-up diz sobre consistência?

---

## Cenário 5 — Chat 1:1 + grupos pequenos

Mensagens texto, presença online, grupos ≤ 50. Sem videochamada.

**Perguntas**

1. O que é síncrono (WebSocket) e o que pode ser store-and-forward?  
2. Ordem das mensagens: por conversa? Relógio de servidor?  
3. Presença: TTL no Redis — o que acontece se o cliente sumir sem `disconnect`?

> Use a [ficha Chat](casos-entrevista.md). Mock **opcional** no caminho completo (**sem lab Compose**).

---

## Cenário 6 — “Coloca Kubernetes e Kafka e resolve”

Startup, 3 devs, produto ainda pivota. Slide de consultoria: 12 microsserviços, malha, event bus no dia 1. O problema real é um encurtador interno com 50 QPS.

**Perguntas**

1. Liste **3 razões** para *não* fazer isso agora (escada do [10](../10-arquitetura/), envelope desta teoria).  
2. Qual building block **primeiro** se o GET doer — fila, cache ou mais pods?  
3. Que evidência dos labs **A/C** (e B se couber) você mostraria à coordenação?

---

## Exercício de síntese (caminho completo)

Em **uma página** (papel ou quadro):

1. Diagrama de **um** produto (encurtador **ou** feed **ou** notificação — escolha um).  
2. **Três números** de envelope (QPS read, QPS write, storage ou #máquinas) com premissas.  
3. **Uma falha** nomeada e o comportamento esperado.  
4. **Um mecanismo** da trilha (01–10) que sustenta o deep dive.

Compare com um colega. Não precisa subir Compose.

---

## Fechamento coletivo (sala)

No quadro: “passo 1 em 5 min”; um número de envelope; um SPOF; a frase “Kubernetes não é o deep dive”.

---

## Rubrica

| Nível | Esperado |
|-------|----------|
| **Insuficiente** | Lista de ferramentas sem escopo nem número. |
| **Básico** | Passos 1–2 presentes; deep dive genérico. |
| **Bom** | 4 passos; 1 trade-off claro; cita lab ou módulo. |
| **Ótimo** | Híbrido consciente; falha + 10× + métrica; distingue moda de gargalo. |

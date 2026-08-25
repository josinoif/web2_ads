# Mock de entrevista — protocolo e scripts

**Módulo:** [11 — System Design](README.md)  
**Pré-requisito:** [teoria.md](teoria.md) · labs A–D (mínimo) · [decisoes.md](decisoes.md) · fichas relevantes  
**Duração:** 45 min de entrevista + 15 min de debrief.

> O entrevistador **não** entrega o gabarito. Ele pressiona com “e se…”.  
> O candidato **não** abre [casos-entrevista.md](casos-entrevista.md) durante o mock.

| Mock | Caso | Quando |
|------|------|--------|
| **1** | Notification | Caminho **mínimo** (lab D + ficha + cenário 3) |
| **2** | YouTube | Caminho **completo** |
| **Opcional** | Chat | Completo, se sobrar tempo (ficha 8 primeiro) |

---

## Protocolo

| Papel | Faz |
|-------|-----|
| **Candidato** | Conduz os 4 passos; desenha; pede buy-in; lista entidades/API no passo 2. |
| **Entrevistador** | Lê o script; responde só o que for perguntado; usa os “e se…”. |
| **Observador** (opcional) | Marca a rubrica em silêncio. |

### Cronômetro sugerido

| Minuto | Passo |
|--------|-------|
| 0–8 | Escopo |
| 8–20 | High-level + entidades/API + buy-in |
| 20–40 | Deep dive |
| 40–45 | Wrap-up |
| 45–60 | Debrief (rubrica + 1 melhoria) |

### Rubrica (marque 0–2 em cada)

| Critério | 0 | 1 | 2 |
|----------|---|---|---|
| Escopo | Sai desenhando | Pergunta pouco | Recorta + anota SLA |
| Envelope | Sem número | 1 número solto | Premissas + QPS/storage |
| High-level | Caos de caixas | Caminho feliz ok | Sync/async + entidades + buy-in |
| Deep dive | Genérico | 1 gargalo | Trade-off + evidência trilha |
| Wrap-up | Esquece | SPOF ou 10× | SPOF + 10× + métrica/falha |

**Insuficiente** ≤ 4 · **Básico** 5–6 · **Bom** 7–8 · **Ótimo** 9–10.

---

## Mock 1 — Notification (caminho mínimo)

**Estudo antes (sem gabarito oral):** [lab D](lab-notificacao-canais/) + ficha 5 em [casos-entrevista.md](casos-entrevista.md) + cenário 3 em [decisoes.md](decisoes.md).  
**Depois do mock:** [exemplo-notificacao.md](exemplo-notificacao.md) — não durante.

> **Evidência vs quadro:** lab D = isolamento push/e-mail (`provar-isolamento.sh`). Idempotência no retry = [06](../06-falhas-timeout/) / oral — o Compose **não** reenvia o mesmo evento.

### Enunciado (ler em voz alta)

> “Desenhe um sistema de notificações: quando um evento de negócio acontece (ex.: pedido confirmado), o usuário pode receber push, e-mail e SMS conforme preferências.”

### Requisitos ocultos (só revele se perguntarem)

| Se perguntar… | Responda |
|---------------|----------|
| Escala | 5k eventos/min no pico; 70% só push; 25% e-mail; 5% SMS |
| Latência | Push: tentar < 2 s; e-mail: até alguns minutos ok |
| Canal fora | Se e-mail cair, push/SMS **seguem** |
| Retry | At-least-once; duplicata de e-mail é ruim |
| Preferências | Usuário pode desligar SMS |
| Template | Fora detalhar o editor de texto |

### “E se…” (use 3)

1. O gateway de e-mail está em timeout — a borda do produto espera?  
2. 10× eventos no Black Friday — onde coloca a fila?  
3. O publisher retria o mesmo evento — como não mandar 2 SMS?

### Direção (debrief — não ler no mock)

- Escopo: 3 canais; preferências; sem editor visual.  
- High-level: evento → filas **por canal** → workers → gateways; 202 na borda.  
- Deep dive: idempotency key; isolamento de falha por canal ([lab D](lab-notificacao-canais/), [06](../06-falhas-timeout/), [10](../10-arquitetura/) lab B).  
- Wrap-up: SMS SPOF; lag por fila; métrica bounce/429 ([09](../09-observabilidade/)).  

### Sinais de Ótimo

Não colocou SMTP no request síncrono; separou canais; falou idempotência antes do “e se…” de retry.

---

## Mock 2 — YouTube (caminho completo)

> **Sem lab Compose neste módulo.** Evidência observável = [08](../08-armazenamento-arquivos/) (blob ≠ metadado) + ficha YouTube (CDN em 90 s). Declare isso no debrief se o candidato pedir “onde vi isso no Docker”.

### Enunciado (ler em voz alta)

> “Desenhe um serviço de vídeos estilo YouTube: upload e reprodução. Sem live, sem ads, sem comentários — a menos que sobre tempo.”

### Requisitos ocultos (só revele se perguntarem)

| Se perguntar… | Responda |
|---------------|----------|
| Watch QPS | Pico 50k starts/min (~800/s) — **escala didática**, não YouTube real |
| Upload | 500 uploads/hora no pico; vídeo médio 100 MB |
| Processamento | 360p para “publicado”; 720/1080 depois |
| CDN | Pode assumir CDN existente; detalhe a *origem* (ficha YouTube, 90 s) |
| Metadado | Título, dono, status (processing/ready), duração |
| DRM | Fora |

### “E se…” (use 3)

1. O worker de transcode cai no meio do job — o usuário vê o quê?  
2. 10× watch no feriado — transcoder ou CDN/cache?  
3. Metadado `ready` mas o objeto 360p sumiu — como detecta?

### Direção (debrief — não ler no mock)

- Escopo: upload + watch; Watch ≫ upload.  
- High-level: metadado; upload **direto** ao object storage; fila; player ← CDN ← storage.  
- Deep dive: metadado ≠ blob ([08](../08-armazenamento-arquivos/)); CDN em 90 s (ficha).  
- Wrap-up: transcoder fora do play path; 10× watch ≠ 10× ffmpeg; p99 TTFB ([09](../09-observabilidade/)).  

### Sinais de Ótimo

Separou upload de watch; citou object storage; status eventual “processando”; falou CDN sem inventar PoP.

---

## Mock opcional — Chat (caminho completo)

### Enunciado

> “Desenhe um chat: 1:1 e grupos de até 50. Texto apenas. Sem videochamada.”

Leia a [ficha Chat](casos-entrevista.md) **antes** (estudo); **não** durante o mock.

### Requisitos ocultos

| Se perguntar… | Responda |
|---------------|----------|
| Escala | 1 M DAU; pico 10k conexões; msg 200 B |
| Entrega | At-least-once; cliente pode deduplicar |
| Ordem | Por conversa; não global |
| Offline | Store + entrega ao reconectar |
| Presença | online / last seen; ~30 s |
| Mídia / E2E | Fora |

### “E se…” (use 3)

1. Um servidor WS cai.  
2. 10× msgs num grupo de 50.  
3. Dois dispositivos do mesmo usuário.

### Direção (debrief)

WS/long-poll na borda; store de mensagens; presença TTL separada; seq por conversa; sticky ou pub/sub entre gateways.  
Ponte: [01](../01-comunicacao/), [03](../03-consistencia-cap/), [06](../06-falhas-timeout/), [07](../07-cache-distribuido/).

### Sinais de Ótimo

Perguntou entrega/ordem *antes* do WS; não virou news feed.

---

## Roteiro do debrief (15 min)

1. Candidato: “o que eu faria diferente com +10 min?”  
2. Entrevistador: 1 ponto forte + 1 buraco (escopo, número, entidades ou falha).  
3. Observador: nota da rubrica.  
4. Turma: *qual building block da trilha salvou o deep dive?*

Troque os papéis entre Mock 1 e Mock 2.

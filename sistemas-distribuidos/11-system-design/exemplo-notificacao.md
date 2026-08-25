# Modelo falado — Notification system (4 passos)

**Módulo:** [11 — System Design](README.md)  

> **Não abra este arquivo antes do Mock 1.**  
> 1) Ficha Notification em [casos-entrevista.md](casos-entrevista.md) — cubra a “Direção”, 10 min no papel.  
> 2) Cenário 3 em [decisoes.md](decisoes.md).  
> 3) **Só então** compare com o texto abaixo — idealmente *depois* de um ensaio oral, não no meio do mock.

> Tom de **entrevista oral** (~8–12 min). Números = requisitos típicos do [Mock 1](mock-entrevista.md).

---

## Passo 1 — Escopo

“Notificações multi-canal a partir de um evento de negócio — push, e-mail e SMS.  
Assumo pico de **~5k eventos/min**; a maioria só push; SMS é minoria e mais caro.  
Push tenta **menos de 2 s**; e-mail pode levar minutos.  
Fora: editor visual de template, marketing blast, app iOS em si.  
Se o e-mail cair, push e SMS **continuam**. Preferências: o usuário pode desligar SMS.”

---

## Passo 2 — High-level + dados + buy-in

“Entidades: `Event { id, tipo, user_id, payload }`, `Preference`, `NotificationJob { canal, status, idempotency_key }`.  

API da borda do produto: algo como `POST /events` → **202** (aceito).  
Não chamo SMTP no request.

```text
Produto → Publisher → fila_push → worker → gateway push
                    → fila_email → worker → SMTP
                    → fila_sms   → worker → SMS
Preferencias ──► workers consultam antes de enviar
```

Está ok detalharmos **isolamento por canal** e **idempotência no retry**?”

---

## Passo 3 — Deep dive

**Filas por canal:** “Um worker de e-mail lento não pode segurar o push — por isso filas separadas. Evidência: [lab D](lab-notificacao-canais/) (`provar-isolamento.sh`); borda 202 no [10](../10-arquitetura/) lab B; filas no [01](../01-comunicacao/).”

**Idempotência:** “Publisher e workers são at-least-once. Cada job leva `idempotency_key` (ex.: `event_id + canal`). Se retriar, o gateway SMS não cobra duas vezes. Evidência de *retry/idempotência* na trilha: [06](../06-falhas-timeout/) e lab A; o **lab D** prova isolamento de canal, não o reenvio.”

**Preferências:** “Antes de enfileirar SMS, leio preferência (cache curto ok — [07](../07-cache-distribuido/)).”

---

## Passo 4 — Wrap-up

“SPOF: gateway SMS — circuit breaker / fila DLQ; não derruba push.  
10× eventos: escala workers por canal + profundidade de fila, não a borda HTTP.  
Métricas: lag por fila, taxa de bounce, 429 do provider, jobs em DLQ ([09](../09-observabilidade/)).  
Fora deste bloco: conteúdo do template e A/B de copy.”

---

## O que a trilha prova / não prova

| Diz na entrevista | Evidência |
|-------------------|-----------|
| Borda aceita sem esperar o miolo | [10](../10-arquitetura/) lab B; lab D 202 |
| Fila por canal (e-mail ≠ push) | [lab D](lab-notificacao-canais/) `provar-isolamento.sh` |
| Fila / fan-out | [01](../01-comunicacao/); notificador do 10 |
| Retry + idempotência | [06](../06-falhas-timeout/); lab A — **não** o lab D |
| SMTP/SMS de produção | **Não** — diga que ficou de fora |

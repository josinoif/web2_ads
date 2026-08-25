# Workshop de decisões — Qual estilo de arquitetura?

**Módulo:** [10 — Arquitetura](README.md)  
**Faça depois** da [teoria](teoria.md) e, de preferência, do [lab A](tutorial-monolito-vs-servicos.md). O [lab B](tutorial-sync-vs-eventos.md) fortalece os cenários 3 e híbridos.  
**Objetivo:** escolher **estilo (ou híbrido)** — sem gabarito único.  
Termos: [glossario.md](glossario.md).  
**Gabarito:** [decisoes-gabarito.md](decisoes-gabarito.md) — só depois de tentar.

---

## Como usar

Para cada cenário:

1. Nomeie o **estilo** (ou híbrido: monólito + fila, service-based, pipeline, MS + eventos…).  
2. Liste **2 ganhos** e **2 custos** (use o termo **taxa distribuída** quando fizer sentido).  
3. Cite **evidência** (lab A/B ou módulos 01–09).  
4. Diga **como validaria** (falha de um hop, p99 na borda, deploy, consistência).

| Critério | Pergunta rápida |
|----------|-----------------|
| Time / deploy | Um time ou vários ritmos? |
| Pico / latência na borda | O aluno precisa do resultado *agora*? |
| Dados | Quem é dono da escrita? ([teoria §8](teoria.md)) |
| Ops | Aguenta a taxa distribuída ([06](../06-falhas-timeout/), [09](../09-observabilidade/))? |
| Moda | “Microsserviços porque é moderno” passa no cenário 6? |

### Modelo de resposta (exemplo fictício — não é um cenário abaixo)

> **Cenário X — “app de lista de presença com 1 estagiário”**  
> 1. Estilo: **monólito layered** (modular).  
> 2. Ganhos: um deploy; transação local. Custos: falha/escala do conjunto; se o time crescer, deploy acoplado.  
> 3. Evidência: lab A — matar “análise” no monólito derruba o processo.  
> 4. Validaria: um `POST` + `kill` do processo; tempo de build único no CI.

---

## Cenário 1 — MVP de entrega de trabalhos

Turma piloto, **1 time**, 3 meses, domínio ainda muda toda sprint. Carga baixa.

**Perguntas**

1. Monólito layered, service-based ou microsserviços?  
2. Depois do [lab A](tutorial-monolito-vs-servicos.md): o que você *não* ganha ao abrir 3 processos agora?  
3. Se o pico no prazo doer, monólito + fila resolve sem MS?

---

## Cenário 2 — Quatro times, deploys independentes

Times: matrícula, boletim, avisos, biblioteca. Cada um quer soltar versão sem esperar os outros. Carga desigual (boletim explode no fim do bimestre).

**Perguntas**

1. Que estilo (ou híbrido) cabe?  
2. Ownership de dados: um Postgres compartilhado ainda é “microsserviço”?  
3. Como [05](../05-escalabilidade/) (escala seletiva) e lab A (isolamento de *processo*) entram na justificativa — e o que ainda falta para MS real?

---

## Cenário 3 — Pico de envio no prazo + análise pesada

23h59: centenas de `POST /provas`. Análise antplágio leva segundos. Aluno precisa de recibo; parecer pode ser depois.

**Perguntas**

1. Sync na borda ou EDA? Evidência do [lab B](tutorial-sync-vs-eventos.md).  
2. Isso força microsserviços — ou monólito + fila basta?  
3. Consistência: o painel da coordenação pode ver status eventual? ([03](../03-consistencia-cap/))

---

## Cenário 4 — Legados institucionais

Portal precisa falar com ERP (financeiro), sistema da secretaria e biblioteca — times e stacks diferentes, contratos antigos.

**Cola de sala (1 slide mental):**

```text
[Portal] --ACL--> [Adaptador ERP] ----> [ERP legado]
[Portal] --contrato--> [Secretaria]
         \--eventos?--> [Biblioteca]   (se o fato for estável)
```

Integração explícita ≠ “quebrar o monólito em 12 MS”. ACL protege o modelo do portal; ESB é *uma* forma de orquestrar — não a única.

**Perguntas**

1. Onde SOA / integração explícita ajuda? Onde atrapalha (ESB SPOF / SOA theater)?  
2. Orquestração vs coreografia (teoria §8) — qual cabe melhor? Onde entra **ACL**?  
3. Como isso difere de “só quebrar o monólito do portal em MS”?

---

## Cenário 5 — Compartilhar materiais entre campi (P2P?)

Alguém propõe rede P2P para PDFs entre campi, sem servidor central de arquivos.

**Perguntas**

1. Quando P2P (Tanenbaum; super-peer/DHT) faz sentido?  
2. Por que o **núcleo** de notas/matrícula quase nunca é P2P?  
3. Alternativa alinhada ao curso: object storage + metadado ([08](../08-armazenamento-arquivos/))?

---

## Cenário 6 — “Vamos de microsserviços porque é moderno”

Startup acadêmica, 2 devs, sem on-call, domínio instável. Slide de consultoria recomenda 12 microsserviços no dia 1.

**Perguntas**

1. Liste **3 razões** para *não* fazer isso agora.  
2. Qual caminho na **escada** (teoria §1): monólito → (+ fila) → service-based → MS?  
3. Depois dos labs A e B: que evidência você mostraria à coordenação?

---

## Exercício de síntese (caminho completo)

Desenhe **um** portal (borda + análise + store(s)) em uma página e anote:

1. Estilo escolhido para o estado atual (MVP **ou** 4 times — escolha um).  
2. **Dois** mecanismos da trilha que entram no desenho (ex.: fila [01], réplica [02], timeout [06], cache [07], trace [09]).  
3. Um custo da **taxa distribuída** que você aceita e como validaria.

Não precisa subir Compose — é papel/quadro. Compare com um colega.

---

## Fechamento coletivo (sala)

No quadro: MVP vs 4 times; onde entra **fila**; um custo que o [09](../09-observabilidade/) precisa cobrir se distribuir.

---

## Rubrica

| Nível | Esperado |
|-------|----------|
| **Insuficiente** | Só “microsserviços” ou “monólito” sem custo nem contexto. |
| **Básico** | Nomeia um estilo adequado ao cenário. |
| **Bom** | Estilo + 2 trade-offs; cita lab ou módulo; distingue pipeline ≠ MS. |
| **Ótimo** | Híbrido consciente; dados/ops/time; escada de evolução; síntese com mecanismos da trilha. |

# 01 — Comunicação

**Conceito:** comunicação **síncrona** (RPC/gRPC) vs **assíncrona** (filas de mensagens).  
**Mini-projeto âncora (filas):** correção / análise de provas em lote.  
**Stack:** Python 3 · Docker Compose · Redis · gRPC (bloco B)

Pré-requisito: [00 — Ambiente Docker](../00-ambiente-docker/).

---

## Por onde começar

| Material | Para quê |
|----------|----------|
| **[tutorial-correcao-prova.md](tutorial-correcao-prova.md)** | Passo a passo do lab + conceitos + experimentos |
| **[lab/](lab/)** | Código (API, worker, Compose, scripts) |

---

## Visão do módulo

| Bloco | Tema | Status |
|-------|------|--------|
| **A** | Filas — correção de provas em lote | tutorial + lab prontos |
| **B** | gRPC (consulta tipada de status) | a fazer |
| **C** | Comparação fila vs gRPC no mesmo domínio | a fazer |

---

## Bloco A em uma frase

O professor envia dezenas de provas; a API **aceita rápido** e coloca jobs numa **fila**; **workers** analisam depois. O tutorial mostra o contraste com o caminho síncrono e provoca o sistema (worker parado, escala, `kill` no meio do job) para evidenciar desacoplamento, pico, falha parcial e consistência eventual.

---

## Subir o lab (atalho)

```bash
cd sistemas-distribuidos/01-comunicacao/lab
docker compose up -d --build
curl -s http://localhost:8080/health
```

Siga o tutorial completo a partir daí.

---

## Bloco B (resumo) — gRPC

No mesmo domínio:

- Fila = “analise esta prova quando puder”  
- gRPC = “qual o status da prova 042 **agora**?”

Detalhamento na próxima iteração do material.

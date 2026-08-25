# Gabarito enxuto — Decisões (11)

**Abra só depois** de tentar [decisoes.md](decisoes.md). Não é a única resposta certa — é um espelho.

| Cenário | Direção razoável | Evidência | Risco se errar |
|---------|------------------|-----------|----------------|
| **1** Encurtador | Escopo: encurtar + redirect. High-level: POST→store; GET→cache→store. Deep dive: ID (contador, lab A) **ou** cache/301. Wrap-up: Redis SPOF; 10× reads = cache/CDN; **spam de POST** → rate limit (lab C), não só pods. | `medir-leitura.sh`, `provar-colisao.sh`, lab C | Hash curto; 301 sem discutir mudança de destino; ignorar reads≫writes; ignorar abuso |
| **2** Rate limit | Limiter na borda (Redis); lab = **janela fixa**; na oral cite token bucket / sliding window. Fail-closed se a API for crítica (**503** se Redis down; **429** se cota). **Não** substitui escala ([05](../05-escalabilidade/)) — protege. | `provar-cota.sh`, `provar-redis-down.sh` | Só “mais pods”; fail-open em pagamento; LB como único limite; chamar o lab de token bucket |
| **3** Notification | Borda 202 + fila por canal. Isolamento: lab D. Retry + idempotência = [06](../06-falhas-timeout/) (**quadro** — lab D não reenvia). E-mail down ≠ push down. | `provar-isolamento.sh` | SMTP no request; um worker para todos os canais; e-mail duplicado no retry |
| **4** Feed | Híbrido: push para comum, pull para celebridade (lab B + Exp. 4; N=40 no lab → multiplique na oral). Worker down → eventual. | `provar-celebridade.sh`, `provar-leitura.sh`, `provar-worker.sh` | Push puro para celebridade; só Kafka no slide; negar eventual |
| **5** Chat | WS na borda; persistência; presença TTL. Ordem por conversa. Grupos ≤ 50. Ficha 8 (**sem lab Compose**). | ficha 8 | Tratar chat como feed; presença sem TTL; ordem global |
| **6** Moda K8s/Kafka | Não. Escada ([10](../10-arquitetura/)); envelope (~50 QPS); primeiro cache se GET doer (lab A); rate limit se spam (lab C). | labs A/C | Taxa distribuída sem benefício |
| **Síntese** | Diagrama + 3 números + 1 falha + 1 mecanismo da trilha | — | Caixas sem premissa nem evidência |

---

## Rubrica (espelho rápido)

- Cita lab A/B/C/D ou módulo com o trade-off certo → rumo a Bom/Ótimo.  
- Só “usar Kubernetes/Kafka” sem QPS/falha → Insuficiente.

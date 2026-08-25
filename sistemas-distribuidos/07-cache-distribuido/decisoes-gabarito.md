# Gabarito enxuto — decisões (módulo 07)

> **Só depois** do workshop em [decisoes.md](decisoes.md). Abrir cedo reduz o aprendizado.

Use para calibrar — são critérios, não redação única.

---

## Cenário 1 — Boletim

1. Redis sim; local **não** basta com N APIs (cada uma diverge).  
2. Invalidate no PUT prioriza read-your-writes; TTL sozinho aceita janela stale.  
3. Exp. 3: hit com nota antiga; Exp. 4: miss + valor novo.  
4. Hit sem invalidate = prioriza velocidade (stale possível); invalidate = dado mais fresco após escrita (read-your-writes). Analogia CAP — não o teorema.

## Cenário 2 — Vagas

1. **Não** cachear contagem de vagas (ou TTL≈0 / sempre fonte).  
2. Stale → overbooking; CAP/locks dos módulos 03/04.  
3. Cachear ementa, horário, nome da disciplina (leitura estável).

## Cenário 3 — Avisos

1. TTL ~30 s costuma bastar; invalidate se o aviso for “urgente agora”.  
2. Lab: publish sem DEL → total/título antigos até flush/TTL.  
3. Boletim exige C percebida maior que o feed.

## Cenário 4 — Duas APIs

1. Dict local: api1 hit, api2 miss (ou valores diferentes).  
2. Script: Redis → api2 hit; local → api2 miss.  
3. Sim — hot key / Redis vira camada a observar ([05](../05-escalabilidade/), [09](../09-observabilidade/)).

## Cenário 5 — Stampede

1. `store_reads_na_rajada` ≈ N misses paralelos (ignore o aquecimento).  
2. Lock/single-flight no miss quente; jitter (`set-jitter.sh`) para não sincronizar expires — **no pico, combine os dois**.  
3. Mesma ideia do herd de retries no 06.

## Cenário 6 — Write-through vs aside

1. Through: cache sempre alinhado no write (mais latência/complexidade); aside: simples, precisa política de invalidate/TTL.  
2. Aside + invalidate isola o conceito e espelha o padrão mais comum em apps.

---

## Frase-modelo de fechamento

> Cache acelera porque **pode mentir um pouco**; a arquitetura define *quanto* e *quem corrige*.

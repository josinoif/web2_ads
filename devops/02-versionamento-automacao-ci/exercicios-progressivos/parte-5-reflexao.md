# Parte 5 — Reflexão Final (30 min)

**Objetivo:** Responder a perguntas provocativas sobre CI, automação e responsabilidade, consolidando uma visão crítica (nível ensino superior) sobre os limites e trade-offs das práticas do módulo.

---

## Perguntas provocativas

Responda de forma **curta mas fundamentada** (5–10 linhas por pergunta), usando conceitos do módulo e, se quiser, as referências (Humble & Farley, SRE).

---

### 1. CI aumenta velocidade ou burocracia?

- Em que condições o CI **acelera** o time (feedback rápido, menos retrabalho, integração frequente)?
- Em que condições o CI pode virar **burocracia** (pipeline lento, muitos gates, medo de mudar o pipeline)?
- Conclusão: o que faz a diferença entre “CI que acelera” e “CI que atrapalha”?

---

### 2. Automação elimina responsabilidade humana?

- A automação (pipeline, testes, deploy) **substitui** a responsabilidade do desenvolvedor ou **muda** o tipo de responsabilidade?
- Quem é responsável quando o pipeline está verde mas o código em produção falha? E quando o pipeline está mal configurado (falso positivo)?
- Em uma frase: a automação elimina ou redistribui a responsabilidade?

---

### 3. Trunk-based é sempre melhor?

- Em que contextos o **Trunk-Based Development** (uma branch principal, integração muito frequente) faz mais sentido?
- Em que contextos outra estratégia (ex.: Git Flow, branches de release) pode ser mais adequada (ex.: releases planejadas, compliance, múltiplas versões em produção)?
- Conclusão: “trunk-based é sempre melhor” é verdadeiro ou depende do contexto?

---

### 4. O que acontece se o pipeline estiver errado?

- Cenário: o pipeline **passa** (verde) mas os testes não cobrem um bug crítico, ou o lint está desatualizado e deixa passar código ruim. O que acontece com a **confiança** do time e com as **métricas** (change failure rate, lead time)?
- O que o time pode fazer para **reduzir o risco** de um pipeline “errado” (falso positivo)? (Ex.: revisar testes, manter lint atualizado, monitorar falhas em produção.)

---

## Formato de entrega

- **Texto curto** (1–2 páginas) com as quatro respostas, ou
- **Discussão em sala** com anotações do grupo sobre cada pergunta.

O importante é demonstrar que você consegue **relacionar conceitos** (CI, automação, versionamento, métricas) e **avaliar criticamente** limites e contextos, não apenas descrever ferramentas.

---

## Fechamento do módulo

Com a reflexão e a **entrega avaliativa** ([entrega-avaliativa.md](../entrega-avaliativa.md)) você encerra o Módulo 2. O módulo não é sobre ferramenta: é sobre **versionamento como controle de risco**, **CI como feedback rápido**, **automação como escalabilidade** e **pipeline como linha de produção de software** — como Humble & Farley descrevem em *Entrega Contínua*.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 4 — Quebra Controlada (1h)](parte-4-quebra-controlada.md) | **↑ Índice**<br>[Módulo 2 — Versionamento e integração contínua](../README.md) | **Próximo →**<br>[Entrega Avaliativa do Módulo 2](../entrega-avaliativa.md) |

<!-- nav:end -->

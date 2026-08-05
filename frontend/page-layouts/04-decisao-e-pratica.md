# 4. Decisão e prática: quando usar o quê

Na hora de montar um layout, você precisa decidir: **Flexbox ou Grid?** **CSS puro ou framework?** **Um breakpoint ou vários?** Esta seção organiza critérios para essas escolhas e mostra como o pensamento crítico se aplica no dia a dia e em entrevistas.

---

## Flexbox ou Grid?

Use o fluxo abaixo como guia rápido:

1. **O layout é em uma única direção (linha ou coluna)?**  
   Ex.: navbar, lista horizontal, stack vertical de cards.  
   → **Flexbox.**

2. **Preciso alinhar ou distribuir itens em uma linha/coluna (centralizar, space-between)?**  
   → **Flexbox.**

3. **O layout tem claramente linhas e colunas ao mesmo tempo (página com header, sidebar, main, footer; ou grade de produtos)?**  
   → **Grid.**

4. **Preciso nomear regiões (header, main, sidebar) para ler o CSS e manter depois?**  
   → **Grid** com `grid-template-areas`.

5. **Dentro de uma célula do Grid, os itens são em linha ou coluna?**  
   → O container da célula pode ser **Flexbox** (Grid organiza o macro; Flexbox organiza o micro).

Não existe “um é melhor que o outro”: são **complementares**. Em muitos layouts você usa os dois: Grid para a estrutura da página ou da seção, Flexbox para os componentes internos.

---

## Framework ou CSS puro?

| Situação | Tendência |
|----------|-----------|
| Projeto novo, prazo curto, equipe que já usa Bootstrap/Tailwind | **Framework** acelera (grid e componentes prontos). |
| Projeto com design system próprio (tokens, componentes já em CSS) | **CSS puro** (Flexbox/Grid) pode ser suficiente; framework pode duplicar ou conflitar. |
| Aprendizado e controle total | **CSS puro** ajuda a fixar Flexbox e Grid. |
| Manutenção de código legado que já usa framework | Seguir o **framework** existente; refatorar para “puro” só se houver benefício claro. |
| Protótipo ou MVP | **Framework** costuma ser mais rápido. |
| Performance extrema (landing crítica, mobile 3G) | **CSS puro** com apenas o necessário pode gerar menos peso que um framework completo. |

A decisão deve considerar **prazo**, **equipe**, **consistência** e **performance**. Saber Flexbox e Grid em CSS puro dá base para usar bem qualquer framework (Bootstrap, Tailwind, etc.), porque a maioria deles abstrai exatamente esses conceitos.

---

## Breakpoints: quantos e onde?

- **Mobile-first:** Comece pelo layout mobile; use `min-width` para adaptar para telas maiores. Evite “desktop-first” com muitos `max-width`, que tende a ser mais confuso.
- **Pontos de quebra comuns (referência):** 640px (sm), 768px (md), 1024px (lg), 1280px (xl). Não são obrigatórios; ajuste ao seu design (onde o layout realmente “quebra”).
- **Conteúdo antes de números:** “Em qual largura o menu lateral fica apertado?” — esse pode ser seu breakpoint. Preferir **conteúdo** a “tablet = 768px” genérico.
- **Grid com `minmax` e `auto-fill`:** Muitas vezes você reduz a necessidade de vários breakpoints — o número de colunas passa a depender do espaço disponível.

---

## Perguntas típicas em entrevistas

- **“Como você faria um layout de três colunas que vira uma em mobile?”**  
  Resposta forte: Grid com `grid-template-columns: 1fr` no mobile e `repeat(3, 1fr)` em `min-width: 768px` (ou similar); ou Flexbox com `flex-wrap` e itens com `min-width` e `flex: 1 1 0`. Mencione mobile-first.

- **“Qual a diferença entre Flexbox e Grid?”**  
  Flexbox = uma dimensão (eixo principal); Grid = duas dimensões (linhas e colunas). Dê um exemplo de uso de cada (navbar com Flexbox, página com header/sidebar/main com Grid).

- **“Como garantir que botões sejam fáceis de tocar no mobile?”**  
  Alvos de toque: mínimo 44×44px (min-height/min-width ou padding), espaçamento entre controles, eventual `@media (pointer: coarse)` para aumentar ainda mais em dispositivos touch.

- **“O que você considera para escolher entre usar um framework de CSS ou escrever o layout à mão?”**  
  Cite: prazo, tamanho da equipe, existência de design system, necessidade de performance e manutenção. Mostre que a escolha depende do contexto.

---

## Resumo da seção

- **Flexbox** para uma dimensão e alinhamento; **Grid** para duas dimensões e regiões nomeadas; os dois se complementam.
- **Framework** acelera quando o contexto permite; **CSS puro** dá controle e base para entender qualquer ferramenta.
- **Breakpoints** baseados no conteúdo, mobile-first; Grid com `minmax`/`auto-fill` reduz dependência de muitos media queries.
- Em **entrevistas**, demonstre que você sabe escolher com critério e explicar o “porquê”.

**Próximo:** [05-desafios-tecnicos.md](05-desafios-tecnicos.md) — Desafios técnicos com layout, usabilidade e decisão.

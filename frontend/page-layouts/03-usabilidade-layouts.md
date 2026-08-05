# 3. Usabilidade e layouts: conceitos e implementação

Usabilidade é o grau em que uma interface é **fácil de usar** e permite que o usuário atinja seus objetivos com eficiência e satisfação. O **layout** é uma das principais ferramentas para alcançar isso: ele define onde as coisas aparecem, quanto espaço têm e como se comportam em diferentes telas. Esta seção liga conceitos clássicos de usabilidade aos recursos de CSS (Flexbox, Grid, espaçamento, breakpoints) e mostra **como implementar** cada ideia no código.

---

## Hierarquia visual

**O que é:** A hierarquia visual indica **o que é mais importante** na tela — título principal maior e em destaque, subtítulos menores, texto de apoio discreto. O usuário “escaneia” a página e entende a ordem de importância sem precisar ler tudo.

**Por que importa:** Páginas sem hierarquia parecem planas e confusas; o usuário não sabe por onde começar. Em formulários, botões de ação principal devem se destacar; em listas, o item em foco deve ser claro.

**Como implementar:**

- **Tamanho:** Use níveis de título (`h1` > `h2` > `h3`) e tamanhos de fonte em escala (ex.: `1.5rem` para título de seção, `1rem` para corpo, `0.875rem` para secundário). No layout, reserve mais espaço para o título principal (margin-bottom maior, ou uma “área” dedicada no Grid).
- **Contraste e peso:** Títulos em `font-weight: 700`, texto secundário em `font-weight: 400` e cor mais suave (`color: #666`). O layout não muda, mas a tipografia reforça a hierarquia.
- **Posição:** O conteúdo mais importante costuma vir primeiro (topo da página ou topo do card). Em Grid, você pode garantir que o “hero” ou o título ocupe uma área inteira; em Flexbox, use `order` com cuidado (lembre-se da acessibilidade: a ordem no DOM deve continuar lógica).
- **Espaço em branco:** Dar “ar” em volta do título principal (padding/margin) aumenta o destaque. Agrupe elementos relacionados com menos espaço entre si e mais espaço entre grupos (lei da proximidade).

**Recursos necessários:** CSS de tipografia (`font-size`, `font-weight`, `line-height`), margens e paddings, Grid/Flexbox para posicionar blocos. Conhecimento de design de tipos ajuda, mas não é obrigatório para aplicar uma escala simples.

**Exemplo (trecho):**

```css
.hero {
  padding: 3rem 1.5rem;
  text-align: center;
}

.hero h1 {
  font-size: clamp(1.75rem, 5vw, 2.5rem);
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.hero p {
  font-size: 1rem;
  color: #555;
  max-width: 40ch;
  margin-inline: auto;
}
```

---

## Espaçamento e ritmo

**O que é:** Espaçamento consistente cria **ritmo visual** e separa claramente seções, cards e elementos interativos. Muito pouco espaço deixa a tela apertada; demais pode fragmentar demais a leitura.

**Por que importa:** Ritmo previsível reduz carga cognitiva: o usuário “sabe” onde esperar o próximo bloco. Em listas e formulários, espaçamento uniforme melhora a leitura e a clareza.

**Como implementar:**

- **Escala fixa:** Defina uma escala de espaçamentos (ex.: `0.25rem`, `0.5rem`, `1rem`, `1.5rem`, `2rem`, `3rem`) e use sempre esses valores para `margin`, `padding` e `gap`. Assim o layout fica consistente em toda a aplicação.
- **Gap em Flexbox e Grid:** Use `gap` no container em vez de margin nos filhos quando o objetivo for “espaço entre itens”. Facilita manutenção e evita colapso de margens.
- **Lei da proximidade:** Elementos relacionados (título + parágrafo, label + input) com menos espaço entre si; grupos diferentes com mais espaço (ex.: `margin-bottom: 1.5rem` em cada card, `gap: 1rem` entre label e input dentro do card).
- **Unidades:** Prefira `rem` para espaçamento (acessível a quem altera o tamanho da fonte do navegador). `em` pode ser útil em componentes que precisam escalar com o tamanho da fonte local.

**Recursos necessários:** Variáveis CSS (`--space-1`, `--space-2`) ou tokens do projeto, `gap`, `margin`, `padding`. Flexbox e Grid para aplicar gap em listas e grades.

**Exemplo (variáveis + gap):**

```css
:root {
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 1rem;
  --space-4: 1.5rem;
  --space-5: 2rem;
}

.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}

.card {
  padding: var(--space-3);
}

.card h3 {
  margin-bottom: var(--space-2);
}
```

---

## Alvos de toque (mobile)

**O que é:** Em dispositivos touch, os elementos clicáveis (links, botões, ícones) precisam ter **tamanho mínimo** para serem tocados com precisão e sem frustração. Diretrizes comuns falam em pelo menos **44×44 px** (Apple) ou **48×48 dp** (Material) para a área clicável.

**Por que importa:** Botões ou links muito pequenos geram erros de toque, zoom desnecessário e reclamação. Em mobile, layout e tamanho dos controles são parte direta da usabilidade.

**Como implementar:**

- **Tamanho mínimo:** Garanta `min-height` e `min-width` (ou `padding` suficiente) para que a área clicável atinja pelo menos 44px. Ex.: `min-height: 44px; padding: 0.75rem 1.25rem` no botão.
- **Área de toque maior que o visual:** O elemento pode parecer um ícone pequeno, mas o “hit area” pode ser maior (padding generoso ou `::before`/`::after` com `position: absolute` e área maior). Isso melhora a usabilidade sem alterar tanto o visual.
- **Espaço entre alvos:** Evite botões ou links colados; um pouco de `gap` ou margin reduz toques acidentais no elemento vizinho.
- **Media query para touch:** Em telas pequenas (ou quando `hover: none`), você pode aumentar padding e min-height dos controles. Ex.: `@media (max-width: 768px) { .btn { min-height: 48px; padding: 0.875rem 1.5rem; } }`.

**Recursos necessários:** CSS para `min-height`, `min-width`, `padding`; media queries; conhecimento das recomendações de a11y (WCAG 2.5.5 – Target Size).

**Exemplo:**

```css
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  padding: 0.5rem 1rem;
  /* ... */
}

@media (pointer: coarse) {
  .btn {
    min-height: 48px;
    padding: 0.75rem 1.25rem;
  }
}
```

`pointer: coarse` indica dispositivo com ponteiro “grosseiro” (touch), útil para aumentar alvos só onde faz sentido.

---

## Layout responsivo e breakpoints

**O que é:** O layout **responde** ao tamanho da viewport: colunas que viram uma, menu que vira hambúrguer, textos que não quebram a tela. Breakpoints são os “pontos de quebra” em que você muda a estrutura (ex.: 768px, 1024px).

**Por que importa:** Usuários acessam de celular, tablet e desktop. Um layout que só funciona em uma largura fixa prejudica uma parte grande do público.

**Como implementar:**

- **Mobile-first:** Comece o CSS pelo layout para telas pequenas; depois use `min-width` em media queries para ajustar para telas maiores. Ex.: uma coluna por padrão; a partir de 768px, duas colunas; a partir de 1024px, três.
- **Unidades fluidas:** Use `%`, `fr`, `vw`/`vh` com cuidado, e `clamp()` ou `min()`/`max()` para fontes e espaços que precisam crescer/encolher com a tela. Ex.: `font-size: clamp(1rem, 2.5vw, 1.25rem)`.
- **Grid e Flexbox responsivos:** `grid-template-columns: repeat(auto-fill, minmax(280px, 1fr))` já adapta o número de colunas. Em Flexbox, `flex-wrap: wrap` e larguras mínimas nos itens (`min-width: 280px; flex: 1 1 280px`) produzem efeito parecido.
- **Conteúdo que não estoura:** `max-width: 100%` em imagens e vídeos; `overflow-x: auto` ou `overflow-x: auto` em tabelas quando necessário; evite larguras fixas em px para blocos principais.

**Recursos necessários:** Media queries, unidades relativas, Flexbox com wrap e Grid com `minmax`/`auto-fill`. Conceito de viewport e de “mobile-first”.

**Exemplo (breakpoint + grid):**

```css
.gallery {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

@media (min-width: 640px) {
  .gallery {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .gallery {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## Acessibilidade (a11y) e layout

**O que é:** Acessibilidade garante que a interface seja utilizável por pessoas com diferentes capacidades (leitores de tela, navegação por teclado, baixa visão, etc.). O layout influencia **ordem de leitura**, **foco visível** e **não sobreposição de conteúdo**.

**Por que importa:** É questão de inclusão e, em muitos contextos, de conformidade (WCAG). Ordem visual confusa ou focos invisíveis tornam o produto inutilizável para parte dos usuários.

**Como implementar:**

- **Ordem do DOM:** A ordem em que os elementos aparecem no HTML é a ordem de leitura para leitores de tela. Evite usar `order` no Flexbox (ou `grid-column`/`grid-row`) de forma que inverta uma ordem lógica. Se o visual “precisa” ser diferente, avalie se dá para manter a ordem lógica no DOM e só ajustar posição com cuidado.
- **Foco visível:** Botões e links devem ter um contorno ou destaque quando focados pelo teclado (`:focus-visible`). Não remova o outline sem substituir por um estilo visível (ex.: `outline: 2px solid blue; outline-offset: 2px`).
- **Área de foco:** O elemento focado deve estar inteiro visível na tela. Scroll ou posicionamento que esconda o foco atrapalha quem navega por teclado.
- **Contraste e tamanho:** Texto legível (contraste mínimo e tamanho de fonte adequado) e alvos de toque com tamanho mínimo (como na seção anterior) fazem parte da a11y e são implementados via CSS (cor, `font-size`, `min-height`/padding).
- **Landmarks:** Use elementos semânticos (`<header>`, `<main>`, `<nav>`, `<aside>`, `<footer>`) para que leitores de tela identifiquem regiões. O layout (Grid/Flexbox) apenas posiciona esses blocos; a semântica vem do HTML.

**Recursos necessários:** HTML semântico, CSS para `:focus` e `:focus-visible`, conhecimento básico de WCAG (níveis A e AA). Testes com teclado e com leitor de tela (ex.: NVDA, VoiceOver).

**Exemplo (foco visível):**

```css
a:focus-visible,
button:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}

/* Não esconda o outline sem substituir */
a:focus {
  outline: none;
}

a:focus-visible {
  outline: 2px solid blue;
  outline-offset: 2px;
}
```

---

## Resumo: usabilidade → implementação

| Conceito de usabilidade | O que fazer no layout/CSS |
|-------------------------|----------------------------|
| **Hierarquia visual** | Tamanhos de fonte em escala, peso, cor, espaço em branco; Grid/Flex para posicionar blocos importantes. |
| **Espaçamento e ritmo** | Escala de espaços (variáveis), `gap`, margin/padding consistentes, lei da proximidade. |
| **Alvos de toque** | `min-height`/`min-width` ≥ 44–48px, padding generoso, `@media (pointer: coarse)` se necessário. |
| **Layout responsivo** | Mobile-first, media queries, Grid com `minmax`/`auto-fill`, Flexbox com wrap, unidades fluidas. |
| **Acessibilidade** | Ordem do DOM lógica, `:focus-visible`, landmarks HTML, contraste e tamanho de alvos. |

Com esses conceitos e recursos você consegue **justificar** decisões de layout (“aumentamos o alvo de toque para atender WCAG”) e **implementar** interfaces mais usáveis. Os exercícios e desafios a seguir vão fixar essa ligação na prática.

---

**Próximo:** [04-decisao-e-pratica.md](04-decisao-e-pratica.md) — Quando usar Flexbox, Grid, framework ou CSS puro.

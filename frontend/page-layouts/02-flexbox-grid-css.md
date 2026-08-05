# 2. Flexbox e CSS Grid em profundidade

Flexbox e CSS Grid são os dois mecanismos nativos do CSS para **controlar a disposição dos elementos** na tela. Entender como cada um funciona e quando usá-lo é a base para construir layouts responsivos, acessíveis e fáceis de manter — com ou sem framework.

---

## Flexbox: layout em uma dimensão

Flexbox organiza os **itens ao longo de um eixo** — uma linha (horizontal) ou uma coluna (vertical). Você define o **container** como `display: flex` e controla direção, alinhamento, quebra de linha e crescimento dos itens.

### Conceitos centrais

- **Container flex:** o elemento com `display: flex` (ou `inline-flex`). Só os **filhos diretos** viram itens flex.
- **Eixo principal:** a direção em que os itens “fluem”. Se `flex-direction` for `row` (padrão), o eixo principal é horizontal; se for `column`, é vertical.
- **Eixo transversal:** perpendicular ao principal. Serve para alinhar os itens na outra dimensão (ex.: centralizar verticalmente quando o eixo principal é horizontal).
- **Tamanho:** você controla como os itens crescem (`flex-grow`), encolhem (`flex-shrink`) e qual o tamanho base (`flex-basis`). O atalho `flex: 1 1 auto` é muito usado para “dividir o espaço igualmente”.

### Propriedades do container (o “pai”)

| Propriedade | Valores típicos | Efeito |
|-------------|-----------------|--------|
| `display` | `flex`, `inline-flex` | Ativa o Flexbox. |
| `flex-direction` | `row`, `row-reverse`, `column`, `column-reverse` | Define o eixo principal (e o sentido dos itens). |
| `flex-wrap` | `nowrap`, `wrap`, `wrap-reverse` | Itens em uma linha ou quebram para a próxima. |
| `justify-content` | `flex-start`, `flex-end`, `center`, `space-between`, `space-around`, `space-evenly` | Alinha os itens **no eixo principal**. |
| `align-items` | `stretch`, `flex-start`, `flex-end`, `center`, `baseline` | Alinha os itens **no eixo transversal**. |
| `align-content` | (como justify-content) | Só faz efeito com `flex-wrap: wrap`; alinha as **linhas** no eixo transversal. |
| `gap` | `0.5rem`, `1rem`, etc. | Espaço entre itens (evita margin nos filhos). |

### Propriedades dos itens (os “filhos”)

| Propriedade | Exemplo | Efeito |
|-------------|---------|--------|
| `flex-grow` | `1` | O item pode crescer para preencher espaço sobrando. |
| `flex-shrink` | `0` | O item não encolhe (útil para manter tamanho mínimo). |
| `flex-basis` | `200px`, `50%` | Tamanho “inicial” antes de grow/shrink. |
| `flex` | `1 1 0`, `0 0 auto` | Atalho para grow, shrink e basis. |
| `align-self` | `center`, `flex-end` | Sobrescreve `align-items` só para aquele item. |
| `order` | `-1`, `1`, `2` | Ordem visual (não muda a ordem no DOM; cuidado com acessibilidade). |

### Exemplo prático: barra de navegação

Uma navbar com logo à esquerda e links à direita é um clássico de Flexbox: um único eixo (linha), com `justify-content: space-between` para separar os dois grupos.

```css
.navbar {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  gap: 1rem;
}

.navbar-links {
  display: flex;
  gap: 1.5rem;
}
```

```html
<nav class="navbar">
  <a href="/" class="logo">Minha Marca</a>
  <div class="navbar-links">
    <a href="/sobre">Sobre</a>
    <a href="/contato">Contato</a>
  </div>
</nav>
```

- O container `.navbar` é flex em linha; `space-between` empurra logo e links para as pontas.
- `.navbar-links` também é flex, com `gap` entre os links — sem precisar de margin em cada um.

### Exemplo prático: card com conteúdo e botão no rodapé

Um card em que o conteúdo preenche o meio e o botão fica “grudado” embaixo: Flexbox em **coluna** com o conteúdo crescendo e o botão com tamanho fixo.

```css
.card {
  display: flex;
  flex-direction: column;
  min-height: 280px;
}

.card-body {
  flex: 1 1 auto; /* cresce e encolhe, base automática */
  padding: 1rem;
}

.card-footer {
  flex: 0 0 auto;
  padding: 1rem;
  border-top: 1px solid #eee;
}
```

- `flex: 1 1 auto` no `.card-body` faz esse bloco ocupar o espaço restante; o rodapé fica sempre embaixo.

### Quando Flexbox brilha

- **Um eixo só:** linhas de conteúdo (navbar, toolbar, lista horizontal), ou coluna única (stack de blocos).
- **Alinhamento fino:** centralizar algo (container com `display: flex`, `justify-content: center`, `align-items: center`).
- **Distribuição de espaço:** “estes dois blocos dividem o espaço igual” (`flex: 1` em cada).
- **Componentes de interface:** botões com ícone + texto, badges, chips.

---

## CSS Grid: layout em duas dimensões

Grid organiza os itens em **linhas e colunas ao mesmo tempo**. Você define o container com `display: grid`, declara o tamanho das faixas (colunas e linhas) e opcionalmente posiciona os itens em células específicas.

### Conceitos centrais

- **Container grid:** elemento com `display: grid`. Os filhos diretos viram itens de grid.
- **Faixas (tracks):** as colunas e linhas. Você pode usar `px`, `fr` (fração do espaço livre), `%`, `auto`, `minmax()`.
- **Célula (cell):** a interseção de uma linha com uma coluna.
- **Área (area):** um retângulo de células; você pode nomear áreas e colocar itens nelas com `grid-area`.
- **Gap:** `row-gap`, `column-gap` ou `gap` — espaço entre linhas e colunas.

### Propriedades do container

| Propriedade | Exemplo | Efeito |
|-------------|---------|--------|
| `grid-template-columns` | `1fr 1fr 1fr`, `repeat(3, 1fr)`, `200px 1fr 1fr` | Define as colunas. |
| `grid-template-rows` | `auto 1fr auto` | Define as linhas (útil para layout página inteira). |
| `grid-template-areas` | `"header header" "sidebar main" "footer footer"` | Nomeia áreas para posicionar itens. |
| `grid-template` | Atalho para rows, columns e areas. | |
| `gap` | `1rem`, `1rem 1.5rem` | Espaço entre células. |
| `justify-items`, `align-items` | `start`, `center`, `stretch` | Alinhamento dos itens dentro da célula. |
| `justify-content`, `align-content` | Para quando o grid todo é menor que o container. | |

### Propriedades dos itens

| Propriedade | Exemplo | Efeito |
|-------------|---------|--------|
| `grid-column` | `1 / 3`, `span 2` | Em quais colunas o item se estende. |
| `grid-row` | `2 / 4` | Em quais linhas. |
| `grid-area` | `header`, `1 / 1 / 2 / 3` | Nome de área ou atalho linha/coluna início/fim. |

### Exemplo prático: layout de página (header, sidebar, main, footer)

Grid é ideal quando você tem **blocos principais** (cabeçalho, menu lateral, conteúdo, rodapé) e quer definir suas posições em linha e coluna de uma vez.

```css
.page {
  display: grid;
  grid-template-rows: auto 1fr auto;
  grid-template-columns: 240px 1fr;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  min-height: 100vh;
  gap: 0;
}

.page-header   { grid-area: header; }
.page-sidebar { grid-area: sidebar; }
.page-main    { grid-area: main; }
.page-footer  { grid-area: footer; }
```

```html
<div class="page">
  <header class="page-header">...</header>
  <aside class="page-sidebar">...</aside>
  <main class="page-main">...</main>
  <footer class="page-footer">...</footer>
</div>
```

- Três linhas: altura automática (header), espaço restante (sidebar + main), automática (footer).
- Duas colunas: 240px (sidebar) e `1fr` (main). O header e o footer ocupam as duas colunas graças a `grid-template-areas`.

### Exemplo prático: galeria de cards (responsiva)

Uma grade de cards que tem 3 colunas no desktop, 2 no tablet e 1 no mobile — sem mudar a ordem dos itens no HTML.

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}
```

- `repeat(auto-fill, minmax(280px, 1fr))`: cria o máximo de colunas que cabem com no mínimo 280px cada; todas com a mesma fração do espaço. O número de colunas muda com a largura da tela.
- `gap` uniforme entre os cards.

### Quando Grid brilha

- **Layout em duas dimensões:** página com header, sidebar, main, footer; dashboards com várias regiões.
- **Grades previsíveis:** listas de produtos, galerias, tabelas visuais.
- **Áreas nomeadas:** `grid-template-areas` deixa a intenção do layout muito clara no CSS.
- **Controle por linha e coluna:** “este elemento ocupa da coluna 1 à 3 e da linha 2 à 4”.

---

## Flexbox vs Grid: quando usar cada um?

| Situação | Ferramenta típica |
|----------|-------------------|
| Uma linha ou uma coluna de itens (navbar, lista horizontal, stack vertical) | **Flexbox** |
| Centralizar um bloco (vertical e horizontal) | **Flexbox** (container com justify e align center) |
| Dividir espaço entre poucos itens em uma direção (ex.: dois painéis lado a lado) | **Flexbox** (`flex: 1`) |
| Layout completo da página (header, sidebar, main, footer) | **Grid** |
| Grade de itens (cards, produtos) com muitas células | **Grid** |
| Precisar nomear regiões (header, main, etc.) | **Grid** com `grid-template-areas` |
| Componente pequeno (botão com ícone, card interno) | **Flexbox** |
| Mistura: por exemplo, cada “célula” do Grid é um Flexbox (conteúdo interno) | **Grid + Flexbox** |

Na prática, **Grid e Flexbox se complementam**: o Grid organiza a página ou a seção em regiões; dentro de cada região, o Flexbox organiza o conteúdo em linha ou coluna. Você verá isso nos exemplos de usabilidade e nos exercícios.

---

## Resumo da seção

- **Flexbox** = uma dimensão (eixo principal + transversal). Ideal para barras, stacks, centralização e distribuição de espaço em linha ou coluna.
- **Grid** = duas dimensões (linhas e colunas). Ideal para layouts de página e grades de conteúdo.
- Use **propriedades do container** para definir direção, alinhamento e gaps; use **propriedades dos itens** para crescimento, ordem e posição específica (em Grid).
- **Gap** (flex e grid) evita depender de margin nos filhos e deixa o layout mais previsível.
- Na dúvida: “é uma linha/coluna só?” → Flexbox. “São várias linhas e colunas ou regiões nomeadas?” → Grid.

**Próximo:** [03-usabilidade-layouts.md](03-usabilidade-layouts.md) — Como conceitos de usabilidade se traduzem em layout e em código.

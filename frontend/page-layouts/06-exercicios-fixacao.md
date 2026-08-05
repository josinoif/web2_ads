# 6. Exercícios de fixação (com respostas)

Os exercícios abaixo estão ligados aos conceitos das seções anteriores: Flexbox, Grid, usabilidade e responsividade. Resolva antes de olhar as respostas; use as soluções para conferir e para ver alternativas.

---

## Bloco 1 — Flexbox

### Exercício 1.1

**Enunciado:** O que cada propriedade do container Flexbox faz em uma frase?
- `justify-content: space-between`
- `align-items: center`
- `flex-direction: column`
- `gap: 1rem`

**Resposta:**
- `justify-content: space-between` — Distribui os itens no eixo principal deixando o primeiro no início, o último no fim e o espaço restante dividido entre eles.
- `align-items: center` — Alinha os itens no eixo transversal ao centro (ex.: centraliza verticalmente quando o eixo principal é horizontal).
- `flex-direction: column` — Define o eixo principal como vertical; os itens fluem de cima para baixo.
- `gap: 1rem` — Insere um espaço fixo de 1rem entre os itens (linha e coluna, se houver wrap).

---

### Exercício 1.2

**Enunciado:** Você tem três `<div>` dentro de um container flex. Como fazer com que as duas primeiras ocupem a mesma largura e a terceira ocupe o dobro delas? (Eixo principal horizontal.)

**Resposta:**  
No container: `display: flex`. Nos dois primeiros itens: `flex: 1 1 0` (ou `flex: 1`). No terceiro: `flex: 2 1 0` (ou `flex: 2`). Assim as proporções são 1 : 1 : 2.

```css
.container { display: flex; }
.item1, .item2 { flex: 1; }
.item3 { flex: 2; }
```

---

### Exercício 1.3

**Enunciado:** Centralize um único bloco (div) no meio da tela (vertical e horizontal) usando apenas Flexbox no pai.

**Resposta:**  
O pai (ex.: `body` ou um wrapper com altura da tela) usa Flexbox com justify e align center; o filho não precisa de propriedade especial.

```css
.pai {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
```

---

## Bloco 2 — CSS Grid

### Exercício 2.1

**Enunciado:** Escreva o CSS do container para obter uma grade com 4 colunas de largura igual e espaço de 1rem entre linhas e colunas.

**Resposta:**

```css
.container {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}
```

---

### Exercício 2.2

**Enunciado:** Defina um layout de página com Grid usando `grid-template-areas`: uma linha para `header` (largura total), uma segunda linha com `sidebar` à esquerda e `main` à direita, e uma terceira para `footer` (largura total). Colunas: sidebar 200px, main o resto.

**Resposta:**

```css
.page {
  display: grid;
  grid-template-columns: 200px 1fr;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  min-height: 100vh;
}

.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }
```

---

### Exercício 2.3

**Enunciado:** O que faz `grid-template-columns: repeat(auto-fill, minmax(250px, 1fr))`?

**Resposta:** Cria quantas colunas couberem na largura do container, cada uma com no mínimo 250px e no máximo uma fração igual do espaço (1fr). Se sobrar espaço após preencher as colunas, elas se expandem. O número de colunas varia com a largura da tela (layout responsivo sem media query explícita).

---

## Bloco 3 — Usabilidade

### Exercício 3.1

**Enunciado:** Cite três formas de reforçar a hierarquia visual em um título e um parágrafo abaixo dele.

**Resposta (exemplos):**
1. **Tamanho:** Título com `font-size` maior que o parágrafo.
2. **Peso:** Título com `font-weight: 700`, parágrafo com peso normal.
3. **Espaço:** Menor espaço entre título e parágrafo (`margin-bottom` no título) e maior espaço entre esse bloco e o próximo (lei da proximidade).
4. **Cor:** Título mais escuro, parágrafo em cinza para parecer secundário.

---

### Exercício 3.2

**Enunciado:** Por que alvos de toque de pelo menos 44×44 px são recomendados em mobile? O que você pode fazer no CSS para um botão atender a isso?

**Resposta:** Em telas touch, alvos pequenos causam toques imprecisos e frustração. 44px (Apple) ou 48px (Material) é um mínimo aceito. No CSS: usar `min-height: 44px` e `min-width: 44px` (ou padding suficiente, ex.: `padding: 0.75rem 1.25rem`) no botão para que a área clicável atinja esse tamanho. Em dispositivos touch pode-se aumentar ainda mais com `@media (pointer: coarse)`.

---

### Exercício 3.3

**Enunciado:** O que é “mobile-first” em CSS responsivo? Dê um exemplo com uma coluna no mobile e duas a partir de 768px.

**Resposta:** Mobile-first significa escrever primeiro os estilos para telas pequenas e usar media queries com `min-width` para adicionar ou sobrescrever estilos em telas maiores. Exemplo:

```css
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

Assim o padrão é uma coluna; a partir de 768px passam a ser duas.

---

## Bloco 4 — Integração (Flexbox + Grid + usabilidade)

### Exercício 4.1

**Enunciado:** Dentro de um layout em Grid de 3 colunas, cada célula é um card. O card tem um título no topo, um texto que deve preencher o meio e um botão fixo no rodapé. Que técnica de layout você usa **dentro** do card e por quê?

**Resposta:** Flexbox em coluna no card. O container do card: `display: flex; flex-direction: column;`. O bloco do texto (meio): `flex: 1 1 auto` para ocupar o espaço restante. O rodapé com o botão: `flex: 0 0 auto`. Assim o botão fica sempre embaixo e o texto preenche o meio. Grid define a posição dos cards; Flexbox define a estrutura interna de cada card.

---

### Exercício 4.2

**Enunciado:** Você tem uma navbar com logo e cinco links. Em mobile quer que os links sumam e apareça um ícone de menu. Além do layout (Flexbox), que preocupações de **usabilidade** e **acessibilidade** você deve ter?

**Resposta (resumido):**
- **Alvos de toque:** Ícone do menu e cada link do menu expandido com pelo menos 44px de altura/largura clicável.
- **Ordem e leitura:** Manter a ordem lógica no DOM para leitores de tela (ex.: menu pode estar no HTML depois do logo e ser posicionado com CSS ou exibido/oculto com aria).
- **Foco:** Garantir que o foco do teclado vá para o menu quando aberto e que o foco seja visível (`:focus-visible`).
- **Indicação de estado:** Deixar claro se o menu está aberto ou fechado (aria-expanded, ícone que muda ou texto “Abrir menu” / “Fechar menu”).

---

## Soluções comentadas dos desafios (resumo)

### Desafio 1 — Layout de página (header, main, footer)

**Com Flexbox:**

```css
body, .page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.page-header { flex: 0 0 60px; }
.page-main   { flex: 1 1 auto; padding: 1rem; }
.page-footer { flex: 0 0 auto; }
```

**Com Grid:**

```css
.page {
  min-height: 100vh;
  display: grid;
  grid-template-rows: 60px 1fr auto;
}

.page-header { grid-row: 1; }
.page-main   { grid-row: 2; padding: 1rem; }
.page-footer { grid-row: 3; }
```

Use `<header>`, `<main>` e `<footer>` no HTML para landmarks.

---

### Desafio 2 — Grade de cards responsiva

**Grid com minmax:**

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.card a,
.card button {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
}
```

Breakpoint alternativo: media queries com 1, 2 e 3 colunas (ex.: 1fr; 640px → 2fr; 1024px → 3fr).

---

### Desafio 5 — Escolha de abordagem (respostas sugeridas)

**Projeto A (landing, identidade forte, 1 dev, 1 mês):**  
Recomendação: CSS puro com Grid e Flexbox, ou Tailwind se o dev já dominar. Justificativa: identidade visual forte se beneficia de controle fino; prazo de 1 mês permite configurar um sistema simples (variáveis, um ou dois breakpoints). Framework completo (Bootstrap) pode atrapalhar a customização.

**Projeto B (painel interno, Bootstrap na equipe):**  
Recomendação: Bootstrap. Justificativa: equipe já conhece; painéis com tabelas e formulários se beneficiam dos componentes prontos; prazo curto e consistência interna pesam a favor de manter o stack atual. CSS puro aumentaria tempo de desenvolvimento sem ganho claro nesse contexto.

---

## Referências rápidas

- **Flexbox:** [MDN – Flexbox](https://developer.mozilla.org/pt-BR/docs/Web/CSS/CSS_Flexible_Box_Layout)
- **Grid:** [MDN – CSS Grid Layout](https://developer.mozilla.org/pt-BR/docs/Web/CSS/CSS_Grid_Layout)
- **Usabilidade e acessibilidade:** [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/) (inclui Target Size – 2.5.5)
- **Exemplo completo com Bootstrap:** [grid-layout.md](grid-layout.md) (neste repositório)

---

*Com esses exercícios e desafios você fixa Flexbox, Grid, usabilidade e decisão técnica — a base para construir layouts profissionais em qualquer projeto.*

**Voltar ao índice:** [README.md](README.md)

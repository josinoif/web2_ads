# 5. Desafios técnicos

Os desafios abaixo colocam você em situações reais: layout responsivo, usabilidade e escolha de ferramenta (CSS puro ou framework). Resolva pelo menos um com **CSS puro** (Flexbox e/ou Grid) e um com o **framework** que você estiver usando no curso (Bootstrap, Tailwind, etc.) para comparar abordagens.

---

## Desafio 1 — Layout de página (header, main, footer)

**Cenário:** Você precisa implementar uma página com **cabeçalho fixo no topo**, **conteúdo principal** que preenche o espaço disponível e **rodapé** no final. Em viewports altas, o rodapé deve ficar embaixo da tela (no final do scroll); em telas curtas, a página deve ter no mínimo a altura da viewport (100vh) sem que o rodapé “suba” demais.

**Objetivo:** Montar essa estrutura com **CSS puro** (Flexbox ou Grid), sem framework.

**Entregas:**
- Header com altura fixa (ex.: 60px), main com `flex: 1` ou equivalente (cresce para preencher) e footer com altura automática.
- Página com `min-height: 100vh` e layout em coluna (Flexbox) ou Grid com `grid-template-rows: auto 1fr auto`.
- Conteúdo do main com um pouco de padding; ao aumentar o conteúdo, o footer deve descer naturalmente.

**Perguntas para reflexão:**
- Por que Flexbox ou Grid foi mais adequado nesse caso?
- Como você garantiria que o header e o footer fossem landmarks acessíveis (elementos semânticos)?

---

## Desafio 2 — Grade de cards responsiva com alvos de toque

**Cenário:** Uma listagem de **cards clicáveis** (produtos ou notícias) deve funcionar bem em desktop (várias colunas) e em mobile (uma coluna, botões fáceis de tocar).

**Objetivo:** Implementar a grade com **CSS puro** (Grid ou Flexbox) e garantir que cada card tenha **área clicável** com pelo menos 44px de altura nos elementos interativos e espaçamento adequado entre cards.

**Entregas:**
- Grade que exiba 3 colunas em telas largas, 2 em médias e 1 em pequenas (media queries ou `repeat(auto-fill, minmax(...))`).
- Cada card com título, imagem (ou placeholder) e botão “Ver mais”. O botão (ou o card inteiro, se for link) com `min-height: 44px` na área clicável.
- `gap` entre os cards; sem margin negativa que cause sobreposição.

**Perguntas para reflexão:**
- Como você aumentaria o “hit area” do botão em mobile sem alterar muito o visual?
- Qual critério você usou para os breakpoints (ou para o `minmax`)?

---

## Desafio 3 — Navbar responsiva (desktop horizontal, mobile “hambúrguer”)

**Cenário:** Uma barra de navegação com logo à esquerda e links à direita. Em **desktop** os links ficam em linha; em **mobile** os links ficam ocultos e um ícone de menu (hambúrguer) aparece. Ao clicar no ícone, um menu em coluna é exibido abaixo (ou sobrepondo) o header.

**Objetivo:** Fazer o **layout** da navbar (Flexbox para alinhar logo e links / ícone) e o **espaçamento**; o comportamento de abrir/fechar o menu pode ser com JavaScript simples ou apenas com CSS (`:focus-within` ou checkbox hack). Foque em:
- Navbar com `display: flex`, `justify-content: space-between`, `align-items: center`, altura mínima e padding.
- Links com `gap` entre si e alvos de toque adequados em mobile (min-height 44px no ícone e nos links do menu expandido).

**Entregas:**
- HTML semântico (`<nav>`, lista de links).
- Layout da barra em Flexbox; menu mobile pode ser uma lista que aparece/esconde (com ou sem JS).
- Em mobile, ícone e itens do menu com área de toque ≥ 44px.

**Perguntas para reflexão:**
- Como manter a ordem de leitura lógica para leitores de tela quando o menu está “escondido” no mobile?
- Se usasse um framework (Bootstrap, Tailwind), o que você ganharia e o que perderia nesse componente?

---

## Desafio 4 — Formulário em duas colunas (desktop) e uma (mobile)

**Cenário:** Formulário de cadastro com vários campos. Em **desktop** você quer duas colunas (ex.: nome e sobrenome lado a lado); em **mobile**, uma coluna. Cada campo deve ter label visível e alinhada; espaçamento consistente entre grupos (proximidade).

**Objetivo:** Layout do formulário com **Grid** ou **Flexbox** e media query (ou Grid com `minmax`). Garantir:
- Labels e inputs alinhados; espaço entre label e input menor que entre um grupo de campo e o próximo.
- Dois campos por “linha” em desktop, um em mobile.
- Botões de envio/cancelar com alvo de toque adequado.

**Entregas:**
- Estrutura HTML com `<form>`, `<label>` e `<input>` (e botões). Cada par label+input pode estar em um `<div>` ou `<fieldset>`.
- CSS que organize os campos em 2 colunas a partir de um breakpoint (ex.: 600px) e 1 coluna abaixo disso.
- Escala de espaçamento (ex.: `--space-2` entre label e input, `--space-4` entre grupos).

**Perguntas para reflexão:**
- Como você garantiria que o foco (teclado) fique visível nos inputs e botões?
- Que mudanças faria se o design pedisse três colunas em telas muito grandes?

---

## Desafio 5 — Escolha de abordagem (sem código)

**Cenário:** Dois projetos:
- **A:** Landing page de um produto, forte identidade visual, prazo de 1 mês, 1 dev front.
- **B:** Painel administrativo interno, muitas tabelas e formulários, prazo curto, equipe que já usa Bootstrap.

**Objetivo:** Para cada projeto, recomende **uma** abordagem (CSS puro com Grid/Flexbox, Bootstrap, Tailwind ou outro) e justifique em **até 5 linhas** considerando: prazo, consistência, usabilidade (alvos de toque, hierarquia) e manutenção.

**Entregas:**
- Texto para o Projeto A (recomendação + justificativa).
- Texto para o Projeto B (recomendação + justificativa).

Esse desafio exercita **decisão técnica** e **comunicação** — útil em reuniões e entrevistas.

---

## Como usar os desafios

- **Ordem sugerida:** 1 (estrutura da página) → 2 (grade) → 3 (navbar) → 4 (formulário) → 5 (decisão).
- **Tempo:** Aproximadamente 1–2 h por desafio de implementação; 5 pode ser 20–30 min de escrita + discussão.
- **Comparação:** Refazer o Desafio 1 ou 2 com um framework (ex.: Bootstrap) e comparar: velocidade, liberdade visual e peso do CSS.

Respostas comentadas e trechos de código dos desafios 1, 2 e 5 estão na seção **Soluções comentadas dos desafios** do arquivo [06-exercicios-fixacao.md](06-exercicios-fixacao.md), junto com os exercícios de fixação por bloco.

---

**Próximo:** [06-exercicios-fixacao.md](06-exercicios-fixacao.md) — Exercícios de fixação com respostas.

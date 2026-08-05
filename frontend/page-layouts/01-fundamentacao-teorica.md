# 1. Fundamentação teórica: o que é layout e por que importa

Antes de mergulhar em Flexbox e CSS Grid, vale entender **o que** é layout no contexto web e mobile e **por que** ele é decisivo para o produto, para o usuário e para o seu dia a dia como desenvolvedor.

---

## O que é layout (na web e no mobile)?

**Layout** é a maneira como os elementos da interface — textos, imagens, botões, menus, cards — são **organizados no espaço da tela**. Quem define posição, tamanho, agrupamento e ordem visual é o layout. Não é “só estética”: é a estrutura que permite ao usuário **enxergar, entender e agir** de forma previsível e confortável.

Na **web**, o layout precisa funcionar em telas muito diferentes: desktop largo, tablet, celular em vertical e horizontal. No **mobile** (apps ou sites responsivos), a área útil é menor, os dedos substituem o mouse e a leitura costuma ser em blocos menores. Ou seja: o mesmo “conteúdo” pode exigir **estruturas diferentes** conforme o contexto (ou uma única estrutura que se adapte bem — o famoso layout responsivo).

---

## Por que layout importa?

Três razões centrais:

1. **Usabilidade** — Um layout claro comunica hierarquia (o que é mais importante), reduz confusão e ajuda o usuário a concluir tarefas (preencher um formulário, achar um produto, ler um artigo). Layout bagunçado ou que quebra em certas telas gera abandono e reclamação.
2. **Consistência e manutenção** — Em projetos reais, várias páginas e componentes precisam seguir a mesma “gramática” (margens, colunas, alinhamento). Quem domina as ferramentas de layout (Flexbox, Grid, ou um sistema de grid de framework) consegue manter e evoluir o código sem “gambiarras” de posicionamento.
3. **Mercado** — Vagas de front-end e full-stack pedem “layout responsivo”, “experiência com CSS”, “conhecimento em Flexbox/Grid”. Entrevistas e testes práticos frequentemente envolvem montar uma tela que se comporte bem em desktop e mobile. Saber explicar *por que* você escolheu uma estrutura (ex.: “usei Grid aqui porque é um layout em duas dimensões”) diferencia você de quem só copia código.

Resumindo: layout não é “enfeite”. É **fundação** da interface e da experiência do usuário.

---

## Layout e mercado de trabalho

No dia a dia você vai:

- **Implementar designs** — Um protótipo (Figma, Adobe XD, etc.) chega com colunas, espaçamentos e breakpoints; seu trabalho é traduzir isso em HTML e CSS (Flexbox, Grid, ou classes de um framework) de forma fiel e responsiva.
- **Corrigir quebras** — “No celular o botão some” ou “a tabela estoura a tela” são problemas de layout. Quem entende container, overflow, media queries e flex/grid resolve mais rápido.
- **Participar de decisões** — “Damos duas colunas no mobile ou uma?” “O menu vira hambúrguer ou fica em baixo?” Essas escolhas têm impacto em usabilidade e em implementação; saber as opções e os trade-offs ajuda a equipe a decidir.
- **Entrevistas** — Perguntas como “como você faria um layout de três colunas que vira uma em mobile?” ou “qual a diferença entre Flexbox e Grid?” aparecem em processos seletivos. A fundamentação que você verá neste material sustenta suas respostas.

Ou seja: dominar layout **abre portas** e **reduz atrito** em qualquer projeto front-end.

---

## Conceitos que atravessam todo o tema

Antes de entrar em Flexbox e Grid, fixe estes conceitos; eles voltarão em cada seção.

| Conceito | O que significa |
|----------|------------------|
| **Container e itens** | O **container** é o elemento que “governa” a disposição (ex.: uma `div` com `display: flex`). Os **itens** são os filhos diretos que são posicionados por essa regra. |
| **Eixo e direção** | Em Flexbox falamos em **eixo principal** e **eixo transversal**; a **direção** (linha ou coluna) define como os itens fluem. Em Grid falamos em **linhas e colunas** (duas dimensões ao mesmo tempo). |
| **Responsividade** | O layout se **adapta** ao tamanho da tela (media queries, unidades relativas, grid/flex que reorganiza). Não é “uma página para desktop e outra para mobile”, e sim uma estrutura que responde ao espaço disponível. |
| **Acessibilidade** | A **ordem visual** (o que aparece primeiro na tela) e a **ordem no código** (DOM) devem fazer sentido para leitores de tela e navegação por teclado. Layout não é só “onde fica bonito”; é “onde fica correto” para todos os usuários. |

Na próxima seção entramos em **Flexbox e CSS Grid** em profundidade: como funcionam, quando usar cada um e como eles sustentam os layouts que você vai construir na prática.

---

**Próximo:** [02-flexbox-grid-css.md](02-flexbox-grid-css.md) — Flexbox e CSS Grid em profundidade.

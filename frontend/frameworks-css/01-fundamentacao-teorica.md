# 1. Fundamentação teórica: o que são frameworks CSS e por que o mercado usa

Antes de falar de Bootstrap, Tailwind ou qualquer nome da moda, vale entender **o que** é um framework CSS e **por que** ele existe. Isso vai te dar base para defender (ou questionar) o uso deles em projetos reais e em processos seletivos.

---

## O que é um framework CSS?

Um **framework CSS** é um conjunto de estilos, componentes e convenções que alguém já escreveu e organizou para você reutilizar. Em vez de criar do zero um grid responsivo, botões, cards e formulários, você usa classes, variáveis ou componentes que o framework já oferece.

Resumindo em uma frase: **é uma “biblioteca” de decisões de design e implementação em CSS** (e às vezes um pouco de JavaScript) para acelerar e padronizar a construção de interfaces.

- **Não substitui** o conhecimento de CSS: você ainda precisa entender layout (flexbox, grid), especificidade, responsividade e acessibilidade.
- **Complementa** o trabalho: reduz retrabalho, mantém consistência visual e, em muitos times, é a escolha explícita para “como a gente estiliza as coisas aqui”.

---

## Por que frameworks existem?

Três motivos centrais:

1. **Economia de tempo** — Grids, botões, formulários e modais são repetidos em quase todo projeto. Ter isso pronto (e testado) corta horas de desenvolvimento e de bugs de alinhamento e breakpoint.
2. **Consistência** — Em equipe, “cada um faz do seu jeito” vira pesadelo de manutenção. Um framework impõe um vocabulário comum: as mesmas classes, os mesmos espaçamentos, o mesmo sistema de cores.
3. **Foco em produto, não em roda** — O valor do negócio está em regras de negócio, UX e entrega. Reimplementar um dropdown pela décima vez não entrega valor; usar um que já existe, sim.

Isso não significa que “sempre usar framework” seja a resposta certa. Significa que **a decisão de usar ou não deve ser consciente**, não por moda ou por “sempre foi assim”.

---

## Frameworks no mercado de trabalho

No dia a dia das empresas, você vai esbarrar em:

- **Projetos legados** que já usam Bootstrap (ou outro) há anos. Saber ler e estender esse código é parte do trabalho.
- **Novos projetos** em que a equipe escolhe Tailwind (ou similar) como padrão. Entender a filosofia (utility-first, design tokens) ajuda a seguir o padrão e a propor melhorias.
- **Entrevistas** em que perguntam “por que usaram X?” ou “como fariam um layout responsivo com Y?”. Quem tem fundamentação e prática se destaca.
- **Discussões de arquitetura** em que alguém propõe “vamos tirar o framework e fazer tudo em CSS puro” (ou o contrário). Quem sabe prós e contras consegue participar da decisão com critério.

Ou seja: o mercado não exige que você “só saiba Bootstrap” ou “só Tailwind”. Exige que você **saiba trabalhar com ferramentas de UI, entenda trade-offs e consiga se adaptar** a um stack que já existe ou a uma nova escolha.

---

## Quando um framework ajuda (e quando atrapalha)

### Ajuda quando:

- O **prazo é curto** e o produto precisa de uma UI funcional e consistente rápido.
- A **equipe é grande** ou rotativa, e um padrão visual único reduz conflito e onboarding.
- O **projeto não exige identidade visual única** (ex.: painel interno, MVP, protótipo).
- Você quer **menos CSS customizado para manter** e mais foco em lógica e UX.

### Pode atrapalhar quando:

- O **design é muito específico** e o framework vira luta constante para “escapar” do padrão.
- O **bundle size** é crítico (ex.: site público em 3G) e o framework traz peso desnecessário.
- O time **já tem um design system próprio** (tokens, componentes) e o framework duplica ou conflita com isso.
- O objetivo é **aprender CSS a fundo**; aí faz sentido menos abstração, não mais.

Nenhuma dessas listas é “regra absoluta”. O importante é **saber explicar** por que, no seu contexto, um framework fez sentido (ou não).

---

## Conceitos que continuam valendo com ou sem framework

Independentemente da ferramenta, esses conceitos seguem em pé:

| Conceito | Por que importa |
|----------|------------------|
| **Grid e layout** | Flexbox e CSS Grid são a base; frameworks só expõem isso via classes ou componentes. |
| **Breakpoints e responsividade** | Mobile-first, fluid layout e acessibilidade não são “mágica” do framework. |
| **Especificidade e cascata** | Conflitos de estilo aparecem quando você mistura framework com CSS próprio. |
| **Acessibilidade** | Framework pode ajudar (componentes semânticos), mas a responsabilidade final é do desenvolvedor. |
| **Performance** | Tamanho de CSS, critical path e uso de variáveis/tokens afetam carregamento. |

Conclusão: **framework não substitui fundamentos**. Ele acelera e padroniza; a base continua sendo CSS e boas práticas de front-end.

---

## Resumo da seção

- Framework CSS = conjunto reutilizável de estilos, componentes e convenções.
- Existe para ganhar tempo, manter consistência e deixar o time focar em valor de produto.
- No mercado, você encontra projetos com e sem framework; o que importa é saber trabalhar com eles e argumentar escolhas.
- Usar framework faz sentido em prazos curtos, times grandes e UIs padrão; pode não fazer quando o design é muito único ou o peso do bundle é crítico.
- Os fundamentos de CSS (layout, responsividade, acessibilidade, performance) continuam essenciais com ou sem framework.

Na próxima seção entramos nos **frameworks mais usados no mercado**, com visão crítica de pontos fortes e fracos de cada um.

**Próximo:** [02-frameworks-no-mercado.md](02-frameworks-no-mercado.md)

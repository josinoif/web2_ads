# 2. Frameworks CSS no mercado: visão crítica

Esta seção percorre os frameworks CSS mais presentes no mercado, com foco em **pontos fortes**, **pontos fracos** e **contextos em que cada um brilha (ou não)**. A ideia é você conseguir comparar com critério e não só repetir o que está na documentação.

---

## Bootstrap

**Site oficial:** [getbootstrap.com](https://getbootstrap.com/)

**O que é:** Framework de componentes e grid. Você usa classes como `btn`, `card`, `container`, `row`, `col-md-6` e monta a interface com peças prontas. Nasceu no Twitter, hoje é mantido de forma aberta e é um dos mais usados no mundo.

### Pontos fortes

- **Documentação excelente** — Exemplos, snippets e temas. Qualquer dúvida de “como fazer X” tende a ter resposta na doc ou no Stack Overflow.
- **Ecossistema grande** — Temas, plugins, integrações com React/Vue/Angular (ex.: react-bootstrap). Muitas vagas pedem “conhecimento em Bootstrap”.
- **Produtividade rápida** — Em pouco tempo você monta dashboard, formulário e tabela responsivos sem escrever quase nenhum CSS próprio.
- **Grid estável** — Sistema de 12 colunas com breakpoints claros (`sm`, `md`, `lg`, `xl`). Quem entende o grid entende a maior parte dos layouts.

### Pontos fracos

- **Aparência “de Bootstrap”** — Sites não customizados parecem todos iguais. Para identidade visual forte, é preciso sobrescrever bastante.
- **Peso** — O CSS completo é pesado. Usar só o que precisa (build customizado ou módulos) exige configuração.
- **Especificidade alta** — Conflitos com CSS próprio são comuns; às vezes você precisa `!important` ou classes mais específicas para “ganhar” do Bootstrap.
- **JavaScript** — Componentes como modal e dropdown dependem de JS (ou de uma lib que replique o comportamento). Em projetos 100% estáticos, isso pode ser desnecessário.

### Quando faz sentido

- MVP, protótipo ou painel interno com prazo curto.
- Equipe que já conhece Bootstrap e o projeto não exige identidade visual única.
- Manutenção de projeto legado que já usa Bootstrap.

### No mercado

Muito citado em vagas de front-end e full-stack. Vale saber montar layout, customizar tema (variáveis CSS/Sass) e integrar com um framework JS (React, Vue, etc.) se for o stack da empresa.

---

## Tailwind CSS

**Site oficial:** [tailwindcss.com](https://tailwindcss.com/)

**O que é:** Framework **utility-first**: em vez de componentes prontos (um “botão”), você compõe o visual com classes utilitárias como `flex`, `gap-4`, `bg-blue-500`, `rounded-lg`, `px-4 py-2`. O “componente” é o que você monta no HTML (ou no seu React/Vue).

### Pontos fortes

- **Controle total do visual** — Você não luta contra o estilo padrão de um componente; você define tudo com utilitários. Ótimo para design único e design systems customizados.
- **Bundle enxuto** — Em produção, só entram as classes que você usa (purge/tree-shaking). O CSS final costuma ser menor que o de um Bootstrap completo.
- **Design tokens na mão** — Cores, espaçamentos e breakpoints são configuráveis (tailwind.config). Ótimo para manter consistência com identidade da marca.
- **Tendência no mercado** — Muitas startups e projetos novos adotam Tailwind; saber usar aumenta o leque de vagas e de projetos que você entende rápido.

### Pontos fracos

- **HTML “poluído”** — Muitas classes no mesmo elemento podem assustar no início e dificultar leitura se não houver convenção (ex.: extrair para componentes).
- **Curva de aprendizado** — É preciso decorar (ou consultar) o nome das classes (espaçamento, cores, breakpoints). No começo pode ser mais lento que pegar um componente pronto.
- **Não é “componente pronto”** — Se você quer um modal ou um dropdown “do zero” em 5 minutos, Bootstrap pode ser mais rápido; com Tailwind você monta (ou usa um headless UI).

### Quando faz sentido

- Projeto com identidade visual definida e necessidade de customização.
- Time que gosta de utility-first e já tem (ou quer) um design system.
- Quando o tamanho do CSS e a manutenção a longo prazo importam.

### No mercado

Muito presente em vagas de front-end moderno, React e Next.js. “Tailwind” aparece em descrições de vaga com frequência crescente. Vale saber configurar, usar responsividade (`sm:`, `md:`) e compor componentes reutilizáveis (em React/Vue/Svelte ou até com @apply em CSS).

---

## Bulma

**Site oficial:** [bulma.io](https://bulma.io/)

**O que é:** Framework baseado em **Flexbox**, focado em simplicidade e em **apenas CSS** — sem JavaScript. Componentes como navbar, card e form são estilizados com classes; o comportamento (dropdown, modal) você implementa ou usa uma lib à parte.

### Pontos fortes

- **Simples de aprender** — Menos “coisas” que Bootstrap; nomenclatura clara (`box`, `section`, `columns`).
- **Zero JS como dependência** — Ideal para projetos estáticos ou quando você já usa outro framework JS e não quer conflito.
- **Modular** — Dá para importar só o que precisa (Sass), reduzindo tamanho final.
- **Visual limpo** — Design moderno por padrão; menos “pesado” que Bootstrap clássico.

### Pontos fracos

- **Comunidade menor** — Menos temas, menos respostas prontas, menos vagas que citam Bulma especificamente.
- **Componentes “parados”** — Sem JS, coisas como modal e dropdown precisam de código próprio ou de lib externa.
- **Menos “onipresente” no mercado** — Você pode usar em projeto próprio ou em time que adotou; raro ver como requisito em vaga.

### Quando faz sentido

- Projeto que quer grid e componentes bonitos sem depender de jQuery ou do JS do framework.
- Time que prefere controle total sobre comportamento e só quer ajuda no visual.
- Protótipos ou sites institucionais com visual limpo.

### No mercado

Menos citado em vagas que Bootstrap e Tailwind. Ainda assim, conhecer Bulma mostra que você sabe comparar abordagens (componentes vs utilitários, com/sem JS) e se adapta a stacks diferentes.

---

## Foundation (Zurb)

**Site oficial:** [get.foundation](https://get.foundation/)

**O que é:** Framework responsivo e acessível, com grid avançado, componentes ricos e foco em acessibilidade e em projetos de maior porte. Criado pela Zurb, muito usado em aplicações corporativas e em produtos que precisam de suporte a acessibilidade “de fábrica”.

### Pontos fortes

- **Grid poderoso** — Sistema flexível, blocos de construção sofisticados; quem precisa de layouts complexos e bem controlados costuma gostar.
- **Acessibilidade em foco** — Componentes e documentação com orientações de a11y; atrativo para projetos que precisam cumprir normas (ex.: WCAG).
- **Customizável** — Sass, variáveis e configurações permitem adaptar bastante o framework ao projeto.

### Pontos fracos

- **Curva de aprendizado maior** — Mais conceitos e opções que Bootstrap; pode parecer “pesado” para um projeto simples.
- **Comunidade menor que Bootstrap** — Menos exemplos e menos vagas que mencionam Foundation.
- **Documentação e atualizações** — Em alguns momentos a doc e o ritmo de releases ficaram atrás de Bootstrap e Tailwind.

### Quando faz sentido

- Projetos que priorizam acessibilidade e layouts complexos.
- Empresas ou produtos que já adotaram Foundation como padrão.
- Quando você precisa de um “Bootstrap mais robusto” em termos de grid e a11y.

### No mercado

Aparece em vagas de empresas maiores e em projetos com requisitos fortes de acessibilidade. Saber que existe e como se compara a Bootstrap/Tailwind já é um diferencial em discussões de arquitetura.

---

## Materialize CSS / Material UI (MUI)

**Sites oficiais:** [Materialize CSS](https://materializecss.com/) · [Material UI (MUI)](https://mui.com/)

**Materialize** é um framework CSS que implementa o **Material Design** (linguagem visual do Google). **Material UI (MUI)** é uma biblioteca de componentes para **React** que também segue o Material Design; hoje é muito usada em projetos React.

### Materialize (CSS)

- **Pontos fortes:** Visual reconhecível (Material), componentes prontos, documentação com exemplos.
- **Pontos fracos:** Menos atualizado que os concorrentes; customizar além do Material pode ser trabalhoso; menos presente em vagas novas.
- **Quando faz sentido:** Protótipos ou produtos que querem explicitamente a cara do Material Design e não usam React.

### Material UI (MUI) — React

- **Pontos fortes:** Componentes React ricos (data grid, date picker, etc.), tema customizável, muito usado em dashboards e aplicações enterprise em React.
- **Pontos fracos:** Bundle grande; curva de aprendizado (temas, sobrescrita de estilos); acoplamento a React.
- **Quando faz sentido:** Projeto React que precisa de muitos componentes complexos e quer adotar Material Design como base.

### No mercado

MUI é bem citado em vagas de **React** e front-end. Materialize (CSS puro) aparece menos. Se o foco da vaga for React + UI rápida e “corporativa”, MUI é um nome que vale conhecer.

---

## Resumo comparativo (em uma tabela)

| Framework      | Força principal           | Fraqueza principal        | Melhor quando…                    |
|----------------|---------------------------|---------------------------|-----------------------------------|
| **Bootstrap**  | Componentes prontos, doc  | Visual genérico, peso     | MVP, legado, equipe que já usa    |
| **Tailwind**   | Flexibilidade, bundle     | Muitas classes, curva     | Design único, design system, React/Next |
| **Bulma**      | Simples, só CSS           | Poucos componentes, comunidade | Sem JS, protótipo limpo       |
| **Foundation** | Grid e a11y               | Complexidade, comunidade | Projetos grandes, acessibilidade  |
| **Materialize**| Material Design (CSS)     | Menos atualizado          | Protótipo Material, sem React    |
| **MUI**        | Componentes React ricos   | Peso, acoplamento React   | App React enterprise, dashboard  |

---

## E o “CSS puro”?

Não é framework, mas é a base de tudo. Em muitos projetos:

- **Não se usa framework** — Design system próprio, CSS modules, ou só CSS bem organizado.
- **Framework é usado em parte** — Por exemplo, só o grid de um framework e o resto em CSS próprio.

Saber **quando não usar** um framework também é decisão técnica: projetos pequenos, páginas únicas, ou quando o time já tem um sistema de design implementado em CSS/SCSS.

---

## Referências (páginas oficiais)

| Framework | URL |
|-----------|-----|
| **Bootstrap** | [getbootstrap.com](https://getbootstrap.com/) |
| **Tailwind CSS** | [tailwindcss.com](https://tailwindcss.com/) |
| **Bulma** | [bulma.io](https://bulma.io/) |
| **Foundation** | [get.foundation](https://get.foundation/) |
| **Materialize CSS** | [materializecss.com](https://materializecss.com/) |
| **Material UI (MUI)** | [mui.com](https://mui.com/) |

---

**Próximo:** [03-pensamento-critico-decisao.md](03-pensamento-critico-decisao.md) — Como escolher (ou não) um framework e defender sua decisão.

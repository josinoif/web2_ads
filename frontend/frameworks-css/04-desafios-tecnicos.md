# 4. Desafios técnicos: usando frameworks CSS em problemas reais

Os desafios abaixo simulam situações comuns no mercado: prazos curtos, layout responsivo, migração e decisão de ferramenta. O objetivo é **exercitar o uso do framework** e, ao mesmo tempo, **pensar em por que** você escolheu aquela solução.

Use **um** framework por desafio (Bootstrap, Tailwind ou Bulma são ótimos para começar). Se puder, repita um mesmo desafio com outro framework e compare: tempo, liberdade de customização e sensação de “luta” ou “fluidez”.

---

## Desafio 1 — Dashboard em tempo limitado

**Cenário:** Você entrou em um projeto e precisa entregar um **dashboard interno** em uma semana: sidebar, cabeçalho, área de conteúdo com cards de resumo (métricas) e uma tabela de dados. Não há design pronto; o time só pediu “limpo e funcional”.

**Objetivo:** Montar a estrutura do dashboard (layout responsivo) usando um framework CSS à sua escolha.

**Entregas:**
- Layout com sidebar (colapsável em mobile, se quiser) e área principal.
- Cabeçalho com título e pelo menos um botão ou link.
- Pelo menos 3 cards de “métrica” (número + rótulo) em linha no desktop e empilhados no mobile.
- Uma tabela simples (cabeçalho + 5 linhas de exemplo).

**Perguntas para reflexão (anote ou discuta):**
- Qual framework você escolheu e por quê?
- Quanto tempo levou? O que foi mais rápido e o que deu mais trabalho?
- Se tivesse que refazer com outro framework, o que mudaria no processo?

---

## Desafio 2 — Landing page responsiva

**Cenário:** Uma startup precisa de uma **landing page** para um produto: hero (título, subtítulo, CTA), seção de “como funciona” (3 passos) e rodapé com links. Deve funcionar bem em celular e desktop.

**Objetivo:** Implementar a landing usando grid/utilitários do framework e garantir que quebre de forma legível em telas pequenas.

**Entregas:**
- Hero com título, texto curto e um botão (call-to-action).
- Seção “Como funciona” com 3 blocos (ícone ou número + título + texto) em linha no desktop e em coluna no mobile.
- Rodapé com 3–4 links e copyright.
- Tudo responsivo sem overflow horizontal e com leitura confortável.

**Perguntas para reflexão:**
- Como você tratou os breakpoints (classes do framework ou media queries próprias)?
- O visual ficou “genérico” do framework? Se sim, o que você mudaria para dar mais identidade (cores, fontes, espaçamentos)?

---

## Desafio 3 — Formulário acessível e consistente

**Cenário:** O sistema já usa um framework CSS. Você precisa criar um **formulário de cadastro**: nome, e-mail, senha, confirmação de senha e um checkbox “Li e aceito os termos”. O formulário deve ser acessível (labels associados, foco visível, mensagens de erro claras) e visualmente alinhado ao restante do sistema.

**Objetivo:** Montar o formulário usando **apenas** os componentes/utilitários do framework (inputs, labels, botão, agrupamento) e garantir que:
- Cada campo tenha label associado (clicável).
- Haja um botão de envio e um de “Cancelar” ou “Voltar”.
- O layout fique organizado (ex.: uma coluna em mobile, talvez duas em desktop para campos curtos, se fizer sentido).

**Perguntas para reflexão:**
- O framework facilitou ou atrapalhou a acessibilidade? Você precisou sobrescrever algo?
- Como você organizaria validação (HTML5, JavaScript) e exibição de erros sem sair do padrão visual do framework?

---

## Desafio 4 — “Migração” de layout

**Cenário:** Você recebeu um **HTML + CSS “solto”** (sem framework): um card com título, imagem, texto e botão. O projeto decidiu adotar um framework CSS. Sua tarefa é **reimplementar esse card** usando apenas classes (ou componentes) do framework, mantendo o máximo possível do visual original.

**Objetivo:** Pegar um bloco de layout “manual” e expressá-lo no vocabulário do framework (Bootstrap, Tailwind ou Bulma), sem adicionar CSS customizado (ou o mínimo possível).

**Passos sugeridos:**
1. Escreva (ou pegue) um card simples em HTML + CSS puro (flexbox/grid, padding, borda, etc.).
2. Recrie o mesmo card usando só o framework.
3. Compare: o resultado ficou parecido? O que você perdeu ou ganhou em simplicidade/clareza do código?

**Perguntas para reflexão:**
- Foi fácil ou difícil manter o mesmo “feeling” visual? O framework impôs alguma decisão (ex.: cantos mais arredondados, outro espaçamento)?
- Em um projeto real, quando valeria a pena manter um pouco de CSS próprio em vez de forçar 100% no framework?

---

## Desafio 5 — Escolha de ferramenta (sem código)

**Cenário:** Você é consultado para dar opinião em dois projetos:

- **Projeto A:** App React para gestão de tarefas. Time de 3 devs, 2 já usaram Tailwind. Prazo: 2 meses. Design ainda em definição.
- **Projeto B:** Site institucional de uma prefeitura. HTML/CSS/JS mínimo, foco em acessibilidade e baixo peso. Sem React/Vue.

**Objetivo:** Para cada projeto, recomende **um** caminho (framework específico ou “CSS próprio”) e justifique em **até 5 linhas**, usando critérios de: prazo, equipe, stack, identidade visual e performance.

**Entregas:**
- Texto curto para o Projeto A (recomendação + justificativa).
- Texto curto para o Projeto B (recomendação + justificativa).
- Uma frase sobre o que você faria se o time do Projeto A insistisse em Bootstrap mesmo com 2 devs acostumados a Tailwind (negociação técnica).

Esse desafio não exige código; exige **decisão fundamentada** e comunicação clara — algo que você usará em reuniões e entrevistas.

---

## Como usar os desafios na aula

- **Individual ou em dupla:** Implementar pelo menos os Desafios 1 e 2; o 3 e o 4 aprofundam formulário e “migração”; o 5 é discussão.
- **Tempo sugerido:** Desafio 1 (1–2 h), Desafio 2 (1 h), Desafio 3 (≈1 h), Desafio 4 (≈30 min), Desafio 5 (20 min de escrita + discussão).
- **Comparação:** Se der tempo, refaça o Desafio 1 ou 2 com outro framework e compare: produtividade, liberdade, manutenção.
- **Apresentação:** Um grupo pode mostrar a solução e explicar “por que escolhemos X” e “o que faríamos diferente”.

As respostas comentadas e exemplos de código estão em [05-desafios-resolvidos.md](05-desafios-resolvidos.md).

---

**Próximo:** [05-desafios-resolvidos.md](05-desafios-resolvidos.md) — Soluções comentadas e discussão das decisões.

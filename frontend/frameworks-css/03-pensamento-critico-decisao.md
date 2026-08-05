# 3. Pensamento crítico e tomada de decisão

Escolher um framework CSS (ou decidir não usar nenhum) é uma **decisão técnica**. Como toda decisão, ela tem consequências: prazo, manutenção, onboarding, performance e até a imagem do produto. Esta seção trata de **como pensar** essa escolha e **como comunicá-la** — em equipe, em entrevista ou em um documento de arquitetura.

---

## Por que a decisão importa

- **Prazo:** Um framework adequado acelera; um inadequado gera retrabalho e “gambiarras” para fugir do padrão.
- **Manutenção:** O que a equipe conhece e o que está na base de código hoje influenciam o custo de manter e evoluir o produto.
- **Contratação:** Novos devs chegam e precisam entender o stack; mudar de framework no meio do projeto tem custo.
- **Produto:** Identidade visual, performance e acessibilidade dependem de ferramentas e de como elas são usadas.

Não existe “melhor framework do mundo”. Existe **melhor escolha para um contexto**: projeto, equipe, prazo e objetivos.

---

## Critérios para decidir

Use perguntas como guia; não precisa responder “sim” a tudo para um framework ganhar, mas as respostas ajudam a comparar.

### Sobre o projeto

- **Prazo:** Precisamos de algo funcionando em dias ou temos tempo para montar um design system do zero?
- **Identidade visual:** O produto precisa parecer único ou um visual “padrão” (ex.: Bootstrap ou Material) é aceitável?
- **Tamanho e performance:** O bundle de CSS é crítico (site público, mobile)? Ou é um painel interno onde um framework completo é aceitável?
- **Legado:** Já existe um framework ou um padrão de CSS no projeto? Mudar tem custo e risco.

### Sobre a equipe

- **Experiência:** A equipe já domina algum framework? Introduzir um novo implica tempo de aprendizado.
- **Tamanho e rotatividade:** Times grandes ou com muita entrada/saída se beneficiam de padrão claro (um framework bem adotado).
- **Preferência e cultura:** Alguns times preferem utility-first (Tailwind); outros preferem componentes prontos (Bootstrap). Respeitar isso reduz atrito.

### Sobre o ecossistema

- **Stack principal:** O projeto é React? Vue? Só HTML/CSS? Alguns frameworks têm integração forte (ex.: MUI com React); outros são agnósticos (Bootstrap, Tailwind, Bulma).
- **Design system:** Já existe um? O framework deve se alinhar a ele (tokens, cores, espaçamentos) ou o design system *é* o framework?

Responder a essas perguntas não precisa ser um documento de 20 páginas. Basta ter **argumentos claros** para “por que escolhemos X” ou “por que não usamos framework aqui”.

---

## Trade-offs comuns

Toda escolha tem custo. Reconhecer os trade-offs evita surpresas e ajuda a defender a decisão.

| Se você escolhe… | Ganha | Perde (ou paga) |
|------------------|--------|------------------|
| **Bootstrap** | Velocidade, documentação, componentes prontos | Peso, visual genérico, possíveis conflitos de especificidade |
| **Tailwind** | Flexibilidade, bundle enxuto, design único | Tempo no início, muitas classes no HTML, necessidade de convenções |
| **Bulma** | Simplicidade, só CSS, visual limpo | Menos componentes “comportados”, comunidade menor |
| **Foundation** | Grid e a11y fortes | Curva de aprendizado, menos material de apoio |
| **MUI (React)** | Muitos componentes complexos, Material Design | Peso, acoplamento a React, customização às vezes trabalhosa |
| **Nenhum (CSS próprio)** | Controle total, sem dependência | Tempo, risco de inconsistência, necessidade de disciplina |

Nenhuma linha dessa tabela é “errada”. O que pode ser errado é **não saber** que esse trade-off existe ou **não alinhar** a escolha com o contexto do projeto.

---

## Como argumentar em equipe

Em reunião ou em documento:

1. **Contextualize** — “Para este projeto, o prazo é curto e a equipe já conhece Bootstrap.”
2. **Apresente a opção** — “Sugiro usarmos Bootstrap para o MVP e revisarmos quando tivermos o design system definido.”
3. **Reconheça o trade-off** — “Sabemos que o visual tende a ser genérico no início; vamos customizar cores e tipografia via variáveis.”
4. **Incremente se fizer sentido** — “Se no próximo trimestre priorizarmos identidade visual forte, podemos avaliar migração para Tailwind ou design system próprio.”

Isso mostra que você **pensou no contexto**, não só na ferramenta. Em processo seletivo, esse tipo de raciocínio costuma ser valorizado.

---

## Perguntas típicas em entrevistas

- **“Por que vocês usaram Tailwind (ou Bootstrap) nesse projeto?”**  
  Resposta forte: contexto (prazo, equipe, tipo de produto) + trade-off aceito. Resposta fraca: “porque é o melhor” ou “porque todo mundo usa”.

- **“Como você escolheria um framework CSS para um projeto novo?”**  
  Cite critérios: prazo, equipe, identidade visual, performance, stack (React/Vue/etc.) e legado. Mostre que a escolha depende do contexto.

- **“O que você faria se o design pedisse algo que o framework não oferece?”**  
  Possíveis respostas: customizar com variáveis/theme, sobrescrever com CSS próprio, usar utilitários (no caso Tailwind) ou, em último caso, avaliar outra ferramenta. O importante é mostrar que você pensa em solução, não em desistir do framework à primeira dificuldade.

- **“Prefere Bootstrap ou Tailwind?”**  
  Resposta madura: “Depende do projeto. Para X, escolheria A porque…; para Y, escolheria B porque….” Evite “só gosto de um”.

---

## Exercício de reflexão (antes dos desafios práticos)

Antes de codar nos desafios, vale responder por escrito (ou em discussão em grupo):

1. **Um e-commerce novo, prazo de 3 meses, equipe de 2 devs front.** Que framework você consideraria e por quê?
2. **Um dashboard interno React, já existe MUI em outro projeto da empresa.** Que argumentos você usaria para manter MUI? E para trocar?
3. **Landing page única, forte identidade visual, sem framework JS.** Bootstrap, Tailwind, Bulma ou CSS puro? Justifique em 3 critérios.

Não existe “resposta certa” única. Existe **argumentação coerente com o contexto** que você definiu. Os desafios técnicos na próxima seção vão colocar isso em prática com código.

---

**Próximo:** [04-desafios-tecnicos.md](04-desafios-tecnicos.md) — Desafios práticos com frameworks CSS.

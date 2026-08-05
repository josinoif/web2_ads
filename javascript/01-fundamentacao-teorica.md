# 1. Fundamentação teórica: o que é JavaScript e por que importa

Antes de mergulhar em sintaxe, tipos e assincronismo, vale entender **o que** é JavaScript, **onde** ela roda e **por que** ela é decisiva para o produto, para o usuário e para o seu dia a dia como desenvolvedor.

---

## O que é JavaScript?

**JavaScript** é uma linguagem de programação **dinâmica**, **multiparadigma** e **orientada a eventos**. Ela foi criada para rodar no navegador e dar interatividade às páginas web; hoje também roda no servidor (Node.js), em aplicações mobile (React Native, etc.) e em ferramentas de linha de comando e build.

Características que você vai encontrar em todo o ecossistema:

- **Interpretada** — O código é executado por um motor (V8 no Chrome e no Node, SpiderMonkey no Firefox, etc.), sem compilação prévia para máquina (embora os motores façam JIT internamente).
- **Single-thread** — Um único thread de execução por contexto; operações longas ou de I/O não bloqueiam graças ao **modelo assíncrono** e ao **event loop**.
- **Tipagem dinâmica** — Tipos são associados aos valores em tempo de execução, não declarados na variável; isso exige disciplina para evitar bugs e favorece ferramentas como TypeScript em projetos grandes.
- **Primeira classe: funções** — Funções podem ser atribuídas a variáveis, passadas como argumento e retornadas; isso sustenta callbacks, Promises e padrões funcionais.

Resumindo: JavaScript é a **linguagem da web** no cliente e, com Node.js, uma das principais no servidor. Entender a linguagem — e não só “como usar React ou Express” — é o que permite tomar decisões técnicas com critério e se adaptar a novos frameworks e ambientes.

---

## Onde JavaScript roda?

| Ambiente | O que muda | Exemplos de uso |
|----------|------------|------------------|
| **Navegador** | Acesso ao **DOM**, **BOM**, **Fetch**, eventos de usuário; não há acesso a sistema de arquivos ou processos. | Páginas interativas, SPAs, formulários, chamadas a APIs. |
| **Node.js** | Acesso a **módulos** (`fs`, `http`, `path`, etc.), processos e rede; **não há DOM**. O mesmo event loop e assincronismo. | APIs REST, scripts, ferramentas CLI, servidores. |

A **linguagem** (sintaxe, tipos, Promises, async/await, estruturas de dados) é a mesma nos dois ambientes. O que muda são as **APIs disponíveis**: no navegador você usa `document`, `window`, `fetch`; no Node usa `require`/`import`, `fs`, `http`. Este módulo foca na linguagem; o arquivo [04-js-navegador-node.md](04-js-navegador-node.md) detalha recursos de cada ambiente e faz o link com o material de front-end (DOM, eventos, HTTP).

---

## Por que JavaScript importa no mercado?

Três razões centrais:

1. **Ubiquidade** — Front-end web é quase sempre JavaScript (ou TypeScript que compila para JS). Node.js domina parte grande do back-end em startups e em ferramentas (build, testes, automação). Saber a linguagem abre vagas em front-end, back-end e full-stack.
2. **Entrevistas e testes** — Processos seletivos perguntam sobre closures, event loop, diferença entre `let` e `const`, Promises vs async/await, e pedem exercícios em JavaScript. A fundamentação que você verá aqui sustenta suas respostas.
3. **Manutenção e decisão** — Código legado, novos frameworks e mudanças de stack exigem entender *por que* algo foi escrito de determinada forma. Quem domina a linguagem consegue refatorar, debugar e propor alternativas com critério.

Ou seja: JavaScript não é “só mais uma linguagem”. É a base da maioria dos projetos web e de muitas aplicações modernas; dominá-la **abre portas** e **reduz atrito** em qualquer projeto.

---

## Pensamento crítico e tomada de decisão

Em projetos reais você precisará:

- **Escolher** entre callbacks, Promises e async/await para um fluxo assíncrono — cada um tem custo de legibilidade e manutenção.
- **Decidir** quando usar `Map`/`Set` em vez de objeto ou array — desempenho e semântica importam.
- **Avaliar** impacto de operações síncronas pesadas no event loop (bloqueio da thread única) e quando considerar Worker ou outra solução.
- **Argumentar** em code review ou em entrevista: “usei async/await aqui porque o fluxo fica linear e o tratamento de erro fica centralizado”.

Este material foi pensado para que você não só “use” JavaScript, mas **entenda** os conceitos e **justifique** escolhas. Os arquivos [05-decisao-e-pratica.md](05-decisao-e-pratica.md) e [06-desafios-tecnicos.md](06-desafios-tecnicos.md) aprofundam esse tipo de reflexão.

---

## Conceitos que atravessam todo o tema

Antes de entrar em detalhes da linguagem, fixe estes conceitos; eles voltarão em cada seção.

| Conceito | O que significa |
|----------|------------------|
| **Single-thread e event loop** | Uma única thread executa o código; operações assíncronas (I/O, timers) são delegadas e o resultado é processado quando pronto, sem bloquear a thread. |
| **Assíncrono vs paralelo** | **Assíncrono** = não esperar bloqueando (ex.: `fetch`); **paralelo** = mais de uma thread executando ao mesmo tempo. Em JavaScript no navegador e no Node (padrão), não há paralelismo de código; há concorrência via event loop. |
| **Escopo e ciclo de vida** | Onde uma variável existe e por quanto tempo; `let`/`const` têm escopo de bloco; `var` tem escopo de função (e hoisting). |
| **Imutabilidade e mutação** | Dados imutáveis não são alterados no lugar; mutação pode causar efeitos colaterais difíceis de rastrear. Escolher quando mutar ou não afeta bugs e testes. |

Na próxima seção entramos nos **fundamentos da linguagem**: tipos, variáveis, estruturas de dados, funções e escopo.

---

**Próximo:** [02-linguagem-fundamentos.md](02-linguagem-fundamentos.md) — Tipos, let/const, estruturas de dados, escopo e closures.

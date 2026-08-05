# 5. Decisão e prática: quando usar o quê

Na hora de escrever ou revisar código em JavaScript, você precisa decidir: **Promise ou async/await?** **Map ou Object?** **let ou const?** **Callback ou Promise em API legada?** Esta seção organiza critérios para essas escolhas e mostra como o pensamento crítico se aplica no dia a dia e em entrevistas.

---

## Promise encadeada ou async/await?

| Situação | Tendência |
|----------|------------|
| Fluxo linear com várias operações assíncronas em sequência | **async/await** — mais legível, erro com `try/catch`. |
| Uma ou duas operações simples (ex.: um `fetch` e `.then` para logar) | **Promise com .then** — aceitável e direto. |
| Precisa rodar várias operações “em paralelo” e esperar todas | **Promise.all** com async/await: `const [a, b] = await Promise.all([fetchA(), fetchB()]);` |
| Precisa da primeira que resolver (timeout, competição) | **Promise.race**. |
| Código legado ou API que só retorna callback | Encapsule em Promise: `new Promise((resolve, reject) => { apiLegada((err, data) => err ? reject(err) : resolve(data)); })` e use async/await no resto. |

Regra prática: preferir **async/await** para fluxos com múltiplos passos e tratamento de erro; usar **.then** quando for um único passo ou quando a equipe já tiver padrão estabelecido. Em entrevistas, saber explicar que async/await é açúcar sobre Promises e que ambos são interoperáveis demonstra domínio.

---

## Qual estrutura de dados?

| Necessidade | Estrutura | Motivo |
|-------------|-----------|--------|
| Lista ordenada, índices numéricos | **Array** | Semântica e métodos (map, filter, reduce). |
| Entidade com chaves fixas (ex.: usuário: nome, email) | **Object** | Literal, JSON, acesso `obj.chave`. |
| Chaves que não são string (objeto, número como chave sem converter) | **Map** | Object converte chaves para string. |
| Ordem de inserção importante em mapa chave-valor | **Map** | Object não garante ordem em todas as situações. |
| Lista sem duplicatas ou “já existe?” | **Set** | Unicidade e busca rápida. |
| Remover duplicatas de array | **Set** | `[...new Set(arr)]`. |

Quando um Object “funciona” e as chaves são strings simples, não é obrigatório usar Map; use Map quando a semântica ou a necessidade de chaves não-string justificar. Set é a escolha natural para conjuntos e para deduplicação.

---

## let, const e var

- **const por padrão** — Use para tudo que não vai ser reatribuído; deixa a intenção clara e evita reatribuições acidentais.
- **let** — Só quando a variável precisar ser reatribuída (ex.: contador em loop, acumulador que você reassigna).
- **var** — Evitar em código novo; aparece em código legado e em perguntas de entrevista sobre hoisting e escopo.

Se alguém perguntar “por que const?”, a resposta forte é: escopo de bloco, TDZ (evita uso antes da declaração) e intenção explícita (este valor não será reatribuído).

---

## Callback, Promise ou async/await em APIs

| Contexto | Recomendação |
|----------|--------------|
| Nova API ou novo código | **async/await** (ou retornar Promise). |
| Biblioteca que só aceita callback | Encapsule em Promise uma vez e use async/await no seu código. |
| Manutenção de código que já usa callbacks | Se a mudança for pequena, manter callbacks pode ser aceitável; se for refatorar, migrar para Promise/async. |
| Eventos (ex.: clique, mensagem) | Callback ou listener é natural; para “fazer algo assíncrono após o evento”, use async no handler. |

Não é necessário reescrever todo código legado; o importante é que **novo código** siga um padrão claro (geralmente async/await) e que você saiba converter entre os três quando precisar.

---

## Perguntas típicas em entrevistas

- **“Qual a diferença entre let, const e var?”**  
  Resposta forte: escopo (bloco vs função para var), reatribuição (const não permite), hoisting e TDZ (let/const têm TDZ; var sobe e fica undefined). Mencione que prefere const por padrão.

- **“O que é o event loop?”**  
  Resposta forte: JavaScript é single-thread; o event loop processa a call stack e, quando vazia, processa filas de tarefas (macrotasks e microtasks). Operações assíncronas colocam callbacks nessas filas; isso permite não bloquear enquanto espera I/O.

- **“Quando usar Map em vez de Object?”**  
  Cite: chaves que não são string (objeto, número sem conversão), necessidade de ordem de inserção garantida, semântica de “mapa” com `.size` e métodos `.has`, `.get`, `.set`.

- **“Promise vs async/await?”**  
  Async/await é açúcar sobre Promises; mesmo modelo. Async/await deixa o fluxo linear e o tratamento de erro com try/catch; Promises são úteis para composição (Promise.all, Promise.race) e quando você não está dentro de uma função async.

- **“Assíncrono e paralelo são a mesma coisa?”**  
  Não. Assíncrono = não bloquear a thread enquanto espera (I/O, timer). Paralelo = mais de uma thread executando. Em JS (navegador e Node padrão) há concorrência via event loop, não paralelismo de código; Workers são a exceção para paralelismo.

---

## Resumo da seção

- **Assincronismo:** preferir async/await para fluxos com vários passos; usar Promise.all/race quando precisar de várias operações; encapsular callbacks legados em Promise.
- **Estruturas de dados:** Array para listas; Object para entidades com chaves string; Map para chaves arbitrárias ou ordem; Set para unicidade e deduplicação.
- **Variáveis:** const por padrão, let quando precisar reatribuir, evitar var.
- **APIs:** novo código com async/await; integrar callbacks legados via Promise quando fizer sentido.
- Em **entrevistas**, demonstre que sabe escolher com critério e explicar o “porquê”.

**Próximo:** [06-desafios-tecnicos.md](06-desafios-tecnicos.md) — Desafios técnicos com JavaScript para problemas reais.

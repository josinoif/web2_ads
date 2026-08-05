# 3. Assincronismo: callbacks, Promises, async/await e event loop

JavaScript é **single-thread**: um único thread executa o código. Operações que demoram (rede, disco, timers) não podem bloquear esse thread, senão a interface trava ou o servidor para de atender. O modelo **assíncrono** e o **event loop** permitem iniciar essas operações e processar o resultado quando estiver pronto, sem bloquear. Esta seção cobre callbacks, Promises, async/await, o event loop e a diferença entre processamento assíncrono e paralelo.

---

## Por que assincronismo?

- **No navegador:** requisições HTTP, animações e timers precisam acontecer “em segundo plano”; o usuário continua interagindo enquanto a resposta da API não chega.
- **No Node.js:** leitura de arquivo, chamadas a banco e a outras APIs são I/O; bloquear a thread pararia todo o servidor.

A linguagem não espera a operação terminar para executar o próximo trecho de código. Em vez disso, você registra **o que fazer quando** a operação terminar (callback, Promise ou async/await).

---

## Callbacks

Um **callback** é uma função passada como argumento para ser chamada quando uma operação assíncrona terminar.

```javascript
setTimeout(() => console.log('depois de 1s'), 1000);
fs.readFile('arquivo.txt', (err, data) => {
  if (err) throw err;
  console.log(data.toString());
});
```

Problemas com callbacks em cadeia:

- **Callback hell:** vários níveis de aninhamento, difícil de ler e de tratar erro em cada etapa.
- **Controle de fluxo:** encadear várias operações e tratar erros fica verboso e propenso a bugs.

Por isso, em código moderno, callbacks são usados principalmente em APIs antigas ou em APIs que só expõem callback (ex.: parte da API do Node). O padrão atual é **Promises** e **async/await**.

---

## Promises

Uma **Promise** representa um valor (ou erro) que pode estar disponível **agora ou no futuro**. Ela está em um de três estados: **pending**, **fulfilled** (com valor) ou **rejected** (com motivo de falha).

- **Criar:** `new Promise((resolve, reject) => { ... })` — você chama `resolve(valor)` ou `reject(motivo)` quando a operação terminar.
- **Consumir:** `.then(valor => ...)` para sucesso, `.catch(motivo => ...)` para erro, `.finally(() => ...)` para limpeza em ambos os casos. `.then` e `.catch` retornam **nova Promise**, permitindo encadear.

```javascript
const p = fetch('/api/users')
  .then(res => res.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

Vantagens sobre callbacks: encadeamento linear (um `.then` após o outro), tratamento de erro centralizado em um `.catch` e composição (ex.: `Promise.all`, `Promise.race`).

### Promise.all e Promise.race

- **Promise.all(iterable):** retorna uma Promise que resolve quando **todas** as Promises do iterable resolverem, com array de resultados; rejeita na primeira rejeição.
- **Promise.race(iterable):** resolve ou rejeita assim que **a primeira** Promise resolver ou rejeitar.

Úteis para disparar várias operações em paralelo (no sentido de “todas em andamento”) e esperar o conjunto ou a primeira a terminar.

---

## async/await

**async/await** é açúcar sintático sobre Promises: código assíncrono escrito em estilo **síncrono** (linear, fácil de ler).

- **async:** uma função declarada com `async` **sempre** retorna uma Promise (se retornar valor, a Promise resolve com esse valor).
- **await:** só pode ser usado dentro de função `async`; **pausa** a execução da função até a Promise resolver e retorna o valor resolvido; se a Promise rejeitar, o erro é lançado e pode ser tratado com `try/catch`.

```javascript
async function buscarUsuario(id) {
  try {
    const res = await fetch(`/api/users/${id}`);
    if (!res.ok) throw new Error('Falha na rede');
    const data = await res.json();
    return data;
  } catch (err) {
    console.error(err);
    throw err;
  }
}
```

Vantagens: fluxo legível, tratamento de erro com `try/catch` familiar e composição com Promises (você pode fazer `await Promise.all(...)` para esperar várias operações).

---

## Event loop

O **event loop** é o mecanismo que permite que o JavaScript single-thread processe operações assíncronas. Em resumo:

1. O código síncrono na **call stack** é executado até esvaziar.
2. Quando uma operação assíncrona é concluída (timer, I/O, etc.), o **callback** (ou a resolução da Promise) é colocada em uma **fila de tarefas** (task queue / microtask queue para Promises).
3. O event loop, quando a call stack está vazia, pega a próxima tarefa da fila e executa; isso repete.

Ordem importante: **microtasks** (ex.: callbacks de Promises, `queueMicrotask`) são processadas antes da próxima **macrotask** (ex.: `setTimeout`). Por isso, `Promise.then` pode rodar antes de um `setTimeout(0)`.

Consequência prática: **nunca bloquear a call stack** com loop pesado ou processamento síncrono longo; isso atrasa todas as tarefas na fila (interface trava, servidor não responde). Operações pesadas devem ser quebradas (chunks) ou, em cenários específicos, delegadas (ex.: Worker no navegador, worker threads no Node).

---

## Processamento assíncrono vs paralelo

| Conceito | Significado |
|----------|-------------|
| **Assíncrono** | Não bloquear a thread enquanto se espera I/O ou timer; o resultado é tratado depois, via callback ou Promise. Várias operações podem estar “em andamento” ao mesmo tempo (ex.: várias requisições HTTP). |
| **Paralelo** | Mais de um **thread** executando código ao mesmo time. Em JavaScript (navegador e Node padrão), o código da sua aplicação roda em uma thread; não há paralelismo de código, e sim **concorrência** via event loop. |

No Node.js, I/O é assíncrono (libuv); o trabalho de CPU (cálculos pesados) roda na mesma thread e pode bloquear. Para CPU intensiva, existem Worker Threads (Node) e Web Workers (navegador), que rodam em outra thread — aí sim há paralelismo, com comunicação por mensagens.

Resumindo: **assíncrono** = não bloquear enquanto espera; **paralelo** = mais de uma thread. Em JS, você usa assincronismo o tempo todo; paralelismo é exceção (Workers).

---

## Exercícios resolvidos

Os exercícios abaixo usam cenários do dia a dia (buscar dados de API, montar uma tela, tratar timeout e erros) para fixar callbacks, Promises e async/await. Onde há requisição HTTP, usamos a **JSONPlaceholder** ([https://jsonplaceholder.typicode.com](https://jsonplaceholder.typicode.com)), API pública e gratuita, sem necessidade de chave. Você pode rodar os exemplos no console do navegador (em uma página aberta) ou no Node (versão 18+ com `fetch` nativo).

---

### 1. Ordem de execução: por que “Carregando…” aparece antes dos dados?

**Contexto:** Em qualquer tela que busca dados na rede, você mostra “Carregando…” e, só quando a resposta chega, exibe o conteúdo. O JavaScript não espera a requisição terminar para executar a próxima linha; quem “espera” é o callback (ou a Promise).

**Objetivo:** Ver na prática que o código após iniciar uma operação assíncrona roda **antes** do callback.

```javascript
console.log('1. Tela exibida — mostrando "Carregando..."');

fetch('https://jsonplaceholder.typicode.com/users/1')
  .then((res) => res.json())
  .then((user) => {
    console.log('3. Dados chegaram — agora podemos esconder "Carregando..." e mostrar:', user.name);
  });

console.log('2. Requisição foi disparada; o código segue sem esperar.');
```

**O que observar:** As linhas 1 e 2 aparecem na hora; a linha 3 só depois que a API responder. No seu app, você colocaria o “Carregando…” no passo 1 e a atualização da UI no passo 3. Assim você entende por que a interface não “trava” esperando a rede.

---

### 2. Buscar um usuário na API e tratar sucesso e falha

**Contexto:** Sua aplicação precisa exibir o perfil de um usuário. A API pode responder com sucesso (status 200) ou falhar (rede, 404, 500). Você precisa tratar os dois casos para não quebrar a tela e informar o usuário em caso de erro.

**Objetivo:** Fazer uma requisição real com `fetch`, checar `response.ok` e encadear `.then` e `.catch` para sucesso e falha.

```javascript
const BASE_URL = 'https://jsonplaceholder.typicode.com';

function buscarUsuario(id) {
  return fetch(`${BASE_URL}/users/${id}`)
    .then((res) => {
      if (!res.ok) throw new Error(`Erro na API: ${res.status}`);
      return res.json();
    });
}

// Caso de sucesso (ID existe)
buscarUsuario(1)
  .then((user) => {
    console.log('Perfil carregado:', user.name, '—', user.email);
  })
  .catch((err) => {
    console.error('Não foi possível carregar o perfil:', err.message);
  });

// Caso de falha (ID não existe — a API retorna 200 mesmo para IDs altos, então use um endpoint que falhe ou simule)
fetch(`${BASE_URL}/users/9999`)
  .then((res) => {
    if (!res.ok) throw new Error(`Erro na API: ${res.status}`);
    return res.json();
  })
  .then((user) => console.log(user))
  .catch((err) => console.error('Falha ao buscar usuário:', err.message));
```

**O que observar:** O `.catch` centraliza qualquer erro (rede, status 4xx/5xx, JSON inválido). Na prática, você usaria essa lógica para mostrar um toast ou mensagem na tela em vez de só `console.error`.

---

### 3. Encadeamento: buscar usuário e depois os posts dele

**Contexto:** Na tela de perfil, você precisa do nome do usuário e da lista de posts dele. A API tem um endpoint de usuário e outro de posts (filtrando por `userId`). A segunda requisição **depende** do resultado da primeira: só sabemos o `userId` depois de buscar o usuário.

**Objetivo:** Encadear duas requisições: a segunda usa o resultado da primeira (`.then` retornando nova Promise).

```javascript
const BASE_URL = 'https://jsonplaceholder.typicode.com';

fetch(`${BASE_URL}/users/1`)
  .then((res) => res.json())
  .then((user) => {
    console.log('Usuário:', user.name);
    return fetch(`${BASE_URL}/posts?userId=${user.id}`);
  })
  .then((res) => res.json())
  .then((posts) => {
    console.log('Total de posts:', posts.length);
    console.log('Primeiro post:', posts[0]?.title);
  })
  .catch((err) => console.error('Erro:', err.message));
```

**O que observar:** O primeiro `.then` retorna `fetch(...)`, que é uma Promise. O próximo `.then` só roda quando essa Promise resolver, e recebe o JSON dos posts. Esse padrão é comum sempre que um passo depende do anterior (ex.: login → buscar dados do usuário logado).

---

### 4. Promise.all: carregar usuários e posts ao mesmo tempo na página inicial

**Contexto:** Na página inicial do seu app, você quer exibir um resumo: alguns usuários e algumas postagens. As duas listas vêm de endpoints diferentes e **não dependem** uma da outra. Fazer uma requisição, esperar terminar, e só então fazer a outra deixa a tela mais lenta; o ideal é disparar as duas juntas e esperar as duas antes de montar a UI.

**Objetivo:** Usar `Promise.all` para fazer duas (ou mais) requisições em paralelo e só então usar os resultados.

```javascript
const BASE_URL = 'https://jsonplaceholder.typicode.com';

Promise.all([
  fetch(`${BASE_URL}/users`).then((res) => res.json()),
  fetch(`${BASE_URL}/posts`).then((res) => res.json())
])
  .then(([usuarios, posts]) => {
    console.log('Usuários carregados:', usuarios.length);
    console.log('Posts carregados:', posts.length);
    console.log('Primeiro usuário:', usuarios[0].name);
    console.log('Primeiro post:', posts[0].title);
  })
  .catch((err) => console.error('Falha ao carregar a página inicial:', err.message));
```

**O que observar:** O array de resultados mantém a **mesma ordem** do array de Promises. A Promise de `Promise.all` só resolve quando **todas** tiverem resolvido; se uma falhar, `Promise.all` rejeita e o `.catch` é chamado.

---

### 5. Promise.race: timeout — não deixar o usuário esperando para sempre

**Contexto:** Às vezes a rede está lenta ou a API não responde. Em vez de deixar o usuário olhando “Carregando…” indefinidamente, você define um tempo máximo (ex.: 5 segundos). Se a API não responder a tempo, você mostra “Tempo esgotado. Tente novamente.” e cancela a espera.

**Objetivo:** Usar `Promise.race` entre a requisição real e uma Promise que rejeita após um delay (timeout).

```javascript
const BASE_URL = 'https://jsonplaceholder.typicode.com';
const TIMEOUT_MS = 5000;

function delay(ms) {
  return new Promise((_, reject) =>
    setTimeout(() => reject(new Error('Tempo esgotado. Tente novamente.')), ms)
  );
}

function buscarComTimeout(url) {
  return Promise.race([
    fetch(url).then((res) => {
      if (!res.ok) throw new Error(`Erro: ${res.status}`);
      return res.json();
    }),
    delay(TIMEOUT_MS)
  ]);
}

buscarComTimeout(`${BASE_URL}/users/1`)
  .then((user) => console.log('Usuário:', user.name))
  .catch((err) => console.error(err.message));
```

**O que observar:** Quem resolver (ou rejeitar) primeiro “vence” o `race`. Se a API demorar mais que 5 segundos, o usuário vê a mensagem de timeout em vez de ficar esperando. Em produção, você pode usar `AbortController` para cancelar de fato o `fetch`; o padrão com `Promise.race` ilustra a ideia.

---

### 6. async/await: buscar um post e tratar erro na tela

**Contexto:** Você está refatorando a tela de “detalhe do post”: em vez de vários `.then`, você quer um código em linha reta, fácil de ler, e tratar qualquer erro (rede, 404, etc.) com uma mensagem amigável.

**Objetivo:** Usar `async/await` e `try/catch` para buscar um post em uma API pública e exibir título e corpo, ou uma mensagem de erro.

```javascript
const BASE_URL = 'https://jsonplaceholder.typicode.com';

async function exibirPost(id) {
  try {
    const res = await fetch(`${BASE_URL}/posts/${id}`);
    if (!res.ok) throw new Error(`Post não encontrado (${res.status})`);
    const post = await res.json();
    console.log('Título:', post.title);
    console.log('Corpo:', post.body);
    return post;
  } catch (err) {
    console.error('Não foi possível carregar o post:', err.message);
    throw err;
  }
}

exibirPost(1);   // Post existente
exibirPost(999); // Se a API retornar 404, o catch exibe a mensagem
```

**O que observar:** O `await` “pausa” a função até a Promise resolver; o fluxo fica parecido com código síncrono. Qualquer erro (rede, `res.ok === false`, `res.json()` falhando) cai no `catch`. Na interface real, você trocaria `console.log`/`console.error` por atualizar o DOM ou um estado da aplicação.

---

### 7. async/await com Promise.all: perfil com usuário e posts dele

**Contexto:** Na tela de perfil você precisa, ao mesmo tempo, do usuário (nome, email) e dos posts dele. As duas requisições são independentes: podemos disparar as duas juntas e só depois montar a tela quando as duas tiverem chegado.

**Objetivo:** Dentro de uma função `async`, usar `await Promise.all([...])` para esperar duas requisições em paralelo e então usar os dois resultados.

```javascript
const BASE_URL = 'https://jsonplaceholder.typicode.com';

async function carregarPerfil(userId) {
  try {
    const [userRes, postsRes] = await Promise.all([
      fetch(`${BASE_URL}/users/${userId}`),
      fetch(`${BASE_URL}/posts?userId=${userId}`)
    ]);

    if (!userRes.ok) throw new Error('Usuário não encontrado');
    if (!postsRes.ok) throw new Error('Posts não disponíveis');

    const user = await userRes.json();
    const posts = await postsRes.json();

    console.log('Perfil:', user.name, '—', user.email);
    console.log('Total de posts:', posts.length);
    return { user, posts };
  } catch (err) {
    console.error('Erro ao carregar perfil:', err.message);
    throw err;
  }
}

carregarPerfil(1);
```

**O que observar:** As duas requisições são feitas no mesmo instante; o `await Promise.all` só segue quando as duas tiverem terminado. Assim a tela carrega mais rápido do que se você fizesse uma requisição após a outra.

---

### 8. Event loop: por que a ordem importa na UI

**Contexto:** No seu código você mistura atualizações vindas de requisições (Promises) e um timer (ex.: `setTimeout` para esconder um aviso após 2 segundos). Dependendo da ordem em que você registra os callbacks, a interface pode atualizar em sequências estranhas. Entender microtasks vs macrotasks ajuda a depurar esse tipo de problema.

**Objetivo:** Ver que o callback de uma Promise (microtask) é executado **antes** do callback de um `setTimeout` (macrotask), mesmo com delay 0.

```javascript
console.log('A — Início (código síncrono)');

setTimeout(() => {
  console.log('D — Callback do setTimeout (macrotask): ex. "esconder aviso após 2s"');
}, 0);

fetch('https://jsonplaceholder.typicode.com/users/1')
  .then((res) => res.json())
  .then((user) => {
    console.log('C — Callback da Promise (microtask): ex. "atualizar nome na tela"', user.name);
  });

console.log('B — Fim do código síncrono');
```

**Saída esperada:** A, B, C, D. O event loop esvazia a call stack (A e B), depois processa todas as microtasks (C) e só então a próxima macrotask (D). Assim você entende por que “atualizar nome na tela” pode rodar antes de “esconder aviso”, mesmo que o `setTimeout` tenha sido chamado antes do `fetch`.

---

### 9. Resumo: buscar comentários de um post (async/await de ponta a ponta)

**Contexto:** Você precisa exibir um post e os comentários dele. É um fluxo que você já viu: uma requisição (ou duas em paralelo) e tratamento de erro. Este exemplo junta async/await, `Promise.all` opcional e mensagens claras para o usuário.

**Objetivo:** Implementar um fluxo completo com async/await, usando uma API pública, e exibir o resultado ou uma mensagem de erro.

```javascript
const BASE_URL = 'https://jsonplaceholder.typicode.com';

async function exibirPostComComentarios(postId) {
  console.log('Carregando post e comentários...');

  try {
    const [postRes, commentsRes] = await Promise.all([
      fetch(`${BASE_URL}/posts/${postId}`),
      fetch(`${BASE_URL}/posts/${postId}/comments`)
    ]);

    if (!postRes.ok) throw new Error('Post não encontrado');
    if (!commentsRes.ok) throw new Error('Comentários não disponíveis');

    const post = await postRes.json();
    const comments = await commentsRes.json();

    console.log('Post:', post.title);
    console.log('Corpo:', post.body);
    console.log('Comentários:', comments.length);
    comments.slice(0, 2).forEach((c, i) => console.log(`  ${i + 1}. ${c.name}: ${c.body.slice(0, 50)}...`));

    return { post, comments };
  } catch (err) {
    console.error('Erro:', err.message);
    throw err;
  }
}

exibirPostComComentarios(1);
```

**O que observar:** Um único `try/catch` trata falha de qualquer uma das requisições. No mundo real, você usaria esses dados para preencher elementos no DOM (título, corpo, lista de comentários) e mostraria um aviso ou estado de erro no `catch`.

---

## Resumo da seção

- **Callbacks:** função chamada quando a operação termina; em cadeias longas viram “callback hell”; ainda usados em APIs antigas.
- **Promises:** representam resultado futuro; `.then`/`.catch`/`.finally` encadeiam e centralizam erro; `Promise.all` e `Promise.race` para múltiplas operações.
- **async/await:** escrita linear de código assíncrono; `await` pausa até a Promise resolver; erros com `try/catch`.
- **Event loop:** executa código síncrono primeiro; depois processa filas de tarefas (macrotasks e microtasks); não bloquear a call stack.
- **Assíncrono ≠ paralelo:** assíncrono = não bloquear; paralelo = mais de uma thread (Workers).

**Próximo:** [04-js-navegador-node.md](04-js-navegador-node.md) — Recursos do JavaScript no navegador e no Node.js.

# 7. Exercícios de fixação (com respostas)

Estes exercícios fixam conceitos da **linguagem** (tipos, variáveis, estruturas de dados, assincronismo). Para exercícios que integram **HTTP + DOM + eventos** no navegador, use também o material [../frontend/exercicio_fixacao_http_dom.md](../frontend/exercicio_fixacao_http_dom.md).

---

## Tipos e variáveis

### 1. Tipo e valor

O que `typeof` retorna para cada expressão?

```javascript
typeof 42;
typeof "42";
typeof true;
typeof undefined;
typeof null;
typeof {};
typeof [];
typeof (() => {});
```

**Resposta:**  
`"number"`, `"string"`, `"boolean"`, `"undefined"`, `"object"`, `"object"`, `"object"`, `"function"`. Para array use `Array.isArray([])` → `true`.

---

### 2. let, const e escopo

O que é impresso no console? Por quê?

```javascript
const x = 1;
if (true) {
  const x = 2;
  console.log(x);
}
console.log(x);
```

**Resposta:**  
`2` e depois `1`. O `const x = 2` existe apenas dentro do bloco `if`; o `x` externo continua 1. Isso ilustra escopo de bloco para `const`.

---

### 3. const e mutação

O código abaixo gera erro? Explique.

```javascript
const arr = [1, 2, 3];
arr.push(4);
arr = [1, 2, 3, 4];
```

**Resposta:**  
`arr.push(4)` é permitido: `const` impede **reatribuição**, não a mutação do valor. A linha `arr = [1, 2, 3, 4]` gera erro (reatribuição). Depois do push, `arr` é `[1, 2, 3, 4]`.

---

## Estruturas de dados

### 4. Set e deduplicação

Escreva uma função que recebe um array de números e retorna um novo array sem duplicatas, mantendo a ordem da primeira ocorrência.

**Resposta (exemplo):**

```javascript
function semDuplicatas(arr) {
  return [...new Set(arr)];
}
// ou, sem Set: arr.filter((x, i) => arr.indexOf(x) === i);
```

---

### 5. Map para contagem

Dado um array de strings (ex.: `['a', 'b', 'a', 'c', 'a', 'b']`), retorne um objeto ou Map com a contagem de cada string (ex.: `{ a: 3, b: 2, c: 1 }`).

**Resposta (exemplo com Map):**

```javascript
function contagem(arr) {
  const map = new Map();
  for (const s of arr) {
    map.set(s, (map.get(s) ?? 0) + 1);
  }
  return Object.fromEntries(map); // ou manter Map
}
```

---

### 6. Map vs Object

Quando faz sentido usar `Map` em vez de um objeto literal? Dê dois motivos.

**Resposta (exemplo):**  
(1) Chaves que não são strings (ex.: objeto ou número como chave sem conversão automática). (2) Ordem de inserção garantida ao iterar; necessidade de `.size` e métodos como `.has`, `.get`, `.set` com semântica clara de mapa.

---

## Assincronismo

### 7. Ordem de execução

Em que ordem os `console.log` são executados? Por quê?

```javascript
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve().then(() => console.log('C'));
console.log('D');
```

**Resposta:**  
A, D, C, B. O código síncrono (A e D) roda primeiro. Em seguida o event loop processa as **microtasks** (fila de Promises), então C. Depois vêm as **macrotasks** (setTimeout), então B.

---

### 8. async/await e erro

O que acontece quando `buscarDados()` rejeita? O que é impresso?

```javascript
async function main() {
  try {
    const x = await buscarDados(); // retorna Promise rejeitada
    console.log(x);
  } catch (e) {
    console.log('Erro:', e.message);
  }
}
main();
```

**Resposta:**  
Quando a Promise rejeita, o `await` lança o erro e o fluxo cai no `catch`. Será impresso `Erro: <mensagem da rejeição>`. O `console.log(x)` não roda.

---

### 9. Promise.all

Complete para que `resultados` seja o array de resultados das três requisições (na mesma ordem), e que qualquer falha em uma delas rejeite o conjunto.

```javascript
const urls = ['/api/a', '/api/b', '/api/c'];
const resultados = await Promise.all(urls.map(url => fetch(url).then(r => r.json())));
// ou com async/await dentro do map (retornando Promise):
// const resultados = await Promise.all(urls.map(async url => { const r = await fetch(url); return r.json(); }));
```

**Resposta:**  
`Promise.all` espera todas as Promises; a ordem do array é preservada. Se uma rejeitar, `Promise.all` rejeita com esse motivo. Exemplo alternativo com async/await:

```javascript
const resultados = await Promise.all(
  urls.map(async (url) => {
    const res = await fetch(url);
    if (!res.ok) throw new Error(res.statusText);
    return res.json();
  })
);
```

---

## Integração com o material de front-end

- Para exercícios de **DOM**, **eventos** e **HTTP** (Fetch/Axios) no navegador, use os arquivos listados no [README do módulo](README.md) e o [exercicio_fixacao_http_dom.md](../frontend/exercicio_fixacao_http_dom.md).
- Os conceitos deste módulo (Promises, async/await, estruturas de dados) aplicam-se diretamente a esses exercícios: por exemplo, usar `async/await` com `fetch` e atualizar o DOM com o resultado.

---

**Fim do módulo JavaScript.** Para rever a estrutura completa, volte ao [README](README.md).

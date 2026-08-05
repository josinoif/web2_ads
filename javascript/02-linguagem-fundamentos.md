# 2. Fundamentos da linguagem: tipos, variáveis, estruturas de dados e escopo

Esta seção cobre os conceitos da linguagem que você usa todo dia: tipos de dados, declaração de variáveis (`let`, `const`, `var`), estruturas de dados nativas, funções, escopo e closures. Dominar isso evita bugs e permite tomar decisões conscientes em código e em entrevistas.

---

## Tipos de dados

JavaScript é **dinamicamente tipada**: o tipo está no **valor**, não na variável. O mesmo identificador pode guardar um número e depois uma string (embora isso seja evitado em código limpo).

### Tipos primitivos

| Tipo | Exemplo | Observação |
|------|----------|------------|
| `number` | `42`, `3.14`, `NaN` | Único tipo numérico (inteiro e decimal); `NaN` é do tipo `number`. |
| `string` | `'texto'`, `"texto"`, `` `template ${x}` `` | Aspas simples, duplas ou template literals. |
| `boolean` | `true`, `false` | |
| `undefined` | valor padrão de variável não inicializada | |
| `null` | ausência intencional de valor | |
| `symbol` | `Symbol('id')` | Identificador único, usado em propriedades “privadas” ou em chaves de objeto. |
| `bigint` | `9007199254740991n` | Inteiros maiores que `Number.MAX_SAFE_INTEGER`. |

### Tipo objeto

- **Objeto** (`object`): coleção de pares chave-valor; inclui arrays, funções (que são objetos especiais), datas, etc.
- **Verificação:** `typeof x` retorna `"object"` para objetos e para `null` (bug histórico); para distinguir array/objeto, use `Array.isArray(x)`.

```javascript
typeof 42;           // "number"
typeof "hello";      // "string"
typeof true;         // "boolean"
typeof undefined;    // "undefined"
typeof null;         // "object" (atenção!)
typeof {};           // "object"
typeof [];           // "object"
Array.isArray([]);   // true
```

Entender tipos ajuda a evitar surpresas (ex.: `"5" + 3` é `"53"`, não `8`) e a escolher estruturas de dados adequadas.

---

## let, const e var

### Regras práticas

| Declaração | Escopo | Reatribuição | Hoisting | Uso recomendado |
|------------|--------|--------------|----------|-------------------|
| `const` | bloco | não | sim (temporal dead zone) | preferir para tudo que não vai ser reatribuído |
| `let` | bloco | sim | sim (temporal dead zone) | quando a variável precisa ser reatribuída |
| `var` | função | sim | sim (hoisting “clássico”) | evitar em código novo |

- **Escopo de bloco:** `let` e `const` existem apenas dentro do `{}` onde foram declarados (incluindo `if`, `for`, `while`). `var` ignora blocos e só respeita função.
- **Temporal Dead Zone (TDZ):** Entre o início do bloco e a linha da declaração, `let`/`const` não podem ser acessados; acessar antes gera `ReferenceError`. Isso evita uso antes da declaração.
- **Const e mutação:** `const` impede **reatribuição** da variável, não a mutação do valor. Um objeto ou array declarado com `const` pode ter suas propriedades ou elementos alterados.

```javascript
const obj = { a: 1 };
obj.a = 2;   // permitido
obj = {};    // erro: reatribuição

const arr = [1, 2, 3];
arr.push(4); // permitido
arr = [];    // erro: reatribuição
```

No mercado e em boas práticas, **preferir `const` por padrão** e usar `let` só quando precisar reatribuir; evitar `var` em código novo.

---

## Operadores aritméticos e lógicos

### Operadores aritméticos

| Operador | Significado | Exemplo |
|----------|-------------|---------|
| `+` | Adição (ou concatenação de strings) | `3 + 5` → `8`; `"a" + "b"` → `"ab"`; `"5" + 3` → `"53"` |
| `-` | Subtração | `10 - 3` → `7` |
| `*` | Multiplicação | `4 * 2` → `8` |
| `/` | Divisão | `10 / 4` → `2.5` |
| `%` | Módulo (resto da divisão) | `10 % 3` → `1` |
| `**` | Exponenciação | `2 ** 3` → `8` |

**Atenção:** o `+` com string e número converte para string e concatena. Para somar numericamente, converta antes: `Number("5") + 3` ou `+"5" + 3`.

### Operadores de comparação

| Operador | Significado | Exemplo |
|----------|-------------|---------|
| `==` | Igualdade (com coerção de tipo) | `"5" == 5` → `true` |
| `===` | Igualdade estrita (tipo e valor) | `"5" === 5` → `false` |
| `!=` | Desigualdade (com coerção) | `"5" != 5` → `false` |
| `!==` | Desigualdade estrita | `"5" !== 5` → `true` |
| `<`, `>`, `<=`, `>=` | Menor, maior, menor ou igual, maior ou igual | `3 < 5` → `true` |

**Recomendação:** preferir **`===`** e **`!==`** para evitar surpresas da coerção (ex.: `null == undefined` é `true`; `0 == false` é `true`).

### Operadores lógicos

| Operador | Significado | Uso comum |
|----------|-------------|-----------|
| `&&` | E lógico | Retorna o primeiro valor *falsy* ou o último valor; usado em condições e valores padrão. |
| `\|\|` | OU lógico | Retorna o primeiro valor *truthy* ou o último; usado em fallback (ex.: `nome \|\| "Anônimo"`). |
| `!` | Negação | `!true` → `false`; converte para boolean e inverte. |

Valores **falsy** (avaliados como `false` em contexto booleano): `false`, `0`, `-0`, `""`, `null`, `undefined`, `NaN`, `0n`. Todo o resto é **truthy**.

```javascript
const nome = "";
console.log(nome || "Anônimo");     // "Anônimo"
console.log(0 && "não aparece");    // 0
console.log(2 && 3);                 // 3 (último truthy)
```

### Outros operadores úteis

- **Operador ternário:** `condição ? valorSeTrue : valorSeFalse` — atalho para if/else em expressões.
- **Nullish coalescing (`??`):** retorna o lado direito só quando o esquerdo é `null` ou `undefined` (não para `0` ou `""`). Ex.: `valor ?? "padrão"`.
- **Optional chaining (`?.`):** acessa propriedade só se o anterior existir; evita erro quando `obj` é `null`/`undefined`. Ex.: `obj?.prop?.nested`.

---

## Estruturas de controle: if, else, else if

O fluxo do programa pode ser alterado com condições.

```javascript
if (condição) {
  // executado se condição for truthy
}

if (condição) {
  // bloco 1
} else {
  // bloco 2 (quando condição é falsy)
}

if (x > 10) {
  // x maior que 10
} else if (x > 5) {
  // x entre 6 e 10
} else {
  // x <= 5
}
```

- A **condição** é avaliada como boolean (valores truthy/falsy). Use `===`/`!==` quando quiser comparação estrita.
- **else if** permite encadear várias condições; a primeira que for truthy executa e as demais são ignoradas.
- Boas práticas: evitar aninhamento excessivo (extrair para funções ou usar early return); preferir nomes de variáveis que deixem a intenção clara (`isValid`, `hasPermission`).

---

## Estruturas de repetição

### for

Repete um bloco enquanto a condição for verdadeira; controle explícito de inicialização, condição e incremento.

```javascript
for (let i = 0; i < 5; i++) {
  console.log(i); // 0, 1, 2, 3, 4
}
```

### for...of

Itera sobre **valores** de objetos iteráveis (array, string, Map, Set). Não dá o índice (use `entries()` ou um `for` com índice se precisar).

```javascript
const arr = ["a", "b", "c"];
for (const item of arr) {
  console.log(item); // "a", "b", "c"
}
```

### for...in

Itera sobre **chaves enumeráveis** de um objeto. Para arrays, retorna os índices (como string); prefira `for...of` para arrays. Use para objetos literais quando quiser percorrer propriedades.

```javascript
const obj = { a: 1, b: 2 };
for (const key in obj) {
  console.log(key, obj[key]); // "a" 1, "b" 2
}
```

### while e do...while

- **while:** avalia a condição antes de cada iteração; pode não executar nenhuma vez.
- **do...while:** executa pelo menos uma vez e depois avalia a condição.

```javascript
let n = 0;
while (n < 3) {
  console.log(n);
  n++;
}

let m = 0;
do {
  console.log(m);
  m++;
} while (m < 3);
```

### break e continue

- **break:** encerra o loop (ou o `switch`) imediatamente.
- **continue:** pula para a próxima iteração, ignorando o resto do bloco.

---

## Estruturas de dados

### Array

Lista ordenada, indexada por número (a partir de 0). Aceita qualquer tipo de valor; tamanho variável.

#### Métodos comuns de Array

| Método | Retorno / efeito | Exemplo de uso |
|--------|-------------------|----------------|
| **push(el)** | Adiciona ao final; retorna novo length | `arr.push(4)` |
| **pop()** | Remove e retorna o último elemento | `arr.pop()` |
| **unshift(el)** | Adiciona no início | `arr.unshift(0)` |
| **shift()** | Remove e retorna o primeiro | `arr.shift()` |
| **slice(início, fim)** | Novo array com trecho (fim opcional); não altera o original | `arr.slice(1, 3)` |
| **splice(índice, qtd, ...itens)** | Remove/insere no lugar; retorna removidos | `arr.splice(1, 2, 'x')` |
| **concat(arr2)** | Novo array: original + outro(s) | `arr.concat([4, 5])` |
| **join(sep)** | String com elementos unidos por `sep` | `arr.join(", ")` |
| **indexOf(val)** / **includes(val)** | Índice da primeira ocorrência / se existe | `arr.indexOf(2)`, `arr.includes(2)` |
| **find(fn)** / **findIndex(fn)** | Primeiro elemento/índice que satisfaz `fn` | `arr.find(x => x > 2)` |
| **filter(fn)** | Novo array com elementos que passam no teste | `arr.filter(x => x > 0)` |
| **map(fn)** | Novo array com resultado de `fn` em cada elemento | `arr.map(x => x * 2)` |
| **reduce(fn, inicial)** | Um único valor acumulado | `arr.reduce((acc, x) => acc + x, 0)` |
| **forEach(fn)** | Itera; não retorna novo array | `arr.forEach(x => console.log(x))` |
| **some(fn)** / **every(fn)** | Algum satisfaz? / todos satisfazem? | `arr.some(x => x < 0)` |

**Imutabilidade:** `map`, `filter`, `slice`, `concat` retornam novo array; `push`, `pop`, `splice` alteram o original. Prefira os que retornam novo array quando quiser evitar efeitos colaterais.

```javascript
const nums = [1, 2, 3, 4, 5];
const dobros = nums.map(x => x * 2);           // [2, 4, 6, 8, 10]
const pares = nums.filter(x => x % 2 === 0);  // [2, 4]
const soma = nums.reduce((acc, x) => acc + x, 0); // 15
const temMaiorQue4 = nums.some(x => x > 4);   // true
```

### Map

Mapa chave-valor; chave pode ser qualquer tipo. Ordem de inserção preservada.

#### Métodos e utilidade

| Método | Utilidade | Exemplo |
|--------|-----------|---------|
| **set(chave, valor)** | Define ou atualiza par chave-valor | `map.set("id", 1)` ou `map.set(objRef, dados)` |
| **get(chave)** | Retorna valor ou `undefined` | `map.get("id")` |
| **has(chave)** | Verifica se a chave existe | `map.has("id")` |
| **delete(chave)** | Remove o par; retorna se existia | `map.delete("id")` |
| **clear()** | Remove todos os pares | `map.clear()` |
| **size** | Número de pares (propriedade) | `map.size` |
| **keys()** / **values()** / **entries()** | Iteradores das chaves, valores ou pares [chave, valor] | `for (const [k, v] of map.entries())` |

```javascript
const cache = new Map();
cache.set("user:1", { nome: "Ana" });
cache.set("user:2", { nome: "Bruno" });
console.log(cache.get("user:1")); // { nome: "Ana" }
console.log(cache.has("user:3")); // false
for (const [key, value] of cache) {
  console.log(key, value);
}
```

### Set

Coleção de valores únicos. Ordem de inserção preservada.

#### Métodos e utilidade

| Método | Utilidade | Exemplo |
|--------|-----------|---------|
| **add(valor)** | Adiciona valor (duplicatas são ignoradas) | `set.add(1)` |
| **has(valor)** | Verifica existência (busca rápida) | `set.has(1)` |
| **delete(valor)** | Remove o valor; retorna se existia | `set.delete(1)` |
| **clear()** | Esvazia o set | `set.clear()` |
| **size** | Quantidade de elementos | `set.size` |

Set é iterável: `for (const x of set)` ou `[...set]`.

```javascript
const ids = new Set([1, 2, 2, 3, 1]);
ids.add(4);
ids.add(2); // não altera (já existe)
console.log(ids.size);        // 4
console.log([...ids]);        // [1, 2, 3, 4]
const arr = [1, 1, 2, 2, 3];
const unicos = [...new Set(arr)]; // [1, 2, 3] — remoção de duplicatas
```

### Object (objeto literal)

Coleção de pares chave-valor; chaves são strings ou symbols. Útil para entidades (usuário, produto). Limitação: chaves são convertidas para string (exceto symbol). A ordem de iteração costuma seguir a ordem de inserção para chaves string em engines modernas.

Escolha da estrutura: **Object** para chaves string fixas; **Map** para chaves arbitrárias ou ordem importante; **Set** para unicidade; **Array** para sequências ordenadas.

---

## Manipulação de objetos

### Acesso e alteração de propriedades

- **Notação ponto:** `obj.prop` — quando o nome da propriedade é identificador válido.
- **Notação colchetes:** `obj["prop"]` ou `obj[variavel]` — obrigatória quando o nome tem espaço, hífen, começa com número ou vem de variável.

```javascript
const user = { nome: "João", "idade": 25 };
user.nome = "Maria";
user["idade"] = 26;
const chave = "nome";
console.log(user[chave]); // "Maria"
```

### Adicionar e remover propriedades

```javascript
const obj = { a: 1 };
obj.b = 2;           // adiciona
obj["c"] = 3;       // adiciona
delete obj.b;       // remove a propriedade b
```

### Verificar existência de propriedade

- **in:** verifica se a chave existe (própria ou herdada). Ex.: `"nome" in obj`.
- **hasOwnProperty:** só propriedade própria. Ex.: `obj.hasOwnProperty("nome")`.
- **Object.hasOwn** (ES2022): recomendado para “própria”. Ex.: `Object.hasOwn(obj, "nome")`.

### Iterar sobre propriedades

```javascript
const obj = { a: 1, b: 2, c: 3 };
for (const key of Object.keys(obj)) {
  console.log(key, obj[key]);
}
Object.values(obj);   // [1, 2, 3]
Object.entries(obj);  // [["a", 1], ["b", 2], ["c", 3]]
```

### Copiar e mesclar objetos

- **Shallow copy:** `{ ...obj }` ou `Object.assign({}, obj)` — copia apenas o primeiro nível; objetos aninhados continuam por referência.
- **Mesclar:** `Object.assign(destino, origem1, origem2)` ou spread: `{ ...obj1, ...obj2 }` (propriedades de `obj2` sobrescrevem as de `obj1`).

```javascript
const original = { a: 1, b: { x: 2 } };
const copia = { ...original };
copia.b.x = 99;  // altera também original.b.x (mesma referência)
```

Para cópia profunda, use `structuredClone` (ambiente suportado) ou biblioteca (ex.: lodash `cloneDeep`).

### Desestruturação

Extrair propriedades para variáveis:

```javascript
const user = { nome: "Ana", idade: 30 };
const { nome, idade } = user;
const { nome: n, idade: i } = user;  // renomear
const { nome: nomeUser = "Anônimo" } = user;  // valor padrão
```

---

## Funções: conceito e formas de implementar e usar

Em JavaScript, funções são **cidadãs de primeira classe**: podem ser atribuídas a variáveis, passadas como argumento, retornadas por outras funções e armazenadas em estruturas de dados. Isso permite callbacks, funções de ordem superior e padrões como factory e módulo.

### Formas de declarar/criar funções

| Forma | Sintaxe | Hoisting | Observação |
|-------|---------|----------|------------|
| **Declaração** | `function nome() { }` | Sim (função inteira) | Pode ser chamada antes da linha em que aparece. |
| **Expressão (function)** | `const nome = function () { };` | Não (só a variável) | Função anônima atribuída a variável. |
| **Arrow function** | `const nome = () => { };` ou `(a, b) => a + b` | Não | Sem próprio `this`; herda do escopo léxico. |
| **Método** | `obj.metodo() { }` ou `metodo: function () { }` | Depende do objeto | Função como propriedade de objeto. |

```javascript
// Declaração
function soma(a, b) {
  return a + b;
}

// Expressão
const multiplicar = function (a, b) {
  return a * b;
};

// Arrow function (retorno implícito quando não há { })
const dobrar = (x) => x * 2;
const somar = (a, b) => a + b;

// Parâmetros com valor padrão
function greet(nome = "Visitante") {
  return `Olá, ${nome}`;
}

// Rest parameters (receber vários argumentos como array)
function log(...args) {
  console.log(args);
}
```

### Parâmetros e retorno

- **return:** encerra a função e devolve um valor. Sem `return`, a função retorna `undefined`.
- **Argumentos em excesso** são ignorados; **argumentos faltando** deixam parâmetros como `undefined` (use valor padrão se quiser).
- **arguments** (objeto antigo): em funções não-arrow, `arguments` contém os argumentos passados; em código moderno prefira rest: `...args`.

### Arrow function e `this`

- Funções declaradas com `function` têm próprio `this` (definido pela chamada: objeto, global, etc.).
- **Arrow functions** não têm próprio `this`; usam o `this` do **escopo léxico** (onde foram definidas). Por isso são usadas em callbacks (ex.: `setTimeout`, `addEventListener`, `.map`) quando você quer manter o `this` do contexto externo.

```javascript
const obj = {
  valor: 42,
  normal: function () {
    console.log(this.valor); // 42 (this = obj)
  },
  arrow: () => {
    console.log(this.valor); // undefined (this do escopo externo, não obj)
  }
};
```

### Uso de funções

- **Chamada direta:** `soma(1, 2)`.
- **Callback:** passar função como argumento para outra (ex.: `arr.map(fn)`, `setTimeout(fn, 1000)`).
- **Retorno de função:** factory (função que retorna outra função com “estado” fixo) e closures.
- **IIFE (Immediately Invoked Function Expression):** `(function () { })();` — executa na hora; hoje menos comum com módulos ES e blocos com `let`/`const`.

### Escopo e closures

- **Escopo léxico:** funções “enxergam” as variáveis do lugar onde foram **definidas**, não de onde são **chamadas**.
- **Closure:** função que mantém referência ao ambiente (variáveis do escopo externo) mesmo após a função externa ter terminado. Uso comum: dados “privados”, factories, callbacks que precisam “fixar” um valor.

```javascript
function contador() {
  let count = 0;
  return function () {
    count += 1;
    return count;
  };
}
const inc = contador();
inc(); // 1
inc(); // 2
```

Em entrevistas e em código real, closures aparecem em event handlers, funções de ordem superior e padrões de módulo. Saber explicar “a função interna mantém referência ao escopo da externa” demonstra domínio da linguagem.

---

## Gerenciamento de memória: profundidade, boas práticas e problemas comuns

JavaScript usa **coleta de lixo (garbage collection)**: a engine rastreia referências aos objetos e libera a memória quando não há mais como acessá-los. Você não aloca nem desaloca manualmente, mas **referências que permanecem ativas** impedem a coleta e podem causar vazamento de memória ou uso excessivo.

### Como a coleta de lixo se relaciona com referências

- Um valor é **coletável** quando não existe nenhuma referência ativa (variável, propriedade de objeto, closure, callback registrado) que aponte para ele.
- **Referências ativas** incluem: variáveis no escopo atual, propriedades de objetos ainda acessíveis, funções (closures) que “lembram” do escopo onde foram criadas, e callbacks/listeners ainda registrados (ex.: `addEventListener` sem `removeEventListener`).

### Boas práticas

| Prática | Motivo |
|---------|--------|
| **Evitar referências desnecessárias em closures de longa vida** | Closures mantêm o escopo; se guardarem objetos grandes ou estruturas que crescem, esses dados não são liberados enquanto o closure existir. |
| **Remover listeners quando não forem mais necessários** | `element.removeEventListener(tipo, handler)` — senão o handler (e seu closure) continua referenciado pelo DOM. |
| **Limpar referências em caches e mapas** | Se você guarda dados em `Map`/objeto e não remove entradas antigas, a memória cresce. Implementar TTL ou limite de tamanho. |
| **Evitar variáveis globais para dados grandes** | Objetos no escopo global vivem durante toda a aplicação e não são coletados. |
| **Em loops ou processamento em lote, não acumular em estruturas globais** | Ex.: não fazer `push` em um array global dentro de um loop que roda milhares de vezes sem nunca limpar. |
| **Desreferenciar quando não precisar mais** | Atribuir `null` a variáveis que apontam para objetos grandes quando o uso terminar (ex.: após processar um arquivo grande) pode ajudar a GC a reclamar a memória mais cedo. |

### Más práticas e exemplos de problemas de memória

**1. Closure que retém objeto grande**

```javascript
function criarHandler(dadosGrandes) {
  return function () {
    console.log(dadosGrandes); // closure mantém referência a dadosGrandes
  };
}
const handler = criarHandler(new Array(1000000).fill(0)); // array grande
document.getElementById("btn").addEventListener("click", handler);
// Enquanto o listener existir, dadosGrandes não é coletado.
```

**Solução:** não guardar no closure mais do que o necessário; se só precisar de um id, passar só o id e buscar o resto quando precisar, ou remover o listener quando não for mais usado.

**2. Listeners não removidos**

```javascript
element.addEventListener("click", function () {
  // ...
});
// Se o element for removido do DOM ou a página for uma SPA que não destrói o element,
// o listener pode manter referências (element, closure) e impedir coleta.
```

**Solução:** chamar `removeEventListener` no mesmo handler que foi registrado (por isso usar função nomeada ou guardar referência à função) quando o componente for desmontado ou o element deixar de ser usado.

**3. Acúmulo em cache ou coleção sem limite**

```javascript
const cache = new Map();
function getData(id) {
  if (cache.has(id)) return cache.get(id);
  const data = fetchAlgumaCoisa(id); // objeto grande
  cache.set(id, data);
  return data;
}
// A cada id novo, o cache cresce para sempre; em servidor ou app long-lived, memória sobe sem parar.
```

**Solução:** limite de tamanho (LRU), TTL (time-to-live) ou limpeza periódica; remover entradas antigas quando o cache passar de N itens.

**4. Referências circulares e “acidentalmente globais”**

- **Referências circulares** (objeto A referencia B, B referencia A) em geral **não** são problema para o GC moderno: quando não há referência externa a nenhum dos dois, ambos são coletados.
- **Variável não declarada** (sem `let`/`const`/`var`) em modo não estrito vira propriedade do objeto global (`window` no navegador, `global` no Node), mantendo referência até o fim da aplicação. Sempre declarar variáveis com `let` ou `const`.

**5. Retenção em estruturas de dados de longa vida**

```javascript
const historico = [];
function onEvent(dados) {
  historico.push(dados); // array cresce indefinidamente
}
```

**Solução:** limitar o tamanho do array (ex.: `historico.slice(-100)`) ou usar estrutura com tamanho máximo; em cenários de alto volume, não guardar tudo na memória.

### Resumo de memória

- **Coleta automática:** não há free manual; a GC libera o que não tem mais referência.
- **Problemas típicos:** closures que retêm dados grandes, listeners não removidos, caches/coleções que crescem sem limite, variáveis globais com dados grandes.
- **Boas práticas:** remover listeners, limitar tamanho de caches e buffers, evitar reter em closures só o necessário, desreferenciar (`= null`) quando fizer sentido e, no Node, monitorar memória em produção (ex.: `process.memoryUsage()`).

O evento loop e o modelo assíncrono (próximo arquivo) complementam essa visão: operações longas ou que acumulam dados podem impactar memória e tempo de resposta.

---

## Resumo da seção

- **Tipos:** primitivos (number, string, boolean, undefined, null, symbol, bigint) e objeto; `typeof` e `Array.isArray` para checagens.
- **Operadores:** aritméticos, comparação (preferir `===`/`!==`), lógicos (`&&`, `||`, `!`), ternário, `??`, `?.`.
- **Controle:** if, else, else if; estruturas de repetição (for, for...of, for...in, while, do...while); break e continue.
- **Estruturas de dados:** Array, Map e Set com métodos detalhados e exemplos; Object para entidades; manipulação de objetos (acesso, iteração, cópia, desestruturação).
- **Funções:** conceito de primeira classe; declaração, expressão, arrow function; parâmetros, retorno, `this`; escopo léxico e closures.
- **Memória:** coleta automática; boas práticas (remover listeners, limitar caches, evitar retenção em closures); más práticas e exemplos de vazamentos (closure grande, listeners não removidos, cache sem limite).

**Próximo:** [03-assincronismo-event-loop.md](03-assincronismo-event-loop.md) — Promises, async/await, event loop e processamento assíncrono.

# 6. Desafios técnicos

Os desafios abaixo colocam você em situações reais: uso da linguagem (estruturas de dados, assincronismo, escopo) no navegador ou no Node.js. Resolva pelo menos um no **navegador** (integrando com DOM/eventos ou Fetch, conforme o material em [../frontend/](../frontend/)) e um no **Node** (scripts ou servidor) para fixar a diferença de ambientes.

---

## Desafio 1 — Agregar dados de múltiplas requisições (async/await + estruturas)

**Cenário:** Uma tela precisa exibir uma lista de “posts” com o nome do autor de cada um. Você tem um endpoint de posts e um de usuários; cada post tem `userId`. Buscar todos os posts e, para cada `userId` único, buscar o usuário uma vez; montar um array de posts enriquecidos com o nome do autor.

**Objetivo:** Usar **async/await**, **Promise.all** onde fizer sentido e uma estrutura de dados adequada para não repetir requisição de usuário (ex.: Map userId → user). Evitar “callback hell” e múltiplas requisições para o mesmo usuário.

**Entregas:**
- Código que busca posts (ex.: `https://jsonplaceholder.typicode.com/posts`) e usuários (ex.: `https://jsonplaceholder.typicode.com/users`).
- Uso de **Set** ou **Map** para obter userIds únicos e cachear usuários.
- Lista final com pelo menos `title`, `body` e `authorName` (ou similar).

**Perguntas para reflexão:**
- Por que usar Map para mapear userId → user?
- O que acontece no event loop se você fizer um await por usuário em sequência em vez de Promise.all?

---

## Desafio 2 — Fila de tarefas com processamento assíncrono

**Cenário:** Você precisa processar uma lista de URLs (ex.: 10 links): para cada URL, fazer uma requisição GET e salvar o resultado (ou só o status). Não pode disparar todas de uma vez (para não sobrecarregar o servidor); processar até 2 em paralelo e ir enfileirando as próximas.

**Objetivo:** Implementar um controle de **concorrência** (max 2 requisições ao mesmo tempo) usando Promises. Pode ser com um loop que mantém um “pool” de 2 Promises e só adiciona a próxima quando uma terminar.

**Entregas:**
- Função que recebe array de URLs e número máximo de concorrência (ex.: 2).
- Uso de async/await ou Promises; nenhuma biblioteca externa obrigatória.
- Log ou array de resultados na ordem em que as requisições **terminaram** (pode ser diferente da ordem das URLs).

**Perguntas para reflexão:**
- Como isso se relaciona com o event loop e com “não bloquear a thread”?
- Em Node.js, por que limitar concorrência pode ser importante?

---

## Desafio 3 — Deduplicação e agregação (Set e Map)

**Cenário:** Você tem um array de objetos com `categoria` e `valor` (ex.: vendas por categoria). Precisar (1) listar todas as categorias únicas e (2) para cada categoria, somar os valores.

**Objetivo:** Usar **Set** para as categorias únicas e **Map** (ou Object) para agregação por categoria. Código legível e sem mutação desnecessária onde fizer sentido.

**Entregas:**
- Função que recebe array no formato `[{ categoria: 'A', valor: 10 }, ...]` e retorna objeto com: `{ categorias: ['A', 'B', ...], totaisPorCategoria: { A: 30, B: 15, ... } }`.
- Uso explícito de Set e Map (ou um deles) e justificativa em comentário ou documentação.

**Perguntas para reflexão:**
- Quando um Object seria suficiente em vez de Map para `totaisPorCategoria`?
- Por que Set para categorias em vez de “remover duplicatas” manualmente com filter?

---

## Desafio 4 — Cliente HTTP reutilizável (Node ou navegador)

**Cenário:** Em um projeto você precisa fazer várias requisições para a mesma API base (ex.: `https://api.exemplo.com/v1`), sempre com o mesmo header de autenticação (ex.: `Authorization: Bearer TOKEN`). Em vez de repetir URL base e headers em cada chamada, criar um “cliente” que encapsule isso.

**Objetivo:** Implementar uma função ou objeto que receba a URL base e os headers padrão e exponha métodos como `get(path)`, `post(path, body)` que retornem **Promises** (ou use async/await internamente). No navegador use Fetch; no Node pode usar `https` ou `fetch` (Node 18+).

**Entregas:**
- Código que monta a URL completa (base + path) e adiciona os headers em toda requisição.
- Uso de async/await e tratamento de erro (status não 2xx ou falha de rede).
- Exemplo de uso: `cliente.get('/users')`, `cliente.post('/users', { name: 'João' })`.

**Perguntas para reflexão:**
- Como isso se conecta ao que você viu em [../frontend/http_requests_fetch_api.md](../frontend/http_requests_fetch_api.md) e [../frontend/http_requests_axios.md](../frontend/http_requests_axios.md)?
- Por que retornar Promises (ou funções async) em vez de receber callbacks?

---

## Desafio 5 — Contador e closure (sem variável global)

**Cenário:** Você precisa de um contador que só pode ser alterado através de funções: “incrementar”, “decrementar” e “valor atual”. Nenhuma variável global; o estado do contador deve ficar “protegido” dentro de um closure.

**Objetivo:** Implementar uma função (factory) que retorna um objeto com métodos `increment`, `decrement` e `getValue`. O valor numérico fica em uma variável no escopo da factory, acessível apenas pelas funções retornadas.

**Entregas:**
- Código que cria um ou mais contadores independentes (cada chamada da factory gera um novo estado).
- Exemplo: `const c = createCounter(); c.increment(); c.increment(); c.getValue(); // 2`.

**Perguntas para reflexão:**
- Por que isso é um exemplo de closure?
- Em que situações reais (event listeners, módulos) esse padrão aparece?

---

## Desafio 6 — Escolha de abordagem (sem código)

**Cenário:** A equipe debate como implementar um fluxo em que: (1) o usuário escolhe um item em uma lista; (2) o sistema busca detalhes do item na API; (3) em seguida busca comentários relacionados. Alguém sugere callbacks; outro, Promises com .then; outro, async/await.

**Objetivo:** Redigir um parágrafo justificando **uma** das abordagens (callback, .then ou async/await) para esse fluxo, considerando: legibilidade, tratamento de erro e manutenção. Mencione event loop ou single-thread se fizer sentido.

**Entrega:** Texto curto (5–10 linhas) com sua escolha e critérios. Não é necessário implementar o código.

---

**Próximo:** [07-exercicios-fixacao.md](07-exercicios-fixacao.md) — Exercícios de fixação com respostas.

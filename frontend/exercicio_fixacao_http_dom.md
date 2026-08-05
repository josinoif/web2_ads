# Exercícios de Fixação — HTTP, DOM e Eventos

Estes exercícios integram **requisições HTTP** (Fetch), **manipulação do DOM** e **eventos** no navegador. Para fundamentos da linguagem (Promises, async/await, tipos, estruturas de dados), use o módulo [../javascript/](../javascript/) e os exercícios em [../javascript/07-exercicios-fixacao.md](../javascript/07-exercicios-fixacao.md).

---

### **HTTP**

#### **Nível Fácil**

1. **Pokedex Básica**

   - **Contexto:** Um app precisa exibir o nome de um Pokémon.

   - **Tarefa:** Complete o código abaixo para buscar o nome do Pokémon com ID 1 usando a PokeAPI (https://pokeapi.co/api/v2/pokemon/1) e exibi-lo em um parágrafo.

   - Código inicial:

     ```javascript
     
     fetch('https://pokeapi.co/api/v2/pokemon/1')
       .then(response => response.json())
       .then(data => {
         // Exiba o nome do Pokémon em um parágrafo
       });
     ```

2. **Lista de Produtos**

   - **Contexto:** Um site precisa listar seus produtos.

   - **Tarefa:** Use a FakeStoreAPI (https://fakestoreapi.com/products) para buscar os produtos e exibir os nomes em uma lista. Complete o código abaixo:

   - Código inicial:

     ```javascript
     
     fetch('https://fakestoreapi.com/products')
       .then(response => response.json())
       .then(data => {
         // Para cada produto, crie um elemento de lista e adicione ao DOM
       });
     ```

3. **Detalhes do Clima**

   - **Contexto:** Um site exibe a temperatura de uma cidade.

   - **Tarefa:** Use a API Ninjas (https://api-ninjas.com/api/weather) para buscar a temperatura de "New York" e exibi-la. Complete o código:

   - Código inicial:

     ```javascript
     fetch('https://api-ninjas.com/api/weather?city=New+York', {
       headers: { 'X-Api-Key': 'SUA_API_KEY' }
     })
       .then(response => response.json())
       .then(data => {
         // Exiba a temperatura no DOM
       });
     ```

4. **Buscar Categoria**

   - **Contexto:** Um site exibe produtos por categoria.

   - **Tarefa:** Use a FakeStoreAPI para buscar produtos da categoria "electronics". Adicione o nome de cada produto em uma lista.

   - Código inicial:

     ```javascript
     fetch('https://fakestoreapi.com/products/category/electronics')
       .then(response => response.json())
       .then(data => {
         // Crie e exiba uma lista com os produtos
       });
     ```

#### **Nível Intermediário**

5. **Formulário de Cadastro**

- **Contexto:** Um site precisa registrar novos produtos.

- **Tarefa:** Envie um produto usando o endpoint POST da FakeStoreAPI (https://fakestoreapi.com/products). Complete o código para enviar o nome e o preço do produto:

- Código inicial:

  ```javascript
  const produto = {
    title: 'Novo Produto',
    price: 29.99
  };
  
  fetch('https://fakestoreapi.com/products', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(produto)
  })
    .then(response => response.json())
    .then(data => {
      // Exiba o produto criado no console
    });
  ```

6. **Comparar Pokémons**

- **Contexto:** Um app exibe o Pokémon com maior altura.

- **Tarefa:** Use a PokeAPI para buscar dois Pokémons (ID 1 e ID 4) e exibir qual é o mais alto.

- Código inicial:

  ```javascript
  const ids = [1, 4];
  const promessas = ids.map(id => fetch(`https://pokeapi.co/api/v2/pokemon/${id}`).then(res => res.json()));
  
  Promise.all(promessas).then(pokemons => {
    // Compare os dois Pokémons e exiba o mais alto
  });
  ```

7. **Tabela de Produtos**

- **Contexto:** Um e-commerce exibe produtos em uma tabela.

- **Tarefa:** Use a FakeStoreAPI (https://fakestoreapi.com/products) para buscar os produtos e preencha uma tabela com nome e preço.

- Código inicial:

  ```javascript
  fetch('https://fakestoreapi.com/products')
    .then(response => response.json())
    .then(data => {
      // Para cada produto, crie uma linha na tabela
    });
  ```

### **Manipulação de DOM e Eventos**

#### **Nível Fácil**

8. **Alterar Texto**

- **Contexto:** Um botão altera o texto de um parágrafo.

- **Tarefa:** Complete o código para alterar o texto ao clicar no botão.

- Código inicial:

  ```html
  <p id="texto">Texto original</p>
  <button id="botao">Alterar</button>
  <script>
    document.getElementById('botao').addEventListener('click', () => {
      // Altere o texto do parágrafo para "Texto alterado"
    });
  </script>
  ```

9. **Adicionar Item**

- **Contexto:** Um app permite adicionar itens a uma lista.

- **Tarefa:** Complete o código para adicionar um item "Novo Item" à lista ao clicar no botão.

- Código inicial:

  ```html
  <ul id="lista">
    <li>Item 1</li>
    <li>Item 2</li>
  </ul>
  <button id="adicionar">Adicionar</button>
  <script>
    document.getElementById('adicionar').addEventListener('click', () => {
      // Crie um novo item e adicione à lista
    });
  </script>
  ```

10. **Mudar Cor**

- **Contexto:** Um botão altera a cor de um parágrafo.

- **Tarefa:** Altere a cor do texto para azul ao clicar no botão.

- Código inicial:

  ```html
  <p id="paragrafo">Texto colorido</p>
  <button id="mudarCor">Mudar Cor</button>
  <script>
    document.getElementById('mudarCor').addEventListener('click', () => {
      // Altere a cor do texto para azul
    });
  </script>
  ```



### **HTTP**

#### **Nível Fácil**

11. **Habilidades do Pokémon**

- **Contexto:** Um app exibe as habilidades de um Pokémon.

- **Tarefa:** Complete o código para buscar as habilidades do Pokémon com ID 25 e exibi-las como itens em uma lista.

- Código inicial:

  ```javascript
  fetch('https://pokeapi.co/api/v2/pokemon/25')
    .then(response => response.json())
    .then(data => {
      // Crie uma lista de habilidades do Pokémon
    });
  ```

12. **Categorias da Loja**

- **Contexto:** Uma loja quer exibir suas categorias.

- **Tarefa:** Use a FakeAPI (https://fakeapi.platzi.com/v1/categories) para buscar as categorias e exibi-las em uma lista.

- Código inicial:

  ```javascript
  fetch('https://fakeapi.platzi.com/v1/categories')
    .then(response => response.json())
    .then(data => {
      // Adicione cada categoria a uma lista no DOM
    });
  ```

13. **Produtos por Categoria**

- **Contexto:** Um e-commerce exibe produtos filtrados por categoria.

- **Tarefa:** Faça uma requisição para buscar produtos da categoria "jewelery" e exiba seus nomes.

- Código inicial:

  ```javascript
  fetch('https://fakestoreapi.com/products/category/jewelery')
    .then(response => response.json())
    .then(data => {
      // Exiba os nomes dos produtos no DOM
    });
  ```

14. **Primeiros 5 Pokémons**

- **Contexto:** Um app exibe os nomes dos 5 primeiros Pokémons.

- **Tarefa:** Use a PokeAPI para buscar os primeiros 5 Pokémons e exibi-los em uma lista.

- Código inicial:

  ```javascript
  fetch('https://pokeapi.co/api/v2/pokemon?limit=5')
    .then(response => response.json())
    .then(data => {
      // Adicione cada Pokémon a uma lista no DOM
    });
  ```

#### **Nível Intermediário**

15. **Detalhes do Produto**

- **Contexto:** Um cliente quer ver os detalhes de um produto específico.

- **Tarefa:** Use a FakeStoreAPI para buscar o produto com ID 1 e exibir seu nome, descrição e preço.

- Código inicial:

  ```javascript
  fetch('https://fakestoreapi.com/products/1')
    .then(response => response.json())
    .then(data => {
      // Exiba os detalhes do produto no DOM
    });
  ```

16. **Criar Nova Categoria**

- **Contexto:** Um administrador quer criar uma nova categoria.

- **Tarefa:** Use a FakeAPI para enviar uma requisição POST com o nome da nova categoria.

- Código inicial:

  ```javascript
  const novaCategoria = { name: 'Eletrônicos' };
  
  fetch('https://fakeapi.platzi.com/v1/categories', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(novaCategoria)
  })
    .then(response => response.json())
    .then(data => {
      // Exiba a confirmação no console
    });
  ```

17. **Comparar Produtos**

- **Contexto:** Um cliente quer saber qual produto é mais caro.

- **Tarefa:** Use a FakeStoreAPI para buscar os produtos com ID 1 e ID 2 e exiba o nome do mais caro.

- Código inicial:

  ```javascript
  const ids = [1, 2];
  const promessas = ids.map(id => fetch(`https://fakestoreapi.com/products/${id}`).then(res => res.json()));
  
  Promise.all(promessas).then(produtos => {
    // Compare os preços e exiba o nome do mais caro
  });
  ```

------

### **Manipulação de DOM e Eventos**

#### **Nível Fácil**

18. **Adicionar Parágrafo**

- **Contexto:** Um app permite adicionar parágrafos à página.

- **Tarefa:** Complete o código para adicionar um novo parágrafo ao clicar no botão.

- Código inicial:

  ```html
  <button id="adicionar">Adicionar Parágrafo</button>
  <div id="container"></div>
  <script>
    document.getElementById('adicionar').addEventListener('click', () => {
      // Crie e adicione um novo parágrafo ao container
    });
  </script>
  ```

19. **Alterar Classe**

- **Contexto:** Um botão altera o estilo de um parágrafo.

- **Tarefa:** Complete o código para alternar a classe "destaque" ao clicar no botão.

- Código inicial:

  ```html
  <p id="paragrafo">Texto exemplo</p>
  <button id="alterar">Alterar Estilo</button>
  <script>
    document.getElementById('alterar').addEventListener('click', () => {
      // Altere a classe do parágrafo para "destaque"
    });
  </script>
  ```

20. **Mostrar Mensagem**

- **Contexto:** Um app exibe uma mensagem ao clicar no botão.

- **Tarefa:** Complete o código para exibir "Olá, Mundo!" ao clicar no botão.

- Código inicial:

  ```html
  <button id="mostrar">Mostrar Mensagem</button>
  <p id="mensagem"></p>
  <script>
    document.getElementById('mostrar').addEventListener('click', () => {
      // Exiba a mensagem no parágrafo
    });
  </script>
  ```

21. **Esconder Elemento**

- **Contexto:** Um botão esconde um parágrafo.

- **Tarefa:** Complete o código para esconder o parágrafo ao clicar no botão.

- Código inicial:

  ```html
  <p id="paragrafo">Texto visível</p>
  <button id="esconder">Esconder</button>
  <script>
    document.getElementById('esconder').addEventListener('click', () => {
      // Esconda o parágrafo
    });
  </script>
  ```

22. **Adicionar e Remover Itens**

- **Contexto:** Um app gerencia itens de uma lista.

- **Tarefa:** Complete o código para adicionar ou remover itens da lista ao clicar nos botões.

- Código inicial:

  ```html
  <ul id="lista"></ul>
  <button id="adicionar">Adicionar</button>
  <button id="remover">Remover</button>
  <script>
    document.getElementById('adicionar').addEventListener('click', () => {
      // Adicione um item à lista
    });
  
    document.getElementById('remover').addEventListener('click', () => {
      // Remova o último item da lista
    });
  </script>
  ```

#### **Nível Intermediário**

23. **Validação de Campo**

- **Contexto:** Um formulário valida se um campo está vazio.

- **Tarefa:** Complete o código para exibir um alerta se o campo estiver vazio ao clicar no botão.

- Código inicial:

  ```html
  <input id="campo" type="text" />
  <button id="validar">Validar</button>
  <script>
    document.getElementById('validar').addEventListener('click', () => {
      // Valide se o campo está vazio e exiba um alerta
    });
  </script>
  ```

24. **Contador Dinâmico**

- **Contexto:** Um contador é incrementado automaticamente.

- **Tarefa:** Complete o código para incrementar o contador a cada 1 segundo.

- Código inicial:

  ```html
  <p id="contador">0</p>
  <script>
    let contador = 0;
    setInterval(() => {
      // Incremente o contador e atualize o parágrafo
    }, 1000);
  </script>
  ```

25. **Alterar Imagem ao Clicar**

- **Contexto:** Um botão altera a imagem exibida.

- **Tarefa:** Complete o código para trocar a imagem ao clicar no botão.

- Código inicial:

  ```html
  <img id="imagem" src="imagem1.jpg" />
  <button id="trocar">Trocar Imagem</button>
  <script>
    document.getElementById('trocar').addEventListener('click', () => {
      // Altere o atributo src da imagem
    });
  </script>
  ```
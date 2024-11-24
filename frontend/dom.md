# Introdução a Manipulação de DOM

## O que é DOM?

DOM (Document Object Model) é uma interface de programação para documentos HTML e XML. Ele representa a estrutura do documento como uma árvore de nós, onde cada nó corresponde a uma parte do documento, como um elemento, atributo ou texto. O DOM permite que linguagens de programação, como JavaScript, acessem e manipulem o conteúdo, estrutura e estilo de documentos web de forma dinâmica.

## Utilidade do DOM

A manipulação do DOM é essencial para criar páginas web interativas e dinâmicas. Com o DOM, você pode:

- Alterar o conteúdo de elementos HTML.
- Modificar atributos de elementos HTML.
- Adicionar ou remover elementos HTML.
- Alterar o estilo CSS de elementos.
- Reagir a eventos do usuário, como cliques e pressionamentos de teclas.

## Exemplos de Caso de Uso

### 1. Alterar o Conteúdo de um Elemento

Você pode usar o DOM para alterar o texto de um parágrafo:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de DOM</title>
</head>
<body>
    <p id="meuParagrafo">Texto original</p>
    <button onclick="alterarTexto()">Alterar Texto</button>

    <script>
        function alterarTexto() {
            document.getElementById('meuParagrafo').innerText = 'Texto alterado!';
        }
    </script>
</body>
</html>
```

### 2. Modificar Atributos de um Elemento
Você pode usar o DOM para alterar atributos de um elemento, como a fonte de uma imagem:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de DOM</title>
</head>
<body>
    <img id="minhaImagem" src="imagem1.jpg" alt="Imagem 1">
    <button onclick="alterarImagem()">Alterar Imagem</button>

    <script>
        function alterarImagem() {
            document.getElementById('minhaImagem').src = 'imagem2.jpg';
        }
    </script>
</body>
</html>
```

### 3. Adicionar ou Remover Elementos

Você pode usar o DOM para adicionar ou remover elementos da página:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de DOM</title>
</head>
<body>
    <ul id="minhaLista">
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    <button onclick="adicionarItem()">Adicionar Item</button>
    <button onclick="removerItem()">Remover Item</button>

    <script>
        function adicionarItem() {
            const novoItem = document.createElement('li');
            novoItem.innerText = 'Novo Item';
            document.getElementById('minhaLista').appendChild(novoItem);
        }

        function removerItem() {
            const lista = document.getElementById('minhaLista');
            lista.removeChild(lista.lastElementChild);
        }
    </script>
</body>
</html>

```

### 4. Alterar o Estilo de um Elemento
Você pode usar o DOM para alterar o estilo CSS de um elemento:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Exemplo de DOM</title>
</head>
<body>
    <p id="meuParagrafo">Texto com estilo</p>
    <button onclick="alterarEstilo()">Alterar Estilo</button>

    <script>
        function alterarEstilo() {
            const paragrafo = document.getElementById('meuParagrafo');
            paragrafo.style.color = 'red';
            paragrafo.style.fontSize = '20px';
        }
    </script>
</body>
</html>

```

A manipulação do DOM é uma habilidade fundamental para desenvolvedores web, permitindo a criação de páginas interativas e dinâmicas. Com o DOM, você pode acessar e modificar qualquer parte de um documento HTML ou XML, proporcionando uma experiência de usuário rica e responsiva

# Funções e Atributos Úteis para Manipulação de DOM

Aqui está uma lista de funções e atributos úteis para manipulação de DOM em JavaScript:

1. **`getElementById`**
   - Obtém um elemento pelo seu ID.

2. **`getElementsByClassName`**
   - Obtém uma coleção de elementos que possuem uma determinada classe.

3. **`getElementsByTagName`**
   - Obtém uma coleção de elementos com um determinado nome de tag.

4. **`querySelector`**
   - Obtém o primeiro elemento que corresponde a um seletor CSS especificado.

5. **`querySelectorAll`**
   - Obtém todos os elementos que correspondem a um seletor CSS especificado.

6. **`createElement`**
   - Cria um novo elemento HTML.

7. **`removeChild`**
   - Remove um elemento filho de um elemento pai.

8. **`appendChild`**
   - Adiciona um novo elemento filho a um elemento pai.

9. **`replaceChild`**
   - Substitui um elemento filho por outro.

10. **`setAttribute`**
    - Define um atributo para um elemento.

11. **`getAttribute`**
    - Obtém o valor de um atributo de um elemento.

12. **`classList`**
    - Permite manipular as classes CSS de um elemento (adicionar, remover, alternar classes).

13. **`innerHTML`**
    - Define ou obtém o conteúdo HTML de um elemento.

14. **`innerText`**
    - Define ou obtém o texto de um elemento.

15. **`style`**
    - Permite manipular os estilos CSS de um elemento.

Essas funções e atributos são fundamentais para a manipulação do DOM e permitem criar interações dinâmicas e responsivas em páginas web.


## Exercícios de Manipulação de DOM

### Nível Fácil

1. **Alterar Texto de um Parágrafo**
   - Crie um parágrafo com algum texto e um botão. Quando o botão for clicado, altere o texto do parágrafo.
   - **Dica:** Use `getElementById` e `innerText`.

2. **Mudar Cor de Fundo**
   - Crie um parágrafo e dois botões. Um botão deve mudar a cor de fundo do parágrafo para azul e o outro para vermelho.
   - **Dica:** Use `getElementById` e `style`.

3. **Adicionar Item à Lista**
   - Crie uma lista não ordenada e um botão. Quando o botão for clicado, adicione um novo item à lista.
   - **Dica:** Use `createElement` e `appendChild`.

4. **Mostrar e Esconder Elemento**
   - Crie um parágrafo e um botão. Quando o botão for clicado, o parágrafo deve ser escondido ou mostrado alternadamente.
   - **Dica:** Use `getElementById` e `style.display`.

### Nível Intermediário

5. **Contador de Cliques**
   - Crie um botão e um parágrafo que exibe um contador. Cada vez que o botão for clicado, o contador deve ser incrementado.
   - **Dica:** Use `getElementById` e `innerText`.

6. **Alterar Atributo de Imagem**
   - Crie uma imagem e um botão. Quando o botão for clicado, altere o atributo `src` da imagem para uma nova URL.
   - **Dica:** Use `getElementById` e `setAttribute`.

7. **Adicionar e Remover Classe**
   - Crie um parágrafo e dois botões. Um botão deve adicionar uma classe ao parágrafo e o outro deve remover a classe.
   - **Dica:** Use `getElementById` e `classList.add` / `classList.remove`.

8. **Formulário de Validação**
   - Crie um formulário com um campo de texto e um botão de envio. Valide se o campo de texto não está vazio antes de permitir o envio.
   - **Dica:** Use `getElementById` e `addEventListener` para o evento `submit`.

### Nível Difícil

9. **Tabela Dinâmica**
   - Crie uma tabela com uma linha de cabeçalho e um botão. Quando o botão for clicado, adicione uma nova linha à tabela com dados fictícios.
   - **Dica:** Use `createElement`, `appendChild` e `insertRow`.

10. **Jogo de Memória Simples**
    - Crie um jogo de memória com cartas que podem ser viradas ao clicar. As cartas devem ser embaralhadas e o jogo deve detectar quando todas as cartas foram combinadas.
    - **Dica:** Use `getElementById`, `classList`, e `setTimeout`.


11. **Validação de Formulário em Tempo Real**
    - Crie um formulário com vários campos (nome, email, senha). Adicione validação em tempo real para garantir que os campos sejam preenchidos corretamente antes de permitir o envio do formulário. Exiba mensagens de erro apropriadas para cada campo.
    - **Dica:** Use `getElementById`, `addEventListener` e `classList`.

Esses exercícios ajudarão a praticar a manipulação de DOM em JavaScript e a criar interações dinâmicas e responsivas em páginas web.
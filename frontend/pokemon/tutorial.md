# Tutorial: Listando Pokémons com a API PokeAPI

Neste tutorial, vamos aprender a criar uma listagem de Pokémons utilizando a API [PokeAPI](https://pokeapi.co/). Vamos usar HTML, CSS, JavaScript e Bootstrap para criar nossa aplicação.

## Passo 1: Estrutura Básica do HTML

Primeiro, vamos criar a estrutura básica do nosso arquivo HTML.

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lista de Pokémons</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1 class="my-4">Lista de Pokémons</h1>
        <div id="pokemon-list" class="row"></div>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.bundle.min.js"></script>
    <script src="script.js"></script>
</body>
</html>
```



## Passo 2: Estilizando com CSS

Vamos adicionar um pouco de estilo ao nosso projeto. Crie um arquivo `styles.css` e adicione o seguinte código:

```css
body {
    background-color: #f8f9fa;
}

.pokemon-card {
    margin-bottom: 20px;
}
```



Não se esqueça de incluir o arquivo CSS no HTML:

```html
<link rel="stylesheet" href="styles.css">
```



## Passo 3: Buscando Dados da API

Agora, vamos criar um arquivo `script.js` e adicionar o código para buscar os dados da API e exibir os Pokémons na página.



```javascript
document.addEventListener('DOMContentLoaded', () => {
    const pokemonList = document.getElementById('pokemon-list');

    fetch('https://pokeapi.co/api/v2/pokemon?limit=10')
        .then(response => response.json())
        .then(data => {
            data.results.forEach(pokemon => {
                fetch(pokemon.url)
                    .then(response => response.json())
                    .then(pokemonData => {
                        const pokemonCard = document.createElement('div');
                        pokemonCard.classList.add('col-md-4', 'pokemon-card');
                        pokemonCard.innerHTML = `
                            <div class="card">
                                <img src="${pokemonData.sprites.front_default}" class="card-img-top" alt="${pokemonData.name}">
                                <div class="card-body">
                                    <h5 class="card-title">${pokemonData.name}</h5>
                                    <p class="card-text">ID: ${pokemonData.id}</p>
                                </div>
                            </div>
                        `;
                        pokemonList.appendChild(pokemonCard);
                    });
            });
        });
});
```



## Passo 4: Executando o Projeto

Agora, basta abrir o arquivo HTML no seu navegador e você verá a lista de Pokémons sendo exibida.

## Conclusão

Neste tutorial, aprendemos a criar uma listagem de Pokémons utilizando a API PokeAPI com HTML, CSS, JavaScript e Bootstrap. Você pode expandir este projeto adicionando mais funcionalidades, como paginação, busca e filtros.




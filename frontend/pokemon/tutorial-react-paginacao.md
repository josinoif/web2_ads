# Tutorial: Listando Pokémons com Paginação usando a API PokeAPI com ReactJS e Next.js

Neste tutorial, vamos aprender a criar uma listagem de Pokémons com paginação utilizando a API [PokeAPI](https://pokeapi.co/) com ReactJS e Next.js.

## Passo 1: Criando o Projeto Next.js

Primeiro, vamos criar um novo projeto Next.js. Abra o terminal e execute o seguinte comando:

```bash
npx create-next-app@latest pokemon-list-paginacao
cd pokemon-list-paginacao
```



## Passo 2: Instalando o Bootstrap

Vamos instalar o Bootstrap para estilizar nossa aplicação. Execute o seguinte comando no terminal:

```shell
npm install bootstrap
```



## Passo 3: Configurando o Bootstrap

Abra o arquivo `src/app/layout.js` e importe o CSS do Bootstrap:

```javascript
import 'bootstrap/dist/css/bootstrap.min.css';
```



## Passo 4: Criando a Página de Listagem de Pokémons com Paginação

Vamos criar a página principal que exibirá a lista de Pokémons com paginação. Abra o arquivo `src/app/page.js` e adicione o seguinte código:

```javascript
"use client"

import { useEffect, useState } from 'react';
import Head from 'next/head';
import 'bootstrap/dist/css/bootstrap.min.css';

export default function Home() {

  const [pokemons, setPokemons] = useState([]);
  const [nextPage, setNextPage] = useState(null);
  const [previousPage, setPreviousPage] = useState(null);

  useEffect(() => {
    fetchPokemons('https://pokeapi.co/api/v2/pokemon?limit=30');
  }, []);

  const fetchPokemons = (url) => {
    fetch(url)
      .then(response => response.json())
      .then(data => {
        const fetches = data.results.map(pokemon =>
          fetch(pokemon.url).then(response => response.json())
        );
        Promise.all(fetches).then(pokemonData => setPokemons(pokemonData));
        setNextPage(data.next);
        setPreviousPage(data.previous);
      });

  };

  const handlePreviousPage = () => {
    if (previousPage) {
      fetchPokemons(previousPage);
    }
  };

  const handleNextPage = () => {
    if (nextPage) {
      fetchPokemons(nextPage);
    }
  };

  return (

    <div className="container">
      <Head>
        <title>Lista de Pokémons</title>
      </Head>
      <h1 className="my-4">Lista de Pokémons</h1>
      <div className="row">

        {pokemons.map(pokemon => (

          <div key={pokemon.id} className="col-md-4 pokemon-card mb-4">
            <div className="card h-100 d-flex flex-column">
              <img src={pokemon.sprites.other.dream_world.front_default} className="card-img-top img-fluid" alt={pokemon.name} style={{ height: '200px', objectFit: 'contain' }} />
              <div className="card-body d-flex flex-column">
                <h5 className="card-title">{pokemon.name}</h5>
                <p className="card-text">ID: {pokemon.id}</p>
              </div>
            </div>
          </div>

        ))}

      </div>
      <div className="d-flex justify-content-between my-4">
        <button className="btn btn-primary" onClick={handlePreviousPage} disabled={!previousPage}>
          Anterior
        </button>
        <button className="btn btn-primary" onClick={handleNextPage} disabled={!nextPage}>
          Próxima
        </button>
      </div>
    </div>

  );

}
```



## Passo 5: Executando o Projeto

Agora, basta executar o projeto com o seguinte comando:

```shell
npm run dev
```

Abra o navegador e acesse `http://localhost:3000` para ver a lista de Pokémons sendo exibida com paginação.

## Conclusão

Neste tutorial, aprendemos a criar uma listagem de Pokémons com paginação utilizando a API PokeAPI com ReactJS e Next.js. Você pode expandir este projeto adicionando mais funcionalidades, como busca e filtros.

Espero que tenha gostado deste tutorial!
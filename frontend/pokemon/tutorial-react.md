# Tutorial: Listando Pokémons com a API PokeAPI usando ReactJS e Next.js

Neste tutorial, vamos aprender a criar uma listagem de Pokémons utilizando a API [PokeAPI](https://pokeapi.co/) com ReactJS e Next.js.

## Passo 1: Criando o Projeto Next.js

Primeiro, vamos criar um novo projeto Next.js. Abra o terminal e execute o seguinte comando:

```bash
npx create-next-app@latest pokemon-list
cd pokemon-list
```



## Passo 2: Instalando o Bootstrap

Vamos instalar o Bootstrap para estilizar nossa aplicação. Execute o seguinte comando no terminal:

```shell
npm install bootstrap
```



## Passo 3: Configurando o Bootstrap

Abra o arquivo `layout.js` e importe o CSS do Bootstrap:



```javascript
import 'bootstrap/dist/css/bootstrap.min.css';
import '../styles/globals.css';

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />;
}

export default MyApp;
```



## Passo 4: Criando a Página de Listagem de Pokémons

Vamos criar a página principal que exibirá a lista de Pokémons. Abra o arquivo `pages/index.js` e adicione o seguinte código:

```javascript
"use client";

import { useEffect, useState } from 'react';
import Head from 'next/head';
import 'bootstrap/dist/css/bootstrap.min.css';

export default function Home() {
  const [pokemons, setPokemons] = useState([]);

  useEffect(() => {
    fetch('https://pokeapi.co/api/v2/pokemon?limit=10')
      .then(response => response.json())
      .then(data => {
        const fetches = data.results.map(pokemon =>
          fetch(pokemon.url).then(response => response.json())
        );
        Promise.all(fetches).then(pokemonData => setPokemons(pokemonData));
      });
  }, []);

  return (
    <div className="container">
      <Head>
        <title>Lista de Pokémons</title>
      </Head>
      <h1 className="my-4">Lista de Pokémons</h1>
      <div className="row">
        {pokemons.map(pokemon => (
          <div key={pokemon.id} className="col-md-4 pokemon-card">
            <div className="card">
              <img src={pokemon.sprites.front_default} className="card-img-top" alt={pokemon.name} />
              <div className="card-body">
                <h5 className="card-title">{pokemon.name}</h5>
                <p className="card-text">ID: {pokemon.id}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## Passo 5: Estilizando com CSS

Vamos adicionar um pouco de estilo ao nosso projeto. Crie um arquivo `styles/globals.css` e adicione o seguinte código:

```css
body {
  background-color: #f8f9fa;
}

.pokemon-card {
  margin-bottom: 20px;
}
```

## Passo 6: Executando o Projeto

Agora, basta executar o projeto com o seguinte comando:

```bash
npm run dev
```

Abra o navegador e acesse `http://localhost:3000` para ver a lista de Pokémons sendo exibida.

## Conclusão

Neste tutorial, aprendemos a criar uma listagem de Pokémons utilizando a API PokeAPI com ReactJS e Next.js. Você pode expandir este projeto adicionando mais funcionalidades, como paginação, busca e filtros.

Espero que tenha gostado deste tutorial!


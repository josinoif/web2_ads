# Criação de Listagem em ReactJS

Para criar uma tela de listagem em React, que lê dados de uma API e exibe todos os itens devolvidos em uma tela siga as instruções abaixo:


##  Passo 1: Configurar o Projeto

1. Crie um novo projeto React usando o `create-react-app`:

```bash
npx create-react-app my-form
cd my-form
```

2. Instale o Axios para fazer requisições HTTP:

```bash 
npm install axios
```

##  Passo 2: Criar o componente List

Vamos criar um componente que busca os dados da API e os exibe em uma tabela.

```jsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function ItemList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // URL da sua API no CRUDCrud
    const url = 'https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/users';

    const fetchData = async () => {
      try {
        const response = await axios.get(url);
        setItems(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p>Carregando...</p>;
  if (error) return <p>Erro ao carregar dados: {error}</p>;

  return (
    <div>
      <h2>Lista de Usuários</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nome</th>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item._id}>
              <td>{item._id}</td>
              <td>{item.name}</td>
              <td>{item.email}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ItemList;

```

## Passo 3: Explicação dos Principais Elementos

- **useEffect**: Utilizado para fazer a chamada à API quando o componente é montado. Faz a requisição GET para buscar todos os itens.
- **axios.get**: Faz a requisição para a URL da API.
- **loading, error**: Estados para gerenciar o carregamento e possíveis erros.
- **items.map**: Itera sobre os itens recebidos e os exibe em linhas da tabela.

## Passo 4:  Substitua o YOUR_UNIQUE_ENDPOINT
Substitua `"YOUR_UNIQUE_ENDPOINT"` pelo seu endpoint único fornecido pela CRUDCrud.

## Passo 5: Adicionar Estilo à Tabela

Você pode adicionar um estilo básico à tabela para torná-la mais legível. Adicione o seguinte CSS no arquivo App.css ou no arquivo CSS correspondente:

```css
table {
  width: 100%;
  border-collapse: collapse;
  margin: 20px 0;
}

table, th, td {
  border: 1px solid #ddd;
}

th, td {
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
}

```

## Passo 6: Adicionar o Componente List ao App.js

No arquivo App.js, importe e renderize o componente de listagem:

```jsx
import React from 'react';
import CrudForm from './CrudForm';
import ItemList from './ItemList';

function App() {
  return (
    <div className="App">
      <h1>Cadastro de Usuários</h1>
      <CrudForm />
      <ItemList />
    </div>
  );
}

export default App;

```

## Passo 6: Execute a Aplicacao

Executar a Aplicação

```bash
 npm start
```

Agora você terá uma tela de listagem que exibe todos os itens cadastrados em uma tabela HTML. O componente ItemList faz uma requisição à API, exibe os itens em uma tabela e lida com estados de carregamento e erro.
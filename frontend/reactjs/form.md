# Criação de Formulário em ReactJS

Para criar uma tela de formulário em React que envia dados para uma aplicação CRUD, como a CRUDCrud (um serviço simples de armazenamento de dados via API REST), siga os passos abaixo:

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

##  Passo 2: Criar o Formulário

1. Crie um novo componente `Form.js` na pasta `src`:

```jsx

import React, { useState } from 'react';
import axios from 'axios';

function CrudForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // URL da sua API no CRUDCrud
    const url = 'https://crudcrud.com/api/YOUR_UNIQUE_ENDPOINT/users';

    try {
      const response = await axios.post(url, formData);

      if (response.status === 201) {
        alert('Usuário criado com sucesso!');
        setFormData({ name: '', email: '' });
      } else {
        alert('Erro ao criar usuário.');
      }
    } catch (error) {
      console.error('Erro:', error);
      alert('Erro ao se conectar à API.');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Nome:</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      <button type="submit">Cadastrar</button>
    </form>
  );
}

export default CrudForm;
```

## Passo 3: Explicação dos Principais Elementos

- axios.post: Utiliza o `axios` para fazer uma requisição POST para a URL fornecida com o `formData` como corpo da requisição.
- response.status: Verifica o status da resposta para confirmar se o usuário foi criado com sucesso. O status `201` é o código padrão para uma criação bem-sucedida.

## Passo 4:  Substitua o YOUR_UNIQUE_ENDPOINT
Substitua `"YOUR_UNIQUE_ENDPOINT"` pelo seu endpoint único fornecido pela CRUDCrud.

## Passo 5: Adicionar o Componente Form ao App.js

No arquivo App.js, importe e renderize o seu componente de formulário como antes:


```jsx

import React from 'react';
import CrudForm from './CrudForm';

function App() {
  return (
    <div className="App">
      <h1>Cadastro de Usuários</h1>
      <CrudForm />
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

Agora, o formulário em React utiliza axios para enviar os dados para a API CRUDCrud. A funcionalidade e o fluxo permanecem os mesmos, mas com `axios para gerenciar as requisições HTTP.
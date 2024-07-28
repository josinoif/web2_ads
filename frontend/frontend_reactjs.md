Vamos ajustar o tutorial para que a tela inicial seja a tela de listagem de usuários com opções de cadastrar, editar e deletar usuários diretamente na mesma tela. 

### Passo 1: Configurar o Projeto React

1. Crie um novo projeto React usando `create-react-app`:

```bash
npx create-react-app crud-frontend-react
cd crud-frontend-react
```

2. Instale axios para fazer as requisições HTTP:

```bash
npm install axios
```

### Passo 2: Criar a Estrutura do Projeto

Dentro da pasta `src`, crie uma pasta chamada `components` onde vamos criar nossos componentes.

### Passo 3: Criar o Componente `UserForm`

Crie um arquivo `UserForm.js` dentro da pasta `components`:

```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UserForm = ({ selectedUser, fetchUsers, clearSelectedUser }) => {
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    if (selectedUser) {
      setName(selectedUser.name);
      setAge(selectedUser.age);
      setEmail(selectedUser.email);
    } else {
      setName('');
      setAge('');
      setEmail('');
    }
  }, [selectedUser]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedUser) {
      axios.put(`http://localhost:3000/users/${selectedUser.id}`, { name, age, email })
        .then(() => {
          fetchUsers();
          clearSelectedUser();
        });
    } else {
      axios.post('http://localhost:3000/users', { name, age, email })
        .then(fetchUsers);
    }
    setName('');
    setAge('');
    setEmail('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>{selectedUser ? 'Edit User' : 'Add User'}</h2>
      <div>
        <label>Name</label>
        <input type="text" value={name} onChange={(e) => setName(e.target.value)} required />
      </div>
      <div>
        <label>Age</label>
        <input type="number" value={age} onChange={(e) => setAge(e.target.value)} required />
      </div>
      <div>
        <label>Email</label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </div>
      <button type="submit">{selectedUser ? 'Update' : 'Add'}</button>
      {selectedUser && <button type="button" onClick={clearSelectedUser}>Cancel</button>}
    </form>
  );
};

export default UserForm;
```

### Passo 4: Criar o Componente `UserList`

Crie um arquivo `UserList.js` dentro da pasta `components`:

```javascript
import React from 'react';
import axios from 'axios';

const UserList = ({ users, fetchUsers, setSelectedUser }) => {
  const deleteUser = (id) => {
    axios.delete(`http://localhost:3000/users/${id}`)
      .then(fetchUsers);
  };

  return (
    <div>
      <h2>User List</h2>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Age</th>
            <th>Email</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.name}</td>
              <td>{user.age}</td>
              <td>{user.email}</td>
              <td>
                <button onClick={() => setSelectedUser(user)}>Edit</button>
                <button onClick={() => deleteUser(user.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default UserList;
```

### Passo 5: Configurar o Componente Principal `App`

Atualize o arquivo `App.js` para integrar os componentes `UserForm` e `UserList`:

```javascript
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import UserForm from './components/UserForm';
import UserList from './components/UserList';
import './App.css';

const App = () => {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);

  const fetchUsers = () => {
    axios.get('http://localhost:3000/users')
      .then(res => setUsers(res.data));
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const clearSelectedUser = () => setSelectedUser(null);

  return (
    <div className="App">
      <h1>CRUD Application</h1>
      <UserForm selectedUser={selectedUser} fetchUsers={fetchUsers} clearSelectedUser={clearSelectedUser} />
      <UserList users={users} fetchUsers={fetchUsers} setSelectedUser={setSelectedUser} />
    </div>
  );
};

export default App;
```

### Passo 6: Estilizar a Aplicação

Crie um arquivo `App.css` para adicionar um pouco de estilo:

```css
.App {
  text-align: center;
  max-width: 800px;
  margin: auto;
}

form {
  margin-bottom: 20px;
}

label {
  display: block;
  margin: 10px 0 5px;
}

input {
  padding: 5px;
  margin-bottom: 10px;
  width: 100%;
}

button {
  padding: 10px 20px;
  margin: 5px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
}

th {
  background-color: #f2f2f2;
}
```

### Passo 7: Iniciar a Aplicação

1. Certifique-se de que o servidor Express.js está em execução.

2. Inicie a aplicação React:

```bash
npm start
```

### Conclusão

Agora você tem um frontend React que consome a API CRUD criada com Express.js e MySQL. A tela inicial exibe a lista de usuários com opções de adicionar, editar e deletar usuários diretamente na mesma tela. Para uma aplicação mais completa, considere adicionar tratamento de erros, validação de formulários e autenticação.
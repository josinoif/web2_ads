Vamos configurar um servidor Express para servir apenas os arquivos estáticos do frontend. Este frontend fará requisições para um backend externo. Vamos ajustar o projeto conforme solicitado.

### Estrutura do Projeto

Certifique-se de que você tenha os seguintes arquivos e estrutura:

```
frontend/
├── public/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── server.js
```

### Passo 1: Estrutura HTML

No arquivo `public/index.html`, adicione a estrutura básica:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CRUD Application</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>CRUD Application</h1>
  </header>
  <main>
    <section id="user-form">
      <h2>Add User</h2>
      <form id="form">
        <div>
          <label for="name">Name</label>
          <input type="text" id="name" required>
        </div>
        <div>
          <label for="age">Age</label>
          <input type="number" id="age" required>
        </div>
        <div>
          <label for="email">Email</label>
          <input type="email" id="email" required>
        </div>
        <button type="submit">Add</button>
        <button type="button" id="cancel-button" style="display: none;">Cancel</button>
      </form>
    </section>
    <section id="user-list">
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
        <tbody id="users"></tbody>
      </table>
    </section>
  </main>
  <script src="script.js"></script>
</body>
</html>
```

### Passo 2: Estilo CSS

No arquivo `public/style.css`, adicione os estilos:

```css
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

header {
  background-color: #3f51b5;
  color: white;
  padding: 1rem;
  text-align: center;
}

main {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1rem;
}

section {
  margin-bottom: 2rem;
}

form {
  display: flex;
  flex-direction: column;
}

form div {
  margin-bottom: 1rem;
}

label {
  margin-bottom: 0.5rem;
}

input {
  padding: 0.5rem;
  font-size: 1rem;
}

button {
  padding: 0.5rem;
  font-size: 1rem;
  margin-right: 0.5rem;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  border: 1px solid #ddd;
  padding: 0.5rem;
}

th {
  background-color: #f2f2f2;
}

.actions button {
  margin-right: 0.5rem;
}
```

### Passo 3: Script JavaScript

No arquivo `public/script.js`, adicione o código JavaScript para manipular a API e atualizar a interface:

```javascript
document.addEventListener('DOMContentLoaded', function () {
  const apiUrl = 'http://your-backend-api-url/users'; // Altere para a URL do seu backend
  const userForm = document.getElementById('form');
  const cancelButton = document.getElementById('cancel-button');
  const usersTable = document.getElementById('users');
  let editingUserId = null;

  userForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const age = document.getElementById('age').value;
    const email = document.getElementById('email').value;

    if (editingUserId) {
      updateUser(editingUserId, { name, age, email });
    } else {
      addUser({ name, age, email });
    }
  });

  cancelButton.addEventListener('click', function () {
    clearForm();
  });

  function fetchUsers() {
    fetch(apiUrl)
      .then(response => response.json())
      .then(data => {
        usersTable.innerHTML = '';
        data.forEach(user => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${user.name}</td>
            <td>${user.age}</td>
            <td>${user.email}</td>
            <td class="actions">
              <button onclick="editUser(${user.id}, '${user.name}', ${user.age}, '${user.email}')">Edit</button>
              <button onclick="deleteUser(${user.id})">Delete</button>
            </td>
          `;
          usersTable.appendChild(row);
        });
      });
  }

  window.editUser = function (id, name, age, email) {
    document.getElementById('name').value = name;
    document.getElementById('age').value = age;
    document.getElementById('email').value = email;
    editingUserId = id;
    document.querySelector('h2').textContent = 'Edit User';
    cancelButton.style.display = 'inline';
  };

  window.deleteUser = function (id) {
    fetch(`${apiUrl}/${id}`, { method: 'DELETE' })
      .then(() => fetchUsers());
  };

  function addUser(user) {
    fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(user)
    })
      .then(() => {
        fetchUsers();
        clearForm();
      });
  }

  function updateUser(id, user) {
    fetch(`${apiUrl}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(user)
    })
      .then(() => {
        fetchUsers();
        clearForm();
      });
  }

  function clearForm() {
    document.getElementById('name').value = '';
    document.getElementById('age').value = '';
    document.getElementById('email').value = '';
    editingUserId = null;
    document.querySelector('h2').textContent = 'Add User';
    cancelButton.style.display = 'none';
  }

  fetchUsers();
});
```

### Passo 4: Configurar o Servidor Express

No arquivo `server.js`, configure o servidor Express para servir os arquivos estáticos:

```javascript
const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// Servir arquivos estáticos da pasta 'public'
app.use(express.static(path.join(__dirname, 'public')));

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
```

### Passo 5: Iniciar o Servidor

1. Certifique-se de que o backend externo está em execução e acessível.

2. Inicie o servidor Express para servir o frontend:

```bash
node server.js
```

Agora, ao acessar `http://localhost:3000` no navegador, você verá a interface do CRUD, que faz requisições para o backend externo configurado na variável `apiUrl` no arquivo `script.js`.

### Conclusão

Você configurou um servidor Express para servir um frontend simples utilizando apenas HTML, CSS e JavaScript, que faz requisições para um backend externo. Este setup permite que a aplicação seja acessada através do navegador, mantendo a separação entre o frontend e o backend.
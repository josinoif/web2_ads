Vamos criar uma aplicação CRUD simples usando Express.js com persistência em um banco de dados SQLite. 

### Passo 1: Configurar o Projeto

Primeiro, configure um novo projeto Node.js e instale as dependências necessárias.

1. Crie uma nova pasta para o projeto e inicialize o npm:

```bash
mkdir express-crud
cd express-crud
npm init -y
```

2. Instale as dependências necessárias:

```bash
npm install express sqlite3 body-parser
```

### Passo 2: Configurar o Servidor Express

Crie um arquivo `server.js` e configure o servidor Express:

```javascript
const express = require('express');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const app = express();
const PORT = 3000;

app.use(bodyParser.json());

// Configurar banco de dados SQLite
const db = new sqlite3.Database(':memory:');

// Criar tabela Users
db.serialize(() => {
  db.run('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER, email TEXT)');
});

// Rotas

// Listar todos os usuários
app.get('/users', (req, res) => {
  db.all('SELECT * FROM users', [], (err, rows) => {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    res.json(rows);
  });
});

// Buscar um usuário pelo ID
app.get('/users/:id', (req, res) => {
  const id = req.params.id;
  db.get('SELECT * FROM users WHERE id = ?', [id], (err, row) => {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    if (!row) {
      res.status(404).send('User not found');
      return;
    }
    res.json(row);
  });
});

// Criar um novo usuário
app.post('/users', (req, res) => {
  const { name, age, email } = req.body;
  db.run('INSERT INTO users (name, age, email) VALUES (?, ?, ?)', [name, age, email], function (err) {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    res.status(201).json({ id: this.lastID });
  });
});

// Atualizar um usuário existente
app.put('/users/:id', (req, res) => {
  const id = req.params.id;
  const { name, age, email } = req.body;
  db.run('UPDATE users SET name = ?, age = ?, email = ? WHERE id = ?', [name, age, email, id], function (err) {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    if (this.changes === 0) {
      res.status(404).send('User not found');
      return;
    }
    res.sendStatus(204);
  });
});

// Deletar um usuário
app.delete('/users/:id', (req, res) => {
  const id = req.params.id;
  db.run('DELETE FROM users WHERE id = ?', [id], function (err) {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    if (this.changes === 0) {
      res.status(404).send('User not found');
      return;
    }
    res.sendStatus(204);
  });
});

// Iniciar o servidor
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
```

### Passo 3: Testar a Aplicação

Inicie o servidor:

```bash
node server.js
```

Agora você pode usar ferramentas como Postman ou cURL para testar as rotas CRUD.

### Rotas Disponíveis

- `GET /users` - Lista todos os usuários.
- `GET /users/:id` - Retorna um usuário específico pelo ID.
- `POST /users` - Cria um novo usuário. Espera um corpo JSON com `name`, `age`, e `email`.
- `PUT /users/:id` - Atualiza um usuário existente. Espera um corpo JSON com `name`, `age`, e `email`.
- `DELETE /users/:id` - Deleta um usuário pelo ID.

### Conclusão

Você agora tem uma aplicação CRUD básica usando Express.js com persistência de dados em um banco de dados SQLite. Para uma aplicação mais robusta em produção, você pode considerar usar um banco de dados mais completo como PostgreSQL ou MongoDB e adicionar camadas de autenticação e validação de dados.
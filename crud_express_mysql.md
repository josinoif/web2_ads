Claro! Vamos criar uma aplicação CRUD com Express.js utilizando o banco de dados MySQL.

### Passo 1: Configurar o Projeto

1. Crie uma nova pasta para o projeto e inicialize o npm:

```bash
mkdir express-crud
cd express-crud
npm init -y
```

2. Instale as dependências necessárias:

```bash
npm install express mysql2 body-parser
```

### Passo 2: Configurar o Servidor Express

Crie um arquivo `server.js` e configure o servidor Express:

```javascript
const express = require('express');
const bodyParser = require('body-parser');
const mysql = require('mysql2');
const app = express();
const PORT = 3000;

app.use(bodyParser.json());

// Configurar banco de dados MySQL
const db = mysql.createConnection({
  host: 'localhost',
  user: 'your_username',
  password: 'your_password',
  database: 'your_database'
});

db.connect(err => {
  if (err) {
    console.error('Error connecting to the database:', err.message);
    return;
  }
  console.log('Connected to the MySQL database');
});

// Criar tabela Users
db.query(
  'CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INT, email VARCHAR(255))',
  err => {
    if (err) {
      console.error('Error creating table:', err.message);
      return;
    }
    console.log('Table "users" created or already exists');
  }
);

// Rotas

// Listar todos os usuários
app.get('/users', (req, res) => {
  db.query('SELECT * FROM users', (err, results) => {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    res.json(results);
  });
});

// Buscar um usuário pelo ID
app.get('/users/:id', (req, res) => {
  const id = req.params.id;
  db.query('SELECT * FROM users WHERE id = ?', [id], (err, result) => {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    if (result.length === 0) {
      res.status(404).send('User not found');
      return;
    }
    res.json(result[0]);
  });
});

// Criar um novo usuário
app.post('/users', (req, res) => {
  const { name, age, email } = req.body;
  db.query('INSERT INTO users (name, age, email) VALUES (?, ?, ?)', [name, age, email], (err, result) => {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    res.status(201).json({ id: result.insertId });
  });
});

// Atualizar um usuário existente
app.put('/users/:id', (req, res) => {
  const id = req.params.id;
  const { name, age, email } = req.body;
  db.query('UPDATE users SET name = ?, age = ?, email = ? WHERE id = ?', [name, age, email, id], (err, result) => {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    if (result.affectedRows === 0) {
      res.status(404).send('User not found');
      return;
    }
    res.sendStatus(204);
  });
});

// Deletar um usuário
app.delete('/users/:id', (req, res) => {
  const id = req.params.id;
  db.query('DELETE FROM users WHERE id = ?', [id], (err, result) => {
    if (err) {
      res.status(500).send(err.message);
      return;
    }
    if (result.affectedRows === 0) {
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

### Passo 3: Configurar o Banco de Dados MySQL

Certifique-se de que o MySQL está em execução e que você criou um banco de dados. Substitua `your_username`, `your_password`, e `your_database` pelas suas credenciais e nome do banco de dados.

### Passo 4: Testar a Aplicação

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

Agora você tem uma aplicação CRUD básica usando Express.js com persistência de dados em um banco de dados MySQL. Para uma aplicação mais robusta em produção, considere adicionar camadas de autenticação, validação de dados, e tratamentos de erros mais sofisticados.
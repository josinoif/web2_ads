Claro! Vamos adicionar os passos para configurar o MySQL usando Docker e integrar isso no tutorial Express.js.

### Passo 1: Configurar o MySQL usando Docker

1. Certifique-se de que o Docker está instalado e em execução na sua máquina.

2. Execute o seguinte comando para baixar a imagem do MySQL e iniciar um contêiner:

```bash
docker run --name mysql-container -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=aula_web2 -p 3306:3306 -d mysql:latest
```

3. Acesse o container do MySQL:

```bash
docker exec -it mysql-container mysql -u root -p
```
Isso abrirá o terminal MySQL dentro do container e pedirá a senha de root que você definiu (neste caso, `root`).


### Passo 2: Configurar o Projeto Express.js

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

### Passo 3: Configurar o Servidor Express

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
  user: 'root',
  password: 'root',
  database: 'aula_web2'
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

### Passo 4: Testar a Aplicação

1. Inicie o contêiner MySQL se ainda não estiver em execução:

```bash
docker start mysql-container
```

2. Inicie o servidor Express:

```bash
node server.js
```

### Rotas Disponíveis

- `GET /users` - Lista todos os usuários.
- `GET /users/:id` - Retorna um usuário específico pelo ID.
- `POST /users` - Cria um novo usuário. Espera um corpo JSON com `name`, `age`, e `email`.
- `PUT /users/:id` - Atualiza um usuário existente. Espera um corpo JSON com `name`, `age`, e `email`.
- `DELETE /users/:id` - Deleta um usuário pelo ID.

### Conclusão

Agora você tem uma aplicação CRUD básica usando Express.js com persistência de dados em um banco de dados MySQL, configurado e executado via Docker. Certifique-se de que o Docker e o contêiner MySQL estejam em execução ao iniciar sua aplicação.
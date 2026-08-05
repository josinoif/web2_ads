Tutorial de CRUD com **Express.js 5.2.1** e **mysql2 3.18.2**, usando MySQL em Docker (requer Node.js 18+).

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

2. Instale as dependências necessárias (Express 5.2.1 requer Node.js 18+; mysql2 3.18.2):

```bash
npm install express@5.2.1 mysql2@3.18.2
```

### Passo 3: Configurar o Servidor Express

Crie um arquivo `server.js` e configure o servidor Express. O parsing de JSON é feito com `express.json()` (built-in). Utilizamos a API de **promises** do mysql2 (`mysql2/promise`), compatível com async/await e com o tratamento de erros em middlewares do Express 5.

```javascript
const express = require('express');
const mysql = require('mysql2/promise');
const app = express();
const PORT = 3000;

app.use(express.json());

// Configurar e conectar ao banco de dados MySQL
let db;

async function initDatabase() {
  db = await mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'root',
    database: 'aula_web2'
  });
  console.log('Connected to the MySQL database');

  await db.query(
    'CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INT, email VARCHAR(255))'
  );
  console.log('Table "users" created or already exists');
}

// Rotas

// Listar todos os usuários
app.get('/users', async (req, res) => {
  try {
    const [results] = await db.query('SELECT * FROM users');
    res.json(results);
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// Buscar um usuário pelo ID
app.get('/users/:id', async (req, res) => {
  const id = req.params.id;
  try {
    const [rows] = await db.query('SELECT * FROM users WHERE id = ?', [id]);
    if (rows.length === 0) {
      res.status(404).send('User not found');
      return;
    }
    res.json(rows[0]);
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// Criar um novo usuário
app.post('/users', async (req, res) => {
  const { name, age, email } = req.body;
  try {
    const [result] = await db.query(
      'INSERT INTO users (name, age, email) VALUES (?, ?, ?)',
      [name, age, email]
    );
    res.status(201).json({ id: result.insertId });
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// Atualizar um usuário existente
app.put('/users/:id', async (req, res) => {
  const id = req.params.id;
  const { name, age, email } = req.body;
  try {
    const [result] = await db.query(
      'UPDATE users SET name = ?, age = ?, email = ? WHERE id = ?',
      [name, age, email, id]
    );
    if (result.affectedRows === 0) {
      res.status(404).send('User not found');
      return;
    }
    res.sendStatus(204);
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// Deletar um usuário
app.delete('/users/:id', async (req, res) => {
  const id = req.params.id;
  try {
    const [result] = await db.query('DELETE FROM users WHERE id = ?', [id]);
    if (result.affectedRows === 0) {
      res.status(404).send('User not found');
      return;
    }
    res.sendStatus(204);
  } catch (err) {
    res.status(500).send(err.message);
  }
});

// Iniciar o servidor (inicialização assíncrona)
async function start() {
  await initDatabase();
  app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
  });
}

start().catch((err) => {
  console.error('Failed to start server:', err.message);
  process.exit(1);
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
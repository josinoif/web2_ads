# Módulo 03 - Backend: Configuração Inicial

Neste módulo, você vai configurar o servidor backend usando Node.js e Express.js, e estabelecer a conexão com o banco de dados MySQL.

## Objetivos do Módulo

- ✅ Inicializar o projeto Node.js
- ✅ Instalar dependências necessárias
- ✅ Criar a estrutura de pastas do backend
- ✅ Configurar conexão com MySQL
- ✅ Criar o servidor Express básico
- ✅ Testar se tudo está funcionando

---

## 1. Inicializando o Projeto Node.js

### Passo 1: Navegar até a pasta do backend

Abra o terminal e navegue até a pasta do projeto:

```bash
cd crud-receitas/backend
```

### Passo 2: Inicializar o package.json

Execute o comando:

```bash
npm init -y
```

**O que isso faz?**
- Cria um arquivo `package.json` com configurações padrão
- O `-y` aceita todas as opções padrão automaticamente

**Resultado:** Arquivo `package.json` criado:

```json
{
  "name": "backend",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "ISC"
}
```

---

## 2. Instalando Dependências

Vamos instalar todos os pacotes necessários de uma vez.

### Comando de instalação:

```bash
npm install express mysql2 cors dotenv
```

### O que cada pacote faz:

| Pacote | Descrição |
|--------|-----------|
| **express** | Framework web para criar o servidor e rotas |
| **mysql2** | Driver para conectar ao MySQL (versão atualizada do mysql) |
| **cors** | Permite que o frontend (React) se comunique com o backend |
| **dotenv** | Carrega variáveis de ambiente de um arquivo .env |

### Instalando dependência de desenvolvimento:

```bash
npm install --save-dev nodemon
```

**nodemon:** Reinicia o servidor automaticamente quando você salva alterações no código.

### Verificando instalação:

Abra o `package.json` e confirme que as dependências foram adicionadas:

```json
{
  "dependencies": {
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "express": "^4.18.2",
    "mysql2": "^3.6.0"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

---

## 3. Criando a Estrutura de Pastas

Vamos organizar o código em pastas lógicas.

### Estrutura completa:

```
backend/
├── config/
│   └── database.js      ← Configuração do banco de dados
├── controllers/
│   ├── ingredientesController.js  ← Lógica de ingredientes
│   └── receitasController.js      ← Lógica de receitas
├── routes/
│   ├── ingredientes.js  ← Rotas de ingredientes
│   └── receitas.js      ← Rotas de receitas
├── .env                 ← Variáveis de ambiente (senhas)
├── .gitignore          ← Arquivos a ignorar no Git
├── server.js           ← Arquivo principal do servidor
└── package.json
```

### Criando as pastas:

**No terminal (dentro de backend/):**

```bash
mkdir config controllers routes
```

### Criando os arquivos:

**Windows:**
```bash
type nul > .env
type nul > .gitignore
type nul > server.js
type nul > config\database.js
```

**Mac/Linux:**
```bash
touch .env .gitignore server.js
touch config/database.js
```

---

## 4. Configurando o arquivo .env

O arquivo `.env` armazena informações sensíveis como senhas do banco.

### Abra o arquivo .env e adicione:

```env
# Configurações do Servidor
PORT=3001

# Configurações do Banco de Dados
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha_aqui
DB_NAME=sistema_receitas
DB_PORT=3306
```

### ⚠️ IMPORTANTE:

- **Substitua `sua_senha_aqui`** pela senha real do seu MySQL
- **Não compartilhe este arquivo!** Ele contém informações sensíveis
- Se usar XAMPP, a senha padrão geralmente é vazia: `DB_PASSWORD=`

---

## 5. Configurando o .gitignore

O `.gitignore` evita que arquivos sensíveis sejam enviados para o Git.

### Abra o arquivo .gitignore e adicione:

```
# Dependências
node_modules/

# Variáveis de ambiente
.env

# Logs
*.log
npm-debug.log*

# Sistema operacional
.DS_Store
Thumbs.db
```

**Por que isso é importante?**
- `node_modules/` é muito grande e pode ser reinstalado com `npm install`
- `.env` contém senhas e não deve ser compartilhado

---

## 6. Configurando a Conexão com o Banco

Vamos criar um arquivo para gerenciar a conexão com MySQL.

### Abra `config/database.js` e adicione:

```javascript
// Importa o módulo mysql2 com suporte a Promises
const mysql = require('mysql2/promise');

// Importa o dotenv para ler variáveis do arquivo .env
require('dotenv').config();

// Cria um pool de conexões com o MySQL
// Pool = várias conexões reutilizáveis (mais eficiente)
const pool = mysql.createPool({
    host: process.env.DB_HOST,           // localhost
    user: process.env.DB_USER,           // root
    password: process.env.DB_PASSWORD,   // sua senha
    database: process.env.DB_NAME,       // sistema_receitas
    port: process.env.DB_PORT,           // 3306
    waitForConnections: true,
    connectionLimit: 10,                 // Máximo de 10 conexões simultâneas
    queueLimit: 0
});

// Função para testar a conexão
async function testConnection() {
    try {
        const connection = await pool.getConnection();
        console.log('✅ Conectado ao MySQL com sucesso!');
        connection.release(); // Libera a conexão de volta para o pool
    } catch (error) {
        console.error('❌ Erro ao conectar ao MySQL:', error.message);
        process.exit(1); // Encerra o aplicativo se não conseguir conectar
    }
}

// Exporta o pool para ser usado em outros arquivos
module.exports = { pool, testConnection };
```

### Explicação detalhada:

**1. `mysql2/promise`:**
- Permite usar async/await em vez de callbacks
- Código mais limpo e fácil de ler

**2. `createPool()`:**
- Cria um conjunto de conexões reutilizáveis
- Mais eficiente do que criar uma nova conexão para cada requisição

**3. `process.env.DB_HOST`:**
- Lê valores do arquivo `.env`
- Mantém configurações sensíveis fora do código

**4. `testConnection()`:**
- Testa se a conexão funciona ao iniciar o servidor
- Se falhar, encerra o aplicativo com erro claro

---

## 7. Criando o Servidor Express

Agora vamos criar o servidor principal.

### Abra `server.js` e adicione:

```javascript
// ============================================
// IMPORTAÇÕES
// ============================================

const express = require('express');
const cors = require('cors');
require('dotenv').config();

// Importa a configuração do banco de dados
const { testConnection } = require('./config/database');

// ============================================
// CONFIGURAÇÃO DO EXPRESS
// ============================================

const app = express();
const PORT = process.env.PORT || 3001;

// ============================================
// MIDDLEWARES
// ============================================

// CORS: Permite que o frontend (React) acesse o backend
app.use(cors());

// Permite que o Express entenda JSON no body das requisições
app.use(express.json());

// Permite que o Express entenda dados de formulários
app.use(express.urlencoded({ extended: true }));

// ============================================
// ROTAS
// ============================================

// Rota de teste para verificar se o servidor está rodando
app.get('/', (req, res) => {
    res.json({
        message: 'API do Sistema de Receitas está rodando! 🍳',
        version: '1.0.0',
        endpoints: {
            ingredientes: '/api/ingredientes',
            receitas: '/api/receitas'
        }
    });
});

// Rota para testar a conexão com o banco de dados
app.get('/api/test-db', async (req, res) => {
    try {
        const { pool } = require('./config/database');
        const [rows] = await pool.query('SELECT 1 + 1 AS resultado');
        res.json({
            message: 'Conexão com o banco de dados OK!',
            resultado: rows[0].resultado
        });
    } catch (error) {
        res.status(500).json({
            message: 'Erro ao conectar com o banco de dados',
            error: error.message
        });
    }
});

// ============================================
// AQUI VIRÃO AS ROTAS DE INGREDIENTES E RECEITAS
// (serão adicionadas nos próximos módulos)
// ============================================

// app.use('/api/ingredientes', ingredientesRoutes);
// app.use('/api/receitas', receitasRoutes);

// ============================================
// TRATAMENTO DE ERROS
// ============================================

// Rota 404 - Não encontrado
app.use((req, res) => {
    res.status(404).json({
        error: 'Rota não encontrada',
        message: `A rota ${req.method} ${req.url} não existe`
    });
});

// Tratamento de erros gerais
app.use((err, req, res, next) => {
    console.error('Erro:', err.stack);
    res.status(500).json({
        error: 'Erro interno do servidor',
        message: err.message
    });
});

// ============================================
// INICIALIZAÇÃO DO SERVIDOR
// ============================================

async function startServer() {
    try {
        // Testa a conexão com o banco antes de iniciar
        await testConnection();
        
        // Inicia o servidor
        app.listen(PORT, () => {
            console.log(`\n🚀 Servidor rodando na porta ${PORT}`);
            console.log(`📡 Acesse: http://localhost:${PORT}`);
            console.log(`📊 Teste o banco: http://localhost:${PORT}/api/test-db\n`);
        });
    } catch (error) {
        console.error('❌ Falha ao iniciar o servidor:', error.message);
        process.exit(1);
    }
}

// Inicia o servidor
startServer();
```

### Explicação dos conceitos:

**1. Middlewares:**
```javascript
app.use(express.json());
```
- Middlewares são funções que processam requisições antes de chegarem às rotas
- `express.json()` converte JSON do body em objetos JavaScript

**2. CORS:**
```javascript
app.use(cors());
```
- Por padrão, navegadores bloqueiam requisições entre domínios diferentes
- CORS permite que React (localhost:3000) acesse Express (localhost:3001)

**3. Rotas:**
```javascript
app.get('/', (req, res) => { ... });
```
- `app.get()` define uma rota GET
- `req` = dados da requisição
- `res` = objeto para enviar resposta

**4. Async/Await:**
```javascript
async function startServer() {
    await testConnection();
}
```
- `async` indica que a função pode ter operações assíncronas
- `await` espera a operação terminar antes de continuar

---

## 8. Configurando Scripts do NPM

Vamos facilitar a execução do servidor.

### Abra `package.json` e modifique a seção `scripts`:

```json
{
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  }
}
```

### O que cada script faz:

| Comando | Descrição |
|---------|-----------|
| `npm start` | Inicia o servidor (produção) |
| `npm run dev` | Inicia com nodemon (desenvolvimento) |

---

## 9. Testando o Servidor

Agora vamos ver se tudo está funcionando!

### Passo 1: Iniciar o servidor

No terminal (dentro da pasta `backend/`):

```bash
npm run dev
```

### Resultado esperado:

```
✅ Conectado ao MySQL com sucesso!

🚀 Servidor rodando na porta 3001
📡 Acesse: http://localhost:3001
📊 Teste o banco: http://localhost:3001/api/test-db
```

### Passo 2: Testar no navegador

Abra o navegador e acesse:

**Teste 1:** [http://localhost:3001](http://localhost:3001)

Resposta esperada:
```json
{
  "message": "API do Sistema de Receitas está rodando! 🍳",
  "version": "1.0.0",
  "endpoints": {
    "ingredientes": "/api/ingredientes",
    "receitas": "/api/receitas"
  }
}
```

**Teste 2:** [http://localhost:3001/api/test-db](http://localhost:3001/api/test-db)

Resposta esperada:
```json
{
  "message": "Conexão com o banco de dados OK!",
  "resultado": 2
}
```

### Passo 3: Testar no Postman

1. Abra o Postman
2. Crie uma nova requisição GET
3. URL: `http://localhost:3001`
4. Clique em "Send"
5. Verifique a resposta JSON

---

## 10. Solução de Problemas Comuns

### Erro: "Cannot find module 'express'"

**Causa:** Pacotes não foram instalados

**Solução:**
```bash
npm install
```

### Erro: "Error: Access denied for user"

**Causa:** Senha do MySQL incorreta no `.env`

**Solução:**
1. Verifique a senha no arquivo `.env`
2. Teste conectando direto no MySQL: `mysql -u root -p`

### Erro: "EADDRINUSE: address already in use"

**Causa:** Porta 3001 já está sendo usada

**Solução 1:** Encerre o processo que está usando a porta
```bash
# Windows
netstat -ano | findstr :3001

# Mac/Linux
lsof -ti:3001 | xargs kill
```

**Solução 2:** Mude a porta no `.env`
```env
PORT=3002
```

### Erro: "Unknown database 'sistema_receitas'"

**Causa:** Banco de dados não foi criado

**Solução:**
```sql
CREATE DATABASE sistema_receitas;
```

### Servidor não reinicia automaticamente

**Causa:** nodemon não está instalado

**Solução:**
```bash
npm install --save-dev nodemon
```

---

## Resumo do Módulo

Neste módulo você:
- ✅ Inicializou o projeto Node.js
- ✅ Instalou Express, MySQL2, CORS e Dotenv
- ✅ Criou a estrutura de pastas organizada
- ✅ Configurou variáveis de ambiente (.env)
- ✅ Criou conexão com MySQL usando pool
- ✅ Criou o servidor Express básico
- ✅ Testou conexão com banco de dados
- ✅ Configurou nodemon para desenvolvimento

---

## Próximo Passo

Agora que o servidor está rodando, vamos criar o CRUD de ingredientes!

**➡️ Próximo:** [Módulo 04 - Backend: CRUD de Ingredientes](04-backend-ingredientes.md)

---

## Dicas Importantes

💡 **Sempre use `npm run dev`** durante o desenvolvimento para o servidor reiniciar automaticamente.

💡 **Mantenha o terminal aberto** para ver logs de erros e informações úteis.

💡 **Teste no Postman** antes de integrar com o frontend.

💡 **Commit frequente** usando Git para não perder alterações.

# Tutorial 3: Setup do Ambiente de Desenvolvimento

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Instalar Node.js e gerenciador de pacotes
- Configurar PostgreSQL
- Criar a estrutura inicial do projeto
- Configurar variáveis de ambiente
- Testar a conexão com o banco de dados

## 📖 Conteúdo

### 1. Instalando Node.js

**O que é Node.js?**
- Runtime JavaScript que permite executar JS no servidor
- Inclui npm (Node Package Manager) para gerenciar dependências

**Instalação:**

**Linux (Ubuntu/Debian):**
```bash
# Atualizar repositórios
sudo apt update

# Instalar Node.js e npm
sudo apt install nodejs npm

# Verificar instalação
node --version  # deve mostrar v16+ ou superior
npm --version
```

**macOS:**
```bash
# Usando Homebrew
brew install node

# Verificar instalação
node --version
npm --version
```

**Windows:**
- Baixe o instalador em [nodejs.org](https://nodejs.org/)
- Execute o instalador
- Verifique no CMD: `node --version`

### 2. Instalando PostgreSQL

**Linux (Ubuntu/Debian):**
```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib

# Iniciar serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verificar status
sudo systemctl status postgresql
```

**macOS:**
```bash
# Usando Homebrew
brew install postgresql

# Iniciar serviço
brew services start postgresql
```

**Windows:**
- Baixe o instalador em [postgresql.org](https://www.postgresql.org/download/)
- Execute e siga o wizard
- Anote a senha do usuário postgres

### 3. Configurando o PostgreSQL

**Acessar o console do PostgreSQL:**

```bash
# Linux/macOS
sudo -u postgres psql

# Windows (SQL Shell)
# Use o aplicativo "SQL Shell (psql)" instalado
```

**Criar banco de dados e usuário:**

```sql
-- Criar usuário
CREATE USER tasterank_user WITH PASSWORD 'senha_segura_123';

-- Criar banco de dados
CREATE DATABASE tasterank_db;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE tasterank_db TO tasterank_user;

-- Listar bancos de dados
\l

-- Sair
\q
```

### 4. Estrutura do Projeto Backend

**Criar diretório do projeto:**

```bash
# Criar pasta do projeto
mkdir tasterank-backend
cd tasterank-backend

# Inicializar projeto Node.js
npm init -y
```

**Instalar dependências principais:**

```bash
# Framework web
npm install express

# ORM para PostgreSQL
npm install sequelize pg pg-hstore

# Variáveis de ambiente
npm install dotenv

# Validação de dados
npm install express-validator

# CORS (permitir requisições cross-origin)
npm install cors
```

**Instalar dependências de desenvolvimento:**

```bash
# Nodemon - reinicia servidor automaticamente
npm install --save-dev nodemon

# ESLint - linter para qualidade de código
npm install --save-dev eslint
```

**Estrutura de pastas:**

```
tasterank-backend/
├── src/
│   ├── config/
│   │   └── database.js      # Configuração do banco
│   ├── models/              # Modelos do Sequelize
│   │   ├── index.js
│   │   ├── Restaurante.js
│   │   └── Avaliacao.js
│   ├── controllers/         # Lógica de negócio
│   │   ├── restauranteController.js
│   │   └── avaliacaoController.js
│   ├── routes/              # Definição de rotas
│   │   ├── restauranteRoutes.js
│   │   └── avaliacaoRoutes.js
│   ├── middlewares/         # Middlewares customizados
│   │   └── errorHandler.js
│   └── app.js               # Configuração do Express
├── .env                     # Variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── package.json            # Dependências e scripts
└── server.js               # Ponto de entrada
```

**Criar a estrutura:**

```bash
mkdir -p src/{config,models,controllers,routes,middlewares}
touch src/app.js server.js .env .gitignore
```

### 5. Configurando Variáveis de Ambiente

**Arquivo `.env`:**

```env
# Configuração do Servidor
PORT=3000
NODE_ENV=development

# Configuração do Banco de Dados
# Se já tiver um banco de dados instalado utilize as credenciais do seu banco de dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tasterank_db
DB_USER=tasterank_user
DB_PASSWORD=senha_segura_123

# Outras configurações
CORS_ORIGIN=http://localhost:5173
```

**⚠️ Importante:** Adicione `.env` ao `.gitignore`:

```gitignore
# .gitignore
node_modules/
.env
.env.local
.env.*.local
*.log
dist/
build/
```

### 6. Configurando o Express

**Arquivo `src/app.js`:**

```javascript
const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();

// Middlewares
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173'
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Rota de teste
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'TasteRank API está funcionando!' 
  });
});

// Tratamento de erros 404
app.use((req, res) => {
  res.status(404).json({ 
    error: 'Endpoint não encontrado' 
  });
});

// Tratamento de erros gerais
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ 
    error: 'Erro interno do servidor' 
  });
});

module.exports = app;
```

**Arquivo `server.js`:**

```javascript
const app = require('./src/app');

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`🚀 Servidor rodando na porta ${PORT}`);
  console.log(`📍 http://localhost:${PORT}`);
  console.log(`🏥 Health check: http://localhost:${PORT}/api/health`);
});
```

### 7. Configurando Scripts no package.json

**Edite `package.json`:**

```json
{
  "name": "tasterank-backend",
  "version": "1.0.0",
  "description": "API para sistema de avaliação de restaurantes",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js",
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": ["api", "rest", "express", "postgresql"],
  "author": "Seu Nome",
  "license": "ISC",
  "dependencies": {
    "cors": "^2.8.5",
    "dotenv": "^16.0.3",
    "express": "^4.18.2",
    "express-validator": "^7.0.1",
    "pg": "^8.11.0",
    "pg-hstore": "^2.3.4",
    "sequelize": "^6.32.1"
  },
  "devDependencies": {
    "nodemon": "^3.0.1"
  }
}
```

### 8. Testando o Servidor

**Iniciar o servidor:**

```bash
npm run dev
```

**Saída esperada:**
```
🚀 Servidor rodando na porta 3000
📍 http://localhost:3000
🏥 Health check: http://localhost:3000/api/health
```

**Testar no navegador ou com curl:**

```bash
curl http://localhost:3000/api/health
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "message": "TasteRank API está funcionando!"
}
```

## 🔨 Atividade Prática

### Checklist de Configuração

Verifique se você completou todas as etapas:

- [ ] Node.js instalado (v16+)
- [ ] PostgreSQL instalado e rodando
- [ ] Banco de dados `tasterank_db` criado
- [ ] Usuário `tasterank_user` criado
- [ ] Projeto Node.js inicializado
- [ ] Dependências instaladas
- [ ] Estrutura de pastas criada
- [ ] Arquivo `.env` configurado
- [ ] Arquivo `.gitignore` criado
- [ ] Servidor Express configurado
- [ ] Servidor iniciado com sucesso
- [ ] Endpoint de health check funcionando

### Exercício de Validação

1. **Verificar versões:**
```bash
node --version
npm --version
psql --version
```

2. **Testar conexão com PostgreSQL:**
```bash
psql -h localhost -U tasterank_user -d tasterank_db
# Digite a senha quando solicitado
# Se conectar, digite \q para sair
```

3. **Adicionar um novo endpoint de teste:**

Edite `src/app.js` e adicione:

```javascript
app.get('/api/info', (req, res) => {
  res.json({
    projeto: 'TasteRank',
    versao: '1.0.0',
    ambiente: process.env.NODE_ENV,
    banco: {
      host: process.env.DB_HOST,
      database: process.env.DB_NAME
    }
  });
});
```

Teste acessando `http://localhost:3000/api/info`

## 💡 Conceitos-Chave

- **Node.js** permite executar JavaScript no servidor
- **npm** gerencia dependências do projeto
- **Express** é um framework minimalista para criar APIs
- **PostgreSQL** é nosso banco de dados relacional
- **dotenv** carrega variáveis de ambiente de forma segura
- **nodemon** reinicia o servidor automaticamente durante desenvolvimento
- **CORS** permite requisições de diferentes origens
- `.env` **nunca** deve ser commitado no Git

## ➡️ Próximos Passos

Com o ambiente configurado, no próximo tutorial vamos criar nossos primeiros **modelos com Sequelize**, definindo a estrutura das tabelas de restaurantes e avaliações.

[➡️ Ir para Tutorial 4: Modelagem de Dados e ORM](04-modelagem-orm.md)

---

**Troubleshooting:**
- Se o PostgreSQL não iniciar, verifique se a porta 5432 está livre
- Se houver erro de conexão, confirme usuário e senha no `.env`
- Se o servidor não iniciar, verifique se a porta 3000 está disponível

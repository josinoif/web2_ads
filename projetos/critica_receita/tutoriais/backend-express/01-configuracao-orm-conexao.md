# Tutorial 5: Configuração do ORM e Conexão com BD

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Compreender a arquitetura MVC aplicada a APIs
- Configurar o pool de conexões do Sequelize
- Implementar tratamento de erros de conexão
- Criar middlewares customizados
- Estruturar o código seguindo boas práticas

## 📖 Conteúdo

### 1. Arquitetura MVC para APIs

**MVC (Model-View-Controller)** adaptado para APIs REST:

```
Cliente (Frontend)
       ↓
   [Routes]      ← Define os endpoints e métodos HTTP
       ↓
 [Controllers]   ← Lógica de negócio e validação
       ↓
   [Models]      ← Interação com banco de dados
       ↓
  Banco de Dados
```

**Responsabilidades:**

- **Routes**: Mapear URLs para controllers
- **Controllers**: Processar requisições, validar dados, chamar models
- **Models**: Representar e manipular dados do BD
- **Middlewares**: Interceptar requisições (auth, logging, etc.)

### 2. Melhorando a Configuração do Banco

**Arquivo `src/config/database.js` (versão melhorada):**

```javascript
const { Sequelize } = require('sequelize');
require('dotenv').config();

// Configuração do pool de conexões
const poolConfig = {
  max: 5,           // Máximo de conexões simultâneas
  min: 0,           // Mínimo de conexões mantidas
  acquire: 30000,   // Tempo máximo para adquirir conexão (30s)
  idle: 10000,      // Tempo que conexão fica idle antes de ser liberada
  evict: 1000       // Intervalo para verificar conexões idle
};

// Configuração de logging
const logging = process.env.NODE_ENV === 'development' 
  ? (msg) => console.log(`[Sequelize] ${msg}`)
  : false;

const sequelize = new Sequelize(
  process.env.DB_NAME,
  process.env.DB_USER,
  process.env.DB_PASSWORD,
  {
    host: process.env.DB_HOST,
    port: process.env.DB_PORT || 5432,
    dialect: 'postgres',
    logging,
    pool: poolConfig,
    dialectOptions: {
      // Para produção com SSL
      ...(process.env.NODE_ENV === 'production' && {
        ssl: {
          require: true,
          rejectUnauthorized: false
        }
      })
    },
    define: {
      timestamps: true,
      underscored: true,
      freezeTableName: true
    }
  }
);

// Função para testar conexão com retry
async function connectWithRetry(retries = 5, delay = 2000) {
  for (let i = 0; i < retries; i++) {
    try {
      await sequelize.authenticate();
      console.log('✅ Conexão com PostgreSQL estabelecida');
      return true;
    } catch (error) {
      console.error(`❌ Tentativa ${i + 1}/${retries} falhou:`, error.message);
      
      if (i < retries - 1) {
        console.log(`⏳ Aguardando ${delay / 1000}s antes de tentar novamente...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  console.error('❌ Não foi possível conectar ao banco de dados após várias tentativas');
  process.exit(1);
}

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n⚠️  Encerrando conexões com banco de dados...');
  await sequelize.close();
  console.log('✅ Conexões fechadas');
  process.exit(0);
});

module.exports = { sequelize, connectWithRetry };
```

### 3. Criando Middleware de Erro

**Arquivo `src/middlewares/errorHandler.js`:**

```javascript
/**
 * Classe de erro customizada para erros de API
 */
class ApiError extends Error {
  constructor(statusCode, message, details = null) {
    super(message);
    this.statusCode = statusCode;
    this.details = details;
    this.isOperational = true; // Distingue erros operacionais de bugs
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * Middleware de tratamento de erros
 */
const errorHandler = (err, req, res, next) => {
  let statusCode = err.statusCode || 500;
  let message = err.message || 'Erro interno do servidor';
  
  // Log do erro
  if (process.env.NODE_ENV === 'development') {
    console.error('❌ Erro:', {
      message: err.message,
      stack: err.stack,
      statusCode
    });
  } else {
    console.error('❌ Erro:', message);
  }
  
  // Erros do Sequelize
  if (err.name === 'SequelizeValidationError') {
    statusCode = 400;
    message = 'Erro de validação';
    const errors = err.errors.map(e => ({
      campo: e.path,
      mensagem: e.message
    }));
    
    return res.status(statusCode).json({
      error: message,
      detalhes: errors
    });
  }
  
  if (err.name === 'SequelizeUniqueConstraintError') {
    statusCode = 409;
    message = 'Registro duplicado';
    
    return res.status(statusCode).json({
      error: message,
      detalhes: err.errors.map(e => e.message)
    });
  }
  
  if (err.name === 'SequelizeForeignKeyConstraintError') {
    statusCode = 400;
    message = 'Violação de chave estrangeira';
    
    return res.status(statusCode).json({
      error: message
    });
  }
  
  // Resposta padrão
  res.status(statusCode).json({
    error: message,
    ...(err.details && { detalhes: err.details }),
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
};

/**
 * Wrapper para funções assíncronas
 * Evita try-catch repetitivo
 */
const asyncHandler = (fn) => {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
};

module.exports = { ApiError, errorHandler, asyncHandler };
```

### 4. Middleware de Logging

**Arquivo `src/middlewares/logger.js`:**

```javascript
/**
 * Middleware de logging de requisições
 */
const requestLogger = (req, res, next) => {
  const start = Date.now();
  
  // Interceptar o método res.json para capturar status
  const originalJson = res.json.bind(res);
  
  res.json = function(body) {
    const duration = Date.now() - start;
    
    console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`);
    
    if (process.env.NODE_ENV === 'development' && req.method !== 'GET') {
      console.log('Body:', JSON.stringify(req.body, null, 2));
    }
    
    return originalJson(body);
  };
  
  next();
};

module.exports = { requestLogger };
```

### 5. Middleware de Validação

**Arquivo `src/middlewares/validator.js`:**

```javascript
const { validationResult } = require('express-validator');
const { ApiError } = require('./errorHandler');

/**
 * Middleware para processar resultados de validação
 */
const validate = (req, res, next) => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    const formattedErrors = errors.array().map(err => ({
      campo: err.path,
      mensagem: err.msg,
      valorRecebido: err.value
    }));
    
    throw new ApiError(400, 'Erro de validação', formattedErrors);
  }
  
  next();
};

module.exports = { validate };
```

### 6. Atualizando o App.js

**Arquivo `src/app.js` (versão completa):**

```javascript
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const { errorHandler } = require('./middlewares/errorHandler');
const { requestLogger } = require('./middlewares/logger');

const app = express();

// Segurança
app.use(helmet());

// CORS
app.use(cors({
  origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
  credentials: true
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // Máximo de 100 requisições por IP
  message: 'Muitas requisições deste IP, tente novamente mais tarde.'
});
app.use('/api/', limiter);

// Parsing de body
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Logging
if (process.env.NODE_ENV === 'development') {
  app.use(requestLogger);
}

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV
  });
});

// Rotas da API
// app.use('/api/restaurantes', restauranteRoutes);
// app.use('/api/avaliacoes', avaliacaoRoutes);

// Rota 404
app.use((req, res) => {
  res.status(404).json({
    error: 'Endpoint não encontrado',
    path: req.path
  });
});

// Error handler (deve ser o último middleware)
app.use(errorHandler);

module.exports = app;
```

### 7. Atualizando o Server.js

**Arquivo `server.js` (versão completa):**

```javascript
const app = require('./src/app');
const { sequelize, connectWithRetry } = require('./src/config/database');
const { Restaurante, Avaliacao } = require('./src/models');

const PORT = process.env.PORT || 3000;

async function startServer() {
  try {
    // Conectar ao banco com retry
    await connectWithRetry();
    
    // Sincronizar modelos
    const syncOptions = {
      force: process.env.DB_FORCE_SYNC === 'true',
      alter: process.env.DB_ALTER_SYNC === 'true'
    };
    
    await sequelize.sync(syncOptions);
    console.log('✅ Modelos sincronizados');
    
    // Iniciar servidor
    const server = app.listen(PORT, () => {
      console.log('🚀 Servidor TasteRank iniciado!');
      console.log(`📍 URL: http://localhost:${PORT}`);
      console.log(`🏥 Health: http://localhost:${PORT}/api/health`);
      console.log(`🌍 Ambiente: ${process.env.NODE_ENV}`);
    });
    
    // Graceful shutdown
    process.on('SIGTERM', () => {
      console.log('\n⚠️  SIGTERM recebido, encerrando servidor...');
      server.close(async () => {
        await sequelize.close();
        console.log('✅ Servidor encerrado');
        process.exit(0);
      });
    });
    
  } catch (error) {
    console.error('❌ Erro ao iniciar servidor:', error);
    process.exit(1);
  }
}

startServer();
```

### 8. Variáveis de Ambiente Adicionais

**Atualizar `.env`:**

```env
# Servidor
PORT=3000
NODE_ENV=development

# Banco de Dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tasterank_db
DB_USER=tasterank_user
DB_PASSWORD=senha_segura_123
DB_FORCE_SYNC=false
DB_ALTER_SYNC=false

# CORS
CORS_ORIGIN=http://localhost:5173

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### 9. Instalando Dependências Adicionais

```bash
npm install helmet express-rate-limit
```

## 🔨 Atividade Prática

### Exercício 1: Testar Error Handler

Crie uma rota de teste que dispara um erro:

```javascript
// Em src/app.js
app.get('/api/test-error', (req, res) => {
  throw new Error('Erro de teste!');
});
```

Acesse `http://localhost:3000/api/test-error` e observe o tratamento de erro.

### Exercício 2: Testar Rate Limiting

Use curl ou Postman para fazer mais de 100 requisições em 15 minutos:

```bash
for i in {1..105}; do
  curl http://localhost:3000/api/health
  echo
done
```

Observe quando o rate limiting é ativado.

### Exercício 3: Criar Middleware de Autenticação Simples

Crie um middleware que verifica se há um header `X-API-KEY`:

<details>
<summary>Ver solução</summary>

```javascript
// src/middlewares/auth.js
const { ApiError } = require('./errorHandler');

const checkApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'];
  
  if (!apiKey) {
    throw new ApiError(401, 'API Key não fornecida');
  }
  
  if (apiKey !== process.env.API_KEY) {
    throw new ApiError(403, 'API Key inválida');
  }
  
  next();
};

module.exports = { checkApiKey };
```

</details>

## 💡 Conceitos-Chave

- **Pool de conexões** otimiza uso de recursos do BD
- **Middlewares** interceptam e processam requisições
- **Error handler centralizado** padroniza respostas de erro
- **Graceful shutdown** fecha conexões corretamente
- **Rate limiting** protege contra abuso
- **Helmet** adiciona headers de segurança
- **asyncHandler** elimina try-catch repetitivo

## ➡️ Próximos Passos

Com a configuração robusta do servidor, no próximo tutorial vamos implementar as operações **CREATE e READ** para restaurantes, criando nossos primeiros endpoints funcionais.

[➡️ Ir para Tutorial 6: CRUD - Create e Read](06-crud-create-read.md)

---

**Dica:** Teste cada middleware individualmente para entender seu funcionamento!

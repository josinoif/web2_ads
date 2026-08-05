# Tutorial 8: CORS e Middlewares de Segurança

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Configurar CORS corretamente
- Implementar rate limiting
- Adicionar headers de segurança com Helmet
- Criar middlewares de logging
- Implementar validação de origem
- Proteger contra ataques comuns

## 📖 Conteúdo

### 1. Entendendo CORS

**CORS (Cross-Origin Resource Sharing)** permite que navegadores façam requisições de um domínio para outro.

**Problema sem CORS:**
```
Frontend: http://localhost:5173
Backend:  http://localhost:3000

❌ Bloqueado pelo navegador por segurança
```

**Cenários comuns:**
- Frontend React em `localhost:5173`
- Backend Express em `localhost:3000`
- Frontend em `app.exemplo.com`, backend em `api.exemplo.com`

### 2. Configuração Básica de CORS

**Já configurado em `src/app.js`, vamos melhorar:**

```javascript
const cors = require('cors');

// Configuração básica - permite qualquer origem (APENAS DEV!)
app.use(cors());

// Configuração recomendada - específica
const corsOptions = {
  origin: function (origin, callback) {
    const allowedOrigins = [
      'http://localhost:5173',
      'http://localhost:3000',
      'https://tasterank.com',
      'https://www.tasterank.com'
    ];
    
    // Permitir requisições sem origin (Postman, curl, etc.)
    if (!origin) return callback(null, true);
    
    if (allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Não permitido pelo CORS'));
    }
  },
  credentials: true, // Permite cookies e headers de autenticação
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  exposedHeaders: ['X-Total-Count'], // Headers que o frontend pode acessar
  maxAge: 86400 // Cache de preflight (24 horas)
};

app.use(cors(corsOptions));
```

### 3. CORS com Variáveis de Ambiente

**Atualizar `.env`:**

```env
# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://tasterank.com
```

**Configuração dinâmica:**

```javascript
const getAllowedOrigins = () => {
  const origins = process.env.CORS_ORIGINS || 'http://localhost:5173';
  return origins.split(',').map(origin => origin.trim());
};

const corsOptions = {
  origin: function (origin, callback) {
    const allowedOrigins = getAllowedOrigins();
    
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error(`Origem ${origin} não permitida pelo CORS`));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400
};

app.use(cors(corsOptions));
```

### 4. Helmet - Headers de Segurança

**Helmet** adiciona vários headers de segurança automaticamente:

```bash
npm install helmet
```

**Configuração completa:**

```javascript
const helmet = require('helmet');

// Configuração básica
app.use(helmet());

// Configuração customizada
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  crossOriginEmbedderPolicy: false, // Ajustar conforme necessidade
  crossOriginResourcePolicy: { policy: "cross-origin" }
}));
```

**Headers adicionados pelo Helmet:**
- `X-DNS-Prefetch-Control`: Controla DNS prefetching
- `X-Frame-Options`: Previne clickjacking
- `X-Content-Type-Options`: Previne MIME sniffing
- `X-XSS-Protection`: Ativa proteção XSS do navegador
- `Strict-Transport-Security`: Força HTTPS

### 5. Rate Limiting

**Proteger contra abuso e DDoS:**

```bash
npm install express-rate-limit
```

**Configuração:**

```javascript
const rateLimit = require('express-rate-limit');

// Rate limiter geral
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // Limite de requisições
  message: {
    error: 'Muitas requisições deste IP, tente novamente mais tarde.',
    retryAfter: '15 minutos'
  },
  standardHeaders: true, // Retorna info nos headers RateLimit-*
  legacyHeaders: false, // Desabilita headers X-RateLimit-*
  handler: (req, res) => {
    res.status(429).json({
      error: 'Limite de requisições excedido',
      retryAfter: req.rateLimit.resetTime
    });
  }
});

// Aplicar em todas as rotas da API
app.use('/api/', generalLimiter);

// Rate limiter mais restritivo para criação
const createLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hora
  max: 10, // Máximo 10 criações por hora
  message: {
    error: 'Muitas criações em pouco tempo. Aguarde antes de criar mais.'
  }
});

// Aplicar em rotas específicas
router.post('/', createLimiter, ...);
```

**Rate limiters por endpoint:**

```javascript
// src/middlewares/rateLimiters.js
const rateLimit = require('express-rate-limit');

// Limiter geral
exports.generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: { error: 'Muitas requisições' }
});

// Limiter para autenticação
exports.authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5, // Apenas 5 tentativas de login
  skipSuccessfulRequests: true, // Não conta requisições bem-sucedidas
  message: { error: 'Muitas tentativas de login. Aguarde 15 minutos.' }
});

// Limiter para criação
exports.createLimiter = rateLimit({
  windowMs: 60 * 60 * 1000,
  max: 10,
  message: { error: 'Limite de criações excedido' }
});

// Limiter para buscas pesadas
exports.searchLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1 minuto
  max: 20,
  message: { error: 'Muitas buscas em pouco tempo' }
});
```

### 6. Middleware de Logging Avançado

**src/middlewares/logger.js (versão completa):**

```javascript
const fs = require('fs');
const path = require('path');

// Criar diretório de logs se não existir
const logsDir = path.join(__dirname, '../../logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
}

// Stream para arquivo de log
const accessLogStream = fs.createWriteStream(
  path.join(logsDir, 'access.log'),
  { flags: 'a' } // append
);

const requestLogger = (req, res, next) => {
  const start = Date.now();
  const timestamp = new Date().toISOString();
  
  // Capturar informações da requisição
  const reqInfo = {
    timestamp,
    method: req.method,
    url: req.originalUrl,
    ip: req.ip || req.connection.remoteAddress,
    userAgent: req.get('user-agent')
  };
  
  // Interceptar res.json para capturar resposta
  const originalJson = res.json.bind(res);
  
  res.json = function(body) {
    const duration = Date.now() - start;
    
    // Log estruturado
    const logEntry = {
      ...reqInfo,
      status: res.statusCode,
      duration: `${duration}ms`,
      size: JSON.stringify(body).length
    };
    
    // Console log (desenvolvimento)
    if (process.env.NODE_ENV === 'development') {
      const color = res.statusCode >= 400 ? '\x1b[31m' : '\x1b[32m';
      console.log(
        `${color}[${reqInfo.method}]\x1b[0m ${reqInfo.url} - ` +
        `${res.statusCode} - ${duration}ms`
      );
    }
    
    // Arquivo log (produção)
    if (process.env.NODE_ENV === 'production') {
      accessLogStream.write(JSON.stringify(logEntry) + '\n');
    }
    
    return originalJson(body);
  };
  
  next();
};

// Log de erros
const errorLogger = (err, req, res, next) => {
  const errorLog = {
    timestamp: new Date().toISOString(),
    error: err.message,
    stack: err.stack,
    method: req.method,
    url: req.originalUrl,
    ip: req.ip
  };
  
  const errorLogStream = fs.createWriteStream(
    path.join(logsDir, 'error.log'),
    { flags: 'a' }
  );
  
  errorLogStream.write(JSON.stringify(errorLog) + '\n');
  
  next(err);
};

module.exports = { requestLogger, errorLogger };
```

### 7. App.js Completo com Segurança

**Arquivo `src/app.js` final:**

```javascript
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const mongoSanitize = require('express-mongo-sanitize');
const xss = require('express-xss-sanitizer');
require('dotenv').config();

const { errorHandler } = require('./middlewares/errorHandler');
const { requestLogger, errorLogger } = require('./middlewares/logger');
const { generalLimiter } = require('./middlewares/rateLimiters');

const restauranteRoutes = require('./routes/restauranteRoutes');

const app = express();

// Segurança
app.use(helmet());

// CORS
const getAllowedOrigins = () => {
  const origins = process.env.CORS_ORIGINS || 'http://localhost:5173';
  return origins.split(',').map(origin => origin.trim());
};

app.use(cors({
  origin: function (origin, callback) {
    const allowedOrigins = getAllowedOrigins();
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Não permitido pelo CORS'));
    }
  },
  credentials: true
}));

// Rate limiting
app.use('/api/', generalLimiter);

// Parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Sanitização - Previne NoSQL injection
app.use(mongoSanitize({
  replaceWith: '_',
  onSanitize: ({ req, key }) => {
    console.warn(`Campo suspeito detectado: ${key}`);
  }
}));

// Sanitização - Previne XSS
app.use(xss({
  whiteList: {},
  stripIgnoreTag: true
}));

// Logging
app.use(requestLogger);

// Health check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString()
  });
});

// Rotas
app.use('/api/restaurantes', restauranteRoutes);

// 404
app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint não encontrado' });
});

// Error handlers
app.use(errorLogger);
app.use(errorHandler);

module.exports = app;
```

## 🔨 Atividade Prática

### Exercício 1: Testar CORS

Crie um HTML simples e teste CORS:

```html
<!-- test-cors.html -->
<!DOCTYPE html>
<html>
<body>
  <button onclick="testarAPI()">Testar API</button>
  <div id="resultado"></div>
  
  <script>
    async function testarAPI() {
      try {
        const response = await fetch('http://localhost:3000/api/restaurantes');
        const data = await response.json();
        document.getElementById('resultado').textContent = JSON.stringify(data, null, 2);
      } catch (error) {
        document.getElementById('resultado').textContent = 'Erro: ' + error.message;
      }
    }
  </script>
</body>
</html>
```

### Exercício 2: Testar Rate Limiting

Crie script para testar rate limiting:

```bash
# test-rate-limit.sh
for i in {1..110}; do
  echo "Requisição $i"
  curl http://localhost:3000/api/health
  sleep 0.1
done
```

## 💡 Conceitos-Chave

- **CORS** permite requisições cross-origin
- **Helmet** adiciona headers de segurança
- **Rate limiting** previne abuso
- **Sanitização** previne XSS e injection
- **Logging** ajuda no debug e auditoria
- Sempre configurar **origins específicas** em produção
- **maxAge** cacheia preflight requests

## ➡️ Próximos Passos

Com a API segura e o CRUD completo, no próximo módulo vamos implementar o **sistema de avaliações**, trabalhando com relacionamentos entre tabelas.

[➡️ Ir para Tutorial 9: Criando Sistema de Avaliações](../modulo3/09-create-avaliacoes.md)

# Tutorial: Segurança Essencial em APIs

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Proteger contra ataques comuns (XSS, SQL Injection, CSRF)
- Implementar rate limiting
- Validar e sanitizar entrada de dados
- Configurar headers de segurança
- Gerenciar secrets adequadamente
- Implementar autenticação segura

## 📖 Conteúdo

### 1. Headers de Segurança

**Usando Helmet no Express:**

```javascript
const helmet = require('helmet');

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
}));

// Headers adicionais
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  next();
});
```

### 2. Validação e Sanitização

#### Express Validator

```javascript
const { body, param, validationResult } = require('express-validator');

const validarRestaurante = [
  body('nome')
    .trim()
    .isLength({ min: 3, max: 100 })
    .withMessage('Nome deve ter entre 3 e 100 caracteres')
    .escape(), // Escapa HTML
  
  body('email')
    .optional()
    .isEmail()
    .normalizeEmail()
    .withMessage('Email inválido'),
  
  body('telefone')
    .optional()
    .matches(/^[\d\s\(\)\-\+]+$/)
    .withMessage('Telefone com formato inválido'),
  
  body('descricao')
    .optional()
    .trim()
    .isLength({ max: 500 })
    .escape(),
  
  (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ 
        erros: errors.array().map(e => ({
          campo: e.param,
          mensagem: e.msg,
        }))
      });
    }
    next();
  }
];

router.post('/restaurantes', validarRestaurante, restauranteController.create);
```

#### Validação de Upload

```javascript
const fileFilter = (req, file, cb) => {
  // Validar MIME type
  const allowedMimes = ['image/jpeg', 'image/png', 'image/webp'];
  
  if (!allowedMimes.includes(file.mimetype)) {
    return cb(new Error('Tipo de arquivo não permitido'), false);
  }
  
  // Validar extensão (dupla verificação)
  const ext = path.extname(file.originalname).toLowerCase();
  if (!['.jpg', '.jpeg', '.png', '.webp'].includes(ext)) {
    return cb(new Error('Extensão de arquivo não permitida'), false);
  }
  
  cb(null, true);
};

// Sanitizar nome do arquivo
const sanitizeFilename = (filename) => {
  return filename
    .replace(/[^a-z0-9.-]/gi, '_')
    .toLowerCase()
    .substring(0, 255);
};
```

### 3. Rate Limiting

```javascript
const rateLimit = require('express-rate-limit');

// Limitar requisições gerais
const generalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutos
  max: 100, // 100 requisições
  message: 'Muitas requisições. Tente novamente mais tarde.',
  standardHeaders: true,
  legacyHeaders: false,
});

// Limitar uploads
const uploadLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hora
  max: 10, // 10 uploads
  message: 'Limite de uploads excedido',
});

// Limitar tentativas de login
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: 'Muitas tentativas de login. Aguarde 15 minutos.',
});

app.use('/api/', generalLimiter);
app.use('/api/upload', uploadLimiter);
app.use('/api/auth/login', loginLimiter);
```

### 4. Proteção contra SQL Injection

✅ **Usar Prepared Statements:**

```javascript
// Sequelize (automático)
const restaurantes = await Restaurante.findAll({
  where: {
    categoria: req.query.categoria, // Seguro
  }
});

// Query crua com parâmetros
await sequelize.query(
  'SELECT * FROM restaurantes WHERE categoria = :categoria',
  {
    replacements: { categoria: req.query.categoria },
    type: QueryTypes.SELECT,
  }
);
```

❌ **Nunca concatenar strings:**

```javascript
// PERIGOSO!
const query = `SELECT * FROM restaurantes WHERE id = ${req.params.id}`;
await sequelize.query(query);
```

### 5. Proteção XSS (Cross-Site Scripting)

```javascript
const xss = require('xss');

// Middleware para sanitizar input
const sanitizeBody = (req, res, next) => {
  if (req.body) {
    Object.keys(req.body).forEach(key => {
      if (typeof req.body[key] === 'string') {
        req.body[key] = xss(req.body[key]);
      }
    });
  }
  next();
};

app.use(sanitizeBody);

// Ou sanitizar campos específicos
const sanitizeComment = (text) => {
  return xss(text, {
    whiteList: {}, // Não permitir nenhuma tag HTML
    stripIgnoreTag: true,
  });
};
```

### 6. CORS Seguro

```javascript
const cors = require('cors');

const corsOptions = {
  origin: (origin, callback) => {
    const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];
    
    // Permitir requisições sem origin (mobile, Postman)
    if (!origin) return callback(null, true);
    
    if (allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Origem não permitida pelo CORS'));
    }
  },
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  maxAge: 600, // Cache de preflight por 10 minutos
};

app.use(cors(corsOptions));
```

### 7. Gerenciamento de Secrets

**Arquivo `.env`:**

```env
# NUNCA commitar este arquivo!
DATABASE_PASSWORD=senha_super_secreta_aqui
JWT_SECRET=chave_secreta_256_bits_minimo
API_KEY=sk_live_abc123def456
```

**Validação de secrets:**

```javascript
const crypto = require('crypto');

function validarJwtSecret() {
  const secret = process.env.JWT_SECRET;
  
  if (!secret) {
    throw new Error('JWT_SECRET não definido');
  }
  
  if (secret.length < 32) {
    throw new Error('JWT_SECRET muito curto (mínimo 32 caracteres)');
  }
  
  // Verificar se não é padrão/exemplo
  const fracos = ['secret', '123456', 'password', 'changeme'];
  if (fracos.some(f => secret.toLowerCase().includes(f))) {
    throw new Error('JWT_SECRET fraco ou padrão');
  }
}

validarJwtSecret();
```

### 8. Hashing de Senhas

```javascript
const bcrypt = require('bcrypt');

class PasswordService {
  async hash(password) {
    // Validar força da senha
    if (password.length < 8) {
      throw new Error('Senha deve ter no mínimo 8 caracteres');
    }
    
    const saltRounds = 12; // Custo computacional
    return bcrypt.hash(password, saltRounds);
  }

  async compare(password, hash) {
    return bcrypt.compare(password, hash);
  }

  validarForca(password) {
    const requisitos = {
      minLength: password.length >= 8,
      hasUppercase: /[A-Z]/.test(password),
      hasLowercase: /[a-z]/.test(password),
      hasNumber: /\d/.test(password),
      hasSpecial: /[!@#$%^&*]/.test(password),
    };

    const pontos = Object.values(requisitos).filter(Boolean).length;

    return {
      forte: pontos >= 4,
      requisitos,
    };
  }
}
```

### 9. JWT Seguro

```javascript
const jwt = require('jsonwebtoken');

function gerarToken(payload) {
  return jwt.sign(
    payload,
    process.env.JWT_SECRET,
    {
      expiresIn: '1h',
      issuer: 'tasterank-api',
      audience: 'tasterank-client',
    }
  );
}

function verificarToken(token) {
  try {
    return jwt.verify(token, process.env.JWT_SECRET, {
      issuer: 'tasterank-api',
      audience: 'tasterank-client',
    });
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      throw new Error('Token expirado');
    }
    throw new Error('Token inválido');
  }
}

// Middleware de autenticação
const authMiddleware = (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader) {
    return res.status(401).json({ erro: 'Token não fornecido' });
  }
  
  const [scheme, token] = authHeader.split(' ');
  
  if (scheme !== 'Bearer') {
    return res.status(401).json({ erro: 'Formato de token inválido' });
  }
  
  try {
    const decoded = verificarToken(token);
    req.userId = decoded.id;
    next();
  } catch (error) {
    return res.status(401).json({ erro: error.message });
  }
};
```

### 10. Logs de Segurança

```javascript
const winston = require('winston');

const securityLogger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ 
      filename: 'logs/security.log',
      level: 'warn',
    }),
  ],
});

// Logar eventos de segurança
function logSecurityEvent(event, details) {
  securityLogger.warn({
    event,
    timestamp: new Date().toISOString(),
    ...details,
  });
}

// Exemplos de uso
logSecurityEvent('LOGIN_FAILED', {
  ip: req.ip,
  email: req.body.email,
});

logSecurityEvent('UNAUTHORIZED_ACCESS', {
  ip: req.ip,
  path: req.path,
  userId: req.userId,
});
```

## 🔨 Atividade Prática

### Exercício 1: Implementar Validação Completa

Crie validadores para:
- Criar restaurante
- Criar avaliação
- Upload de imagem
- Login/registro

### Exercício 2: Configurar Rate Limiting

Implemente diferentes limites para:
- Rotas públicas (100/15min)
- Upload (10/hora)
- Login (5/15min)
- API admin (1000/hora)

### Exercício 3: Audit Log

Crie um sistema de auditoria que registre:
- Quem fez a ação
- Quando fez
- Qual ação
- Resultado (sucesso/falha)

## 💡 Conceitos-Chave

- **Defense in Depth**: Múltiplas camadas de segurança
- **Least Privilege**: Mínimo privilégio necessário
- **Fail Secure**: Falhar de forma segura
- **Input Validation**: Nunca confiar em dados do usuário
- **Secrets Management**: Gerenciar credenciais adequadamente

## ➡️ Próximos Passos

- Testes de Segurança
- Monitoramento e Alertas
- Compliance e LGPD

## 📚 Recursos

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Helmet.js](https://helmetjs.github.io/)
- [Express Security Best Practices](https://expressjs.com/en/advanced/best-practice-security.html)

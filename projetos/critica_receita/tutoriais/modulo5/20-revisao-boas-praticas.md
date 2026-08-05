# Tutorial 20: Revisão e Boas Práticas

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Aplicar boas práticas de código
- Preparar aplicação para produção
- Implementar testes básicos
- Otimizar performance
- Documentar código adequadamente
- Configurar deploy

## 📖 Conteúdo

### 1. Checklist de Boas Práticas

#### 📂 Estrutura de Código

```
✅ Separação de responsabilidades (MVC/services)
✅ Componentes pequenos e reutilizáveis
✅ Hooks customizados para lógica compartilhada
✅ Utilitários em pasta separada
✅ Configurações em variáveis de ambiente
✅ Constants em arquivo dedicado
```

#### 🎨 Frontend (React)

```
✅ Usar componentes funcionais com hooks
✅ Props tipadas (ou comentadas)
✅ Evitar prop drilling (usar Context se necessário)
✅ Memoização quando apropriado (React.memo, useMemo, useCallback)
✅ Keys únicas em listas
✅ Cleanup de effects (return no useEffect)
✅ Loading states e error handling
✅ Feedback visual para ações do usuário
✅ Validação de formulários
✅ Acessibilidade (aria-labels, semantic HTML)
```

#### ⚙️ Backend (Express)

```
✅ Validação de inputs
✅ Tratamento de erros centralizado
✅ Logging adequado
✅ Segurança (CORS, Helmet, rate limiting)
✅ Sanitização de dados
✅ Transações em operações críticas
✅ Paginação em listagens
✅ Índices em colunas frequentemente consultadas
✅ Connection pooling
✅ Graceful shutdown
```

### 2. Variáveis de Ambiente

**Backend `.env`:**

```env
# Servidor
NODE_ENV=production
PORT=3000

# Banco de dados
DB_HOST=localhost
DB_PORT=5432
DB_NAME=tasterank
DB_USER=postgres
DB_PASSWORD=senha_segura

# Segurança
JWT_SECRET=seu_secret_super_secreto_aqui
CORS_ORIGIN=https://seu-dominio.com

# Rate Limiting
RATE_LIMIT_WINDOW=15
RATE_LIMIT_MAX=100

# Logging
LOG_LEVEL=info
LOG_FILE=./logs/app.log
```

**Frontend `.env`:**

```env
# API
VITE_API_URL=https://api.seu-dominio.com

# Ambiente
VITE_ENV=production

# Features flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG=false
```

### 3. Constants e Configuração

**Arquivo `src/config/constants.js`:**

```javascript
export const API_CONFIG = {
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
};

export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 10,
  MAX_LIMIT: 100,
};

export const VALIDATION = {
  NOME_MIN_LENGTH: 3,
  NOME_MAX_LENGTH: 100,
  COMENTARIO_MIN_LENGTH: 10,
  COMENTARIO_MAX_LENGTH: 500,
  NOTA_MIN: 1,
  NOTA_MAX: 5,
};

export const CATEGORIAS = [
  'Italiana',
  'Japonesa',
  'Brasileira',
  'Mexicana',
  'Árabe',
  'Hamburgueria',
  'Pizzaria',
  'Vegetariana',
  'Outra',
];

export const ROUTES = {
  HOME: '/',
  RESTAURANTES: '/restaurantes',
  RESTAURANTE_DETALHE: '/restaurantes/:id',
  RESTAURANTE_FORM: '/restaurantes/:id?/formulario',
  AVALIACAO_FORM: '/restaurantes/:id/avaliar',
};

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Erro de conexão. Verifique sua internet.',
  TIMEOUT: 'A requisição demorou muito. Tente novamente.',
  SERVER_ERROR: 'Erro no servidor. Tente novamente mais tarde.',
  NOT_FOUND: 'Recurso não encontrado.',
  VALIDATION_ERROR: 'Dados inválidos. Verifique os campos.',
  UNAUTHORIZED: 'Não autorizado. Faça login novamente.',
};
```

### 4. Testes Básicos

**Instalar dependências:**

```bash
# Backend
npm install --save-dev jest supertest

# Frontend
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
```

**Teste Backend `tests/restaurante.test.js`:**

```javascript
const request = require('supertest');
const app = require('../src/app');
const { sequelize } = require('../src/models');

describe('Restaurantes API', () => {
  beforeAll(async () => {
    await sequelize.sync({ force: true });
  });
  
  afterAll(async () => {
    await sequelize.close();
  });
  
  describe('POST /restaurantes', () => {
    it('deve criar um novo restaurante', async () => {
      const response = await request(app)
        .post('/restaurantes')
        .send({
          nome: 'Restaurante Teste',
          categoria: 'Italiana',
          endereco: 'Rua Teste, 123'
        });
      
      expect(response.status).toBe(201);
      expect(response.body).toHaveProperty('id');
      expect(response.body.nome).toBe('Restaurante Teste');
    });
    
    it('deve retornar erro 400 com dados inválidos', async () => {
      const response = await request(app)
        .post('/restaurantes')
        .send({
          nome: '',
          categoria: 'Italiana'
        });
      
      expect(response.status).toBe(400);
      expect(response.body).toHaveProperty('error');
    });
  });
  
  describe('GET /restaurantes', () => {
    it('deve retornar lista de restaurantes', async () => {
      const response = await request(app).get('/restaurantes');
      
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('restaurantes');
      expect(Array.isArray(response.body.restaurantes)).toBe(true);
    });
  });
});
```

**Teste Frontend `tests/RestauranteCard.test.jsx`:**

```javascript
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import RestauranteCard from '../src/components/restaurantes/RestauranteCard';

describe('RestauranteCard', () => {
  const restauranteMock = {
    id: 1,
    nome: 'Restaurante Teste',
    categoria: 'Italiana',
    endereco: 'Rua Teste, 123',
    avaliacao_media: 4.5
  };
  
  it('deve renderizar nome do restaurante', () => {
    render(
      <BrowserRouter>
        <RestauranteCard restaurante={restauranteMock} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Restaurante Teste')).toBeInTheDocument();
  });
  
  it('deve renderizar categoria', () => {
    render(
      <BrowserRouter>
        <RestauranteCard restaurante={restauranteMock} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Italiana')).toBeInTheDocument();
  });
  
  it('deve renderizar avaliação média', () => {
    render(
      <BrowserRouter>
        <RestauranteCard restaurante={restauranteMock} />
      </BrowserRouter>
    );
    
    expect(screen.getByText('4.5')).toBeInTheDocument();
  });
});
```

**Configurar scripts no `package.json`:**

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### 5. Performance - Build de Produção

**Otimizar build do Vite:**

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui': ['react-toastify', 'date-fns'],
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    minify: 'terser',
    sourcemap: false
  },
  server: {
    port: 5173
  }
});
```

### 6. Documentação de API

**Usar comentários JSDoc:**

```javascript
/**
 * Busca todos os restaurantes com filtros opcionais
 * @async
 * @param {Object} params - Parâmetros de busca
 * @param {number} [params.page=1] - Número da página
 * @param {number} [params.limit=10] - Itens por página
 * @param {string} [params.busca] - Termo de busca
 * @param {string} [params.categoria] - Filtro por categoria
 * @param {string} [params.ordenar='avaliacao_media'] - Campo para ordenação
 * @param {string} [params.direcao='DESC'] - Direção da ordenação
 * @returns {Promise<Object>} Objeto com restaurantes e metadados
 * @throws {Error} Se houver erro na requisição
 */
async function getAll(params = {}) {
  const response = await api.get('/restaurantes', { params });
  return response.data;
}
```

### 7. Logging Estruturado

**Instalar Winston (backend):**

```bash
npm install winston
```

**Configurar logger:**

```javascript
// src/config/logger.js
const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'tasterank-api' },
  transports: [
    new winston.transports.File({ 
      filename: 'logs/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'logs/combined.log' 
    })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

module.exports = logger;
```

**Usar logger:**

```javascript
const logger = require('./config/logger');

// Info
logger.info('Servidor iniciado', { port: 3000 });

// Warning
logger.warn('Taxa de requisições alta', { ip: req.ip });

// Error
logger.error('Erro ao processar requisição', { 
  error: err.message, 
  stack: err.stack 
});
```

### 8. Segurança

**Headers de segurança com Helmet:**

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
    preload: true
  }
}));
```

**Sanitização de inputs:**

```javascript
const validator = require('validator');

function sanitizeInput(input) {
  if (typeof input !== 'string') return input;
  
  // Remover tags HTML
  let sanitized = validator.escape(input);
  
  // Remover caracteres especiais perigosos
  sanitized = sanitized.replace(/[<>]/g, '');
  
  return sanitized.trim();
}
```

### 9. Deploy - Preparação

**Dockerfile (Backend):**

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "src/server.js"]
```

**Dockerfile (Frontend):**

```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: tasterank
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: senha_segura
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  backend:
    build: ./backend
    environment:
      NODE_ENV: production
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: tasterank
      DB_USER: postgres
      DB_PASSWORD: senha_segura
    ports:
      - "3000:3000"
    depends_on:
      - postgres
  
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 10. README Completo

**Template de README.md:**

```markdown
# TasteRank - Sistema de Avaliação de Restaurantes

Sistema full-stack para avaliar e classificar restaurantes.

## 🚀 Tecnologias

- **Backend**: Node.js, Express, PostgreSQL, Sequelize
- **Frontend**: React, Vite, React Router, Axios
- **Outras**: Docker, date-fns, React Toastify

## 📋 Pré-requisitos

- Node.js 18+
- PostgreSQL 14+
- npm ou yarn

## 🔧 Instalação

### Backend

```bash
cd backend
npm install
cp .env.example .env
# Configurar variáveis no .env
npm run migrate
npm run seed
npm start
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Configurar VITE_API_URL
npm run dev
```

## 🐳 Docker

```bash
docker-compose up -d
```

## 🧪 Testes

```bash
npm test
npm run test:coverage
```

## 📚 API Endpoints

### Restaurantes

- `GET /restaurantes` - Listar restaurantes
- `GET /restaurantes/:id` - Obter detalhes
- `POST /restaurantes` - Criar restaurante
- `PUT /restaurantes/:id` - Atualizar restaurante
- `DELETE /restaurantes/:id` - Excluir restaurante

### Avaliações

- `GET /restaurantes/:id/avaliacoes` - Listar avaliações
- `POST /avaliacoes` - Criar avaliação
- `DELETE /avaliacoes/:id` - Excluir avaliação

## 📄 Licença

MIT

## ✨ Autor

Seu Nome
```

## 🔨 Atividade Prática Final

### Projeto Completo

Revisite seu código e aplique:

1. ✅ Extrair magic numbers para constants
2. ✅ Adicionar comentários JSDoc em funções principais
3. ✅ Implementar pelo menos 3 testes
4. ✅ Configurar variáveis de ambiente
5. ✅ Adicionar loading states em todas as requisições
6. ✅ Implementar tratamento de erros completo
7. ✅ Criar README detalhado
8. ✅ Otimizar build de produção

## 💡 Conceitos-Chave Finais

- **Código limpo** é mais importante que código "esperto"
- **Testes** garantem confiança em mudanças
- **Documentação** é parte do código
- **Segurança** deve ser prioridade desde o início
- **Performance** importa, mas legibilidade primeiro
- **Feedback ao usuário** sempre que possível
- **Prepare para produção** desde o desenvolvimento

## 🎓 Você Completou o Curso!

### O que você aprendeu:

✅ **Módulo 1**: Fundamentos (HTTP, bancos relacionais, setup, ORM)  
✅ **Módulo 2**: Backend CRUD (configuração, operações, middleware, segurança)  
✅ **Módulo 3**: Relacionamentos SQL (avaliações, consultas, médias, erros)  
✅ **Módulo 4**: Frontend React (setup, listagem, detalhes, formulários)  
✅ **Módulo 5**: UX e Robustez (feedback, otimização, async avançado, boas práticas)

### 🚀 Próximos Passos

1. **Implementar autenticação** com JWT
2. **Adicionar testes E2E** com Playwright/Cypress
3. **Implementar cache** com Redis
4. **Adicionar upload de imagens** com S3/Cloudinary
5. **Criar sistema de notificações** em tempo real (WebSockets)
6. **Implementar busca avançada** com Elasticsearch
7. **Adicionar analytics** e monitoramento
8. **Deploy em produção** (Vercel, Railway, AWS)

### 📚 Recursos Adicionais

- [Documentação React](https://react.dev)
- [Documentação Express](https://expressjs.com)
- [Sequelize Docs](https://sequelize.org)
- [MDN Web Docs](https://developer.mozilla.org)
- [Clean Code](https://github.com/ryanmcdermott/clean-code-javascript)

---

**Parabéns por completar o curso TasteRank! 🎉**

Continue praticando e construindo projetos cada vez mais complexos!

[⬅️ Voltar ao início](../../README.md)

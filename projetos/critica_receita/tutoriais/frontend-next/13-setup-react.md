# Tutorial 13: Setup do Projeto Next.js (App Router)

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Criar projeto Next.js 13+ com App Router
- Configurar Axios para requisições HTTP
- Estruturar projeto frontend com Server/Client Components
- Implementar camada de serviços e cache
- Configurar variáveis de ambiente e TypeScript básico

## 📖 Conteúdo

### 1. Criando Projeto com Next.js

**Next.js** oferece Server-Side Rendering, Static Generation e API Routes nativas.

```bash
# Criar projeto
npx create-next-app@latest tasterank-frontend

# Responder às perguntas:
# Would you like to use the recommended Next.js defaults? › No, customize settings
# Would you like to use TypeScript? › No
# Which linter would you like to use? › ESLint
# Would you like to use React Compiler?
# Would you like to use Tailwind CSS? › No
# Would you like to use `src/` directory? › Yes
# Would you like to use App Router? › Yes
# Would you like to customize the import alias (`@/*` by default)? Yes
# What import alias would you like configured? … @/*

# Entrar no diretório
cd tasterank-frontend

# Instalar dependências adicionais
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

**Servidor iniciará em:** `http://localhost:3000`

### 2. Instalando Dependências

```bash
# Axios para requisições HTTP
npm install axios

# Outras bibliotecas úteis
npm install date-fns  # Manipulação de datas
npm install clsx      # Utilitário para classes CSS
```

**⚠️ Nota:** Next.js já inclui routing nativo, não precisa de React Router.

### 3. Estrutura do Projeto

```
tasterank-frontend/
├── public/              # Arquivos estáticos
│   ├── favicon.ico
│   └── next.svg
├── src/
│   ├── app/             # App Router (Next.js 13+)
│   │   ├── layout.js    # Layout raiz
│   │   ├── page.js      # Home
│   │   ├── globals.css
│   │   └── restaurantes/
│   │       ├── page.js           # /restaurantes
│   │       ├── [id]/
│   │       │   └── page.js       # /restaurantes/[id]
│   │       └── loading.js        # Skeleton loading
│   ├── components/      # Componentes reutilizáveis
│   │   ├── Navbar.js
│   │   ├── Footer.js
│   │   ├── Header.js
│   │   ├── RestauranteCard.js
│   │   └── AvaliacaoForm.js
│   ├── services/        # Chamadas à API
│   │   ├── api.js       # Config do Axios
│   │   ├── restauranteService.js
│   │   └── avaliacaoService.js
│   ├── hooks/           # Custom hooks
│   │   ├── useRestaurantes.js
│   │   └── useAvaliacoes.js
│   ├── utils/           # Funções auxiliares
│   │   └── formatters.js
│   └── styles/          # CSS modules
│       └── components/
├── .env.local           # Variáveis de ambiente (local)
├── .env.example
├── next.config.js
├── package.json
└── jsconfig.json
```

**Criar estrutura:**

```bash
mkdir -p src/{components,services,hooks,utils,styles/components}
touch src/services/{api,restauranteService,avaliacaoService}.js
touch src/hooks/{useRestaurantes,useAvaliacoes}.js
```

### 4. Configurando Variáveis de Ambiente

**Arquivo `.env.local`:**

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:3000/api
NEXT_PUBLIC_API_TIMEOUT=10000
```

**Arquivo `.env.example`:**

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:3000/api
NEXT_PUBLIC_API_TIMEOUT=10000
```

**⚠️ Importante:** No Next.js, variáveis devem começar com `NEXT_PUBLIC_` para serem acessíveis no frontend

### 5. Configurando Axios

**Arquivo `src/services/api.js`:**

```javascript
import axios from 'axios';

// Criar instância do Axios
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3000/api',
  timeout: process.env.NEXT_PUBLIC_API_TIMEOUT || 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Interceptor de requisição (adicionar token, etc)
api.interceptors.request.use(
  (config) => {
    // Adicionar token se existir (usar typeof window para SSR-safe)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    
    // Log da requisição em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      console.log(`📤 ${config.method.toUpperCase()} ${config.url}`);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Erro na requisição:', error);
    return Promise.reject(error);
  }
);

// Interceptor de resposta (tratar erros)
api.interceptors.response.use(
  (response) => {
    // Log da resposta em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      console.log(`📥 ${response.config.method.toUpperCase()} ${response.config.url}`, response.data);
    }
    
    return response;
  },
  (error) => {
    // Tratar erros comuns
    if (error.response) {
      // Servidor respondeu com erro
      const { status, data } = error.response;
      
      console.error(`❌ Erro ${status}:`, data);
      
      // Tratar códigos específicos
      switch (status) {
        case 401:
          // Não autorizado - redirecionar para login
          console.error('Não autorizado');
          if (typeof window !== 'undefined') {
            // window.location.href = '/login';
          }
          break;
        case 404:
          console.error('Recurso não encontrado');
          break;
        case 500:
          console.error('Erro interno do servidor');
          break;
      }
    } else if (error.request) {
      // Requisição foi feita mas sem resposta
      console.error('❌ Sem resposta do servidor:', error.request);
    } else {
      // Erro ao configurar requisição
      console.error('❌ Erro:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### 6. Serviço de Restaurantes

**Arquivo `src/services/restauranteService.js`:**

```javascript
import api from './api';

const restauranteService = {
  // Listar todos os restaurantes
  getAll: async (params = {}) => {
    try {
      const response = await api.get('/restaurantes', { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  // Buscar restaurante por ID
  getById: async (id) => {
    try {
      const response = await api.get(`/restaurantes/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  // Criar novo restaurante
  create: async (data) => {
    try {
      const response = await api.post('/restaurantes', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  // Atualizar restaurante
  update: async (id, data) => {
    try {
      const response = await api.put(`/restaurantes/${id}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  // Deletar restaurante
  delete: async (id) => {
    try {
      const response = await api.delete(`/restaurantes/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  // Buscar top rated
  getTopRated: async (limit = 10) => {
    try {
      const response = await api.get('/restaurantes/top-rated', {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  // Buscar por categoria
  getByCategoria: async (categoria) => {
    try {
      const response = await api.get(`/restaurantes/categoria/${categoria}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  }
};

export default restauranteService;
```

### 7. Serviço de Avaliações

**Arquivo `src/services/avaliacaoService.js`:**

```javascript
import api from './api';

const avaliacaoService = {
  // Listar avaliações de um restaurante
  getByRestaurante: async (restauranteId, params = {}) => {
    try {
      const response = await api.get(
        `/restaurantes/${restauranteId}/avaliacoes`,
        { params }
      );
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  // Criar avaliação
  create: async (restauranteId, data) => {
    try {
      const response = await api.post(
        `/restaurantes/${restauranteId}/avaliacoes`,
        data
      );
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  // Atualizar avaliação
  update: async (id, data) => {
    try {
      const response = await api.put(`/avaliacoes/${id}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  },
  
  // Deletar avaliação
  delete: async (id) => {
    try {
      const response = await api.delete(`/avaliacoes/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error;
    }
  }
};

export default avaliacaoService;
```

### 8. Layout Raiz do Next.js

**Arquivo `src/app/layout.js`:**

```javascript
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import './globals.css';

export const metadata = {
  title: 'TasteRank - Avalie Restaurantes',
  description: 'Descubra e avalie os melhores restaurantes da sua região',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>
        <div className="app-container">
          <Navbar />
          <main className="main-content">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
```

### 9. Componente Navbar

**Arquivo `src/components/Navbar.js`:**

```javascript
'use client'; // Client Component

import Link from 'next/link';
import './Navbar.css';

export default function Navbar() {
  return (
    <header className="header">
      <nav className="navbar">
        <Link href="/" className="logo">
          <h1>🍽️ TasteRank</h1>
        </Link>
        <ul className="nav-links">
          <li><Link href="/">Home</Link></li>
          <li><Link href="/restaurantes">Restaurantes</Link></li>
        </ul>
      </nav>
    </header>
  );
}
```

**Arquivo `src/components/Navbar.css`:**

```css
.header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.navbar {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
}

.logo {
  text-decoration: none;
  color: white;
}

.logo h1 {
  margin: 0;
  font-size: 1.5rem;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 2rem;
  margin: 0;
  padding: 0;
}

.nav-links a {
  color: white;
  text-decoration: none;
  transition: color 0.3s;
}

.nav-links a:hover {
  color: #3498db;
}
```

### 10. Componente Footer

**Arquivo `src/components/Footer.js`:**

```javascript
export default function Footer() {
  return (
    <footer className="footer">
      <p>&copy; 2024 TasteRank. Todos os direitos reservados.</p>
    </footer>
  );
}
```

### 11. Página Home

**Arquivo `src/app/page.js`:**

```javascript
import Link from 'next/link';
import './home.css';

export default function Home() {
  return (
    <div className="home-container">
      <section className="hero">
        <h1>Bem-vindo ao TasteRank</h1>
        <p>Descubra e avalie os melhores restaurantes da sua região</p>
        <Link href="/restaurantes" className="cta-button">
          Ver Restaurantes
        </Link>
      </section>
      
      <section className="features">
        <div className="feature">
          <h3>🔍 Busque</h3>
          <p>Encontre restaurantes por categoria e localização</p>
        </div>
        <div className="feature">
          <h3>⭐ Avalie</h3>
          <p>Compartilhe sua experiência com a comunidade</p>
        </div>
        <div className="feature">
          <h3>🏆 Descubra</h3>
          <p>Conheça os mais bem avaliados</p>
        </div>
      </section>
    </div>
  );
}
```

**Arquivo `src/app/home.css`:**

```css
.home-container {
  padding: 2rem 0;
}

.hero {
  text-align: center;
  padding: 4rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.cta-button {
  display: inline-block;
  background-color: white;
  color: #667eea;
  padding: 12px 32px;
  border-radius: 4px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.3s;
}

.cta-button:hover {
  background-color: #f0f0f0;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature {
  padding: 2rem;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: center;
}

.feature h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}
```

### 12. Global CSS

**Arquivo `src/app/globals.css`:**

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  background-color: #f5f5f5;
  color: #333;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

.footer {
  background-color: #34495e;
  color: white;
  text-align: center;
  padding: 1rem;
  margin-top: auto;
}
```

## 🔨 Atividade Prática

### Exercício 1: Testar Conexão com API

Crie um componente de teste que faz uma requisição à API:

```javascript
// src/components/ApiTest.js
'use client';

import { useState } from 'react';
import restauranteService from '@/services/restauranteService';

export default function ApiTest() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const testarConexao = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await restauranteService.getAll({ limit: 5 });
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      <button onClick={testarConexao}>Testar API</button>
      {loading && <p>Carregando...</p>}
      {error && <p style={{color: 'red'}}>Erro: {error}</p>}
      {data && <pre>{JSON.stringify(data, null, 2)}</pre>}
    </div>
  );
}
```

**Use no seu layout:**

```javascript
// src/app/page.js
import ApiTest from '@/components/ApiTest';

export default function Home() {
  return (
    <>
      {/* conteúdo anterior */}
      <ApiTest />
    </>
  );
}
```

## Desafio

Execute o frontend e o backend. Você irá identificar alguns bugs de execução. Seu papel como dev é identificar esses erros e corrigi-los com o mínimo de alteração possível no código. 

## 💡 Conceitos-Chave

- **Next.js** oferece SSR, SSG e API Routes nativos
- **App Router** (Next.js 13+) é o novo padrão
- **File-based routing** cria rotas automaticamente
- **'use client'** marca componentes interativos
- **Variáveis de ambiente** devem começar com `NEXT_PUBLIC_`
- **Axios** continua sendo a melhor forma de fazer requisições
- **Metadata** é importante para SEO
- **Layout** envolve todas as páginas via `layout.js`

## Diferenças React + Vite vs Next.js

| Aspecto | React + Vite | Next.js |
|---------|-------------|---------|
| Routing | React Router | File-based (nativo) |
| SSR | ❌ Não | ✅ Sim |
| SSG | ❌ Não | ✅ Sim |
| API Routes | ❌ Precisa backend separado | ✅ Nativo |
| SEO | Manual | Automático com Metadata |
| Build | Vite (rápido) | Next.js (otimizado) |
| Deployment | Qualquer servidor | Vercel (recomendado) |

## ➡️ Próximos Passos

Com o setup completo, no próximo tutorial vamos implementar a **listagem de restaurantes** com busca e filtros.

[➡️ Ir para Tutorial 14: Consumo da API e Listagem](14-consumo-api-listagem.md)

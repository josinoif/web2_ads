# Módulo 06 - Frontend: Configuração Inicial com Next.js

Neste módulo, você vai criar e configurar o projeto Next.js com Tailwind CSS, estabelecer a comunicação com o backend e criar o layout base da aplicação.

## Objetivos do Módulo

- ✅ Criar projeto Next.js 14 com App Router
- ✅ Configurar Tailwind CSS para estilização
- ✅ Instalar e configurar Axios
- ✅ Criar serviço de API
- ✅ Criar layout base (Navbar e Footer)
- ✅ Testar conexão com o backend

---

## 1. Criando o Projeto Next.js

### Passo 1: Navegar até a pasta do projeto

Abra um **novo terminal** (mantenha o backend rodando no outro terminal):

```bash
cd crud-receitas
```

### Passo 2: Criar o projeto Next.js

```bash
npx create-next-app@latest frontend
```

**Respostas recomendadas para as perguntas:**

```
✔ Would you like to use TypeScript? … No
✔ Would you like to use ESLint? … Yes  
✔ Would you like to use Tailwind CSS? … Yes
✔ Would you like to use `src/` directory? … Yes
✔ Would you like to use App Router? … Yes
✔ Would you like to customize the default import alias (@/*)? … No
```

**Por que essas escolhas?**
- ❌ **TypeScript**: Para manter o tutorial mais acessível
- ✅ **ESLint**: Ajuda a encontrar erros no código
- ✅ **Tailwind CSS**: Framework CSS moderno e poderoso
- ✅ **src/ directory**: Melhor organização
- ✅ **App Router**: Nova arquitetura do Next.js (mais moderna)

### Passo 3: Entrar na pasta do projeto

```bash
cd frontend
```

---

## 2. Instalando Dependências Adicionais

```bash
npm install axios react-hot-toast
```

### O que cada pacote faz:

| Pacote | Descrição |
|--------|-----------|
| **axios** | Cliente HTTP para fazer requisições à API |
| **react-hot-toast** | Notificações toast elegantes (alternativa ao react-toastify) |

---

## 3. Entendendo a Estrutura do Next.js

O Next.js 14 com App Router usa uma estrutura baseada em pastas:

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.js          ← Layout global da aplicação
│   │   ├── page.js            ← Página inicial (/)
│   │   ├── globals.css        ← Estilos globais
│   │   ├── receitas/
│   │   │   ├── page.js        ← Lista de receitas (/receitas)
│   │   │   ├── [id]/
│   │   │   │   └── page.js    ← Detalhes (/receitas/123)
│   │   │   ├── novo/
│   │   │   │   └── page.js    ← Nova receita (/receitas/novo)
│   │   │   └── editar/
│   │   │       └── [id]/
│   │   │           └── page.js ← Editar (/receitas/editar/123)
│   │   └── ingredientes/
│   │       └── page.js        ← Ingredientes (/ingredientes)
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── Footer.jsx
│   │   ├── ReceitaCard.jsx
│   │   ├── ReceitaLista.jsx
│   │   └── ReceitaForm.jsx
│   └── services/
│       └── api.js
├── public/
└── package.json
```

**Conceitos importantes:**
- Cada pasta em `app/` vira uma rota automaticamente
- `page.js` define o conteúdo da rota
- `layout.js` define o layout compartilhado
- `[id]` cria rotas dinâmicas

---

## 4. Configurando Variáveis de Ambiente

### Crie o arquivo `.env.local` na raiz do projeto frontend:

```bash
# Na pasta frontend/
touch .env.local
```

### Adicione a URL da API:

```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
```

**⚠️ Importante:**
- Variáveis que começam com `NEXT_PUBLIC_` são acessíveis no navegador
- Nunca coloque senhas ou tokens secretos aqui
- Este arquivo não deve ir para o Git (já está no .gitignore)

---

## 5. Criando o Serviço de API

### Crie a pasta `services`:

```bash
mkdir src/services
```

### Crie o arquivo `src/services/api.js`:

```javascript
// ============================================
// CONFIGURAÇÃO DO AXIOS
// ============================================

import axios from 'axios';

// URL base da API (do arquivo .env.local)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';

// Cria instância do axios com configurações padrão
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 10000 // 10 segundos
});

// ============================================
// SERVIÇOS DE INGREDIENTES
// ============================================

export const ingredientesService = {
    // Listar todos os ingredientes
    listarTodos: async () => {
        const response = await api.get('/ingredientes');
        return response.data;
    },

    // Buscar ingrediente por ID
    buscarPorId: async (id) => {
        const response = await api.get(`/ingredientes/${id}`);
        return response.data;
    },

    // Criar novo ingrediente
    criar: async (dados) => {
        const response = await api.post('/ingredientes', dados);
        return response.data;
    },

    // Atualizar ingrediente
    atualizar: async (id, dados) => {
        const response = await api.put(`/ingredientes/${id}`, dados);
        return response.data;
    },

    // Deletar ingrediente
    deletar: async (id) => {
        const response = await api.delete(`/ingredientes/${id}`);
        return response.data;
    }
};

// ============================================
// SERVIÇOS DE RECEITAS
// ============================================

export const receitasService = {
    // Listar todas as receitas
    listarTodas: async () => {
        const response = await api.get('/receitas');
        return response.data;
    },

    // Buscar receita por ID (com ingredientes)
    buscarPorId: async (id) => {
        const response = await api.get(`/receitas/${id}`);
        return response.data;
    },

    // Criar nova receita
    criar: async (dados) => {
        const response = await api.post('/receitas', dados);
        return response.data;
    },

    // Atualizar receita
    atualizar: async (id, dados) => {
        const response = await api.put(`/receitas/${id}`, dados);
        return response.data;
    },

    // Deletar receita
    deletar: async (id) => {
        const response = await api.delete(`/receitas/${id}`);
        return response.data;
    },

    // Filtrar por categoria
    filtrarPorCategoria: async (categoria) => {
        const response = await api.get(`/receitas/categoria/${categoria}`);
        return response.data;
    },

    // Buscar por nome
    buscarPorNome: async (nome) => {
        const response = await api.get(`/receitas/buscar?nome=${nome}`);
        return response.data;
    }
};

// ============================================
// INTERCEPTOR PARA TRATAMENTO DE ERROS
// ============================================

api.interceptors.response.use(
    response => response,
    error => {
        // Trata diferentes tipos de erro
        if (error.response) {
            // Servidor respondeu com erro
            console.error('Erro da API:', error.response.data);
        } else if (error.request) {
            // Requisição foi feita mas não houve resposta
            console.error('Erro de rede:', error.request);
        } else {
            // Erro ao configurar a requisição
            console.error('Erro:', error.message);
        }
        return Promise.reject(error);
    }
);

export default api;
```

---

## 6. Criando a Navbar

### Crie a pasta `components`:

```bash
mkdir src/components
```

### Crie o arquivo `src/components/Navbar.jsx`:

```javascript
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
    const pathname = usePathname();

    // Função para verificar se a rota está ativa
    const isActive = (path) => {
        return pathname === path;
    };

    return (
        <nav className="bg-gradient-to-r from-purple-600 to-pink-600 shadow-lg">
            <div className="container mx-auto px-4">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <Link href="/" className="flex items-center space-x-2 text-white font-bold text-xl">
                        <span className="text-2xl">🍳</span>
                        <span>Sistema de Receitas</span>
                    </Link>

                    {/* Menu */}
                    <div className="hidden md:flex items-center space-x-1">
                        <Link
                            href="/"
                            className={`px-4 py-2 rounded-lg transition-colors ${
                                isActive('/') 
                                    ? 'bg-white/20 text-white' 
                                    : 'text-white/80 hover:bg-white/10 hover:text-white'
                            }`}
                        >
                            Receitas
                        </Link>
                        <Link
                            href="/receitas/novo"
                            className={`px-4 py-2 rounded-lg transition-colors ${
                                isActive('/receitas/novo') 
                                    ? 'bg-white/20 text-white' 
                                    : 'text-white/80 hover:bg-white/10 hover:text-white'
                            }`}
                        >
                            + Nova Receita
                        </Link>
                        <Link
                            href="/ingredientes"
                            className={`px-4 py-2 rounded-lg transition-colors ${
                                isActive('/ingredientes') 
                                    ? 'bg-white/20 text-white' 
                                    : 'text-white/80 hover:bg-white/10 hover:text-white'
                            }`}
                        >
                            Ingredientes
                        </Link>
                    </div>

                    {/* Menu Mobile (simplificado) */}
                    <div className="md:hidden">
                        <button className="text-white p-2">
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
```

**Explicação dos conceitos:**

**1. `'use client'`:**
- Indica que este é um Client Component
- Necessário para usar hooks como `usePathname`

**2. `usePathname()`:**
- Hook do Next.js que retorna a rota atual
- Usado para destacar o menu ativo

**3. Classes Tailwind:**
- `bg-gradient-to-r from-purple-600 to-pink-600`: Gradiente roxo para rosa
- `hover:bg-white/10`: Fundo branco semi-transparente ao passar o mouse
- `md:flex`: Mostra apenas em telas médias ou maiores

---

## 7. Criando o Footer

### Crie o arquivo `src/components/Footer.jsx`:

```javascript
export default function Footer() {
    const anoAtual = new Date().getFullYear();

    return (
        <footer className="bg-gray-100 border-t border-gray-200 mt-auto">
            <div className="container mx-auto px-4 py-6">
                <div className="text-center text-gray-600">
                    <p className="text-sm">
                        🍳 Sistema de Receitas © {anoAtual}
                    </p>
                    <p className="text-xs mt-1 text-gray-500">
                        CRUD Fullstack com Next.js, Tailwind CSS e Express.js
                    </p>
                </div>
            </div>
        </footer>
    );
}
```

---

## 8. Configurando o Layout Global

### Edite o arquivo `src/app/layout.js`:

```javascript
import { Inter } from 'next/font/google';
import { Toaster } from 'react-hot-toast';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Sistema de Receitas',
  description: 'Gerencie suas receitas culinárias favoritas',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.className} flex flex-col min-h-screen`}>
        <Navbar />
        <main className="flex-1">
          {children}
        </main>
        <Footer />
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 4000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </body>
    </html>
  );
}
```

**Explicação:**
- `Inter`: Fonte do Google otimizada
- `Toaster`: Componente para exibir notificações
- `flex flex-col min-h-screen`: Faz o footer ficar no final da página

---

## 9. Criando a Página Inicial

### Edite o arquivo `src/app/page.js`:

```javascript
'use client';

import { useEffect, useState } from 'react';
import { ingredientesService } from '@/services/api';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function Home() {
  const [ingredientes, setIngredientes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    testarConexao();
  }, []);

  const testarConexao = async () => {
    try {
      const response = await ingredientesService.listarTodos();
      setIngredientes(response.data || []);
      toast.success(`✅ Conectado! ${response.total} ingredientes carregados.`);
    } catch (error) {
      toast.error('❌ Erro ao conectar com a API');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto text-center">
        {/* Cabeçalho */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            🍳 Bem-vindo ao Sistema de Receitas!
          </h1>
          <p className="text-xl text-gray-600">
            Gerencie suas receitas culinárias favoritas de forma simples e organizada
          </p>
        </div>

        {/* Status da Conexão */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          </div>
        ) : (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-semibold text-green-800 mb-2">
              ✅ Frontend Conectado com Sucesso!
            </h2>
            <p className="text-green-700">
              {ingredientes.length} ingredientes encontrados no banco de dados
            </p>
          </div>
        )}

        {/* Cards de Ação */}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <Link href="/" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow border-2 border-transparent group-hover:border-purple-500">
              <div className="text-4xl mb-3">📚</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Ver Receitas</h3>
              <p className="text-sm text-gray-600">
                Explore todas as suas receitas cadastradas
              </p>
            </div>
          </Link>

          <Link href="/receitas/novo" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow border-2 border-transparent group-hover:border-pink-500">
              <div className="text-4xl mb-3">➕</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Nova Receita</h3>
              <p className="text-sm text-gray-600">
                Adicione uma nova receita ao seu catálogo
              </p>
            </div>
          </Link>

          <Link href="/ingredientes" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow border-2 border-transparent group-hover:border-purple-500">
              <div className="text-4xl mb-3">🥕</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Ingredientes</h3>
              <p className="text-sm text-gray-600">
                Gerencie o catálogo de ingredientes
              </p>
            </div>
          </Link>
        </div>

        {/* Recursos */}
        <div className="mt-12 p-6 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            ✨ Recursos do Sistema
          </h3>
          <div className="grid md:grid-cols-2 gap-4 text-left">
            <div className="flex items-start space-x-2">
              <span className="text-green-500">✓</span>
              <span className="text-sm text-gray-700">Crie receitas com múltiplos ingredientes</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-green-500">✓</span>
              <span className="text-sm text-gray-700">Filtre receitas por categoria</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-green-500">✓</span>
              <span className="text-sm text-gray-700">Busque receitas pelo nome</span>
            </div>
            <div className="flex items-start space-x-2">
              <span className="text-green-500">✓</span>
              <span className="text-sm text-gray-700">Interface moderna e responsiva</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
```

---

## 10. Personalizando Estilos Globais

### Edite `src/app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Customizações globais */
@layer base {
  html {
    @apply scroll-smooth;
  }
  
  body {
    @apply bg-gray-50;
  }
}

/* Componentes personalizados */
@layer components {
  .btn-primary {
    @apply bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .btn-danger {
    @apply bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200;
  }
  
  .input-field {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition-all;
  }
  
  .label {
    @apply block text-sm font-medium text-gray-700 mb-2;
  }
}

/* Animações personalizadas */
@layer utilities {
  .animate-fade-in {
    animation: fadeIn 0.5s ease-in;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}
```

---

## 11. Testando a Aplicação

### Passo 1: Iniciar o backend

Em um terminal:
```bash
cd crud-receitas/backend
npm run dev
```

Verifique que está rodando em [http://localhost:3001](http://localhost:3001)

### Passo 2: Iniciar o Next.js

Em outro terminal:
```bash
cd crud-receitas/frontend
npm run dev
```

### Passo 3: Acessar no navegador

Abra [http://localhost:3000](http://localhost:3000)

**Você deve ver:**
- ✅ Navbar com gradiente roxo/rosa
- ✅ Mensagem de boas-vindas
- ✅ Notificação toast verde com quantidade de ingredientes
- ✅ 3 cards de ação (Ver Receitas, Nova Receita, Ingredientes)
- ✅ Lista de recursos do sistema
- ✅ Footer no final da página
- ✅ Layout responsivo

---

## 12. Solução de Problemas Comuns

### Erro: "Network Error" ou CORS

**Causa:** Backend não está rodando ou CORS não configurado

**Solução:**
1. Verifique se o backend está em `http://localhost:3001`
2. Confirme que `app.use(cors())` está no `server.js`

### Erro: "Module not found: Can't resolve '@/services/api'"

**Causa:** Alias `@/` não configurado

**Solução:**
- O Next.js já configura `@/` automaticamente para a pasta `src/`
- Certifique-se de que o arquivo está em `src/services/api.js`

### Erro: "Hydration failed"

**Causa:** Diferença entre renderização servidor/cliente

**Solução:**
- Use `'use client'` em componentes que usam hooks
- Evite `Math.random()` ou `Date.now()` diretamente no JSX

### Tailwind não está funcionando

**Causa:** Tailwind não foi instalado corretamente

**Solução:**
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

## Resumo do Módulo

Neste módulo você:
- ✅ Criou projeto Next.js 14 com App Router
- ✅ Configurou Tailwind CSS para estilização moderna
- ✅ Instalou e configurou Axios para chamadas à API
- ✅ Criou serviço de API centralizado
- ✅ Criou Navbar com gradiente e menu ativo
- ✅ Criou Footer responsivo
- ✅ Configurou layout global com Toaster
- ✅ Criou página inicial com teste de conexão
- ✅ Aprendeu sobre Client e Server Components

---

## Próximo Passo

Agora que o frontend está configurado e conectado, vamos criar a listagem de receitas com filtros e busca!

**➡️ Próximo:** [Módulo 07 - Frontend: Listagem de Receitas](07-frontend-listagem.md)

---

## Dicas Importantes

💡 **`'use client'`** só é necessário quando você usa hooks, eventos ou state.

💡 **Tailwind** permite criar interfaces rapidamente sem CSS customizado.

💡 **`@/`** é um alias para `src/` - facilita importações.

💡 **Hot Reload** - Mudanças aparecem automaticamente no navegador.

💡 **Next.js otimiza** automaticamente imagens, fontes e código.

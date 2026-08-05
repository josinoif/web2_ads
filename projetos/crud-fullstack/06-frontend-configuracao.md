# Módulo 06 - Frontend: Configuração Inicial com Next.js 16, React 19 e Tailwind CSS 4

Este tutorial foi reescrito para funcionar com as versões informadas:
- Next.js 16
- React 19
- Tailwind CSS 4 (novo formato, sem `tailwind.config.js` por padrão)
- PostCSS com `@tailwindcss/postcss`

Ele remove passos obsoletos (como `npx tailwindcss init -p`) e ajusta o CSS global ao padrão do Tailwind v4, evitando o erro de utilitário desconhecido (ex.: `bg-gray-50`).

---

## Checklist
- [ ] Criar projeto Next.js 16 com App Router e src/
- [ ] Instalar dependências (axios, react-hot-toast, @tailwindcss/postcss, autoprefixer)
- [ ] Configurar PostCSS para Tailwind v4
- [ ] Ajustar CSS global para Tailwind v4 (`@import "tailwindcss"`)
- [ ] Configurar layout com import do CSS global
- [ ] Criar serviços de API
- [ ] Criar Navbar e Footer
- [ ] Criar página inicial de teste
- [ ] Rodar backend e frontend
- [ ] Solucionar problemas comuns

---

## 1. Crie o Projeto Next.js

No terminal:

```bash
npx create-next-app@latest frontend
```

Responda:
- TypeScript? Não
- ESLint? Sim
- Tailwind CSS? Sim
- src/ directory? Sim
- App Router? Sim
- Custom import alias? Não

Entre na pasta do projeto:

```bash
cd frontend
```

Observação: Se você já criou sem Tailwind, não tem problema — vamos configurar manualmente abaixo.

---

## 2. Instale as Dependências Adicionais

```bash
npm install axios react-hot-toast
npm install -D @tailwindcss/postcss autoprefixer
```

Notas importantes:
- Tailwind v4 usa o plugin `@tailwindcss/postcss` em vez de `tailwindcss` dentro do `postcss.config.js`.
- Não rode `npx tailwindcss init -p` — esse comando não existe mais no v4, e é a causa do erro `could not determine executable to run`.

---

## 3. Configure o Tailwind CSS 4

O Tailwind v4 simplificou a configuração. Você NÃO precisa de `tailwind.config.js` para começar.

### 3.1. Configure o PostCSS

Crie/edite `postcss.config.js` na raiz do frontend:

```js
export default {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
};
```

### 3.2. Ajuste o CSS Global

No Tailwind v4, use apenas um import no CSS global.

Edite `src/app/globals.css` para conter exatamente:

```css
@import "tailwindcss";

:root {
  --background: #f9fafb;
  --foreground: #111827;
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --font-sans: var(--font-geist-sans);
  --font-mono: var(--font-geist-mono);
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: Arial, Helvetica, sans-serif;
}

/* Estilos para inputs e selects */
input[type="text"],
input[type="number"],
input[type="email"],
input[type="password"],
textarea,
select {
  @apply border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent;
}

/* Classes utilitárias customizadas */
.input-field {
  @apply border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent;
}

.btn-primary {
  @apply bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition-colors;
}

.card {
  @apply bg-white rounded-xl shadow-md p-6;
}

.label {
  @apply block text-sm font-semibold text-gray-700 mb-2;
}

```

- Não use `@tailwind base;`, `@tailwind components;` ou `@tailwind utilities;` no v4 — isso é do v3.
- Não coloque classes utilitárias diretamente em `globals.css`. Use as classes nos componentes/páginas.
- Esse ajuste corrige o erro `CssSyntaxError: Cannot apply unknown utility class 'bg-gray-50'` que ocorre quando o Tailwind v4 não está carregado corretamente.

### 3.3. Opcional: Plugins de Tailwind

Se quiser usar plugins oficiais (forms, typography), adicione ao `globals.css` depois do import:

```css
@import "tailwindcss";
/* @import "@tailwindcss/forms"; */
/* @import "@tailwindcss/typography"; */
```

---

## 4. Importe o CSS Global no Layout

No arquivo `src/app/layout.js` (ou `layout.tsx`), importe o CSS global no topo:

```js
import './globals.css';
```

---

## 5. Configure Variáveis de Ambiente

Crie o arquivo `.env.local` na raiz de `frontend`:

```env
NEXT_PUBLIC_API_URL=http://localhost:3001/api
```

---

## 6. Crie o Serviço de API

Crie `src/services/api.js`:

```js
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
});

export const ingredientesService = {
  listarTodos: async () => (await api.get('/ingredientes')).data,
  buscarPorId: async (id) => (await api.get(`/ingredientes/${id}`)).data,
  criar: async (dados) => (await api.post('/ingredientes', dados)).data,
  atualizar: async (id, dados) => (await api.put(`/ingredientes/${id}`, dados)).data,
  deletar: async (id) => (await api.delete(`/ingredientes/${id}`)).data,
};

export const receitasService = {
  listarTodas: async () => (await api.get('/receitas')).data,
  buscarPorId: async (id) => (await api.get(`/receitas/${id}`)).data,
  criar: async (dados) => (await api.post('/receitas', dados)).data,
  atualizar: async (id, dados) => (await api.put(`/receitas/${id}`, dados)).data,
  deletar: async (id) => (await api.delete(`/receitas/${id}`)).data,
  filtrarPorCategoria: async (categoria) => (await api.get(`/receitas/categoria/${categoria}`)).data,
  buscarPorNome: async (nome) => (await api.get(`/receitas/buscar?nome=${nome}`)).data,
};

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      console.error('Erro da API:', error.response.data);
    } else if (error.request) {
      console.error('Erro de rede:', error.request);
    } else {
      console.error('Erro:', error.message);
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

## 7. Crie Componentes Globais

### 7.1. Navbar (`src/components/Navbar.jsx`)

```js
'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navbar() {
  const pathname = usePathname();
  const isActive = (path) => pathname === path;
  return (
    <nav className="bg-gradient-to-r from-purple-600 to-pink-600 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center space-x-2 text-white font-bold text-xl">
            <span className="text-2xl">🍳</span>
            <span>Sistema de Receitas</span>
          </Link>
          <div className="hidden md:flex items-center space-x-1">
            <Link href="/" className={`px-4 py-2 rounded-lg transition-colors ${isActive('/') ? 'bg-white/20 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'}`}>Receitas</Link>
            <Link href="/receitas/novo" className={`px-4 py-2 rounded-lg transition-colors ${isActive('/receitas/novo') ? 'bg-white/20 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'}`}>+ Nova Receita</Link>
            <Link href="/ingredientes" className={`px-4 py-2 rounded-lg transition-colors ${isActive('/ingredientes') ? 'bg-white/20 text-white' : 'text-white/80 hover:bg-white/10 hover:text-white'}`}>Ingredientes</Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
```

### 7.2. Footer (`src/components/Footer.jsx`)

```js
export default function Footer() {
  const anoAtual = new Date().getFullYear();
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="text-center text-gray-600">
          <p className="text-sm">🍳 Sistema de Receitas © {anoAtual}</p>
          <p className="text-xs mt-1 text-gray-500">CRUD Fullstack com Next.js, Tailwind CSS e Express.js</p>
        </div>
      </div>
    </footer>
  );
}
```

---

## 8. Configure o Layout Global

Edite `src/app/layout.js`:

```js
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
        <main className="flex-1">{children}</main>
        <Footer />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: { background: '#363636', color: '#fff' },
            success: { duration: 3000, iconTheme: { primary: '#10b981', secondary: '#fff' } },
            error: { duration: 4000, iconTheme: { primary: '#ef4444', secondary: '#fff' } },
          }}
        />
      </body>
    </html>
  );
}
```

---

## 9. Página Inicial de Teste

Edite `src/app/page.js`:

```js
'use client';
import { useEffect, useState } from 'react';
import { ingredientesService } from '@/services/api';
import toast from 'react-hot-toast';
import Link from 'next/link';

export default function Home() {
  const [ingredientes, setIngredientes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { testarConexao(); }, []);

  const testarConexao = async () => {
    try {
      const response = await ingredientesService.listarTodos();
      const lista = Array.isArray(response) ? response : (response?.data ?? []);
      setIngredientes(lista);
      toast.success(`✅ Conectado! ${lista.length} ingredientes carregados.`);
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
        <div className="mb-8">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">🍳 Bem-vindo ao Sistema de Receitas!</h1>
          <p className="text-xl text-gray-600">Gerencie suas receitas culinárias favoritas de forma simples e organizada</p>
        </div>
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
          </div>
        ) : (
          <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-semibold text-green-800 mb-2">✅ Frontend Conectado com Sucesso!</h2>
            <p className="text-green-700">{ingredientes.length} ingredientes encontrados no banco de dados</p>
          </div>
        )}
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <Link href="/" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow border-2 border-transparent group-hover:border-purple-500">
              <div className="text-4xl mb-3">📚</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Ver Receitas</h3>
              <p className="text-sm text-gray-600">Explore todas as suas receitas cadastradas</p>
            </div>
          </Link>
          <Link href="/receitas/novo" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow border-2 border-transparent group-hover:border-pink-500">
              <div className="text-4xl mb-3">➕</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Nova Receita</h3>
              <p className="text-sm text-gray-600">Adicione uma nova receita ao seu catálogo</p>
            </div>
          </Link>
          <Link href="/ingredientes" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow border-2 border-transparent group-hover:border-purple-500">
              <div className="text-4xl mb-3">🥕</div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Ingredientes</h3>
              <p className="text-sm text-gray-600">Gerencie o catálogo de ingredientes</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
```

---

## 10. Teste o Projeto

1) Inicie o backend:
```bash
cd ../backend
npm run dev
```

2) Inicie o frontend:
```bash
cd ../frontend
npm run dev
```

3) Acesse:
- http://localhost:3000

Você deverá ver a interface inicial, navbar, footer e um toast confirmando a conexão.

---

## 11. Solução de Problemas Comuns

- Tailwind não aplica classes (ex.: `bg-gray-50` aparece como desconhecida):
  - Confirme que `src/app/globals.css` contém apenas `@import "tailwindcss";`.
  - Confirme que `postcss.config.js` está usando `@tailwindcss/postcss`.
  - Reinicie o servidor (`npm run dev`) após alterar configurações.
  - Evite usar `@tailwind base/components/utilities` — isso é do v3.

- Erro ao rodar `npx tailwindcss init -p`:
  - Não use esse comando no v4. Ele foi removido. A configuração está toda no CSS e no PostCSS.

- API não responde / CORS:
  - Verifique se o backend está rodando.
  - Cheque `NEXT_PUBLIC_API_URL` no `.env.local`.

---

## Resumo
- Tutorial compatível com Next.js 16, React 19 e Tailwind CSS 4.
- Configuração mínima: `postcss.config.js` + `@import "tailwindcss"` em `globals.css`.
- Sem `tailwind.config.js` e sem `npx tailwindcss init -p`.
- Páginas e componentes prontos para testar conexão com o backend.

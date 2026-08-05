# Tutorial: Login, Context de autenticação e rota protegida (React 19)

Neste tutorial você vai implementar um fluxo de autenticação moderno: tela de login com **`useActionState`**, Context que guarda usuário e token, e uma rota protegida com **React Router v7** que redireciona para login se o usuário não estiver autenticado.

## Passo 1: Criar o projeto e instalar dependências

```bash
npm create vite@latest tutorial-auth -- --template react
cd tutorial-auth
npm install
npm install react-router-dom
```

## Passo 2: Criar o AuthContext

Crie a pasta `src/contexts` e o arquivo `src/contexts/AuthContext.jsx`:

```jsx
import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    const t = localStorage.getItem('token');
    if (t) {
      setToken(t);
      setUser({ nome: 'Usuário' }); // Em produção: decodifique o JWT ou consulte a API
    }
  }, []);

  const login = async (email /*, senha */) => {
    const fakeToken = 'token-' + Date.now();
    localStorage.setItem('token', fakeToken);
    setToken(fakeToken);
    setUser({ nome: email });
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  const value = { user, token, login, logout, isAuthenticated: !!token };

  return (
    <AuthContext value={value}>
      {children}
    </AuthContext>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth deve ser usado dentro de <AuthProvider>');
  return ctx;
}
```

> Repare no `<AuthContext value={value}>` (nova sintaxe do React 19).

## Passo 3: Botão reutilizável com `useFormStatus`

Crie `src/components/BotaoEnviar.jsx`:

```jsx
import { useFormStatus } from 'react-dom';

function BotaoEnviar({ children }) {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Enviando…' : children}
    </button>
  );
}

export default BotaoEnviar;
```

## Passo 4: Tela de Login com `useActionState`

Crie `src/pages/Login.module.css`:

```css
.wrapper {
  max-width: 400px;
  margin: 40px auto;
  padding: 24px;
  font-family: system-ui, sans-serif;
}

.formGroup {
  margin-bottom: 16px;
}

.label {
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
}

.input {
  display: block;
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.error {
  color: #b00020;
  margin-top: 8px;
}
```

Crie `src/pages/Login.jsx`:

```jsx
import { useActionState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import BotaoEnviar from '../components/BotaoEnviar';
import styles from './Login.module.css';

function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [state, formAction] = useActionState(async (prev, formData) => {
    const email = formData.get('email')?.toString().trim();
    const senha = formData.get('senha')?.toString();

    if (!email || !senha) {
      return { ok: false, erro: 'Preencha email e senha.' };
    }

    try {
      await login(email, senha);
      return { ok: true, erro: null };
    } catch (e) {
      return { ok: false, erro: e.message ?? 'Falha no login.' };
    }
  }, { ok: false, erro: null });

  useEffect(() => {
    if (isAuthenticated) navigate('/dashboard');
  }, [isAuthenticated, navigate]);

  return (
    <div className={styles.wrapper}>
      <h2>Login</h2>
      <form action={formAction}>
        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="email">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            required
            className={styles.input}
          />
        </div>
        <div className={styles.formGroup}>
          <label className={styles.label} htmlFor="senha">Senha</label>
          <input
            id="senha"
            name="senha"
            type="password"
            required
            className={styles.input}
          />
        </div>
        <BotaoEnviar>Entrar</BotaoEnviar>
        {state.erro && <p className={styles.error}>{state.erro}</p>}
      </form>
    </div>
  );
}

export default Login;
```

Destaques:

- `useActionState` cuida do estado de erro e do `pending` (implícito em `useFormStatus`).
- `useEffect` observa `isAuthenticated` e navega depois que o Context é atualizado.

## Passo 5: Rota protegida

Crie `src/components/RotaProtegida.jsx`:

```jsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function RotaProtegida({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default RotaProtegida;
```

## Passo 6: Páginas Home e Dashboard

**`src/pages/Home.jsx`:**

```jsx
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div>
      <h2>Home</h2>
      <p><Link to="/login">Fazer login</Link></p>
    </div>
  );
}

export default Home;
```

**`src/pages/Dashboard.jsx`:**

```jsx
import { useAuth } from '../contexts/AuthContext';

function Dashboard() {
  const { user, logout } = useAuth();
  return (
    <div>
      <h2>Dashboard</h2>
      <p>Olá, {user?.nome}!</p>
      <button onClick={logout}>Sair</button>
    </div>
  );
}

export default Dashboard;
```

## Passo 7: Configurar App com Router e AuthProvider

Substitua `src/App.jsx`:

```jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import RotaProtegida from './components/RotaProtegida';
import Home from './pages/Home';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route
            path="/dashboard"
            element={
              <RotaProtegida>
                <Dashboard />
              </RotaProtegida>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
```

## Passo 8: Executar a aplicação

```bash
npm run dev
```

Testes manuais:

1. Acesse `/dashboard` sem estar logado → redireciona para `/login`.
2. Preencha email/senha e envie → botão "Enviando…", depois vai para `/dashboard`.
3. Recarregue a página → continua logado (token no `localStorage`).
4. Clique em "Sair" → volta a ser anônimo e `/dashboard` volta a redirecionar para `/login`.

## Explicação dos principais elementos

- **`<AuthContext value={value}>`**: sintaxe nova do React 19 (sem `.Provider`).
- **`useActionState`**: elimina `useState` para `pending` e `erro` no formulário.
- **`useFormStatus`**: `BotaoEnviar` fica "Enviando…" automaticamente.
- **`RotaProtegida`**: consulta o Context e usa `<Navigate>` para redirecionar.
- **`useNavigate`**: redireciona para `/dashboard` após login bem-sucedido (poderíamos também usar `<Navigate>` condicional no render).

## Próximos passos

No módulo [10 - Arquivos](../10-arquivos/) você verá como enviar e receber arquivos (upload e download) combinando `<form action>`, `useActionState` e `FormData`.

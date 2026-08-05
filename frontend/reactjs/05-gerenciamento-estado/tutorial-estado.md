# Tutorial: Tema e estado compartilhado com Context (React 19)

Neste tutorial você vai criar um tema (claro/escuro) e um estado de "usuário logado" usando a Context API e o hook `useContext`, com a **nova sintaxe `<Context value={...}>` do React 19**.

## Passo 1: Configurar o projeto

```bash
npm create vite@latest tutorial-estado -- --template react
cd tutorial-estado
npm install
```

## Passo 2: Criar o contexto de tema

Crie o arquivo `src/contexts/ThemeContext.jsx`:

```jsx
import { createContext, useContext, useState } from 'react';

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [tema, setTema] = useState('claro');

  const alternarTema = () => {
    setTema((t) => (t === 'claro' ? 'escuro' : 'claro'));
  };

  return (
    <ThemeContext value={{ tema, alternarTema }}>
      {children}
    </ThemeContext>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme deve ser usado dentro de <ThemeProvider>');
  return ctx;
}
```

> Atenção: `<ThemeContext value={...}>` usa a nova sintaxe do React 19. Não precisa de `.Provider`.

## Passo 3: Criar o contexto de autenticação

Crie o arquivo `src/contexts/AuthContext.jsx`:

```jsx
import { createContext, useContext, useState } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);

  const login = (nome) => setUsuario({ nome });
  const logout = () => setUsuario(null);

  return (
    <AuthContext value={{ usuario, login, logout }}>
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

## Passo 4: Componente Painel com CSS Module e estilos dinâmicos

Crie o arquivo `src/components/Painel.module.css`:

```css
.painel {
  padding: 24px;
  min-height: 200px;
  border-radius: 8px;
}

.separator {
  margin: 16px 0;
  border: none;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}
```

Crie o arquivo `src/components/Painel.jsx`:

```jsx
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import styles from './Painel.module.css';

function Painel() {
  const { tema, alternarTema } = useTheme();
  const { usuario, login, logout } = useAuth();

  /* Cores dinâmicas via style inline; layout fixo no CSS Module. */
  const temaEstilos = {
    backgroundColor: tema === 'claro' ? '#f5f5f5' : '#333',
    color: tema === 'claro' ? '#333' : '#fff',
  };

  return (
    <div className={styles.painel} style={temaEstilos}>
      <h2>Painel</h2>
      <p>Tema atual: {tema}</p>
      <button onClick={alternarTema}>Alternar tema</button>

      <hr className={styles.separator} />

      {usuario ? (
        <>
          <p>Olá, {usuario.nome}!</p>
          <button onClick={logout}>Sair</button>
        </>
      ) : (
        <>
          <p>Você não está logado.</p>
          <button onClick={() => login('Aluno')}>Entrar</button>
        </>
      )}
    </div>
  );
}

export default Painel;
```

## Passo 5: Envolver a aplicação com os Providers

Crie `src/App.module.css`:

```css
.container {
  padding: 24px;
  max-width: 500px;
  margin: 0 auto;
}
```

Edite `src/App.jsx`:

```jsx
import styles from './App.module.css';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import Painel from './components/Painel';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <div className={styles.container}>
          <h1>Estado global com Context (React 19)</h1>
          <Painel />
        </div>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
```

## Passo 6: Executar a aplicação

```bash
npm run dev
```

Teste: alterne o tema (fundo e texto devem mudar) e faça login/logout (mensagens e botões devem atualizar).

## Explicação dos principais elementos

- **`createContext(null)`**: cria o "canal" de dados. Usamos `null` como default e validamos no custom hook.
- **`<ThemeContext value={...}>`**: nova sintaxe do React 19 (equivalente ao antigo `<ThemeContext.Provider value={...}>`).
- **`useTheme`/`useAuth`**: custom hooks que encapsulam o consumo e lançam erro se usados fora do Provider.
- **Dois Providers independentes**: um componente pode consumir ambos sem conflito.
- **Estilos**: layout fixo no CSS Module; cores que dependem de `tema` em `style={}` (valor dinâmico).

## Bônus: usando `use` em vez de `useContext`

Com o novo hook `use` do React 19, você pode ler o mesmo contexto **dentro de um condicional**. Substitua `useContext(AuthContext)` por `use(AuthContext)` para experimentar:

```jsx
import { use } from 'react';
// ...
function Painel({ mostrarUsuario }) {
  // Pode aparecer dentro do if — useContext não permitiria!
  if (mostrarUsuario) {
    const { usuario } = use(AuthContext);
    // ...
  }
}
```

## Próximos passos

No módulo [06 - Rotas](../06-rotas/) você verá como usar o **React Router v7** para criar rotas no frontend e, depois, como proteger rotas com base no estado de autenticação.

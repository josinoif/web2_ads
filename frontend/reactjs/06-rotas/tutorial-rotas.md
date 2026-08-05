# Tutorial: Rotas com React Router v7

Neste tutorial você vai configurar o **React Router v7** em um projeto React 19, criar rotas para Home, Sobre e um detalhe com parâmetro, e usar `Link`, `NavLink` e `useNavigate`.

## Passo 1: Criar o projeto e instalar o React Router

```bash
npm create vite@latest tutorial-rotas -- --template react
cd tutorial-rotas
npm install
npm install react-router-dom
```

> O `react-router-dom` v7 é compatível com React 19.

## Passo 2: Criar os componentes de página

Crie a pasta `src/pages` e os arquivos:

**`src/pages/Home.jsx`:**

```jsx
function Home() {
  return (
    <div>
      <h2>Home</h2>
      <p>Bem-vindo à página inicial.</p>
    </div>
  );
}

export default Home;
```

**`src/pages/Sobre.jsx`:**

```jsx
function Sobre() {
  return (
    <div>
      <h2>Sobre</h2>
      <p>Esta é a página sobre o projeto.</p>
    </div>
  );
}

export default Sobre;
```

**`src/pages/Usuario.jsx`:**

```jsx
import { useParams, useNavigate } from 'react-router-dom';

function Usuario() {
  const { id } = useParams();
  const navigate = useNavigate();

  return (
    <div>
      <h2>Usuário</h2>
      <p>ID do usuário: {id}</p>
      <button onClick={() => navigate('/')}>Voltar para Home</button>
    </div>
  );
}

export default Usuario;
```

**`src/pages/NaoEncontrada.jsx`:**

```jsx
import { Link } from 'react-router-dom';

function NaoEncontrada() {
  return (
    <div>
      <h2>404 — Página não encontrada</h2>
      <Link to="/">Voltar ao início</Link>
    </div>
  );
}

export default NaoEncontrada;
```

## Passo 3: Criar o layout com navegação

Crie `src/components/Layout.module.css`:

```css
.container {
  padding: 24px;
  max-width: 720px;
  margin: 0 auto;
  font-family: system-ui, sans-serif;
}

.nav {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.navLink {
  text-decoration: none;
  color: #333;
}

.active {
  color: #0a7f2e;
  font-weight: 600;
}
```

Crie `src/components/Layout.jsx`:

```jsx
import { NavLink, Outlet } from 'react-router-dom';
import styles from './Layout.module.css';

function Layout() {
  const linkClass = ({ isActive }) =>
    isActive ? `${styles.navLink} ${styles.active}` : styles.navLink;

  return (
    <div className={styles.container}>
      <nav className={styles.nav}>
        <NavLink to="/" end className={linkClass}>Home</NavLink>
        <NavLink to="/sobre" className={linkClass}>Sobre</NavLink>
        <NavLink to="/usuario/1" className={linkClass}>Usuário 1</NavLink>
      </nav>
      <Outlet />
    </div>
  );
}

export default Layout;
```

- **`NavLink`** aplica a classe "active" automaticamente quando a rota casa.
- **`end`** impede que a rota "/" fique ativa em todas as páginas.
- **`Outlet`** é onde o React Router renderiza o componente filho.

## Passo 4: Configurar o Router no App

Substitua `src/App.jsx`:

```jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Sobre from './pages/Sobre';
import Usuario from './pages/Usuario';
import NaoEncontrada from './pages/NaoEncontrada';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="sobre" element={<Sobre />} />
          <Route path="usuario/:id" element={<Usuario />} />
          <Route path="*" element={<NaoEncontrada />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
```

- **`index`**: rota filha que casa com o path do pai (aqui `/`).
- **`usuario/:id`**: `:id` é um parâmetro; em `Usuario` você lê com `useParams().id`.
- **`path="*"`**: captura qualquer URL não definida (404).

## Passo 5: Executar a aplicação

```bash
npm run dev
```

Navegue pelos links, acesse `/usuario/42` direto na URL para ver o parâmetro e clique em "Voltar para Home" para testar o `useNavigate`. Tente acessar `/inexistente` para ver a página 404.

## Explicação dos principais elementos

- **`BrowserRouter`**: usa a API History; a URL no navegador reflete a rota atual.
- **`Routes` / `Route`**: cada `<Route>` associa um `path` a um `element`.
- **`NavLink`**: versão de `Link` que conhece a rota atual (útil para menu).
- **`Outlet`**: dentro de um layout, renderiza o componente da rota filha ativa.
- **`useParams`**: retorna um objeto com os parâmetros da URL.
- **`useNavigate`**: hook para navegar programaticamente (após login, salvar, etc.).

## Próximos passos

No módulo [07 - Layouts](../07-layouts/) você verá como estruturar cabeçalho, menu e área de conteúdo de forma responsiva com CSS Modules.

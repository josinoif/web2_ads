# Tutorial: Layout com header, menu e conteúdo responsivo (React 19)

Neste tutorial você vai criar um layout reutilizável com cabeçalho, navegação e área de conteúdo usando **CSS Modules** e estilos responsivos, em um projeto Vite 8 + React 19.

## Passo 1: Criar o projeto

```bash
npm create vite@latest tutorial-layouts -- --template react
cd tutorial-layouts
npm install
```

## Passo 2: Estrutura de pastas

```bash
mkdir -p src/components src/pages
```

## Passo 3: Componente Header com CSS Module

Crie `src/components/Header.module.css`:

```css
.header {
  padding: 16px 24px;
  background-color: #2c3e50;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.title {
  margin: 0;
  font-size: 1.5rem;
}
```

Crie `src/components/Header.jsx`:

```jsx
import styles from './Header.module.css';

function Header() {
  return (
    <header className={styles.header}>
      <h1 className={styles.title}>Minha Aplicação</h1>
    </header>
  );
}

export default Header;
```

## Passo 4: Componente Menu com CSS Module

Crie `src/components/Menu.module.css`:

```css
.nav {
  padding: 12px 24px;
  background-color: #34495e;
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.link {
  color: white;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
```

Crie `src/components/Menu.jsx`:

```jsx
import styles from './Menu.module.css';

function Menu() {
  const links = [
    { href: '#/', label: 'Início' },
    { href: '#/sobre', label: 'Sobre' },
    { href: '#/contato', label: 'Contato' },
  ];

  return (
    <nav className={styles.nav}>
      {links.map(link => (
        <a key={link.label} href={link.href} className={styles.link}>
          {link.label}
        </a>
      ))}
    </nav>
  );
}

export default Menu;
```

(Em um projeto com React Router, substitua os `<a>` por `<Link to="...">` e use a mesma classe.)

## Passo 5: Componente Layout com CSS Module (e responsivo)

Crie `src/components/Layout.module.css`:

```css
.wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main {
  flex: 1;
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.footer {
  padding: 16px;
  text-align: center;
  background-color: #ecf0f1;
  margin-top: auto;
}

.footerText {
  margin: 0;
}

@media (max-width: 600px) {
  .main {
    padding: 16px;
  }
}
```

Crie `src/components/Layout.jsx`:

```jsx
import styles from './Layout.module.css';
import Header from './Header';
import Menu from './Menu';

function Layout({ children }) {
  return (
    <div className={styles.wrapper}>
      <Header />
      <Menu />
      <main className={styles.main}>
        {children}
      </main>
      <footer className={styles.footer}>
        <p className={styles.footerText}>Curso React — Módulo Layouts</p>
      </footer>
    </div>
  );
}

export default Layout;
```

- **flex: 1** no `main`: a área de conteúdo ocupa o espaço restante entre menu e footer.
- **margin-top: auto** no footer: mantém o rodapé no final da página.
- **Media query**: em telas menores que 600px, o padding do conteúdo reduz.

## Passo 6: Página de conteúdo

Crie `src/pages/Inicio.jsx`:

```jsx
function Inicio() {
  return (
    <div>
      <h2>Bem-vindo</h2>
      <p>Este é o conteúdo principal dentro do layout. O header e o menu permanecem fixos; apenas esta área muda conforme a navegação.</p>
    </div>
  );
}

export default Inicio;
```

## Passo 7: Usar o Layout no App

Substitua `src/App.jsx`:

```jsx
import Layout from './components/Layout';
import Inicio from './pages/Inicio';

function App() {
  return (
    <Layout>
      <Inicio />
    </Layout>
  );
}

export default App;
```

## Passo 8: Executar a aplicação

```bash
npm run dev
```

Redimensione a janela para ver o layout se adaptar (flex-wrap no menu e media query no main).

## Explicação dos principais elementos

- **CSS Modules**: cada componente de layout tem seu `.module.css`; as classes são escopadas e não conflitam com o restante da aplicação.
- **Layout**: componente que recebe `children` e os coloca dentro de `<main>`; header e footer são fixos na estrutura.
- **Flexbox**: `wrapper` em coluna com `main` com `flex: 1` e `footer` com `margin-top: auto` garante o rodapé sempre no final.
- **Responsividade**: a media query no `Layout.module.css` altera apenas o padding do conteúdo em telas pequenas, sem precisar de `!important`.

## Próximos passos

No módulo [08 - Integração com APIs](../08-integracao-apis/) você verá como consumir APIs REST e construir formulários e listagens que se conectam a um backend.

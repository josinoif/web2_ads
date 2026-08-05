# Tutorial: Criando e reutilizando componentes (React 19)

Neste tutorial você vai criar três componentes (`Cabecalho`, `Card` e `Rodape`), usar props e composição, e aplicar **CSS Modules** para estilização seguindo boas práticas do React 19.

## Passo 1: Configurar o projeto

Se ainda não tiver um projeto React, crie um com Vite (React 19):

```bash
npm create vite@latest tutorial-componentes -- --template react
cd tutorial-componentes
npm install
```

## Passo 2: Criar a pasta de componentes

Dentro de `src`, crie a pasta `components`:

```bash
mkdir src/components
```

## Passo 3: Componente Cabecalho com CSS Module

Crie o arquivo `src/components/Cabecalho.module.css`:

```css
.header {
  padding: 16px;
  background-color: #333;
  color: white;
}

.title {
  margin: 0;
  font-size: 1.5rem;
}
```

Crie o arquivo `src/components/Cabecalho.jsx`:

```jsx
import styles from './Cabecalho.module.css';

function Cabecalho({ titulo }) {
  return (
    <header className={styles.header}>
      <h1 className={styles.title}>{titulo}</h1>
    </header>
  );
}

export default Cabecalho;
```

- **CSS Module**: o arquivo `.module.css` gera classes com nomes únicos (ex.: `Cabecalho_header_a1b2c3`), evitando conflitos com outros componentes.
- **styles.header**: em tempo de build, vira o nome real da classe. Use sempre a notação de objeto importado.

## Passo 4: Componente Card com CSS Module

Crie o arquivo `src/components/Card.module.css`:

```css
.card {
  border: 1px solid #ddd;
  padding: 16px;
  margin: 16px 0;
  border-radius: 8px;
}

.cardTitle {
  margin-top: 0;
  margin-bottom: 12px;
  font-size: 1.25rem;
}
```

Crie o arquivo `src/components/Card.jsx`:

```jsx
import styles from './Card.module.css';

function Card({ titulo, children }) {
  return (
    <div className={styles.card}>
      <h2 className={styles.cardTitle}>{titulo}</h2>
      {children}
    </div>
  );
}

export default Card;
```

- **children**: conteúdo passado entre as tags do componente (ex.: `<Card titulo="...">conteúdo aqui</Card>`).

## Passo 5: Componente Rodape com CSS Module

Crie o arquivo `src/components/Rodape.module.css`:

```css
.footer {
  padding: 16px;
  text-align: center;
  background-color: #f0f0f0;
  margin-top: 24px;
}

.footerText {
  margin: 0;
}
```

Crie o arquivo `src/components/Rodape.jsx`:

```jsx
import styles from './Rodape.module.css';

function Rodape() {
  return (
    <footer className={styles.footer}>
      <p className={styles.footerText}>Curso de React — Tutorial de Componentes</p>
    </footer>
  );
}

export default Rodape;
```

## Passo 6: App com CSS Module

Crie o arquivo `src/App.module.css`:

```css
.app {
  min-height: 100vh;
}

.main {
  padding: 24px;
  max-width: 600px;
  margin: 0 auto;
}
```

Abra `src/App.jsx` e substitua pelo seguinte:

```jsx
import styles from './App.module.css';
import Cabecalho from './components/Cabecalho';
import Card from './components/Card';
import Rodape from './components/Rodape';

function App() {
  return (
    <div className={styles.app}>
      <Cabecalho titulo="Minha Aplicação" />
      <main className={styles.main}>
        <Card titulo="Primeiro card">
          <p>Este é o conteúdo do primeiro card. Usamos a prop <code>children</code> para exibi-lo.</p>
        </Card>
        <Card titulo="Segundo card">
          <ul>
            <li>Item 1</li>
            <li>Item 2</li>
          </ul>
        </Card>
      </main>
      <Rodape />
    </div>
  );
}

export default App;
```

- **Cabecalho** recebe a prop `titulo="Minha Aplicação"`.
- **Card** é usado duas vezes com títulos e conteúdos diferentes (passados como `children`).
- **Rodape** não recebe props.

## Passo 7: Bônus — `ref` como prop (React 19)

Se quiser ver a novidade do React 19 em ação, adicione um campo de busca focado automaticamente. Crie `src/components/BuscaFoco.jsx`:

```jsx
import { useEffect, useRef } from 'react';

function CampoBusca({ ref, placeholder }) {
  return <input ref={ref} placeholder={placeholder} />;
}

export default function BuscaFoco() {
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return <CampoBusca ref={inputRef} placeholder="Buscar..." />;
}
```

Repare: **não é necessário `forwardRef`**. No React 19 a `ref` chega como uma prop normal do componente `CampoBusca`.

Você pode incluir `<BuscaFoco />` dentro de um `Card` para testar.

## Passo 8: Executar a aplicação

```bash
npm run dev
```

Você deve ver o cabeçalho, dois cards com conteúdo distinto e o rodapé. Se incluiu o `BuscaFoco`, o campo receberá foco automaticamente ao carregar.

## Explicação dos principais elementos

- **CSS Modules**: cada componente importa seu próprio `.module.css`; as classes são aplicadas com `className={styles.nomeDaClasse}`. Os nomes são transformados em produção para evitar colisões.
- **Props**: `titulo` e `children` são passados do `App` para `Cabecalho` e `Card`; os componentes só exibem o que recebem.
- **Composição**: `App` é composto por `Cabecalho`, `Card` (duas vezes) e `Rodape`.
- **export default**: permite que `App.jsx` importe cada componente com `import Nome from './components/Nome'`.

## Próximos passos

No módulo [03 - Ciclo de vida](../03-ciclo-de-vida/) você verá como os componentes nascem, atualizam e são desmontados, e como isso se relaciona com o `useEffect`.

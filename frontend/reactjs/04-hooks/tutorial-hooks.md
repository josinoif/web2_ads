# Tutorial: Aplicando vários hooks em um componente (React 19)

Neste tutorial você vai construir um pequeno painel que usa **`useState`**, **`useEffect`**, **`useMemo`**, **`useCallback`**, **`useActionState`** e **`useFormStatus`** juntos: um contador, um título dinâmico, uma lista filtrada, uma função memorizada e um formulário com Action.

## Passo 1: Configurar o projeto

Crie um projeto React 19 com Vite:

```bash
npm create vite@latest tutorial-hooks -- --template react
cd tutorial-hooks
npm install
```

## Passo 2: Estilos com CSS Module

Crie o arquivo `src/App.module.css`:

```css
.container {
  padding: 24px;
  max-width: 480px;
  margin: 0 auto;
  font-family: system-ui, sans-serif;
}

.section {
  margin-bottom: 20px;
  padding: 16px;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
}

.row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.erro {
  color: #b00020;
}

.ok {
  color: #0a7f2e;
}
```

## Passo 3: Componente botão com `useFormStatus`

Crie `src/BotaoEnviar.jsx`:

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

> Importe de **`react-dom`**, não de `react`.

## Passo 4: Criar o componente com vários hooks

Substitua o conteúdo de `src/App.jsx` pelo seguinte:

```jsx
import { useState, useEffect, useMemo, useCallback, useActionState } from 'react';
import styles from './App.module.css';
import BotaoEnviar from './BotaoEnviar';

const LISTA = ['React', 'JavaScript', 'TypeScript', 'HTML', 'CSS', 'Node'];

async function enviarComentario(prevState, formData) {
  const texto = formData.get('texto')?.trim();
  if (!texto) {
    return { ok: false, erro: 'Digite um comentário.' };
  }

  await new Promise((resolve) => setTimeout(resolve, 700));
  return { ok: true, erro: null, ultimo: texto };
}

function App() {
  const [count, setCount] = useState(0);
  const [filtro, setFiltro] = useState('');
  const [state, formAction] = useActionState(enviarComentario, {
    ok: false,
    erro: null,
    ultimo: '',
  });

  useEffect(() => {
    document.title = `Contador: ${count}`;
  }, [count]);

  const listaFiltrada = useMemo(() => {
    return LISTA.filter((item) =>
      item.toLowerCase().includes(filtro.toLowerCase())
    );
  }, [filtro]);

  const incrementar = useCallback(() => {
    setCount((c) => c + 1);
  }, []);

  return (
    <div className={styles.container}>
      <h1>Painel com Hooks (React 19)</h1>

      <section className={styles.section}>
        <h2>Contador (useState + useEffect + useCallback)</h2>
        <p>
          Contador: <strong>{count}</strong>
        </p>
        <button onClick={incrementar}>Incrementar</button>
      </section>

      <section className={styles.section}>
        <h2>Filtro (useMemo)</h2>
        <label className={styles.row}>
          Filtrar:
          <input
            type="text"
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
          />
        </label>
        <ul>
          {listaFiltrada.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>

      <section className={styles.section}>
        <h2>Comentário (useActionState + useFormStatus)</h2>
        <form action={formAction}>
          <div className={styles.row}>
            <input name="texto" placeholder="Seu comentário" />
            <BotaoEnviar>Enviar</BotaoEnviar>
          </div>
        </form>
        {state.erro && <p className={styles.erro}>{state.erro}</p>}
        {state.ok && (
          <p className={styles.ok}>Enviado: "{state.ultimo}"</p>
        )}
      </section>
    </div>
  );
}

export default App;
```

## Passo 5: Executar a aplicação

```bash
npm run dev
```

Teste:

1. Altere o contador (o título da aba do navegador deve mudar).
2. Digite no campo de filtro (a lista é filtrada em tempo real).
3. Envie um comentário: o botão vira "Enviando…" e fica desabilitado; ao terminar, aparece a mensagem de sucesso (ou de erro se você enviar vazio).

## Explicação dos principais elementos

- **`useState`**: `count` e `filtro` são estados locais; ao mudar, o componente re-renderiza.
- **`useEffect`**: o efeito roda quando `count` muda; atualiza `document.title`.
- **`useMemo`**: `listaFiltrada` é recalculada só quando `filtro` muda, evitando trabalho desnecessário.
- **`useCallback`**: `incrementar` é uma função estável; em um componente filho `React.memo`, passar essa função evita re-renders.
- **`useActionState`**: gerencia automaticamente o retorno da Action `enviarComentario` e o estado `pending` implícito. Repare que **não** usamos `useState` para controle do botão, nem `onSubmit`/`preventDefault`.
- **`useFormStatus`**: dentro do `BotaoEnviar`, lê `pending` do `<form>` pai sem precisar receber prop.

## Próximos passos

No módulo [05 - Gerenciamento de estado](../05-gerenciamento-estado/) você verá quando usar estado local vs global e como usar a Context API (nova sintaxe `<Context>` do React 19) com `useContext` ou `use`.

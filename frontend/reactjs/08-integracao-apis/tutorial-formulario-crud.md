# Tutorial: Formulário CRUD com Actions (React 19)

Neste tutorial você vai criar uma tela de cadastro que envia dados para uma API REST usando o padrão moderno do React 19: **`useActionState`** + **`<form action>`** + **`useFormStatus`**. Usamos o serviço gratuito [CRUDCrud](https://crudcrud.com) (que gera um endpoint REST temporário) como backend.

## Passo 1: Configurar o projeto

1. Crie um novo projeto React 19 com Vite:

```bash
npm create vite@latest my-form -- --template react
cd my-form
npm install
```

2. Instale o Axios para as requisições HTTP:

```bash
npm install axios
```

## Passo 2: Obter um endpoint no CRUDCrud

Acesse [crudcrud.com](https://crudcrud.com) e copie o **endpoint único** (formato: `https://crudcrud.com/api/XXXX`).

Crie `.env` na raiz com a URL base:

```
VITE_API_URL=https://crudcrud.com/api/COLE_SEU_ENDPOINT_AQUI
```

> As variáveis de ambiente no Vite precisam começar com `VITE_` para serem expostas ao cliente.

## Passo 3: Estilos com CSS Module

Crie `src/CrudForm.module.css`:

```css
.formGroup {
  margin-bottom: 16px;
}

.label {
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
}

.input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.button {
  padding: 8px 16px;
  cursor: pointer;
  background: #0a7f2e;
  color: white;
  border: none;
  border-radius: 4px;
}

.button:disabled {
  background: #999;
  cursor: not-allowed;
}

.success {
  color: #0a7f2e;
  margin-top: 8px;
}

.error {
  color: #b00020;
  margin-top: 8px;
}
```

## Passo 4: Botão reutilizável com `useFormStatus`

Crie `src/BotaoEnviar.jsx`:

```jsx
import { useFormStatus } from 'react-dom';
import styles from './CrudForm.module.css';

function BotaoEnviar({ children = 'Enviar' }) {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending} className={styles.button}>
      {pending ? 'Enviando…' : children}
    </button>
  );
}

export default BotaoEnviar;
```

## Passo 5: Componente do formulário com `useActionState`

Crie `src/CrudForm.jsx`:

```jsx
import { useActionState } from 'react';
import axios from 'axios';
import styles from './CrudForm.module.css';
import BotaoEnviar from './BotaoEnviar';

const API_URL = import.meta.env.VITE_API_URL;

async function cadastrarUsuario(prevState, formData) {
  const nome = formData.get('name')?.toString().trim();
  const email = formData.get('email')?.toString().trim();

  if (!nome || !email) {
    return { status: 'error', mensagem: 'Preencha nome e email.' };
  }

  try {
    const res = await axios.post(`${API_URL}/users`, { name: nome, email });
    if (res.status === 201) {
      return { status: 'success', mensagem: `Usuário "${nome}" criado!` };
    }
    return { status: 'error', mensagem: `Erro (${res.status}) ao criar usuário.` };
  } catch (err) {
    return {
      status: 'error',
      mensagem: err?.message ?? 'Erro ao se conectar à API.',
    };
  }
}

function CrudForm() {
  const [state, formAction] = useActionState(cadastrarUsuario, {
    status: 'idle',
    mensagem: '',
  });

  return (
    <form action={formAction}>
      <div className={styles.formGroup}>
        <label htmlFor="name" className={styles.label}>Nome</label>
        <input
          id="name"
          name="name"
          type="text"
          required
          className={styles.input}
        />
      </div>

      <div className={styles.formGroup}>
        <label htmlFor="email" className={styles.label}>Email</label>
        <input
          id="email"
          name="email"
          type="email"
          required
          className={styles.input}
        />
      </div>

      <BotaoEnviar>Cadastrar</BotaoEnviar>

      {state.status === 'success' && (
        <p className={styles.success}>{state.mensagem}</p>
      )}
      {state.status === 'error' && (
        <p className={styles.error}>{state.mensagem}</p>
      )}
    </form>
  );
}

export default CrudForm;
```

Pontos-chave:

- **`<form action={formAction}>`** dispensa `onSubmit` e `preventDefault`.
- **`formData.get('name')`** lê os campos diretamente — não precisa de estado para cada input.
- **`useActionState`** gera o `formAction` e o `state` devolvido pela função.
- **`useFormStatus`** (dentro do `BotaoEnviar`) sabe automaticamente que o form está submetendo.

## Passo 6: Usar o formulário no App

Crie `src/App.module.css`:

```css
.container {
  max-width: 500px;
  margin: 0 auto;
  padding: 24px;
  font-family: system-ui, sans-serif;
}

.title {
  margin-bottom: 24px;
}
```

Substitua `src/App.jsx`:

```jsx
import styles from './App.module.css';
import CrudForm from './CrudForm';

function App() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Cadastro de Usuários (React 19)</h1>
      <CrudForm />
    </div>
  );
}

export default App;
```

## Passo 7: Executar a aplicação

```bash
npm run dev
```

Preencha o formulário e envie. O botão fica "Enviando…" durante a requisição; ao completar, aparece a mensagem de sucesso. Se o endpoint estiver vazio ou inválido, aparece a mensagem de erro.

## Explicação dos principais elementos

- **`useActionState(action, initial)`**: cria `formAction` e gerencia o estado retornado pela `action`.
- **`<form action={formAction}>`**: no React 19, a prop `action` aceita uma função que recebe `FormData`.
- **`useFormStatus`**: componente filho (`BotaoEnviar`) lê o status de pending sem precisar receber prop.
- **Variáveis de ambiente do Vite**: `import.meta.env.VITE_API_URL` é injetado em tempo de build.

## Próximos passos

No próximo tutorial, [tutorial-listagem-api.md](tutorial-listagem-api.md), você vai criar a listagem que consome os dados gravados por este formulário.

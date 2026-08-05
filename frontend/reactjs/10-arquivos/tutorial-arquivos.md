# Tutorial: Upload e listagem/download de arquivos (React 19)

Neste tutorial você vai criar um formulário de **upload** usando `<form action>` + `useActionState` + `useFormStatus`, e uma área que simula **listagem e download**. Usamos [httpbin.org](https://httpbin.org) como endpoint de eco para testar o envio.

## Passo 1: Configurar o projeto

```bash
npm create vite@latest tutorial-arquivos -- --template react
cd tutorial-arquivos
npm install
npm install axios
```

## Passo 2: Botão reutilizável com `useFormStatus`

Crie a pasta `src/components` e o arquivo `src/components/BotaoEnviar.jsx`:

```jsx
import { useFormStatus } from 'react-dom';

function BotaoEnviar({ children = 'Enviar' }) {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Enviando…' : children}
    </button>
  );
}

export default BotaoEnviar;
```

## Passo 3: Componente de Upload com `useActionState`

Crie `src/components/UploadArquivo.module.css`:

```css
.section {
  margin-bottom: 24px;
}

.preview {
  margin-top: 8px;
  font-size: 14px;
  color: #555;
}

.success {
  color: #0a7f2e;
}

.error {
  color: #b00020;
}
```

Crie `src/components/UploadArquivo.jsx`:

```jsx
import { useActionState } from 'react';
import axios from 'axios';
import BotaoEnviar from './BotaoEnviar';
import styles from './UploadArquivo.module.css';

async function enviarArquivo(prev, formData) {
  const arquivo = formData.get('arquivo');

  if (!arquivo || !(arquivo instanceof File) || arquivo.size === 0) {
    return { status: 'error', mensagem: 'Selecione um arquivo válido.' };
  }

  const MAX_MB = 5;
  if (arquivo.size > MAX_MB * 1024 * 1024) {
    return {
      status: 'error',
      mensagem: `Arquivo maior que ${MAX_MB}MB.`,
    };
  }

  try {
    const fd = new FormData();
    fd.append('arquivo', arquivo);

    const res = await axios.post('https://httpbin.org/post', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    if (res.status >= 200 && res.status < 300) {
      return {
        status: 'success',
        mensagem: `Arquivo "${arquivo.name}" enviado (${formatar(arquivo.size)}).`,
      };
    }
    return { status: 'error', mensagem: `HTTP ${res.status}` };
  } catch (err) {
    return { status: 'error', mensagem: err.message };
  }
}

function formatar(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function UploadArquivo() {
  const [state, formAction] = useActionState(enviarArquivo, {
    status: 'idle',
    mensagem: '',
  });

  return (
    <div className={styles.section}>
      <h3>Upload de arquivo</h3>
      <form action={formAction}>
        <input type="file" name="arquivo" />
        <BotaoEnviar>Enviar</BotaoEnviar>
      </form>
      {state.status === 'success' && (
        <p className={styles.success}>{state.mensagem}</p>
      )}
      {state.status === 'error' && (
        <p className={styles.error}>{state.mensagem}</p>
      )}
    </div>
  );
}

export default UploadArquivo;
```

Destaques:

- O `<input type="file" name="arquivo" />` automaticamente entra no `FormData` passado para a action — **não precisa de `useState` nem `onChange`**.
- A action valida tamanho/tipo e devolve `{ status, mensagem }`.
- O `BotaoEnviar` cuida do `pending` via `useFormStatus`.

## Passo 4: Listagem e download (simulado)

Crie `src/components/ListaArquivos.module.css`:

```css
.list {
  list-style: none;
  padding: 0;
}

.item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 8px;
}

.hint {
  font-size: 12px;
  color: #666;
}
```

Crie `src/components/ListaArquivos.jsx`:

```jsx
import styles from './ListaArquivos.module.css';

const arquivosSimulados = [
  { id: 1, nome: 'documento.pdf', url: '#' },
  { id: 2, nome: 'imagem.png', url: '#' },
];

function ListaArquivos() {
  const handleDownload = (nome, url) => {
    if (url === '#') {
      alert('Em produção, aqui seria o link real de download da API.');
      return;
    }
    const link = document.createElement('a');
    link.href = url;
    link.download = nome;
    link.click();
  };

  return (
    <div>
      <h3>Arquivos disponíveis</h3>
      <ul className={styles.list}>
        {arquivosSimulados.map((arq) => (
          <li key={arq.id} className={styles.item}>
            <span>{arq.nome}</span>
            <button onClick={() => handleDownload(arq.nome, arq.url)}>
              Baixar
            </button>
          </li>
        ))}
      </ul>
      <p className={styles.hint}>
        Para download real, a API deve retornar a URL do arquivo ou o blob; o frontend usa essa URL em um &lt;a download&gt; ou cria um Object URL a partir do blob.
      </p>
    </div>
  );
}

export default ListaArquivos;
```

### Exemplo: download a partir de um blob

Se a API devolver o arquivo como blob, você pode forçar o download assim:

```jsx
async function baixar(url, nomeSugerido) {
  const res = await fetch(url);
  const blob = await res.blob();
  const href = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = href;
  link.download = nomeSugerido;
  link.click();
  URL.revokeObjectURL(href);
}
```

## Passo 5: Integrar no App

Crie `src/App.module.css`:

```css
.container {
  padding: 24px;
  max-width: 560px;
  margin: 0 auto;
  font-family: system-ui, sans-serif;
}

.title {
  margin-bottom: 24px;
}
```

Edite `src/App.jsx`:

```jsx
import styles from './App.module.css';
import UploadArquivo from './components/UploadArquivo';
import ListaArquivos from './components/ListaArquivos';

function App() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Upload e download (React 19)</h1>
      <UploadArquivo />
      <ListaArquivos />
    </div>
  );
}

export default App;
```

## Passo 6: Executar a aplicação

```bash
npm run dev
```

Selecione um arquivo e clique em Enviar. Você verá o botão "Enviando…", depois a mensagem de sucesso com o nome e tamanho do arquivo. A listagem mostra como disparar um download; em produção você usaria a URL retornada pela API.

## Explicação dos principais elementos

- **`FormData`**: montado automaticamente a partir do `<form>`; campos com `name` são incluídos.
- **`<input type="file" name="arquivo">`**: o browser já coloca o `File` no FormData.
- **`useActionState`**: gerencia o retorno da action (`status` + `mensagem`).
- **`useFormStatus`**: o botão é desabilitado e muda o texto sem precisar de prop.
- **Download**: usando um `<a>` temporário com `download` ou `URL.createObjectURL(blob)`.

## Próximos passos

No módulo [11 - Multimídia](../11-multimidia/) você verá como exibir e controlar áudio, vídeo e imagens em React.

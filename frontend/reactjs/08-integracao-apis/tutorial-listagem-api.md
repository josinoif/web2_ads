# Tutorial: Listagem consumindo API REST

Neste tutorial você vai criar uma tela que lê dados de uma API e exibe todos os itens em uma tabela, com estados de **loading**, **erro** e **sucesso**. Continuamos no mesmo projeto do [tutorial anterior](tutorial-formulario-crud.md), usando [CRUDCrud](https://crudcrud.com) como backend.

## Passo 1: Pré-requisitos

Certifique-se de já ter no projeto:

- `VITE_API_URL` em `.env` apontando para seu endpoint CRUDCrud.
- `axios` instalado (`npm install axios`).

## Passo 2: Estilos com CSS Module

Crie o arquivo `src/ItemList.module.css`:

```css
.section {
  margin-top: 32px;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin: 16px 0;
}

.th,
.td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.th {
  background-color: #f2f2f2;
}

.actions {
  display: flex;
  gap: 8px;
}

.refreshBtn {
  margin-bottom: 12px;
}

.status {
  font-style: italic;
}

.error {
  color: #b00020;
}
```

## Passo 3: Criar o componente de listagem

Crie `src/ItemList.jsx`:

```jsx
import { useCallback, useEffect, useState } from 'react';
import axios from 'axios';
import styles from './ItemList.module.css';

const API_URL = import.meta.env.VITE_API_URL;

function ItemList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const carregar = useCallback(async ({ signal } = {}) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await axios.get(`${API_URL}/users`, { signal });
      setItems(data);
    } catch (err) {
      if (axios.isCancel?.(err) || err.name === 'CanceledError') return;
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    carregar({ signal: controller.signal });
    return () => controller.abort();
  }, [carregar]);

  const remover = async (id) => {
    if (!confirm('Remover este usuário?')) return;
    try {
      await axios.delete(`${API_URL}/users/${id}`);
      setItems((atual) => atual.filter((u) => u._id !== id));
    } catch (err) {
      alert(`Erro ao remover: ${err.message}`);
    }
  };

  return (
    <section className={styles.section}>
      <h2>Lista de Usuários</h2>
      <button className={styles.refreshBtn} onClick={() => carregar()}>
        Recarregar
      </button>

      {loading && <p className={styles.status}>Carregando…</p>}
      {error && <p className={styles.error}>Erro ao carregar: {error}</p>}

      {!loading && !error && (
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.th}>ID</th>
              <th className={styles.th}>Nome</th>
              <th className={styles.th}>Email</th>
              <th className={styles.th}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 && (
              <tr>
                <td colSpan={4} className={styles.td}>
                  Nenhum usuário cadastrado ainda.
                </td>
              </tr>
            )}
            {items.map((u) => (
              <tr key={u._id}>
                <td className={styles.td}>{u._id}</td>
                <td className={styles.td}>{u.name}</td>
                <td className={styles.td}>{u.email}</td>
                <td className={styles.td}>
                  <div className={styles.actions}>
                    <button onClick={() => remover(u._id)}>Remover</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}

export default ItemList;
```

Pontos importantes:

- **`AbortController`**: cancela a requisição se o componente desmontar antes da resposta, evitando warnings e atualização em componente desmontado.
- **`useCallback` + `useEffect`**: estabiliza `carregar` e permite reaproveitá-la no botão "Recarregar".
- **Estados explícitos**: `loading`, `error`, `items` cobrem as três fases da requisição.
- **`axios.isCancel` / `CanceledError`**: axios usa `CanceledError` ao abortar; checamos ambos por compatibilidade.

## Passo 4: Usar a listagem no App

Edite `src/App.jsx` para incluir a listagem abaixo do formulário:

```jsx
import styles from './App.module.css';
import CrudForm from './CrudForm';
import ItemList from './ItemList';

function App() {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Cadastro de Usuários (React 19)</h1>
      <CrudForm />
      <ItemList />
    </div>
  );
}

export default App;
```

## Passo 5: Executar a aplicação

```bash
npm run dev
```

Cadastre um usuário pelo formulário, clique em "Recarregar" na listagem e veja o usuário aparecer na tabela. Experimente o botão "Remover".

## Explicação dos principais elementos

- **`useEffect` com cleanup**: o `AbortController` garante que a requisição é cancelada se o componente desmontar.
- **`axios.get` / `axios.delete`**: sintaxe enxuta e tratamento de JSON automático.
- **`items.map` + `key`**: cada linha da tabela tem um `key` estável (`_id` do CRUDCrud).

## Dica: migrar para TanStack Query

Em apps reais, substitua este padrão por **TanStack Query**:

```jsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

function useUsuarios() {
  return useQuery({
    queryKey: ['usuarios'],
    queryFn: async () => (await axios.get(`${API_URL}/users`)).data,
  });
}
```

O hook devolve `data`, `isLoading`, `error` e gerencia cache, refetch e invalidação automaticamente. Em listagens/detalhes que aparecem em várias telas, o ganho é grande.

## Próximos passos

No módulo [09 - Autenticação](../09-autenticacao/) você fará login com `useActionState` e protegerá rotas.

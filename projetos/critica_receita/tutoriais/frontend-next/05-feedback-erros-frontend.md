# Tutorial 5: Feedback e Tratamento de Erros no Frontend (Next.js)

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar sistema de notificações toast com Next.js
- Criar componente de feedback visual
- Centralizar tratamento de erros
- Usar Providers no layout raiz
- Implementar estados de erro gracefully

## 📖 Conteúdo

### 1. Instalando React Toastify

Biblioteca para notificações elegantes:

```bash
npm install react-toastify
```

**Criar Providers Component `app/providers.js`:**

```javascript
'use client';

import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export function Providers({ children }) {
  return (
    <>
      {children}
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={true}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="light"
      />
    </>
  );
}
```

**Usar no Root Layout `app/layout.js`:**

```javascript
import { Providers } from "./providers";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import "./globals.css";

export const metadata = {
  title: "TasteRank - Avalie Restaurantes",
  description: "Descubra e avalie os melhores restaurantes da sua região",
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>
        <Providers>
          <div className="app-container">
            <Navbar />
            <main className="main-content">{children}</main>
            <Footer />
          </div>
        </Providers>
      </body>
    </html>
  );
}

```

### 2. Usando Toast nas Operações

**Substituir `alert()` por `toast()` em Client Components:**

```javascript
'use client'; // Necessário para usar hooks

import { toast } from 'react-toastify';

// Sucesso
toast.success('Avaliação enviada com sucesso!');

// Erro
toast.error('Erro ao enviar avaliação');

// Aviso
toast.warn('Preencha todos os campos obrigatórios');

// Info
toast.info('Carregando dados...');

// Personalizado
toast('Operação concluída', {
  position: 'bottom-center',
  autoClose: 5000,
  className: 'custom-toast'
});
```

**Nota**: O directive `'use client'` é necessário em componentes que usam hooks do React, como `useState`, `useEffect`, ou toast notifications.

### 3. Utilitário Centralizado de Notificações

**Arquivo `src/services/notificacao.js`:**

```javascript
import { toast } from 'react-toastify';

const notificacao = {
  sucesso: (mensagem) => {
    toast.success(mensagem, {
      position: 'top-right',
      autoClose: 3000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    });
  },
  
  erro: (mensagem) => {
    toast.error(mensagem, {
      position: 'top-right',
      autoClose: 5000,
      hideProgressBar: false,
      closeOnClick: true,
      pauseOnHover: true,
      draggable: true,
    });
  },
  
  aviso: (mensagem) => {
    toast.warn(mensagem, {
      position: 'top-right',
      autoClose: 4000,
    });
  },
  
  info: (mensagem) => {
    toast.info(mensagem, {
      position: 'top-right',
      autoClose: 3000,
    });
  },
  
  // Notificação de loading com promise
  comPromise: async (promise, mensagens) => {
    return toast.promise(
      promise,
      {
        pending: mensagens.pendente || 'Processando...',
        success: mensagens.sucesso || 'Operação realizada!',
        error: mensagens.erro || 'Erro na operação'
      }
    );
  }
};

export default notificacao;
```

### 4. Refatorando Tratamento de Erros

Vamos **separar responsabilidades** do arquivo `api.js` do Tutorial 1. Atualmente ele mistura:
1. ❌ Configuração do Axios
2. ❌ Tratamento de erros
3. ❌ Logging
4. ❌ Notificações (novo)

**Melhor abordagem: Separar em módulos especializados**

#### 4.1. Criar Utilitário de Tratamento de Erros

**Arquivo `src/services/errorHandler.js`:**

```javascript
/**
 * Trata erros de API e retorna mensagem amigável
 */
export function tratarErroAPI(error) {
  // Sem resposta do servidor (rede, timeout, etc)
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return 'A requisição demorou muito. Tente novamente.';
    }
    if (error.message === 'Network Error') {
      return 'Erro de conexão. Verifique sua internet.';
    }
    return 'Erro ao conectar ao servidor';
  }
  
  const { status, data } = error.response;
  
  // Erros HTTP comuns
  switch (status) {
    case 400:
      return data?.error || 'Requisição inválida';
    case 401:
      return 'Não autorizado. Faça login novamente.';
    case 403:
      return 'Você não tem permissão para esta ação';
    case 404:
      return data?.error || 'Recurso não encontrado';
    case 409:
      return data?.error || 'Conflito: registro já existe';
    case 422:
      return data?.error || 'Dados inválidos';
    case 429:
      return 'Muitas requisições. Aguarde um momento.';
    case 500:
      return 'Erro interno do servidor';
    case 503:
      return 'Servidor temporariamente indisponível';
    default:
      return data?.error || `Erro ${status}: ${error.message}`;
  }
}

/**
 * Formata erro para retorno padronizado
 */
export function formatarErro(error) {
  return {
    error: tratarErroAPI(error),
    status: error.response?.status,
    errors: error.response?.data?.errors || {}
  };
}
```

#### 4.2. Atualizar `src/services/api.js` - Versão Refatorada

**Agora com responsabilidade única: configurar cliente HTTP**

```javascript
import axios from 'axios';
import { tratarErroAPI, formatarErro } from './errorHandler';
import notificacao from './notificacao';

// Criar instância do Axios
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3000/api',
  timeout: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT) || 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor - adicionar token e logging
api.interceptors.request.use(
  (config) => {
    // Adicionar token se existir (SSR-safe)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    
    // Log em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      console.log(`📤 ${config.method.toUpperCase()} ${config.url}`);
    }
    
    return config;
  },
  (error) => {
    console.error('❌ Erro na requisição:', error);
    return Promise.reject(error);
  }
);

// Response interceptor - tratar erros e notificar
api.interceptors.response.use(
  (response) => {
    // Log em desenvolvimento
    if (process.env.NODE_ENV === 'development') {
      console.log(`📥 ${response.config.method.toUpperCase()} ${response.config.url}`, response.data);
    }
    return response;
  },
  (error) => {
    console.error('❌ Erro na resposta:', error);
    
    // Mostrar notificação automática (exceto se silencioso)
    if (!error.config?.silencioso) {
      const mensagem = tratarErroAPI(error);
      notificacao.erro(mensagem);
    }
    
    // Retornar erro formatado
    return Promise.reject(formatarErro(error));
  }
);

export default api;
```

**O que melhorou:**
- ✅ **Separação de responsabilidades**: Tratamento de erros em módulo separado
- ✅ **Reutilizável**: `errorHandler.js` pode ser usado em qualquer lugar
- ✅ **Testável**: Funções puras são mais fáceis de testar
- ✅ **Manutenível**: Cada arquivo tem uma responsabilidade clara
- ✅ **DRY**: Evita duplicação de lógica de tratamento de erros

### 5. Atualizando Formulário com Notificações

**Modificar `app/restaurantes/[id]/avaliar/page.js`:**

Vamos atualizar o formulário do Tutorial 4 para usar notificações toast ao invés de `alert()`:

```javascript
'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import notificacao from '@/services/notificacao';
import avaliacaoService from '@/services/avaliacaoService';
import restauranteService from '@/services/restauranteService';
import RatingStars from '@/components/RatingStars';
import './page.css';

export default function AvaliacaoForm({ params }) {
  const { id } = use(params); // ID do restaurante
  const router = useRouter();
  
  const [restaurante, setRestaurante] = useState(null);
  const [nota, setNota] = useState(0);
  const [comentario, setComentario] = useState('');
  const [autor, setAutor] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [errors, setErrors] = useState({});
  
  useEffect(() => {
    buscarRestaurante();
  }, [id]);
  
  const buscarRestaurante = async () => {
    try {
      const data = await restauranteService.getById(id);
      setRestaurante(data);
    } catch (err) {
      setError('Restaurante não encontrado');
      notificacao.erro('Restaurante não encontrado');
    }
  };
  
  const validarFormulario = () => {
    const novosErros = {};
    
    if (!autor.trim()) {
      novosErros.autor = 'Nome do autor é obrigatório';
    } else if (autor.trim().length < 2) {
      novosErros.autor = 'Nome deve ter pelo menos 2 caracteres';
    }
    
    if (nota === 0) {
      novosErros.nota = 'Selecione uma nota de 1 a 5';
    }
    
    if (nota < 1 || nota > 5) {
      novosErros.nota = 'A nota deve estar entre 1 e 5';
    }
    
    if (comentario.trim() === '') {
      novosErros.comentario = 'O comentário é obrigatório';
    } else if (comentario.trim().length < 10) {
      novosErros.comentario = 'O comentário deve ter pelo menos 10 caracteres';
    } else if (comentario.length > 500) {
      novosErros.comentario = 'O comentário deve ter no máximo 500 caracteres';
    }
    
    setErrors(novosErros);
    return Object.keys(novosErros).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validarFormulario()) {
      notificacao.aviso('Preencha todos os campos corretamente');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      let restaurante_id = parseInt(id);
      const dados = {
        restaurante_id: restaurante_id,
        nota: parseFloat(nota),
        comentario: comentario.trim(),
        autor: autor.trim()
      };
      
      await avaliacaoService.create(restaurante_id, dados);
      
      // Usar notificação ao invés de alert
      notificacao.sucesso('Avaliação enviada com sucesso!');
      router.push(`/restaurantes/${id}`);
      
    } catch (err) {
      setError(err.error || 'Erro ao enviar avaliação');
      
      // Se o backend retornar erros de validação
      if (err.errors) {
        setErrors(err.errors);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handleNotaChange = (novaNota) => {
    setNota(novaNota);
    
    // Limpar erro quando usuário seleciona nota
    if (errors.nota) {
      setErrors(prev => ({ ...prev, nota: null }));
    }
  };
  
  const handleComentarioChange = (e) => {
    setComentario(e.target.value);
    
    // Limpar erro quando usuário digita
    if (errors.comentario) {
      setErrors(prev => ({ ...prev, comentario: null }));
    }
  };
  
  const handleAutorChange = (e) => {
    setAutor(e.target.value);
    
    // Limpar erro quando usuário digita
    if (errors.autor) {
      setErrors(prev => ({ ...prev, autor: null }));
    }
  };
  
  if (!restaurante) {
    return <div className="loading">Carregando...</div>;
  }
  
  return (
    <div className="avaliacao-form-page">
      <div className="form-header">
        <h1>Avaliar Restaurante</h1>
        <p className="restaurante-nome">📍 {restaurante.nome}</p>
      </div>
      
      <form onSubmit={handleSubmit} className="avaliacao-form">
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="autor">
            Seu Nome <span className="required">*</span>
          </label>
          <input
            type="text"
            id="autor"
            value={autor}
            onChange={handleAutorChange}
            placeholder="Digite seu nome"
            maxLength={100}
            className={errors.autor ? 'error' : ''}
          />
          {errors.autor && (
            <span className="error-message">{errors.autor}</span>
          )}
        </div>
        
        <div className="form-group">
          <label htmlFor="nota">
            Nota <span className="required">*</span>
          </label>
          <div className="nota-selector">
            <RatingStars
              rating={nota}
              size="large"
              interactive={true}
              onChange={handleNotaChange}
            />
            <span className="nota-numero">
              {nota > 0 ? nota.toFixed(1) : 'Clique para selecionar'}
            </span>
          </div>
          {errors.nota && (
            <span className="error-message">{errors.nota}</span>
          )}
        </div>
        
        <div className="form-group">
          <label htmlFor="comentario">
            Comentário <span className="required">*</span>
          </label>
          <textarea
            id="comentario"
            value={comentario}
            onChange={handleComentarioChange}
            placeholder="Compartilhe sua experiência..."
            rows={6}
            maxLength={500}
            className={errors.comentario ? 'error' : ''}
          />
          <div className="textarea-info">
            <span className="char-count">{comentario.length}/500</span>
          </div>
          {errors.comentario && (
            <span className="error-message">{errors.comentario}</span>
          )}
        </div>
        
        <div className="form-actions">
          <button
            type="button"
            onClick={() => router.back()}
            className="btn btn-secondary"
          >
            Voltar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Enviando...' : 'Enviar Avaliação'}
          </button>
        </div>
      </form>
    </div>
  );
}
```

**O que mudou em relação ao Tutorial 16:**
- ✅ Importado `notificacao` do serviço
- ✅ Substituído `alert()` por `notificacao.sucesso()`
- ✅ Adicionado `notificacao.aviso()` na validação
- ✅ Adicionado `notificacao.erro()` ao buscar restaurante
- ✅ Mantida toda a estrutura, validações e lógica do Tutorial 16
- ✅ Os erros de API já serão notificados automaticamente pelo interceptor

### 6. Componente de Confirmação

**Arquivo `src/components/ConfirmDialog.js`:**

```javascript
import './ConfirmDialog.css';

function ConfirmDialog({ 
  titulo, 
  mensagem, 
  onConfirm, 
  onCancel,
  confirmText = 'Confirmar',
  cancelText = 'Cancelar',
  tipo = 'danger' // 'danger', 'warning', 'info'
}) {
  return (
    <div className="confirm-overlay">
      <div className="confirm-dialog">
        <div className={`dialog-header ${tipo}`}>
          <h3>{titulo}</h3>
        </div>
        
        <div className="dialog-body">
          <p>{mensagem}</p>
        </div>
        
        <div className="dialog-footer">
          <button
            onClick={onCancel}
            className="btn btn-secondary"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            className={`btn btn-${tipo}`}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmDialog;
```

**Arquivo src/components/ConfirmDialog.css:**

```css
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.confirm-dialog {
  background: white;
  border-radius: 8px;
  min-width: 400px;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.dialog-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
}

.dialog-header.danger {
  background: #fee;
  color: #c33;
}

.dialog-header.warning {
  background: #ffc;
  color: #860;
}

.dialog-body {
  padding: 1.5rem;
}

.dialog-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}
```

### 7. Usando ConfirmDialog

```javascript
'use client';

import { useState } from 'react';
import ConfirmDialog from '@/components/ConfirmDialog';

function MeuComponente() {
  const [showConfirm, setShowConfirm] = useState(false);
  
  const handleDeleteClick = () => {
    setShowConfirm(true);
  };
  
  const handleConfirmDelete = async () => {
    setShowConfirm(false);
    
    try {
      await minhaService.delete(id);
      notificacao.sucesso('Item excluído!');
    } catch (err) {
      // Erro já tratado pelo interceptor
    }
  };
  
  return (
    <>
      <button onClick={handleDeleteClick}>Excluir</button>
      
      {showConfirm && (
        <ConfirmDialog
          titulo="Confirmar Exclusão"
          mensagem="Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita."
          onConfirm={handleConfirmDelete}
          onCancel={() => setShowConfirm(false)}
          confirmText="Sim, excluir"
          cancelText="Cancelar"
          tipo="danger"
        />
      )}
    </>
  );
}
```

### 8. Componente de Estado Vazio

**Arquivo `src/components/EmptyState.js`:**

```javascript
import './EmptyState.css';

function EmptyState({ 
  icone = '📭', 
  titulo, 
  mensagem, 
  action 
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icone}</div>
      <h3>{titulo}</h3>
      <p>{mensagem}</p>
      {action && (
        <button 
          onClick={action.onClick}
          className="btn btn-primary"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}

export default EmptyState;
```

**Uso:**

```javascript
{avaliacoes.length === 0 && (
  <EmptyState
    icone="⭐"
    titulo="Nenhuma avaliação ainda"
    mensagem="Seja o primeiro a avaliar este restaurante!"
    action={{
      label: 'Avaliar agora',
      onClick: () => router.push(`/restaurantes/${id}/avaliar`)
    }}
  />
)}
```

### 9. Hook Customizado para Notificações

**Arquivo `src/hooks/useNotificacao.js`:**

```javascript
import { useCallback } from 'react';
import notificacao from '@/services/notificacao';

function useNotificacao() {
  const notificarSucesso = useCallback((mensagem) => {
    notificacao.sucesso(mensagem);
  }, []);
  
  const notificarErro = useCallback((erro) => {
    const mensagem = typeof erro === 'string' ? erro : erro.error || 'Erro desconhecido';
    notificacao.erro(mensagem);
  }, []);
  
  const notificarAviso = useCallback((mensagem) => {
    notificacao.aviso(mensagem);
  }, []);
  
  const notificarInfo = useCallback((mensagem) => {
    notificacao.info(mensagem);
  }, []);
  
  return {
    sucesso: notificarSucesso,
    erro: notificarErro,
    aviso: notificarAviso,
    info: notificarInfo
  };
}

export default useNotificacao;
```

**Uso:**

```javascript
'use client';

import useNotificacao from '@/hooks/useNotificacao';

export default function MeuComponente() {
  const notificacao = useNotificacao();
  
  const salvar = async () => {
    try {
      await api.post('/dados', formData);
      notificacao.sucesso('Dados salvos!');
    } catch (err) {
      notificacao.erro(err);
    }
  };
  
  return <button onClick={salvar}>Salvar</button>;
}
```

## 🔨 Atividade Prática

### Exercício 1: Implementar Toast de Loading

Mostre toast enquanto operação está em andamento:

```javascript
const salvar = async () => {
  const toastId = toast.loading('Salvando...');
  
  try {
    await api.post('/dados', data);
    toast.update(toastId, { 
      render: 'Salvo com sucesso!', 
      type: 'success', 
      isLoading: false,
      autoClose: 3000
    });
  } catch (err) {
    toast.update(toastId, { 
      render: 'Erro ao salvar', 
      type: 'error', 
      isLoading: false,
      autoClose: 3000
    });
  }
};
```

### Exercício 2: Criar Sistema de Undo

Permitir desfazer ação por alguns segundos:

```javascript
const excluir = (id) => {
  let cancelado = false;
  
  toast.info(
    <div>
      Item excluído{' '}
      <button onClick={() => { cancelado = true; toast.dismiss(); }}>
        Desfazer
      </button>
    </div>,
    {
      autoClose: 5000,
      onClose: () => {
        if (!cancelado) {
          // Realmente excluir
          api.delete(`/items/${id}`);
        }
      }
    }
  );
};
```

## 💡 Conceitos-Chave

- **Toast notifications** melhoram feedback visual
- **Centralizar tratamento de erros** evita repetição
- **Interceptors Axios** processam todas as respostas
- **Componentes de feedback** (empty states, confirmações)
- **Hooks customizados** encapsulam lógica reutilizável
- Sempre dar feedback visual ao usuário
- Mensagens de erro devem ser claras e acionáveis

## ➡️ Próximos Passos

Com feedback visual implementado, vamos otimizar a **experiência do usuário** com loading states, debounce e cache.

[➡️ Ir para Tutorial 6: Otimização de UX](06-otimizacao-ux.md)

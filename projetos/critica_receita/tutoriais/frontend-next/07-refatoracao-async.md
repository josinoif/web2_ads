# Tutorial 7: Refatoração e Código Assíncrono Avançado

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar retry logic avançado
- Usar AbortController para cancelar requisições
- Implementar request batching
- Criar queue de requisições
- Otimizar código assíncrono
- Aplicar padrões de design para async

## 📖 Conteúdo

### 1. Retry Logic com Exponential Backoff

**Utilitário `src/utils/retry.js`:**

```javascript
/**
 * Tenta executar uma função async com retry automático
 * @param {Function} fn - Função async para executar
 * @param {Object} options - Opções de configuração
 * @returns {Promise} Resultado da função
 */
async function retry(fn, options = {}) {
  const {
    maxAttempts = 3,
    delay = 1000,
    backoff = 2,
    onRetry = null,
    shouldRetry = (error) => true
  } = options;
  
  let lastError;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Verificar se deve tentar novamente
      if (!shouldRetry(error) || attempt === maxAttempts) {
        throw error;
      }
      
      // Calcular delay com exponential backoff
      const waitTime = delay * Math.pow(backoff, attempt - 1);
      
      if (onRetry) {
        onRetry(attempt, maxAttempts, waitTime, error);
      }
      
      console.log(`Tentativa ${attempt}/${maxAttempts} falhou. Tentando novamente em ${waitTime}ms...`);
      
      // Aguardar antes de tentar novamente
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
  
  throw lastError;
}

export default retry;
```

**Usando retry:**

```javascript
import retry from '../utils/retry';
import notificacao from '../utils/notificacao';

async function buscarDadosCriticos() {
  return retry(
    () => api.get('/dados-importantes'),
    {
      maxAttempts: 3,
      delay: 1000,
      backoff: 2,
      onRetry: (attempt, maxAttempts, waitTime) => {
        notificacao.info(`Tentando reconectar... (${attempt}/${maxAttempts})`);
      },
      shouldRetry: (error) => {
        // Só retenta em erros de rede ou timeout
        return error.code === 'ECONNABORTED' || 
               error.message === 'Network Error' ||
               error.response?.status >= 500;
      }
    }
  );
}
```

### 2. AbortController - Cancelar Requisições

**Hook `src/hooks/useFetch.js`:**

```javascript
import { useState, useEffect, useRef } from 'react';

function useFetch(url, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const abortControllerRef = useRef(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Criar novo AbortController
        abortControllerRef.current = new AbortController();
        
        setLoading(true);
        setError(null);
        
        const response = await fetch(url, {
          ...options,
          signal: abortControllerRef.current.signal
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
        
      } catch (err) {
        // Ignorar erros de cancelamento
        if (err.name !== 'AbortError') {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
    
    // Cleanup: cancelar requisição se componente desmontar
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [url]);
  
  const refetch = () => {
    setLoading(true);
  };
  
  return { data, loading, error, refetch };
}

export default useFetch;
```

**Usando AbortController com Axios:**

```javascript
import { useEffect, useRef } from 'react';
import api from '../services/api';

function MeuComponente() {
  const abortControllerRef = useRef();
  
  useEffect(() => {
    const controller = new AbortController();
    abortControllerRef.current = controller;
    
    const fetchData = async () => {
      try {
        const response = await api.get('/dados', {
          signal: controller.signal
        });
        // Processar resposta
      } catch (err) {
        if (err.name === 'CanceledError') {
          console.log('Requisição cancelada');
        }
      }
    };
    
    fetchData();
    
    return () => {
      controller.abort();
    };
  }, []);
  
  return <div>...</div>;
}
```

### 3. Request Batching - Agrupar Requisições

**Utilitário `src/utils/batcher.js`:**

```javascript
class RequestBatcher {
  constructor(batchFn, options = {}) {
    this.batchFn = batchFn;
    this.delay = options.delay || 50;
    this.maxSize = options.maxSize || 10;
    
    this.queue = [];
    this.timer = null;
  }
  
  add(request) {
    return new Promise((resolve, reject) => {
      this.queue.push({ request, resolve, reject });
      
      if (this.queue.length >= this.maxSize) {
        this.flush();
      } else if (!this.timer) {
        this.timer = setTimeout(() => this.flush(), this.delay);
      }
    });
  }
  
  async flush() {
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    
    if (this.queue.length === 0) return;
    
    const batch = this.queue.splice(0, this.maxSize);
    const requests = batch.map(item => item.request);
    
    try {
      const results = await this.batchFn(requests);
      
      batch.forEach((item, index) => {
        item.resolve(results[index]);
      });
    } catch (error) {
      batch.forEach(item => {
        item.reject(error);
      });
    }
  }
}

export default RequestBatcher;
```

**Exemplo de uso:**

```javascript
import RequestBatcher from '../utils/batcher';
import api from './api';

// Criar batcher para buscar múltiplos restaurantes
const restauranteBatcher = new RequestBatcher(
  async (ids) => {
    const response = await api.post('/restaurantes/batch', { ids });
    return response.data;
  },
  { delay: 100, maxSize: 20 }
);

// Usar em vários componentes
async function getRestaurante(id) {
  return restauranteBatcher.add(id);
}

// Múltiplas chamadas próximas serão agrupadas em uma única requisição
Promise.all([
  getRestaurante(1),
  getRestaurante(2),
  getRestaurante(3)
]);
// Resulta em apenas 1 requisição: POST /restaurantes/batch { ids: [1,2,3] }
```

### 4. Queue de Requisições

**Utilitário `src/utils/queue.js`:**

```javascript
class RequestQueue {
  constructor(concurrency = 3) {
    this.concurrency = concurrency;
    this.running = 0;
    this.queue = [];
  }
  
  add(fn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ fn, resolve, reject });
      this.process();
    });
  }
  
  async process() {
    if (this.running >= this.concurrency || this.queue.length === 0) {
      return;
    }
    
    this.running++;
    const { fn, resolve, reject } = this.queue.shift();
    
    try {
      const result = await fn();
      resolve(result);
    } catch (error) {
      reject(error);
    } finally {
      this.running--;
      this.process();
    }
  }
  
  clear() {
    this.queue = [];
  }
  
  get size() {
    return this.queue.length;
  }
}

// Criar instância global
const requestQueue = new RequestQueue(5); // Máximo 5 requisições simultâneas

export default requestQueue;
```

**Usando a queue:**

```javascript
import requestQueue from '../utils/queue';

async function uploadMultipleFiles(files) {
  const uploads = files.map(file => 
    requestQueue.add(() => api.post('/upload', file))
  );
  
  return Promise.all(uploads);
}
```

### 5. Padrão Circuit Breaker

**Utilitário `src/utils/circuitBreaker.js`:**

```javascript
class CircuitBreaker {
  constructor(fn, options = {}) {
    this.fn = fn;
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 60000;
    this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
    
    this.failureCount = 0;
    this.nextAttempt = Date.now();
  }
  
  async execute(...args) {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'HALF_OPEN';
    }
    
    try {
      const result = await this.fn(...args);
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  onSuccess() {
    this.failureCount = 0;
    if (this.state === 'HALF_OPEN') {
      this.state = 'CLOSED';
    }
  }
  
  onFailure() {
    this.failureCount++;
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.resetTimeout;
      console.warn(`Circuit breaker opened. Next attempt in ${this.resetTimeout}ms`);
    }
  }
  
  reset() {
    this.state = 'CLOSED';
    this.failureCount = 0;
  }
}

export default CircuitBreaker;
```

**Uso:**

```javascript
import CircuitBreaker from '../utils/circuitBreaker';
import api from './api';

const getRestaurantesBreaker = new CircuitBreaker(
  () => api.get('/restaurantes'),
  {
    failureThreshold: 3,
    resetTimeout: 30000
  }
);

async function buscarRestaurantes() {
  try {
    return await getRestaurantesBreaker.execute();
  } catch (err) {
    if (err.message === 'Circuit breaker is OPEN') {
      notificacao.erro('Serviço temporariamente indisponível');
      // Retornar dados do cache ou mock
      return getCachedData();
    }
    throw err;
  }
}
```

### 6. Async Iterators para Paginação

**Hook `src/hooks/usePagination.js`:**

```javascript
import { useState, useCallback } from 'react';

function usePagination(fetchFn, pageSize = 10) {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  
  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;
    
    setLoading(true);
    
    try {
      const data = await fetchFn(page, pageSize);
      
      setItems(prev => [...prev, ...data.items]);
      setHasMore(data.hasMore);
      setPage(prev => prev + 1);
    } catch (err) {
      console.error('Erro ao carregar mais itens:', err);
    } finally {
      setLoading(false);
    }
  }, [fetchFn, page, pageSize, loading, hasMore]);
  
  const reset = useCallback(() => {
    setItems([]);
    setPage(1);
    setHasMore(true);
  }, []);
  
  return { items, loading, hasMore, loadMore, reset };
}

export default usePagination;
```

### 7. Memoização de Requisições

**Hook `src/hooks/useMemoizedFetch.js`:**

```javascript
import { useEffect, useRef, useState } from 'react';

function useMemoizedFetch(key, fetcher, dependencies = []) {
  const cache = useRef(new Map());
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const cacheKey = JSON.stringify({ key, dependencies });
    
    if (cache.current.has(cacheKey)) {
      setData(cache.current.get(cacheKey));
      setLoading(false);
      return;
    }
    
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await fetcher();
        
        cache.current.set(cacheKey, result);
        setData(result);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [key, ...dependencies]);
  
  return { data, loading };
}

export default useMemoizedFetch;
```

### 8. Parallel vs Sequential Execution

**Executar em paralelo (mais rápido):**

```javascript
async function buscarDadosParalelo() {
  const [restaurantes, categorias, avaliacoes] = await Promise.all([
    api.get('/restaurantes'),
    api.get('/categorias'),
    api.get('/avaliacoes/recentes')
  ]);
  
  return { restaurantes, categorias, avaliacoes };
}
```

**Executar sequencialmente (quando há dependências):**

```javascript
async function buscarDadosSequencial() {
  const restaurante = await api.get('/restaurantes/1');
  const avaliacoes = await api.get(`/restaurantes/${restaurante.id}/avaliacoes`);
  const media = await api.get(`/restaurantes/${restaurante.id}/media`);
  
  return { restaurante, avaliacoes, media };
}
```

**Promise.allSettled (não falha se uma promise falhar):**

```javascript
async function buscarDadosRobustos() {
  const results = await Promise.allSettled([
    api.get('/restaurantes'),
    api.get('/categorias'),
    api.get('/avaliacoes')
  ]);
  
  const [restaurantes, categorias, avaliacoes] = results.map(result => 
    result.status === 'fulfilled' ? result.value : null
  );
  
  return { restaurantes, categorias, avaliacoes };
}
```

### 9. Race Condition - Prevenção

**Problema comum:**

```javascript
// ❌ ERRADO: Race condition
function SearchComponent() {
  const [busca, setBusca] = useState('');
  const [resultados, setResultados] = useState([]);
  
  useEffect(() => {
    // Se usuário digitar rápido, requisições antigas podem chegar depois
    buscarAPI(busca).then(setResultados);
  }, [busca]);
}
```

**Solução:**

```javascript
// ✅ CORRETO: Ignorar resultados desatualizados
function SearchComponent() {
  const [busca, setBusca] = useState('');
  const [resultados, setResultados] = useState([]);
  
  useEffect(() => {
    let isCurrentRequest = true;
    
    buscarAPI(busca).then(dados => {
      if (isCurrentRequest) {
        setResultados(dados);
      }
    });
    
    return () => {
      isCurrentRequest = false;
    };
  }, [busca]);
}
```

**Ou com AbortController:**

```javascript
useEffect(() => {
  const controller = new AbortController();
  
  buscarAPI(busca, { signal: controller.signal })
    .then(setResultados)
    .catch(err => {
      if (err.name !== 'AbortError') {
        console.error(err);
      }
    });
  
  return () => controller.abort();
}, [busca]);
```

## 🔨 Atividade Prática

### Exercício 1: Implementar Prefetching

Carregar dados antes do usuário precisar:

```javascript
function RestauranteCard({ restaurante }) {
  const prefetchDetalhes = () => {
    // Pré-carregar dados ao passar mouse
    queryClient.prefetchQuery(
      ['restaurante', restaurante.id],
      () => restauranteService.getById(restaurante.id)
    );
  };
  
  return (
    <Link 
      to={`/restaurantes/${restaurante.id}`}
      onMouseEnter={prefetchDetalhes}
    >
      {restaurante.nome}
    </Link>
  );
}
```

### Exercício 2: Implementar Request Deduplication

Evitar requisições duplicadas simultâneas:

```javascript
const requestCache = new Map();

async function fetchWithDedup(key, fetcher) {
  if (requestCache.has(key)) {
    return requestCache.get(key);
  }
  
  const promise = fetcher().finally(() => {
    requestCache.delete(key);
  });
  
  requestCache.set(key, promise);
  return promise;
}
```

## 💡 Conceitos-Chave

- **Retry logic** aumenta resiliência
- **AbortController** previne memory leaks
- **Request batching** reduz overhead
- **Circuit breaker** protege serviços instáveis
- **Promise.all** para operações paralelas
- **Race conditions** devem ser prevenidas
- Sempre limpar recursos em cleanup

## ➡️ Próximos Passos

Para finalizar, vamos fazer uma **revisão completa de boas práticas** e preparar o projeto para produção!

[➡️ Ir para Tutorial 20: Revisão e Boas Práticas](20-revisao-boas-praticas.md)

# Tutorial 6: Otimização de UX (Next.js)

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Usar Image do Next.js para otimização
- Implementar Link com prefetch automático
- Usar dynamic() para lazy loading
- Criar skeleton screens
- Otimizar renderizações com Next.js

## 📖 Conteúdo

### 1. Otimizar Imagens com Next.js Image

**Melhorar `src/components/RestauranteCard.js` adicionando imagem:**

Se seu restaurante tem uma imagem, use o componente `Image` do Next.js para otimização automática:

```javascript
'use client';

import Link from 'next/link';
import Image from 'next/image';
import './RestauranteCard.css';

export default function RestauranteCard({ restaurante }) {
  const { id, nome, categoria, endereco, avaliacao_media, imagem } = restaurante;
  
  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    
    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(<span key={i} className="star full">★</span>);
      } else if (i === fullStars && hasHalfStar) {
        stars.push(<span key={i} className="star half">★</span>);
      } else {
        stars.push(<span key={i} className="star empty">☆</span>);
      }
    }
    
    return stars;
  };
  
  return (
    <Link href={`/restaurantes/${id}`} className="restaurante-card">
      {imagem && (
        <div className="card-image">
          <Image
            src={imagem}
            alt={nome}
            width={300}
            height={200}
            priority={false}
            placeholder="blur"
            blurDataURL="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 200'%3E%3Crect fill='%23f0f0f0'/%3E%3C/svg%3E"
          />
        </div>
      )}
      
      <div className="card-header">
        <h3>{nome}</h3>
        <span className="categoria-badge">{categoria}</span>
      </div>
      
      <div className="card-body">
        {endereco && (
          <p className="endereco">📍 {endereco}</p>
        )}
        
        <div className="rating">
          <div className="stars">
            {renderStars(parseFloat(avaliacao_media) || 0)}
          </div>
          <span className="rating-number">
            {parseFloat(avaliacao_media).toFixed(1)}
          </span>
        </div>
      </div>
    </Link>
  );
}
```

**src/components/RestauranteCard.css:**

```css

/* adicionar as classes abaixo  */

.card-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
  border-radius: 8px 8px 0 0;
  position: relative;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

**Benefícios do Image do Next.js:**
- ✅ Lazy loading automático
- ✅ Redimensionamento responsivo
- ✅ Suporte a WebP e formatos modernos
- ✅ Blur placeholder enquanto carrega
- ✅ Evita CLS (Cumulative Layout Shift)

### 2. Link do Next.js com Prefetch Automático

**Usar `<Link>` do Next.js em listas:**

O `RestauranteCard` já usa `Link` corretamente! Isso garante:

```javascript
// ✅ Correto - Link já está em uso no RestauranteCard
<Link href={`/restaurantes/${id}`} className="restaurante-card">
  {/* conteúdo do card */}
</Link>
```

**Benefícios do Link do Next.js:**
- ✅ Prefetch automático em produção
- ✅ Navegação sem page reload
- ✅ Carregamento da página em background
- ✅ Melhor percepção de velocidade

**Quando desativar prefetch:**

```javascript
// Desativar prefetch para links que não são críticos
<Link href="/raramente-acessado" prefetch={false}>
  Link
</Link>
```

### 3. Lazy Loading com dynamic() para Componentes Pesados

**Carregar componentes sob demanda:**

Exemplo: Não carrega `AvaliacaoForm` até o usuário clicar em "Avaliar":

```javascript
'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { use } from 'react';

// Componente carregado apenas quando necessário
const AvaliacaoForm = dynamic(
  () => import('@/components/AvaliacaoForm'),
  {
    loading: () => <p>Carregando formulário...</p>,
    ssr: false
  }
);

export default function RestauranteDetalhe({ params }) {
  const { id } = use(params);
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  
  return (
    <div>
      <h1>Detalhes do Restaurante</h1>
      
      <button onClick={() => setMostrarFormulario(true)}>
        Avaliar Restaurante
      </button>
      
      {mostrarFormulario && <AvaliacaoForm restauranteId={id} />}
    </div>
  );
}
```

**Quando usar dynamic():**
- ✅ Componentes em modais ou abas (carregam apenas se necessário)
- ✅ Editores de código/texto pesados
- ✅ Gráficos e bibliotecas grandes
- ✅ Features opcionais que nem todo usuário usa

**⚠️ Não use para:**
- ❌ Componentes críticos acima da fold
- ❌ Componentes que precisam de SSR (usar com `ssr: true`)

### 4. Skeleton Screens com Server Components

**Componente `components/SkeletonCard.js`:**

```javascript
import './SkeletonCard.css';

export function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton skeleton-title"></div>
      <div className="skeleton skeleton-badge"></div>
      <div className="skeleton skeleton-text"></div>
      <div className="skeleton skeleton-rating"></div>
    </div>
  );
}
```

**Usando Suspense para carregamento gracioso:**

```javascript
import { Suspense } from 'react';
import { SkeletonCard } from '@/components/SkeletonCard';
import RestaurantesList from '@/components/RestaurantesList';

export default function Page() {
  return (
    <div className="restaurantes-grid">
      <Suspense fallback={<SkeletonCard />}>
        <RestaurantesList />
      </Suspense>
    </div>
  );
}
```

**Server Component RestaurantesList:**

```javascript
// Componente SERVIDOR (sem 'use client')
export default async function RestaurantesList() {
  const restaurantes = await fetch(
    `${process.env.API_URL}/restaurantes`,
    { next: { revalidate: 60 } } // ISR - Revalidar a cada 60s
  ).then(res => res.json());
  
  return restaurantes.map(r => (
    <div key={r.id} className="card">
      {/* renderizar restaurante */}
    </div>
  ));
}
```

### 5. Hook de Debounce para Busca Otimizada

**Arquivo `src/hooks/useDebounce.js`:**

Reduz requisições desnecessárias enquanto usuário digita:

```javascript
import { useState, useEffect } from 'react';

function useDebounce(value, delay = 500) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => clearTimeout(timer);
  }, [value, delay]);
  
  return debouncedValue;
}

export default useDebounce;
```

**Usando em SearchBar:**

Já está implementado no Tutorial 14! O `SearchBar` do `RestaurantesPage` usa debounce para filtrar:

```javascript
// Em src/app/restaurantes/page.js (Tutorial 14)
const handleSearch = (termo) => {
  setBusca(termo);
  setPage(1);
};

// Após mudança, useEffect dispara busca com filtros
useEffect(() => {
  buscarRestaurantes();
}, [busca, categoriaFiltro, ordenacao, page]);
```

**Melhor abordagem: Adicionar debounce explícito:**

```javascript
'use client';

import { useState, useEffect } from 'react';
import useDebounce from '@/hooks/useDebounce';
import restauranteService from '@/services/restauranteService';

export default function SearchBar({ onSearch }) {
  const [busca, setBusca] = useState('');
  const buscaDebounced = useDebounce(busca, 500);
  
  useEffect(() => {
    if (buscaDebounced) {
      onSearch(buscaDebounced);
    }
  }, [buscaDebounced, onSearch]);
  
  return (
    <input
      type="text"
      value={busca}
      onChange={(e) => setBusca(e.target.value)}
      placeholder="Buscar restaurantes..."
    />
  );
}
```

**Benefício:**
- ✅ Se usuário digita "pizza", não faz 4 requisições (p-i-z-z-a)
- ✅ Só faz requisição 500ms após parar de digitar
- ✅ Reduz carga no servidor e melhora UX

### 6. Otimização com React.memo

**Evitar re-renders desnecessários:**

```javascript
'use client';

import { memo } from 'react';

const RestauranteCard = memo(function RestauranteCard({ restaurante }) {
  return (
    <div className="card">
      <h3>{restaurante.nome}</h3>
      <p>{restaurante.categoria}</p>
      <span className="rating">{restaurante.avaliacao_media}</span>
    </div>
  );
});

export default RestauranteCard;
```

**Com função de comparação customizada:**

```javascript
const RestauranteCard = memo(
  ({ restaurante }) => (
    <div className="card">
      <h3>{restaurante.nome}</h3>
    </div>
  ),
  (prevProps, nextProps) => {
    // Retornar true se props são iguais (não re-render)
    return prevProps.restaurante.id === nextProps.restaurante.id &&
           prevProps.restaurante.avaliacao_media === nextProps.restaurante.avaliacao_media;
  }
);
```

### 7. Indicador de Progresso Linear

**Componente `components/LinearProgress.js`:**

```javascript
'use client';

import './LinearProgress.css';

export default function LinearProgress({ value, max = 100, color = 'primary' }) {
  const percentage = (value / max) * 100;
  
  return (
    <div className="linear-progress">
      <div 
        className={`progress-bar ${color}`}
        style={{ width: `${percentage}%` }}
      ></div>
    </div>
  );
}
```

**CSS:**

```css
.linear-progress {
  width: 100%;
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 2px;
}

.progress-bar.primary {
  background: linear-gradient(90deg, #3498db, #2980b9);
}

.progress-bar.success {
  background: linear-gradient(90deg, #2ecc71, #27ae60);
}

.progress-bar.warning {
  background: linear-gradient(90deg, #f39c12, #e67e22);
}

.progress-bar.danger {
  background: linear-gradient(90deg, #e74c3c, #c0392b);
}
```

### 7. Cache Simples de Requisições com Hook

**Hook `src/hooks/useCache.js`:**

Evita fazer a mesma requisição múltiplas vezes em um curto período:

```javascript
import { useState, useEffect, useRef } from 'react';

function useCache(key, fetcher, ttl = 60000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const cache = useRef(new Map());
  
  useEffect(() => {
    const fetchData = async () => {
      // Verificar cache
      const cached = cache.current.get(key);
      if (cached && Date.now() - cached.timestamp < ttl) {
        setData(cached.data);
        setLoading(false);
        return;
      }
      
      // Buscar dados
      try {
        setLoading(true);
        const result = await fetcher();
        
        // Salvar no cache
        cache.current.set(key, {
          data: result,
          timestamp: Date.now()
        });
        
        setData(result);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [key, fetcher, ttl]);
  
  const invalidate = () => {
    cache.current.delete(key);
  };
  
  return { data, loading, error, invalidate };
}

export default useCache;
```

**Exemplo de uso:**

```javascript
'use client';

import useCache from '@/hooks/useCache';
import restauranteService from '@/services/restauranteService';

export default function RestauranteDetail({ id }) {
  // Cache de 30 segundos
  const { data: restaurante, loading, error } = useCache(
    `restaurante-${id}`,
    () => restauranteService.getById(id),
    30000 // TTL: 30 segundos
  );
  
  if (loading) return <div>Carregando...</div>;
  if (error) return <div>Erro ao carregar</div>;
  
  return (
    <div>
      <h1>{restaurante.nome}</h1>
      {/* ... */}
    </div>
  );
}
```

**Benefício:**
- ✅ Se mesmo restaurante é acessado 3 vezes em 30s, API é chamada apenas 1 vez
- ✅ Melhora performance e reduz carga do servidor

### 8. Componente LoadingButton para Feedback Visual

Componente reutilizável que mostra estado de carregamento:

**Componente `src/components/LoadingButton.js`:**

```javascript
import './LoadingButton.css';

function LoadingButton({ 
  loading, 
  children, 
  onClick, 
  disabled,
  className = '',
  ...props 
}) {
  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className={`loading-button ${className} ${loading ? 'loading' : ''}`}
      {...props}
    >
      {loading && (
        <span className="spinner-small"></span>
      )}
      <span className={loading ? 'button-text-hidden' : ''}>
        {children}
      </span>
    </button>
  );
}

export default LoadingButton;
```

**CSS `src/components/LoadingButton.css`:**

```css
.loading-button {
  position: relative;
  min-width: 120px;
  transition: opacity 0.2s ease;
}

.loading-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-button.loading {
  pointer-events: none;
}

.spinner-small {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.button-text-hidden {
  opacity: 0;
}

@keyframes spin {
  to { transform: translate(-50%, -50%) rotate(360deg); }
}
```

**Uso no formulário:**

Já está implementado! O botão do formulário de avaliação (Tutorial 4/5) mostra "Enviando..." durante o carregamento:

```javascript
<button 
  type="submit" 
  disabled={loading}
  className="btn btn-primary"
>
  {loading ? 'Enviando...' : 'Enviar Avaliação'}
</button>
```

**Para usar o componente LoadingButton:**

```javascript
import LoadingButton from '@/components/LoadingButton';

export default function MeuComponente() {
  const [loading, setLoading] = useState(false);
  
  const handleSalvar = async () => {
    setLoading(true);
    try {
      await api.post('/dados', formData);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <LoadingButton 
      loading={loading} 
      onClick={handleSalvar}
      className="btn btn-primary"
    >
      Salvar
    </LoadingButton>
  );
}
```

## 🔨 Atividade Prática

### Exercício 1: Implementar Busca com Sugestões

Mostre sugestões enquanto usuário digita:

```javascript
const [sugestoes, setSugestoes] = useState([]);
const buscaDebounced = useDebounce(busca, 300);

useEffect(() => {
  if (buscaDebounced.length >= 3) {
    buscarSugestoes(buscaDebounced);
  }
}, [buscaDebounced]);
```

### Exercício 2: Adicionar Animações de Transição

Use Framer Motion para animações suaves:

```bash
npm install framer-motion
```

```javascript
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  {/* Conteúdo */}
</motion.div>
```

## 💡 Conceitos-Chave

- **Skeleton screens** melhoram percepção de velocidade
- **Debounce** reduz requisições desnecessárias
- **Validação em tempo real** melhora feedback
- **Infinite scroll** melhora navegação em listas grandes
- **React.memo** otimiza re-renders
- **Cache** reduz chamadas à API
- Sempre priorizar **percepção de performance**

## ➡️ Próximos Passos

Com UX otimizada, vamos refatorar o código para usar **async/await** de forma mais robusta e implementar padrões avançados.

[➡️ Ir para Tutorial 7: Refatoração e Código Assíncrono](07-refatoracao-async.md)

# Tutorial 14: Consumo da API e Listagem

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Usar hooks useState e useEffect no Next.js
- Consumir API REST no Next.js
- Implementar loading states
- Tratar erros de requisição
- Criar componentes de listagem
- Implementar busca e filtros com URL params

## 📖 Conteúdo

### 1. Hooks Essenciais

**useState** - Gerenciar estado local
**useEffect** - Executar efeitos colaterais (requisições, etc)

```javascript
'use client'; // Client Component (necessário para hooks)

import { useState, useEffect } from 'react';

function MeuComponente() {
  const [dados, setDados] = useState([]);          // Estado
  const [loading, setLoading] = useState(true);    // Loading
  const [error, setError] = useState(null);        // Erro
  
  useEffect(() => {
    // Executado após renderização
    buscarDados();
  }, []); // [] = executa apenas uma vez
  
  const buscarDados = async () => {
    // Lógica de busca
  };
  
  return <div>...</div>;
}

export default MeuComponente;
```

**⚠️ Importante:** Componentes com hooks precisam ser marcados com `'use client'`

### 2. Página de Listagem de Restaurantes

**Arquivo `src/app/restaurantes/page.js`:**

```javascript
'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import restauranteService from '@/services/restauranteService';
import RestauranteCard from '@/components/RestauranteCard';
import SearchBar from '@/components/SearchBar';
import FilterBar from '@/components/FilterBar';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import Pagination from '@/components/Pagination';
import './restaurantes.css';

export default function RestaurantesPage() {
  const searchParams = useSearchParams();
  
  const [restaurantes, setRestaurantes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Estados de filtros (sincronizados com URL)
  const [busca, setBusca] = useState(searchParams.get('busca') || '');
  const [categoriaFiltro, setCategoriaFiltro] = useState(searchParams.get('categoria') || '');
  const [ordenacao, setOrdenacao] = useState(searchParams.get('ordenacao') || 'avaliacao_media');
  const [page, setPage] = useState(parseInt(searchParams.get('page')) || 1);
  
  const [totalPages, setTotalPages] = useState(1);
  
  useEffect(() => {
    buscarRestaurantes();
  }, [busca, categoriaFiltro, ordenacao, page]);
  
  const buscarRestaurantes = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {
        page,
        limit: 12,
        ...(busca && { busca }),
        ...(categoriaFiltro && { categoria: categoriaFiltro }),
        ordenar: ordenacao,
        direcao: 'DESC'
      };
      
      const data = await restauranteService.getAll(params);
      
      setRestaurantes(data.restaurantes || []);
      setTotalPages(data.totalPaginas || 1);
      
      // Atualizar URL sem recarregar
      const urlParams = new URLSearchParams();
      if (busca) urlParams.set('busca', busca);
      if (categoriaFiltro) urlParams.set('categoria', categoriaFiltro);
      if (ordenacao) urlParams.set('ordenacao', ordenacao);
      if (page > 1) urlParams.set('page', page);
      
      window.history.replaceState(null, '', `?${urlParams.toString()}`);
      
    } catch (err) {
      setError(err.error || 'Erro ao carregar restaurantes');
      console.error('Erro ao buscar restaurantes:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSearch = (termo) => {
    setBusca(termo);
    setPage(1); // Resetar para primeira página
  };
  
  const handleCategoriaChange = (categoria) => {
    setCategoriaFiltro(categoria);
    setPage(1);
  };
  
  const handleOrdenacaoChange = (ordem) => {
    setOrdenacao(ordem);
  };
  
  if (loading && page === 1) {
    return <Loading />;
  }
  
  if (error) {
    return (
      <ErrorMessage 
        message={error} 
        onRetry={buscarRestaurantes} 
      />
    );
  }
  
  return (
    <div className="restaurantes-list-page">
      <header className="page-header">
        <h1>Restaurantes</h1>
        <p>Encontre os melhores lugares para comer</p>
      </header>
      
      <div className="filters-section">
        <SearchBar 
          value={busca}
          onChange={handleSearch}
          placeholder="Buscar restaurantes..."
        />
        
        <FilterBar
          categoria={categoriaFiltro}
          onCategoriaChange={handleCategoriaChange}
          ordenacao={ordenacao}
          onOrdenacaoChange={handleOrdenacaoChange}
        />
      </div>
      
      {restaurantes.length === 0 ? (
        <div className="no-results">
          <h3>Nenhum restaurante encontrado</h3>
          <p>Tente ajustar os filtros de busca</p>
        </div>
      ) : (
        <>
          <div className="restaurantes-grid">
            {restaurantes.map(restaurante => (
              <RestauranteCard 
                key={restaurante.id} 
                restaurante={restaurante} 
              />
            ))}
          </div>
          
          {totalPages > 1 && (
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              onPageChange={setPage}
            />
          )}
        </>
      )}
    </div>
  );
}
```

### 3. Componente Card de Restaurante

**Arquivo `src/components/RestauranteCard.js`:**

```javascript
'use client';

import Link from 'next/link';
import './RestauranteCard.css';

export default function RestauranteCard({ restaurante }) {
  const { id, nome, categoria, endereco, avaliacao_media } = restaurante;
  
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

**CSS `src/components/RestauranteCard.css`:**

```css
.restaurante-card {
  display: block;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  text-decoration: none;
  color: inherit;
  cursor: pointer;
}

.restaurante-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.card-header h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.2rem;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.categoria-badge {
  display: inline-block;
  background: #3498db;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
}

.card-body {
  padding: 1rem;
}

.endereco {
  margin: 0 0 1rem 0;
  color: #666;
  font-size: 0.9rem;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stars {
  display: flex;
  gap: 0.25rem;
  font-size: 1.2rem;
}

.star {
  color: #ffc107;
}

.star.empty {
  color: #ddd;
}

.rating-number {
  font-weight: bold;
  color: #333;
  min-width: 40px;
}
```

### 4. Componente de Busca

**Arquivo `src/components/SearchBar.js`:**

```javascript
'use client';

import { useState } from 'react';
import './SearchBar.css';

export default function SearchBar({ value, onChange, placeholder = 'Buscar...' }) {
  const [inputValue, setInputValue] = useState(value);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    onChange(inputValue);
  };
  
  const handleClear = () => {
    setInputValue('');
    onChange('');
  };
  
  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder={placeholder}
        className="search-input"
      />
      
      {inputValue && (
        <button 
          type="button" 
          onClick={handleClear}
          className="clear-button"
        >
          ✕
        </button>
      )}
      
      <button type="submit" className="search-button">
        🔍 Buscar
      </button>
    </form>
  );
}
```

**CSS `src/components/SearchBar.css`:**

```css
.search-bar {
  display: flex;
  gap: 0.5rem;
  background: white;
  padding: 0.75rem;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
  transition: border-color 0.3s;
}

.search-bar:focus-within {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0.5rem;
  font-size: 1rem;
  font-family: inherit;
}

.clear-button {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.clear-button:hover {
  background: #c0392b;
}

.search-button {
  background: #27ae60;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.3s;
}

.search-button:hover {
  background: #229954;
}
```

### 5. Componente de Filtros

**Arquivo `src/components/FilterBar.js`:**

```javascript
'use client';

import './FilterBar.css';

export default function FilterBar({ 
  categoria, 
  onCategoriaChange, 
  ordenacao, 
  onOrdenacaoChange 
}) {
  const categorias = [
    'Todas',
    'Italiana',
    'Japonesa',
    'Brasileira',
    'Mexicana',
    'Árabe',
    'Hamburgueria',
    'Pizzaria',
    'Vegetariana',
    'Outra'
  ];
  
  const opcoesOrdenacao = [
    { value: 'avaliacao_media', label: 'Melhor Avaliados' },
    { value: 'nome', label: 'Nome (A-Z)' },
    { value: 'created_at', label: 'Mais Recentes' }
  ];
  
  return (
    <div className="filter-bar">
      <div className="filter-group">
        <label>Categoria:</label>
        <select 
          value={categoria}
          onChange={(e) => onCategoriaChange(e.target.value === 'Todas' ? '' : e.target.value)}
          className="filter-select"
        >
          {categorias.map(cat => (
            <option key={cat} value={cat === 'Todas' ? '' : cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>
      
      <div className="filter-group">
        <label>Ordenar por:</label>
        <select
          value={ordenacao}
          onChange={(e) => onOrdenacaoChange(e.target.value)}
          className="filter-select"
        >
          {opcoesOrdenacao.map(opcao => (
            <option key={opcao.value} value={opcao.value}>
              {opcao.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
```

**CSS `src/components/FilterBar.css`:**

```css
.filter-bar {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: bold;
  color: #333;
  font-size: 0.95rem;
}

.filter-select {
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.3s;
  min-width: 150px;
}

.filter-select:hover {
  border-color: #3498db;
}

.filter-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

@media (max-width: 768px) {
  .filter-bar {
    flex-direction: column;
    gap: 1rem;
  }

  .filter-select {
    width: 100%;
  }
}
```

### 6. Componente de Loading

**Arquivo `src/components/Loading.js`:**

```javascript
import './Loading.css';

export default function Loading({ message = 'Carregando...' }) {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  );
}
```

**CSS `src/components/Loading.css`:**

```css
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 1rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### 7. Componente de Erro

**Arquivo `src/components/ErrorMessage.js`:**

```javascript
'use client';

import './ErrorMessage.css';

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-container">
      <div className="error-icon">❌</div>
      <h3>Ops! Algo deu errado</h3>
      <p>{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="retry-button">
          🔄 Tentar Novamente
        </button>
      )}
    </div>
  );
}
```

**CSS `src/components/ErrorMessage.css`:**

```css
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 1rem;
  background: #fff3f3;
  border-radius: 8px;
  padding: 2rem;
  margin: 2rem 0;
}

.error-icon {
  font-size: 4rem;
}

.error-container h3 {
  margin: 0;
  color: #e74c3c;
  font-size: 1.5rem;
}

.error-container p {
  margin: 0.5rem 0;
  color: #666;
  text-align: center;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.3s;
}

.retry-button:hover {
  background: #2980b9;
}
```

### 8. Componente de Paginação

**Arquivo `src/components/Pagination.js`:**

```javascript
'use client';

import './Pagination.css';

export default function Pagination({ currentPage, totalPages, onPageChange }) {
  const pages = [];
  
  // Lógica para mostrar páginas (ex: 1 ... 4 5 6 ... 10)
  const maxVisible = 5;
  let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
  let endPage = Math.min(totalPages, startPage + maxVisible - 1);
  
  if (endPage - startPage < maxVisible - 1) {
    startPage = Math.max(1, endPage - maxVisible + 1);
  }
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  
  return (
    <div className="pagination">
      <button
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1}
        className="page-button"
      >
        ← Anterior
      </button>
      
      {startPage > 1 && (
        <>
          <button onClick={() => onPageChange(1)} className="page-number">
            1
          </button>
          {startPage > 2 && <span className="ellipsis">...</span>}
        </>
      )}
      
      {pages.map(page => (
        <button
          key={page}
          onClick={() => onPageChange(page)}
          className={`page-number ${currentPage === page ? 'active' : ''}`}
        >
          {page}
        </button>
      ))}
      
      {endPage < totalPages && (
        <>
          {endPage < totalPages - 1 && <span className="ellipsis">...</span>}
          <button onClick={() => onPageChange(totalPages)} className="page-number">
            {totalPages}
          </button>
        </>
      )}
      
      <button
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages}
        className="page-button"
      >
        Próxima →
      </button>
    </div>
  );
}
```

**CSS `src/components/Pagination.css`:**

```css
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #eee;
}

.page-button,
.page-number {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  background: white;
  color: #333;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
  min-width: 40px;
  text-align: center;
}

.page-button:hover:not(:disabled) {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.page-number.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.page-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ellipsis {
  color: #666;
  padding: 0.5rem;
}

@media (max-width: 768px) {
  .pagination {
    gap: 0.25rem;
  }

  .page-button,
  .page-number {
    padding: 0.4rem 0.7rem;
    font-size: 0.9rem;
  }
}
```

## 🎨 Estilos CSS

### Arquivo `src/app/restaurantes/restaurantes.css`

```css
/* Layout principal */
.restaurantes-list-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* Header */
.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.page-header p {
  font-size: 1.1rem;
  color: #666;
}

/* Seção de filtros */
.filters-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}

/* Grid de restaurantes */
.restaurantes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

/* Sem resultados */
.no-results {
  text-align: center;
  padding: 3rem 1rem;
  background: #f0f0f0;
  border-radius: 8px;
  margin: 2rem 0;
}

.no-results h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.no-results p {
  color: #666;
}

@media (max-width: 768px) {
  .restaurantes-grid {
    grid-template-columns: 1fr;
  }

  .page-header h1 {
    font-size: 1.8rem;
  }

  .filters-section {
    flex-direction: column;
  }
}
```

## 🔨 Atividades Práticas

### Exercício 1: Adicionar Filtro por Avaliação

Modifique `src/app/restaurantes/page.js` para adicionar filtro de avaliação mínima:

```javascript
// Adicionar ao estado
const [avaliacaoMin, setAvaliacaoMin] = useState(searchParams.get('avaliacaoMin') || 0);

// Adicionar aos params de requisição
...(avaliacaoMin > 0 && { avaliacaoMin })

// Adicionar ao FilterBar
<div className="filter-group">
  <label>Avaliação Mínima:</label>
  <input
    type="range"
    min="0"
    max="5"
    step="0.5"
    value={avaliacaoMin}
    onChange={(e) => setAvaliacaoMin(e.target.value)}
  />
  <span>{avaliacaoMin} ⭐</span>
</div>
```

### Exercício 2: Implementar Debounce na Busca

Evite requisições a cada tecla digitada:

```javascript
useEffect(() => {
  const timer = setTimeout(() => {
    buscarRestaurantes();
  }, 500); // 500ms de delay
  
  return () => clearTimeout(timer);
}, [busca, categoriaFiltro, ordenacao, page]);
```

### Exercício 3: Adicionar Skeleton Loading

Crie um componente de skeleton para melhor UX:

```javascript
// src/components/RestauranteSkeleton.js
export default function RestauranteSkeleton() {
  return (
    <div className="restaurante-card skeleton">
      <div className="skeleton-header"></div>
      <div className="skeleton-body"></div>
    </div>
  );
}

// CSS
.restaurante-card.skeleton {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```

## 💡 Conceitos-Chave

- **useState**: Gerencia estado local do componente
- **useEffect**: Executa efeitos colaterais (requisições API, etc)
- **useSearchParams**: Acessa query strings da URL no Next.js
- **Array de dependências**: Controla quando o efeito executa
- **Loading states**: Melhoram UX durante requisições
- **Error handling**: Sempre tratar erros de API
- **Key prop**: Obrigatória em listas para otimizar renders
- **Client Components**: Necessários para hooks com `'use client'`
- **URL State**: Mantém estado sincronizado com URL para bookmarks

## 📚 Arquivos Criados

```
src/
├── app/
│   └── restaurantes/
│       ├── page.js              # Página principal de listagem
│       └── restaurantes.css     # Estilos da listagem
└── components/
    ├── RestauranteCard.js       # Card do restaurante
    ├── RestauranteCard.css
    ├── SearchBar.js             # Barra de busca
    ├── SearchBar.css
    ├── FilterBar.js             # Barra de filtros
    ├── FilterBar.css
    ├── Loading.js               # Loading spinner
    ├── Loading.css
    ├── ErrorMessage.js          # Mensagem de erro
    ├── Pagination.js            # Paginação
    └── Pagination.css
```

## ➡️ Próximos Passos

Com a listagem funcionando corretamente, no **Tutorial 15** vamos criar a **página de detalhes** do restaurante com:
- Rota dinâmica `[id]/page.js`
- Integração com avaliações
- Componentes de detalhe e rating
- Link para avaliar

[➡️ Ir para Tutorial 15: Página de Detalhes do Item](15-detalhe-item.md)

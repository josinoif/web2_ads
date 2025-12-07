# Tutorial 15: Página de Detalhes do Item

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Usar rotas dinâmicas no Next.js
- Acessar parâmetros de rota
- Fazer requisições de detalhe por ID
- Exibir dados relacionados (avaliações)
- Estruturar página de detalhes
- Implementar navegação contextual

## 📖 Conteúdo

### 1. Entendendo Rotas Dinâmicas no Next.js

**Rotas Dinâmicas** - Use `[id]` no nome da pasta

```
src/app/restaurantes/[id]/page.js
```

**Acessar parâmetro:**

```javascript
import { use } from 'react';

export default function RestauranteDetail({ params }) {
  const { id } = use(params); // Unwrap params Promise
}
```

### 2. Página de Detalhes do Restaurante

**Arquivo `src/app/restaurantes/[id]/page.js`:**

```javascript
'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import restauranteService from '@/services/restauranteService';
import avaliacaoService from '@/services/avaliacaoService';
import AvaliacaoCard from '@/components/AvaliacaoCard';
import RatingStars from '@/components/RatingStars';
import Loading from '@/components/Loading';
import ErrorMessage from '@/components/ErrorMessage';
import './restaurante-detail.css';

export default function RestauranteDetail({ params }) {
  const { id } = use(params);
  const router = useRouter();
  
  const [restaurante, setRestaurante] = useState(null);
  const [avaliacoes, setAvaliacoes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [loadingAvaliacoes, setLoadingAvaliacoes] = useState(false);
  
  useEffect(() => {
    buscarDetalhes();
    buscarAvaliacoes();
  }, [id]);
  
  const buscarDetalhes = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await restauranteService.getById(id);
      setRestaurante(data);
    } catch (err) {
      setError(err.error || 'Erro ao carregar restaurante');
      console.error('Erro ao buscar restaurante:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const buscarAvaliacoes = async () => {
    setLoadingAvaliacoes(true);
    
    try {
      const data = await avaliacaoService.getByRestaurante(id);
      setAvaliacoes(data);
    } catch (err) {
      console.error('Erro ao buscar avaliações:', err);
    } finally {
      setLoadingAvaliacoes(false);
    }
  };
  
  const handleDelete = async () => {
    if (!window.confirm('Tem certeza que deseja excluir este restaurante?')) {
      return;
    }
    
    try {
      await restauranteService.delete(id);
      alert('Restaurante excluído com sucesso!');
      router.push('/restaurantes');
    } catch (err) {
      alert(err.error || 'Erro ao excluir restaurante');
    }
  };
  
  if (loading) {
    return <Loading message="Carregando detalhes..." />;
  }
  
  if (error) {
    return (
      <ErrorMessage 
        message={error}
        onRetry={buscarDetalhes}
      />
    );
  }
  
  if (!restaurante) {
    return (
      <div className="not-found">
        <h2>Restaurante não encontrado</h2>
        <Link href="/restaurantes">← Voltar para listagem</Link>
      </div>
    );
  }
  
  return (
    <div className="restaurante-detalhe-page">
      <div className="breadcrumb">
        <Link href="/restaurantes">Restaurantes</Link>
        <span> / </span>
        <span>{restaurante.nome}</span>
      </div>
      
      <div className="restaurante-header">
        <div className="header-content">
          <h1>{restaurante.nome}</h1>
          <span className="categoria-badge">{restaurante.categoria}</span>
        </div>
        
        <div className="header-actions">
          <Link 
            href={`/restaurantes/${id}/editar`}
            className="btn btn-secondary"
          >
            ✏️ Editar
          </Link>
          <button 
            onClick={handleDelete}
            className="btn btn-danger"
          >
            🗑️ Excluir
          </button>
        </div>
      </div>
      
      <div className="restaurante-info">
        <div className="info-card rating-card">
          <h3>Avaliação Geral</h3>
          <div className="rating-display">
            <div className="rating-number">
              {parseFloat(restaurante.avaliacao_media).toFixed(1)}
            </div>
            <div>
              <RatingStars rating={parseFloat(restaurante.avaliacao_media)} />
              <p className="total-avaliacoes">
                {avaliacoes.length} avaliação(ões)
              </p>
            </div>
          </div>
        </div>
        
        {restaurante.endereco && (
          <div className="info-card">
            <h3>📍 Localização</h3>
            <p>{restaurante.endereco}</p>
          </div>
        )}
        
        {restaurante.telefone && (
          <div className="info-card">
            <h3>📞 Contato</h3>
            <p>{restaurante.telefone}</p>
          </div>
        )}
        
        {restaurante.website && (
          <div className="info-card">
            <h3>🌐 Website</h3>
            <a href={restaurante.website} target="_blank" rel="noopener noreferrer">
              Visitar site
            </a>
          </div>
        )}
      </div>
      
      <div className="avaliacoes-section">
        <div className="section-header">
          <h2>Avaliações</h2>
          <Link 
            href={`/restaurantes/${id}/avaliar`}
            className="btn btn-primary"
          >
            ⭐ Adicionar Avaliação
          </Link>
        </div>
        
        {loadingAvaliacoes ? (
          <Loading message="Carregando avaliações..." />
        ) : avaliacoes.length === 0 ? (
          <div className="no-avaliacoes">
            <p>Nenhuma avaliação ainda. Seja o primeiro a avaliar!</p>
          </div>
        ) : (
          <div className="avaliacoes-list">
            {avaliacoes.map(avaliacao => (
              <AvaliacaoCard 
                key={avaliacao.id} 
                avaliacao={avaliacao}
                restauranteId={id}
                onDelete={buscarAvaliacoes}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
```

### 3. Componente Card de Avaliação

**Arquivo `src/components/AvaliacaoCard.js`:**

```javascript
'use client';

import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import avaliacaoService from '@/services/avaliacaoService';
import RatingStars from './RatingStars';
import './AvaliacaoCard.css';

export default function AvaliacaoCard({ avaliacao, restauranteId, onDelete }) {
  const [deleting, setDeleting] = useState(false);
  
  const handleDelete = async () => {
    if (!window.confirm('Tem certeza que deseja excluir esta avaliação?')) {
      return;
    }
    
    setDeleting(true);
    try {
      await avaliacaoService.delete(avaliacao.id);
      alert('Avaliação excluída com sucesso!');
      onDelete?.();
    } catch (err) {
      alert(err.error || 'Erro ao excluir avaliação');
    } finally {
      setDeleting(false);
    }
  };
  
  const dataFormatada = formatDistanceToNow(new Date(avaliacao.createdAt), {
    addSuffix: true,
    locale: ptBR
  });
  
  return (
    <div className="avaliacao-card">
      <div className="avaliacao-header">
        <div>
          <div className="rating-stars">
            <RatingStars rating={avaliacao.nota} size="small" />
            <span className="nota">{avaliacao.nota.toFixed(1)}</span>
          </div>
          <p className="data">{dataFormatada}</p>
        </div>
        
        <button 
          onClick={handleDelete}
          disabled={deleting}
          className="btn-delete"
          title="Excluir avaliação"
        >
          🗑️
        </button>
      </div>
      
      <div className="avaliacao-body">
        <p className="comentario">{avaliacao.comentario}</p>
      </div>
    </div>
  );
}
```

### 4. Componente RatingStars

**Arquivo `src/components/RatingStars.js`:**

```javascript
'use client';

import './RatingStars.css';

export default function RatingStars({ 
  rating = 0, 
  size = 'medium',
  interactive = false,
  onChange = null
}) {
  const stars = [];
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  
  const renderStar = (index) => {
    let starClass = 'empty';
    
    if (index < fullStars) {
      starClass = 'full';
    } else if (index === fullStars && hasHalfStar) {
      starClass = 'half';
    }
    
    if (interactive) {
      return (
        <button
          key={index}
          type="button"
          className={`star ${starClass} interactive`}
          onClick={() => onChange?.(index + 1)}
          onMouseEnter={() => {
            // Hover effect opcional
          }}
        >
          ★
        </button>
      );
    }
    
    return (
      <span key={index} className={`star ${starClass}`}>
        ★
      </span>
    );
  };
  
  for (let i = 0; i < 5; i++) {
    stars.push(renderStar(i));
  }
  
  return (
    <div className={`rating-stars size-${size} ${interactive ? 'interactive' : ''}`}>
      {stars}
    </div>
  );
}
```

**Arquivo `src/components/AvaliacaoCard.css`:**

```css
.avaliacao-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1.5rem;
  transition: box-shadow 0.2s;
}

.avaliacao-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.avaliacao-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.avaliacao-header > div {
  flex: 1;
}

.rating-stars {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.avaliacao-header .nota {
  font-weight: bold;
  font-size: 1.25rem;
  color: #f39c12;
  margin-left: 0.5rem;
}

.data {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
}

.btn-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.25rem;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.btn-delete:hover:not(:disabled) {
  background-color: #ffebee;
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.avaliacao-body {
  margin-top: 1rem;
}

.comentario {
  color: #333;
  line-height: 1.6;
  margin: 0;
}
```

### 4. Componente RatingStars

**Arquivo `src/components/RatingStars.js`:**

```javascript
'use client';

import './RatingStars.css';

export default function RatingStars({ 
  rating = 0, 
  size = 'medium',
  interactive = false,
  onChange = null
}) {
  const stars = [];
  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  
  const renderStar = (index) => {
    let starClass = 'empty';
    
    if (index < fullStars) {
      starClass = 'full';
    } else if (index === fullStars && hasHalfStar) {
      starClass = 'half';
    }
    
    if (interactive) {
      return (
        <button
          key={index}
          type="button"
          className={`star ${starClass} interactive`}
          onClick={() => onChange?.(index + 1)}
          onMouseEnter={() => {
            // Hover effect opcional
          }}
        >
          ★
        </button>
      );
    }
    
    return (
      <span key={index} className={`star ${starClass}`}>
        ★
      </span>
    );
  };
  
  for (let i = 0; i < 5; i++) {
    stars.push(renderStar(i));
  }
  
  return (
    <div className={`rating-stars size-${size} ${interactive ? 'interactive' : ''}`}>
      {stars}
    </div>
  );
}
```

**Arquivo `src/components/RatingStars.css`:**

```css
.rating-stars {
  display: inline-flex;
  gap: 0.25rem;
}

.star {
  color: #ddd;
  font-size: 1.5rem;
}

.star.full {
  color: #f39c12;
}

.star.half {
  background: linear-gradient(90deg, #f39c12 50%, #ddd 50%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.star.empty {
  color: #ddd;
}

/* Tamanhos */
.rating-stars.size-small .star {
  font-size: 1rem;
}

.rating-stars.size-medium .star {
  font-size: 1.5rem;
}

.rating-stars.size-large .star {
  font-size: 2rem;
}

/* Interativo */
.rating-stars.interactive .star {
  cursor: pointer;
  transition: transform 0.2s, color 0.2s;
  background: none;
  border: none;
  padding: 0;
}

.rating-stars.interactive .star:hover {
  transform: scale(1.2);
  color: #f39c12;
}
```

### 5. Instalando date-fns

Para formatação de datas:

```bash
npm install date-fns
```

**Uso:**

```jsx
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

const dataFormatada = format(
  new Date('2024-01-15T10:30:00'),
  "dd/MM/yyyy 'às' HH:mm",
  { locale: ptBR }
);
// Resultado: "15/01/2024 às 10:30"
```

### 6. Melhorando o Service de Avaliações

**Adicionar ao `src/services/avaliacaoService.js`:**

```javascript
const avaliacaoService = {
  // ... métodos existentes
  
  getByRestaurante: async (restauranteId) => {
    const response = await api.get(`/restaurantes/${restauranteId}/avaliacoes`);
    return response.data.avaliacoes || [];
  },
  
  delete: async (id) => {
    const response = await api.delete(`/avaliacoes/${id}`);
    return response.data;
  }
};

export default avaliacaoService;
```

### 7. CSS da Página de Detalhes

**Arquivo `src/app/restaurantes/[id]/restaurante-detail.css`:**

```css
.restaurante-detalhe-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.breadcrumb {
  margin-bottom: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.breadcrumb a {
  color: #3498db;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.restaurante-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #eee;
}

.header-content {
  flex: 1;
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  color: #333;
}

.categoria-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #3498db;
  color: white;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.btn-primary {
  background: #27ae60;
  color: white;
}

.btn-primary:hover {
  background: #229954;
}

.restaurante-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
}

.info-card h3 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #333;
}

.info-card p {
  margin: 0;
  color: #666;
}

.info-card a {
  color: #3498db;
  text-decoration: none;
}

.info-card a:hover {
  text-decoration: underline;
}

.rating-card {
  grid-column: span 2;
}

.rating-display {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.rating-number {
  font-size: 4rem;
  font-weight: bold;
  color: #f39c12;
  line-height: 1;
}

.total-avaliacoes {
  margin-top: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.avaliacoes-section {
  margin-top: 3rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.75rem;
  color: #333;
}

.no-avaliacoes {
  text-align: center;
  padding: 3rem;
  background: #f8f9fa;
  border-radius: 8px;
  color: #666;
}

.no-avaliacoes p {
  margin: 0.5rem 0;
}

.avaliacoes-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.not-found {
  text-align: center;
  padding: 4rem 2rem;
}

.not-found h2 {
  margin-bottom: 1rem;
  color: #666;
}

.not-found a {
  color: #3498db;
  text-decoration: none;
  font-size: 1.1rem;
}

.not-found a:hover {
  text-decoration: underline;
}

/* Responsividade */
@media (max-width: 768px) {
  .restaurante-header {
    flex-direction: column;
    gap: 1rem;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn {
    flex: 1;
    justify-content: center;
  }

  .rating-card {
    grid-column: span 1;
  }

  .rating-display {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .rating-number {
    font-size: 3rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .section-header .btn {
    width: 100%;
    justify-content: center;
  }
}
```

## 🔨 Atividade Prática

### Exercício 1: Adicionar Gráfico de Distribuição de Notas

Mostre quantas avaliações cada nota teve:

```jsx
const calcularDistribuicao = (avaliacoes) => {
  const dist = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  
  avaliacoes.forEach(av => {
    const nota = Math.floor(av.nota);
    dist[nota]++;
  });
  
  return dist;
};
```

### Exercício 2: Implementar Edição de Avaliação

Adicione funcionalidade de editar avaliação inline:

```jsx
const [editandoId, setEditandoId] = useState(null);

// Passar para AvaliacaoCard
onEdit={(id) => setEditandoId(id)}
```

## 💡 Conceitos-Chave

- **params** - Acessa parâmetros de rotas dinâmicas no Next.js
- **useRouter()** - Hook do Next.js para navegação programática
- **window.confirm()** - Confirmação nativa do navegador antes de ações destrutivas
- **date-fns** - Biblioteca para formatação e manipulação de datas
- **formatDistanceToNow()** - Formata data relativa (ex: "há 2 horas")
- Separar busca de detalhes e dados relacionados em requests diferentes
- Breadcrumbs melhoram navegação e contexto
- Sempre validar se dados existem antes de renderizar
- Loading states para melhor experiência do usuário

## ➡️ Próximos Passos

Agora vamos criar o **formulário de avaliação** para permitir que usuários avaliem restaurantes.

[➡️ Ir para Tutorial 16: Formulário de Avaliação](16-formulario-avaliacao.md)

# Tutorial 4: Formulário de Avaliação

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Criar formulários controlados no React
- Validar dados no frontend
- Enviar dados para API (POST/PUT)
- Gerenciar estado de formulários
- Implementar feedback visual
- Redirecionar após sucesso

## 📖 Conteúdo

### 1. Formulários Controlados no Next.js

**Componentes Controlados** - O React controla o valor dos inputs

```javascript
'use client';

import { useState } from 'react';

export default function MeuForm() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault(); // Evita reload da página
    
    // Processar dados
    console.log({ nome, email });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={nome}                          // Estado controla valor
        onChange={(e) => setNome(e.target.value)}  // Atualiza estado
      />
      
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      
      <button type="submit">Enviar</button>
    </form>
  );
}
```

**⚠️ Importante:** Componentes com hooks precisam ser marcados com `'use client'`

### 2. Página de Formulário de Avaliação

**Arquivo `src/app/restaurantes/[id]/avaliar/page.js`:**

```javascript
'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
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
      
      alert('Avaliação enviada com sucesso!');
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
            placeholder="Conte-nos sobre sua experiência..."
            rows={6}
            maxLength={500}
            className={errors.comentario ? 'error' : ''}
          />
          <div className="textarea-footer">
            <span className="char-count">
              {comentario.length}/500 caracteres
            </span>
            {errors.comentario && (
              <span className="error-message">{errors.comentario}</span>
            )}
          </div>
        </div>
        
        <div className="form-actions">
          <button
            type="button"
            onClick={() => router.push(`/restaurantes/${id}`)}
            className="btn btn-secondary"
            disabled={loading}
          >
            Cancelar
          </button>
          
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || nota === 0 || !autor.trim()}
          >
            {loading ? 'Enviando...' : 'Enviar Avaliação'}
          </button>
        </div>
      </form>
    </div>
  );
}
```

### 3. CSS do Formulário

**Arquivo `src/app/restaurantes/[id]/avaliar/page.css`:**

```css
.avaliacao-form-page {
  max-width: 700px;
  margin: 0 auto;
  padding: 2rem;
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h1 {
  margin: 0 0 0.5rem 0;
}

.restaurante-nome {
  font-size: 1.2rem;
  color: #666;
  margin: 0;
}

.avaliacao-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

.required {
  color: #e74c3c;
}

.nota-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.nota-selector .rating-stars {
  cursor: pointer;
}

.nota-numero {
  font-size: 1.2rem;
  font-weight: bold;
  color: #f39c12;
  min-width: 180px;
}

input[type="text"] {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input[type="text"]:focus {
  outline: none;
  border-color: #3498db;
}

input[type="text"].error {
  border-color: #e74c3c;
}

textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 1rem;
  resize: vertical;
  transition: border-color 0.3s;
}

textarea:focus {
  outline: none;
  border-color: #3498db;
}

textarea.error {
  border-color: #e74c3c;
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.char-count {
  font-size: 0.875rem;
  color: #666;
}

.error-message {
  color: #e74c3c;
  font-size: 0.875rem;
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.alert-error {
  background: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #eee;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}
```

### 4. Atualizar RatingStars para Modo Interativo

**Modificar `src/components/RatingStars.js`:**

```javascript
'use client';

import { useState } from 'react';
import './RatingStars.css';

export default function RatingStars({ rating, size = 'medium', interactive = false, onChange }) {
  const [hoveredStar, setHoveredStar] = useState(null);
  
  const displayRating = interactive && hoveredStar !== null ? hoveredStar : rating;
  
  const handleClick = (index) => {
    if (interactive && onChange) {
      onChange(index + 1);
    }
  };
  
  const handleMouseEnter = (index) => {
    if (interactive) {
      setHoveredStar(index + 1);
    }
  };
  
  const handleMouseLeave = () => {
    if (interactive) {
      setHoveredStar(null);
    }
  };
  
  const stars = [];
  
  for (let i = 0; i < 5; i++) {
    const filled = i < Math.floor(displayRating);
    
    stars.push(
      <span
        key={i}
        className={`star ${filled ? 'full' : 'empty'} ${size} ${interactive ? 'interactive' : ''}`}
        onClick={() => handleClick(i)}
        onMouseEnter={() => handleMouseEnter(i)}
        onMouseLeave={handleMouseLeave}
      >
        {filled ? '★' : '☆'}
      </span>
    );
  }
  
  return <div className="rating-stars">{stars}</div>;
}
```

**Atualizar CSS em `src/components/RatingStars.css`:**

```css
.rating-stars {
  display: flex;
  gap: 0.25rem;
}

.star {
  color: #f39c12;
  transition: all 0.2s;
}

.star.empty {
  color: #ddd;
}

.star.medium {
  font-size: 1.5rem;
}

.star.large {
  font-size: 2.5rem;
}

.star.interactive {
  cursor: pointer;
}

.star.interactive:hover {
  transform: scale(1.2);
}
```

### 5. Formulário de Edição de Restaurante

**Arquivo `src/app/restaurantes/[id]/editar/page.js`:**

```javascript
'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import restauranteService from '@/services/restauranteService';

export default function RestauranteForm({ params }) {
  const { id } = use(params);
  const router = useRouter();
  const isEdit = Boolean(id);
  
  const [formData, setFormData] = useState({
    nome: '',
    categoria: '',
    endereco: '',
    telefone: '',
    site: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  useEffect(() => {
    if (isEdit) {
      buscarRestaurante();
    }
  }, [id]);
  
  const buscarRestaurante = async () => {
    try {
      const data = await restauranteService.getById(id);
      setFormData({
        nome: data.nome || '',
        categoria: data.categoria || '',
        endereco: data.endereco || '',
        telefone: data.telefone || '',
        site: data.site || ''
      });
    } catch (err) {
      alert('Erro ao carregar restaurante');
      router.push('/restaurantes');
    }
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Limpar erro do campo
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };
  
  const validarFormulario = () => {
    const novosErros = {};
    
    if (!formData.nome.trim()) {
      novosErros.nome = 'Nome é obrigatório';
    }
    
    if (!formData.categoria) {
      novosErros.categoria = 'Categoria é obrigatória';
    }
    
    setErrors(novosErros);
    return Object.keys(novosErros).length === 0;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validarFormulario()) {
      return;
    }
    
    setLoading(true);
    
    try {
      if (isEdit) {
        await restauranteService.update(id, formData);
        alert('Restaurante atualizado com sucesso!');
      } else {
        const response = await restauranteService.create(formData);
        alert('Restaurante criado com sucesso!');
        router.push(`/restaurantes/${response.id}`);
        return;
      }
      
      router.push(`/restaurantes/${id}`);
      
    } catch (err) {
      alert(err.error || 'Erro ao salvar restaurante');
      if (err.errors) {
        setErrors(err.errors);
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="restaurante-form-page">
      <h1>{isEdit ? 'Editar' : 'Novo'} Restaurante</h1>
      
      <form onSubmit={handleSubmit} className="form">
        <div className="form-group">
          <label>Nome *</label>
          <input
            type="text"
            name="nome"
            value={formData.nome}
            onChange={handleChange}
            className={errors.nome ? 'error' : ''}
          />
          {errors.nome && <span className="error-message">{errors.nome}</span>}
        </div>
        
        <div className="form-group">
          <label>Categoria *</label>
          <select
            name="categoria"
            value={formData.categoria}
            onChange={handleChange}
            className={errors.categoria ? 'error' : ''}
          >
            <option value="">Selecione...</option>
            <option value="Italiana">Italiana</option>
            <option value="Japonesa">Japonesa</option>
            <option value="Brasileira">Brasileira</option>
            <option value="Mexicana">Mexicana</option>
            <option value="Árabe">Árabe</option>
            <option value="Hamburgueria">Hamburgueria</option>
            <option value="Pizzaria">Pizzaria</option>
            <option value="Vegetariana">Vegetariana</option>
            <option value="Outra">Outra</option>
          </select>
          {errors.categoria && <span className="error-message">{errors.categoria}</span>}
        </div>
        
        <div className="form-group">
          <label>Endereço</label>
          <input
            type="text"
            name="endereco"
            value={formData.endereco}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label>Telefone</label>
          <input
            type="tel"
            name="telefone"
            value={formData.telefone}
            onChange={handleChange}
          />
        </div>
        
        <div className="form-group">
          <label>Website</label>
          <input
            type="url"
            name="site"
            value={formData.site}
            onChange={handleChange}
            placeholder="https://..."
          />
        </div>
        
        <div className="form-actions">
          <button
            type="button"
            onClick={() => router.back()}
            className="btn btn-secondary"
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </form>
    </div>
  );
}
```

## 🔨 Atividade Prática

### Exercício 1: Adicionar Campo de Título

Adicione campo opcional "título" na avaliação:

```jsx
const [titulo, setTitulo] = useState('');

<input
  type="text"
  value={titulo}
  onChange={(e) => setTitulo(e.target.value)}
  placeholder="Ex: Melhor pizza da cidade!"
  maxLength={100}
/>
```

### Exercício 2: Implementar Preview da Avaliação

Mostre preview da avaliação antes de enviar:

```jsx
const [showPreview, setShowPreview] = useState(false);

// Componente de preview
{showPreview && (
  <div className="preview-card">
    <RatingStars rating={nota} />
    <p>{comentario}</p>
  </div>
)}
```

## 💡 Conceitos-Chave

- **Formulários controlados** - React controla o estado
- **e.preventDefault()** evita reload da página
- **Validação client-side** melhora UX
- **Feedback visual** de erros por campo
- **Estados de loading** durante requisições
- **router.push()** para redirecionamento programático no Next.js
- **use(params)** para acessar parâmetros de rota dinâmica
- Sempre validar no backend também!

## ➡️ Próximos Passos

Formulários funcionando! No próximo módulo vamos melhorar a **experiência do usuário** com feedback visual e tratamento de erros.

[➡️ Ir para Tutorial 5: Feedback e Tratamento de Erros](05-feedback-erros-frontend.md)

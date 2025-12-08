# Tutorial 21: Upload de Imagem de Perfil

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Implementar upload de imagens com Next.js App Router
- Criar preview de imagens antes do upload
- Validar tipo e tamanho de arquivos no cliente
- Enviar arquivos com FormData e Axios
- Exibir progresso de upload
- Integrar com endpoints de upload do backend

## 📖 Conteúdo

### 1. Componente de Upload de Imagem

**Arquivo `src/components/ImageUpload.js`:**

```javascript
'use client';

import { useState, useRef } from 'react';
import Image from 'next/image';
import styles from './ImageUpload.module.css';

export default function ImageUpload({ 
  currentImageUrl, 
  onUpload, 
  onDelete,
  maxSizeMB = 2,
  acceptedTypes = ['image/jpeg', 'image/png', 'image/webp']
}) {
  const [preview, setPreview] = useState(currentImageUrl || null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    // Validar tipo
    if (!acceptedTypes.includes(file.type)) {
      throw new Error(
        `Tipo de arquivo não permitido. Use: ${acceptedTypes.map(t => t.split('/')[1]).join(', ')}`
      );
    }

    // Validar tamanho
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      throw new Error(`Arquivo muito grande. Tamanho máximo: ${maxSizeMB}MB`);
    }

    return true;
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);

    try {
      validateFile(file);

      // Criar preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);

      // Fazer upload automaticamente
      handleUpload(file);
    } catch (err) {
      setError(err.message);
      setPreview(currentImageUrl || null);
    }
  };

  const handleUpload = async (file) => {
    setUploading(true);
    setError(null);
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', file);

      await onUpload(formData, (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        setProgress(percentCompleted);
      });

      // Sucesso - manter preview
    } catch (err) {
      setError(err.message || 'Erro ao enviar imagem');
      setPreview(currentImageUrl || null);
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Deseja remover a imagem?')) return;

    setUploading(true);
    setError(null);

    try {
      await onDelete();
      setPreview(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(err.message || 'Erro ao remover imagem');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.preview}>
        {preview ? (
          <div className={styles.imageWrapper}>
            <Image
              src={preview}
              alt="Preview"
              fill
              style={{ objectFit: 'cover' }}
              unoptimized={preview.startsWith('data:')}
            />
            {!uploading && (
              <button
                type="button"
                onClick={handleDelete}
                className={styles.deleteButton}
                aria-label="Remover imagem"
              >
                ×
              </button>
            )}
          </div>
        ) : (
          <div className={styles.placeholder}>
            <svg
              className={styles.icon}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p>Nenhuma imagem</p>
          </div>
        )}
      </div>

      {uploading && (
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${progress}%` }}
          />
          <span className={styles.progressText}>{progress}%</span>
        </div>
      )}

      {error && (
        <div className={styles.error} role="alert">
          {error}
        </div>
      )}

      <div className={styles.actions}>
        <input
          ref={fileInputRef}
          type="file"
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          className={styles.fileInput}
          disabled={uploading}
          id="image-upload"
        />
        <label
          htmlFor="image-upload"
          className={styles.uploadButton}
        >
          {uploading ? 'Enviando...' : preview ? 'Alterar Imagem' : 'Selecionar Imagem'}
        </label>
      </div>

      <p className={styles.hint}>
        Formatos aceitos: JPG, PNG, WebP. Tamanho máximo: {maxSizeMB}MB
      </p>
    </div>
  );
}
```

### 2. Estilos do Componente

**Arquivo `src/components/ImageUpload.module.css`:**

```css
.container {
  width: 100%;
  max-width: 400px;
}

.preview {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 8px;
  overflow: hidden;
  border: 2px dashed #ddd;
  background: #f9f9f9;
  position: relative;
}

.imageWrapper {
  width: 100%;
  height: 100%;
  position: relative;
}

.deleteButton {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 0, 0, 0.8);
  color: white;
  border: none;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  transition: background 0.2s;
  z-index: 10;
}

.deleteButton:hover {
  background: rgba(255, 0, 0, 1);
}

.placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.icon {
  width: 48px;
  height: 48px;
  margin-bottom: 8px;
}

.progressBar {
  width: 100%;
  height: 24px;
  background: #f0f0f0;
  border-radius: 12px;
  margin-top: 12px;
  position: relative;
  overflow: hidden;
}

.progressFill {
  height: 100%;
  background: linear-gradient(90deg, #4caf50, #81c784);
  transition: width 0.3s ease;
}

.progressText {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 12px;
  font-weight: 600;
  color: #333;
}

.error {
  background: #ffebee;
  color: #c62828;
  padding: 8px 12px;
  border-radius: 4px;
  margin-top: 8px;
  font-size: 14px;
}

.actions {
  margin-top: 12px;
}

.fileInput {
  display: none;
}

.uploadButton {
  display: inline-block;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
  text-align: center;
}

.uploadButton:hover {
  background: #0056b3;
}

.uploadButton:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.hint {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
}
```

### 3. Integrar no Formulário de Restaurante

**Arquivo `src/app/restaurantes/[id]/edit/page.js`:**

```javascript
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import restauranteService from '@/services/restauranteService';
import ImageUpload from '@/components/ImageUpload';
import styles from './edit.module.css';

export default function EditRestaurantePage({ params }) {
  const router = useRouter();
  const [restaurante, setRestaurante] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    nome: '',
    categoria: '',
    endereco: '',
    telefone: '',
    descricao: '',
  });

  useEffect(() => {
    loadRestaurante();
  }, [params.id]);

  const loadRestaurante = async () => {
    try {
      const data = await restauranteService.getById(params.id);
      setRestaurante(data);
      setFormData({
        nome: data.nome || '',
        categoria: data.categoria || '',
        endereco: data.endereco || '',
        telefone: data.telefone || '',
        descricao: data.descricao || '',
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await restauranteService.update(params.id, formData);
      router.push(`/restaurantes/${params.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleImageUpload = async (formData, onProgress) => {
    await restauranteService.uploadImage(params.id, formData, onProgress);
    // Recarregar dados para obter nova URL da imagem
    await loadRestaurante();
  };

  const handleImageDelete = async () => {
    await restauranteService.deleteImage(params.id);
    await loadRestaurante();
  };

  if (loading) return <div>Carregando...</div>;
  if (error && !restaurante) return <div>Erro: {error}</div>;

  return (
    <div className={styles.container}>
      <h1>Editar Restaurante</h1>

      <form onSubmit={handleSubmit} className={styles.form}>
        <section className={styles.section}>
          <h2>Imagem do Restaurante</h2>
          <ImageUpload
            currentImageUrl={restaurante?.image_url}
            onUpload={handleImageUpload}
            onDelete={handleImageDelete}
          />
        </section>

        <section className={styles.section}>
          <h2>Informações Básicas</h2>

          <div className={styles.field}>
            <label htmlFor="nome">Nome *</label>
            <input
              type="text"
              id="nome"
              name="nome"
              value={formData.nome}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="categoria">Categoria *</label>
            <select
              id="categoria"
              name="categoria"
              value={formData.categoria}
              onChange={handleInputChange}
              required
            >
              <option value="">Selecione...</option>
              <option value="Italiana">Italiana</option>
              <option value="Japonesa">Japonesa</option>
              <option value="Brasileira">Brasileira</option>
              <option value="Fast Food">Fast Food</option>
              <option value="Vegetariana">Vegetariana</option>
            </select>
          </div>

          <div className={styles.field}>
            <label htmlFor="endereco">Endereço</label>
            <input
              type="text"
              id="endereco"
              name="endereco"
              value={formData.endereco}
              onChange={handleInputChange}
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="telefone">Telefone</label>
            <input
              type="tel"
              id="telefone"
              name="telefone"
              value={formData.telefone}
              onChange={handleInputChange}
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="descricao">Descrição</label>
            <textarea
              id="descricao"
              name="descricao"
              value={formData.descricao}
              onChange={handleInputChange}
              rows={4}
            />
          </div>
        </section>

        {error && (
          <div className={styles.error} role="alert">
            {error}
          </div>
        )}

        <div className={styles.actions}>
          <button
            type="button"
            onClick={() => router.back()}
            className={styles.cancelButton}
            disabled={submitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className={styles.submitButton}
            disabled={submitting}
          >
            {submitting ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </form>
    </div>
  );
}
```

### 4. Atualizar Service de Restaurantes

**Arquivo `src/services/restauranteService.js`:**

```javascript
import api from './api';

const restauranteService = {
  async getAll(params = {}) {
    const response = await api.get('/restaurantes', { params });
    return response.data;
  },

  async getById(id) {
    const response = await api.get(`/restaurantes/${id}`);
    return response.data;
  },

  async create(data) {
    const response = await api.post('/restaurantes', data);
    return response.data;
  },

  async update(id, data) {
    const response = await api.put(`/restaurantes/${id}`, data);
    return response.data;
  },

  async delete(id) {
    await api.delete(`/restaurantes/${id}`);
  },

  async uploadImage(id, formData, onUploadProgress) {
    const response = await api.post(`/restaurantes/${id}/imagem`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },

  async deleteImage(id) {
    await api.delete(`/restaurantes/${id}/imagem`);
  },
};

export default restauranteService;
```

### 5. Configurar Next.js para Imagens Externas

**Arquivo `next.config.js`:**

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '3001',
        pathname: '/uploads/**',
      },
      {
        protocol: 'https',
        hostname: 'your-api-domain.com',
        pathname: '/uploads/**',
      },
    ],
  },
};

module.exports = nextConfig;
```

## 🔨 Atividade Prática

### Exercício 1: Testar Upload

1. Criar/editar restaurante
2. Selecionar imagem (JPG < 2MB)
3. Verificar preview e barra de progresso
4. Confirmar imagem salva no backend
5. Testar remoção de imagem

### Exercício 2: Validações

Teste cenários de erro:
- Arquivo muito grande (> 2MB)
- Tipo não permitido (PDF, GIF)
- Arquivo corrompido
- Erro de rede (desligar backend)

### Exercício 3: Melhorar UX

Adicione:
- Crop/resize de imagem antes do upload
- Múltiplos tamanhos (thumbnail, full)
- Drag & drop na área de preview
- Suporte a múltiplas imagens (galeria)

## 💡 Conceitos-Chave

- **FormData**: API para enviar arquivos multipart
- **FileReader**: Ler arquivos no navegador
- **onUploadProgress**: Callback do Axios para progresso
- **useRef**: Referência ao input file para reset
- **Image (Next.js)**: Componente otimizado para imagens
- **unoptimized**: Desabilitar otimização para data URLs

## 🛡️ Boas Práticas

1. **Validação**:
   - Sempre validar no cliente E servidor
   - Verificar tipo MIME real, não apenas extensão
   - Limitar tamanho para evitar uploads enormes

2. **UX**:
   - Mostrar preview antes do upload
   - Exibir progresso para uploads longos
   - Permitir cancelamento
   - Feedback claro de sucesso/erro

3. **Performance**:
   - Comprimir imagens grandes antes do upload
   - Usar lazy loading para imagens na listagem
   - Implementar cache de imagens

4. **Acessibilidade**:
   - Rótulos descritivos para inputs
   - Mensagens de erro anunciadas por screen readers
   - Suporte a teclado (tab, enter)

5. **Segurança**:
   - Validar extensões permitidas
   - Verificar content-type
   - Sanitizar nomes de arquivo no backend
   - Usar HTTPS em produção

## ➡️ Próximos Passos

- Implementar crop de imagens com react-image-crop
- Adicionar suporte a drag & drop
- Criar galeria com múltiplas imagens
- Otimizar imagens com sharp no backend

## 📚 Recursos

- [Next.js Image Component](https://nextjs.org/docs/app/api-reference/components/image)
- [MDN FileReader API](https://developer.mozilla.org/en-US/docs/Web/API/FileReader)
- [Axios Upload Progress](https://axios-http.com/docs/req_config)
- [FormData API](https://developer.mozilla.org/en-US/docs/Web/API/FormData)

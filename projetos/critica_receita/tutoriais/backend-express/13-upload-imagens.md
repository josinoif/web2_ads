# Tutorial 13: Upload de Imagens de Perfil (Express)

## 🎯 Objetivos de Aprendizado

Ao final deste tutorial, você será capaz de:
- Configurar multer para upload de arquivos
- Validar tipo MIME e tamanho de imagens
- Salvar arquivos com nomes seguros
- Servir arquivos estáticos via Express
- Atualizar e remover imagens de perfil
- Limpar recursos em caso de erro

## 📖 Conteúdo

### 1. Instalando Dependências

```bash
npm install multer
npm install file-type  # Validação de MIME real
```

### 2. Configurando o Multer

**Arquivo `src/config/upload.js`:**

```javascript
const multer = require('multer');
const path = require('path');
const crypto = require('crypto');
const fs = require('fs').promises;

// Diretório de upload
const uploadDir = process.env.UPLOAD_DIR || './uploads';

// Criar diretório se não existir
(async () => {
  try {
    await fs.mkdir(uploadDir, { recursive: true });
    console.log('📁 Diretório de uploads criado/verificado');
  } catch (error) {
    console.error('Erro ao criar diretório de uploads:', error);
  }
})();

// Configuração de storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    // Gerar nome único: hash + timestamp + extensão
    const hash = crypto.randomBytes(16).toString('hex');
    const ext = path.extname(file.originalname);
    cb(null, `${hash}-${Date.now()}${ext}`);
  }
});

// Filtro de tipos permitidos
const fileFilter = (req, file, cb) => {
  const allowedMimes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  
  if (allowedMimes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error('Tipo de arquivo não permitido. Use JPEG, PNG ou WebP.'), false);
  }
};

// Configuração do multer
const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 2 * 1024 * 1024, // 2MB
  }
});

module.exports = { upload, uploadDir };
```

### 3. Atualizando o Controller

**Adicionar ao `src/controllers/restauranteController.js`:**

```javascript
const path = require('path');
const fs = require('fs').promises;
const { uploadDir } = require('../config/upload');

/**
 * UPLOAD IMAGE - Upload de imagem de perfil
 * POST /api/restaurantes/:id/image
 */
exports.uploadImage = async (req, res) => {
  const { id } = req.params;
  
  if (!req.file) {
    throw new ApiError('Nenhuma imagem foi enviada', 400);
  }
  
  // Buscar restaurante
  const restaurante = await Restaurante.findByPk(id);
  
  if (!restaurante) {
    // Remover arquivo se restaurante não existe
    await fs.unlink(req.file.path).catch(() => {});
    throw new ApiError('Restaurante não encontrado', 404);
  }
  
  // Remover imagem antiga se existir
  if (restaurante.image_url) {
    const oldImagePath = path.join(uploadDir, path.basename(restaurante.image_url));
    await fs.unlink(oldImagePath).catch(() => {
      console.log('Imagem antiga não encontrada ou já removida');
    });
  }
  
  // Construir URL pública
  const baseUrl = process.env.BASE_URL || `http://localhost:${process.env.PORT || 3000}`;
  const imageUrl = `${baseUrl}/uploads/${req.file.filename}`;
  
  // Atualizar registro
  restaurante.image_url = imageUrl;
  await restaurante.save();
  
  res.json({
    mensagem: 'Imagem enviada com sucesso',
    imageUrl
  });
};

/**
 * DELETE IMAGE - Remover imagem de perfil
 * DELETE /api/restaurantes/:id/image
 */
exports.deleteImage = async (req, res) => {
  const { id } = req.params;
  
  const restaurante = await Restaurante.findByPk(id);
  
  if (!restaurante) {
    throw new ApiError('Restaurante não encontrado', 404);
  }
  
  if (!restaurante.image_url) {
    throw new ApiError('Restaurante não possui imagem', 400);
  }
  
  // Remover arquivo
  const imagePath = path.join(uploadDir, path.basename(restaurante.image_url));
  await fs.unlink(imagePath).catch(() => {
    console.log('Arquivo de imagem não encontrado');
  });
  
  // Limpar URL
  restaurante.image_url = null;
  await restaurante.save();
  
  res.json({
    mensagem: 'Imagem removida com sucesso'
  });
};
```

### 4. Criando as Rotas

**Atualizar `src/routes/restauranteRoutes.js`:**

```javascript
const express = require('express');
const router = express.Router();
const restauranteController = require('../controllers/restauranteController');
const { upload } = require('../config/upload');
const asyncHandler = require('../middlewares/asyncHandler');

// ... outras rotas ...

// Upload de imagem
router.post(
  '/:id/image',
  upload.single('image'),
  asyncHandler(restauranteController.uploadImage)
);

// Remover imagem
router.delete(
  '/:id/image',
  asyncHandler(restauranteController.deleteImage)
);

module.exports = router;
```

### 5. Servindo Arquivos Estáticos

**Atualizar `src/app.js`:**

```javascript
const express = require('express');
const path = require('path');
const { uploadDir } = require('./config/upload');

const app = express();

// ... outras configurações ...

// Servir arquivos estáticos (uploads)
app.use('/uploads', express.static(uploadDir));

// ... resto do código ...

module.exports = app;
```

### 6. Variáveis de Ambiente

**Adicionar ao `.env`:**

```env
UPLOAD_DIR=./uploads
BASE_URL=http://localhost:3000
```

### 7. Middleware de Tratamento de Erros do Multer

**Adicionar ao `src/middlewares/errorHandler.js`:**

```javascript
// Tratar erros do Multer
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        erro: 'Arquivo muito grande. Tamanho máximo: 2MB'
      });
    }
    return res.status(400).json({
      erro: error.message
    });
  }
  
  next(error);
});
```

## 🔨 Atividade Prática

### Exercício 1: Testar Upload

**Crie o arquivo `tests/upload-tests.http` no VS Code:**

```http
### Variáveis
@baseUrl = http://localhost:3000/api

### Upload de imagem (coloque uma imagem.jpg na pasta tests/)
POST {{baseUrl}}/restaurantes/1/imagem
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="imagem"; filename="imagem.jpg"
Content-Type: image/jpeg

< ./tests/imagem.jpg
------WebKitFormBoundary7MA4YWxkTrZu0gW--

### Verificar restaurante após upload
GET {{baseUrl}}/restaurantes/1

### Acessar imagem diretamente
# GET http://localhost:3000/uploads/nome-arquivo.jpg

### Remover imagem
DELETE {{baseUrl}}/restaurantes/1/imagem
```

**💡 Para upload de arquivos, use:**
- **Thunder Client** (extensão VS Code)
- **Postman** para interface gráfica
- **REST Client** com sintaxe acima

### Exercício 2: Testar Validações

Teste os seguintes cenários:
- ✅ Upload de imagem válida (JPEG, PNG, WebP < 2MB)
- ❌ Arquivo muito grande (> 2MB)
- ❌ Tipo de arquivo inválido (PDF, TXT)
- ✅ Substituir imagem existente
- ✅ Remover imagem
   - Método: `POST`
   - URL: `http://localhost:3000/api/restaurantes/1/image`
   - Body: form-data
     - Key: `image` (tipo File)
     - Value: selecionar uma imagem JPEG/PNG

2. **Verificar resposta:**
```json
{
  "mensagem": "Imagem enviada com sucesso",
  "imageUrl": "http://localhost:3000/uploads/abc123-1234567890.jpg"
}
```

3. **Acessar imagem no navegador:**
   - Abrir URL retornada

4. **Remover imagem:**
   - Método: `DELETE`
   - URL: `http://localhost:3000/api/restaurantes/1/image`

### Exercício 2: Validações

Teste os cenários:
- ✅ Upload de imagem válida (JPEG, PNG, WebP)
- ❌ Upload de arquivo muito grande (> 2MB)
- ❌ Upload de tipo inválido (PDF, TXT)
- ✅ Substituir imagem existente
- ✅ Remover imagem
- ❌ Tentar upload sem arquivo

### Exercício 3: Adicionar Thumbnail (Desafio)

Instale `sharp` para gerar miniaturas:

```bash
npm install sharp
```

Modifique o controller para criar versão reduzida:

```javascript
const sharp = require('sharp');

// Após salvar arquivo original
const thumbnailPath = path.join(uploadDir, `thumb-${req.file.filename}`);
await sharp(req.file.path)
  .resize(300, 300, { fit: 'cover' })
  .toFile(thumbnailPath);
```

## 💡 Conceitos-Chave

- **Multer**: Middleware para upload multipart/form-data
- **Storage**: Define onde e como arquivos são salvos
- **FileFilter**: Valida tipo de arquivo antes de salvar
- **Nomes seguros**: Hash + timestamp previnem colisões e ataques
- **Limpeza**: Sempre remover arquivos órfãos em caso de erro
- **Limites**: Proteger servidor com limites de tamanho
- **Servir estáticos**: `express.static()` para acessar uploads

## ➡️ Próximos Passos

No próximo tutorial, você aprenderá a:
- Integrar upload no frontend Next.js
- Criar preview de imagens
- Implementar progress bar de upload
- Validar no cliente antes de enviar

## 📚 Recursos Adicionais

- [Documentação Multer](https://github.com/expressjs/multer)
- [Sharp - Processamento de Imagens](https://sharp.pixelplumbing.com/)
- [Express Static Files](https://expressjs.com/en/starter/static-files.html)
- [MIME Types](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types)

# Tutorial: Upload e download em disco (Express + Multer)

Neste tutorial você vai criar uma API em **Node.js com Express** que recebe arquivos via upload multipart, salva em uma pasta configurável no disco e oferece um endpoint de download. Usaremos **Multer** para tratar o upload.

## Passo 1: Criar o projeto

```bash
mkdir upload-disco && cd upload-disco
npm init -y
npm install express multer
```

## Passo 2: Estrutura de pastas

Crie a pasta onde os arquivos serão salvos (fora do código, por boa prática). No projeto, crie:

```
upload-disco/
├── uploads/          # Pasta de armazenamento (pode ser .gitignore)
├── src/
│   └── server.js
├── package.json
└── .env.example      # Exemplo de variável UPLOAD_DIR
```

Adicione no `package.json` o script de start:

```json
"scripts": {
  "start": "node src/server.js"
}
```

## Passo 3: Configurar Multer e rota de upload

Crie o arquivo `src/server.js`:

```javascript
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Pasta de uploads (configurável por variável de ambiente)
const UPLOAD_DIR = process.env.UPLOAD_DIR || path.join(__dirname, '..', 'uploads');

if (!fs.existsSync(UPLOAD_DIR)) {
  fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Multer: armazenamento em disco com nome único
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPLOAD_DIR),
  filename: (req, file, cb) => {
    const unique = Date.now() + '-' + Math.round(Math.random() * 1e9);
    const ext = path.extname(file.originalname) || '';
    cb(null, unique + ext);
  },
});

const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5 MB
  fileFilter: (req, file, cb) => {
    const allowed = /\.(jpg|jpeg|png|pdf)$/i;
    if (allowed.test(file.originalname)) {
      cb(null, true);
    } else {
      cb(new Error('Apenas jpg, png e pdf são permitidos.'));
    }
  },
});

// POST /upload — um único arquivo no campo "arquivo"
app.post('/upload', upload.single('arquivo'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Nenhum arquivo enviado.' });
  }
  res.status(201).json({
    message: 'Arquivo salvo.',
    filename: req.file.filename,
    originalName: req.file.originalname,
    size: req.file.size,
  });
});

// GET /download/:filename — download pelo nome gerado
app.get('/download/:filename', (req, res) => {
  const filename = req.params.filename;
  const filepath = path.join(UPLOAD_DIR, filename);
  if (!fs.existsSync(filepath)) {
    return res.status(404).json({ error: 'Arquivo não encontrado.' });
  }
  res.download(filepath);
});

app.listen(PORT, () => {
  console.log(`Servidor em http://localhost:${PORT}`);
  console.log(`Uploads em: ${UPLOAD_DIR}`);
});
```

## Passo 4: Executar e testar

Inicie o servidor:

```bash
node src/server.js
```

Teste o upload com curl (substitua `caminho/para/arquivo.pdf` por um arquivo real):

```bash
curl -X POST -F "arquivo=@caminho/para/arquivo.pdf" http://localhost:3000/upload
```

A resposta deve trazer `filename` (nome gerado). Para baixar:

```bash
curl -O -J "http://localhost:3000/download/NOME_GERADO"
```

Ou abra no navegador: `http://localhost:3000/download/NOME_GERADO`.

## Explicação dos principais elementos

- **UPLOAD_DIR**: pasta onde os arquivos são gravados; use variável de ambiente em produção para não depender do caminho do projeto.
- **multer.diskStorage**: `destination` é a pasta; `filename` gera um nome único (timestamp + aleatório + extensão) para evitar sobrescrita.
- **limits.fileSize**: limita o tamanho (ex.: 5 MB) para evitar arquivos gigantes.
- **fileFilter**: validação no backend pela extensão; em produção pode-se validar também pelo `mimetype`.
- **upload.single('arquivo')**: espera um único arquivo no campo do form chamado `arquivo`. O frontend deve usar o mesmo nome no `FormData`.
- **res.download(filepath)**: envia o arquivo como anexo; o navegador abre a caixa de salvar.

## Limitações em produção

Com **múltiplas instâncias** da API, cada uma terá sua própria pasta `uploads`. Um upload que cair na instância A não estará disponível na B. Para produção com mais de uma instância, use object storage (MinIO ou S3), tratado nos módulos 03 e 04.

## Próximos passos

No módulo [03 - MinIO](../03-minio/) você usará object storage S3-compatível com MinIO em Docker e um backend que envia arquivos para o MinIO em vez do disco.

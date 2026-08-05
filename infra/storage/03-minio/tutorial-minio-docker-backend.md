# Tutorial: MinIO com Docker e backend Express

Neste tutorial você vai (1) subir o **MinIO** com Docker, (2) criar um bucket pelo Console e (3) implementar uma API Express que faz upload e download de arquivos no MinIO usando o SDK oficial para Node.js.

## Passo 1: Subir o MinIO com Docker

No terminal:

```bash
docker run -d -p 9000:9000 -p 9001:9001 --name minio \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

- **9000**: API S3 (backend conecta aqui).
- **9001**: Console web.

Acesse no navegador: **http://localhost:9001**. Login: `minioadmin` / `minioadmin`.

## Passo 2: Criar um bucket no Console

1. No Console MinIO, clique em **Buckets** e em **Create Bucket**.
2. Nome do bucket: `uploads` (ou outro de sua preferência).
3. Confirme. O bucket será usado pelo backend.

## Passo 3: Criar o projeto Node e instalar o SDK MinIO

```bash
mkdir minio-backend && cd minio-backend
npm init -y
npm install express multer minio
```

## Passo 4: Código do servidor (upload e download)

Crie o arquivo `src/server.js`:

```javascript
const express = require('express');
const multer = require('multer');
const path = require('path');
const { Client: MinioClient } = require('minio');

const app = express();
const PORT = 3000;

const BUCKET = process.env.MINIO_BUCKET || 'uploads';

const minioClient = new MinioClient({
  endPoint: process.env.MINIO_ENDPOINT || 'localhost',
  port: parseInt(process.env.MINIO_PORT || '9000', 10),
  useSSL: process.env.MINIO_USE_SSL === 'true',
  accessKey: process.env.MINIO_ACCESS_KEY || 'minioadmin',
  secretKey: process.env.MINIO_SECRET_KEY || 'minioadmin',
});

// Garantir que o bucket existe
async function ensureBucket() {
  const exists = await minioClient.bucketExists(BUCKET);
  if (!exists) await minioClient.makeBucket(BUCKET);
}
ensureBucket().catch(console.error);

// Multer em memória (o buffer será enviado ao MinIO)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const allowed = /\.(jpg|jpeg|png|pdf)$/i;
    cb(null, allowed.test(file.originalname));
  },
});

// POST /upload — envia o arquivo para o MinIO
app.post('/upload', upload.single('arquivo'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'Nenhum arquivo enviado.' });

  const key = Date.now() + '-' + path.basename(req.file.originalname);

  try {
    await minioClient.putObject(BUCKET, key, req.file.buffer, req.file.size, {
      'Content-Type': req.file.mimetype,
    });
    res.status(201).json({
      message: 'Arquivo enviado ao MinIO.',
      key,
      originalName: req.file.originalname,
      size: req.file.size,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro ao enviar para o MinIO.' });
  }
});

// GET /download/:key — gera URL presigned para download
app.get('/download/:key', async (req, res) => {
  const key = req.params.key;
  try {
    const url = await minioClient.presignedGetObject(BUCKET, key, 3600); // 1 hora
    res.redirect(url);
  } catch (err) {
    console.error(err);
    res.status(404).json({ error: 'Objeto não encontrado.' });
  }
});

app.listen(PORT, () => {
  console.log(`Servidor em http://localhost:${PORT}`);
  console.log(`MinIO bucket: ${BUCKET}`);
});
```

Adicione em `package.json`:

```json
"scripts": {
  "start": "node src/server.js"
}
```

## Passo 5: Executar e testar

Com o MinIO rodando e o bucket criado:

```bash
node src/server.js
```

Upload com curl (substitua pelo caminho de um arquivo):

```bash
curl -X POST -F "arquivo=@./seu-arquivo.pdf" http://localhost:3000/upload
```

A resposta traz o campo `key`. Para baixar, use no navegador ou com curl:

```bash
curl -L "http://localhost:3000/download/KEY_RETORNADA"
```

Ou abra no navegador: `http://localhost:3000/download/KEY_RETORNADA`. Você será redirecionado para uma URL temporária do MinIO que entrega o arquivo.

## Explicação dos principais elementos

- **MinioClient**: configuração com endpoint, porta, accessKey e secretKey. Em produção use variáveis de ambiente.
- **putObject(bucket, key, stream ou buffer, size, meta)**: envia o arquivo ao MinIO. Como usamos `multer.memoryStorage()`, o corpo está em `req.file.buffer`; o tamanho é `req.file.size` e o tipo em `Content-Type`.
- **key**: nome lógico do objeto no bucket (ex.: timestamp + nome original). Não é caminho de pasta no disco; no MinIO é apenas uma string que identifica o objeto.
- **presignedGetObject(bucket, key, expirySeconds)**: gera uma URL temporária que qualquer um pode usar para fazer GET no objeto, sem precisar das credenciais. O backend redireciona o cliente para essa URL.

## Próximos passos

No módulo [04 - S3 e nuvem](../04-s3-cloud/) você verá como usar a AWS S3 ou o LocalStack (emulado S3 local) com o mesmo tipo de operações.

# Tutorial: S3 com LocalStack (e opção AWS S3)

Neste tutorial você vai usar a **API S3** com **LocalStack** para praticar em casa sem conta AWS. O mesmo padrão de código serve para **AWS S3** real: basta trocar endpoint e credenciais (variáveis de ambiente).

## Opção A: LocalStack (recomendado para estudo)

### Passo 1: Subir o LocalStack com Docker

```bash
docker run -d --name localstack \
  -p 4566:4566 -p 4510-4559:4510-4559 \
  -e SERVICES=s3 \
  localstack/localstack
```

A API S3 do LocalStack fica em **http://localhost:4566**.

### Passo 2: Criar um bucket no LocalStack

Instale o AWS CLI (se ainda não tiver) e configure um profile que aponte para o LocalStack:

```bash
aws --endpoint-url=http://localhost:4566 s3 mb s3://uploads
```

Ou use o SDK no próprio backend para criar o bucket na primeira execução (veja Passo 4).

### Passo 3: Projeto Node e dependências

```bash
mkdir s3-backend && cd s3-backend
npm init -y
npm install express multer @aws-sdk/client-s3 @aws-sdk/s3-request-presigner
```

### Passo 4: Código do servidor (S3-compatível)

Crie `src/server.js`:

```javascript
const express = require('express');
const multer = require('multer');
const path = require('path');
const { S3Client, PutObjectCommand, GetObjectCommand, CreateBucketCommand, HeadBucketCommand } = require('@aws-sdk/client-s3');
const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');

const app = express();
const PORT = 3000;

const BUCKET = process.env.S3_BUCKET || 'uploads';
const isLocalStack = process.env.S3_USE_LOCALSTACK === 'true';

const s3Client = new S3Client({
  region: process.env.AWS_REGION || 'us-east-1',
  ...(isLocalStack && {
    endpoint: process.env.S3_ENDPOINT || 'http://localhost:4566',
    forcePathStyle: true,
    credentials: {
      accessKeyId: 'test',
      secretAccessKey: 'test',
    },
  }),
});

async function ensureBucket() {
  try {
    await s3Client.send(new HeadBucketCommand({ Bucket: BUCKET }));
  } catch {
    await s3Client.send(new CreateBucketCommand({ Bucket: BUCKET }));
  }
}
ensureBucket().catch(console.error);

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const allowed = /\.(jpg|jpeg|png|pdf)$/i;
    cb(null, allowed.test(file.originalname));
  },
});

app.post('/upload', upload.single('arquivo'), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'Nenhum arquivo enviado.' });

  const key = Date.now() + '-' + path.basename(req.file.originalname);

  try {
    await s3Client.send(new PutObjectCommand({
      Bucket: BUCKET,
      Key: key,
      Body: req.file.buffer,
      ContentType: req.file.mimetype,
    }));
    res.status(201).json({
      message: 'Arquivo enviado ao S3.',
      key,
      originalName: req.file.originalname,
      size: req.file.size,
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Erro ao enviar para o S3.' });
  }
});

app.get('/download/:key', async (req, res) => {
  const key = req.params.key;
  try {
    const command = new GetObjectCommand({ Bucket: BUCKET, Key: key });
    const url = await getSignedUrl(s3Client, command, { expiresIn: 3600 });
    res.redirect(url);
  } catch (err) {
    console.error(err);
    res.status(404).json({ error: 'Objeto não encontrado.' });
  }
});

app.listen(PORT, () => {
  console.log(`Servidor em http://localhost:${PORT}`);
  console.log(`Bucket: ${BUCKET}, LocalStack: ${isLocalStack}`);
});
```

Adicione em `package.json`: `"start": "node src/server.js"`.

### Passo 5: Executar com LocalStack

Defina a variável e inicie:

```bash
export S3_USE_LOCALSTACK=true
node src/server.js
```

Teste o upload:

```bash
curl -X POST -F "arquivo=@./seu-arquivo.pdf" http://localhost:3000/upload
```

Use o `key` retornado para baixar: `http://localhost:3000/download/KEY`.

---

## Opção B: AWS S3 real

1. Crie um bucket no console AWS S3 (ex.: `meu-app-uploads`) e anote a região.
2. Crie um usuário IAM com permissão `AmazonS3FullAccess` (ou política restrita ao bucket) e gere **Access Key** e **Secret Key**.
3. **Não** defina `S3_USE_LOCALSTACK`. Configure:

```bash
export AWS_ACCESS_KEY_ID=sua_access_key
export AWS_SECRET_ACCESS_KEY=sua_secret_key
export AWS_REGION=sa-east-1
export S3_BUCKET=meu-app-uploads
```

4. Inicie o servidor: `node src/server.js`. O SDK usará o endpoint padrão da AWS para a região configurada.

---

## Explicação dos principais elementos

- **S3Client**: configuração do cliente AWS SDK v3. Com `endpoint` e `forcePathStyle` apontamos para LocalStack; sem isso, usa AWS real.
- **PutObjectCommand**: envia o objeto (Body = buffer, Key = nome no bucket, ContentType = mimetype).
- **getSignedUrl(GetObjectCommand, expiresIn)**: gera URL presigned para GET; o cliente é redirecionado e baixa direto do S3/LocalStack sem o backend enviar os bytes.
- **CreateBucketCommand / HeadBucketCommand**: garantem que o bucket existe (útil no LocalStack, onde o bucket pode ser criado na primeira execução).

---

## Próximos passos

No módulo [05 - Comparação e prática](../05-comparacao-pratica/) você verá uma tabela resumo e boas práticas para decidir entre filesystem, MinIO e S3 em projetos reais.

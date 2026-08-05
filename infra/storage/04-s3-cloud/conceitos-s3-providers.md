# S3 e provedores de object storage em nuvem

## Introdução

O **Amazon S3** (Simple Storage Service) é o serviço de object storage mais usado na nuvem. Outros provedores oferecem APIs semelhantes (Google Cloud Storage, Azure Blob Storage). Entender conceitos do S3 ajuda a usar tanto a AWS quanto emuladores locais como o **LocalStack**, que permitem estudar e desenvolver sem conta em nuvem.

---

## Conceitos do Amazon S3

- **Região (region)**: os buckets são criados em uma região (ex.: `us-east-1`, `sa-east-1`). Latência e custo podem variar por região; os dados ficam armazenados nela.
- **Bucket**: container de objetos; o nome é globalmente único na AWS. Políticas e permissões podem ser definidas no nível do bucket.
- **IAM (Identity and Access Management)**: usuários e funções com permissões (ex.: `s3:PutObject`, `s3:GetObject`) para acessar buckets. Em aplicações, usamos **credenciais** (access key + secret key) de um usuário ou role com permissão no bucket.
- **Endpoint**: URL da API por região (ex.: `https://s3.sa-east-1.amazonaws.com`). O SDK usa região e endpoint automaticamente quando configurado.
- **Presigned URL**: URL temporária gerada com as credenciais do backend que delega GET ou PUT ao cliente sem expor as chaves. Muito usado para download ou upload direto do navegador para o S3.

Segurança: nunca coloque access key e secret em código ou repositório; use variáveis de ambiente ou serviços de secrets. Em produção, prefira IAM roles quando a aplicação roda na própria AWS.

---

## LocalStack

**LocalStack** emula vários serviços AWS (incluindo S3) na sua máquina. Útil para desenvolver e testar sem gastar com a nuvem e sem precisar de conta AWS. A API é compatível com S3; você pode usar o AWS SDK para JavaScript (ou outro) apontando o endpoint para `http://localhost:4566` (por padrão).

Limitação: não substitui a AWS em cenários de alta durabilidade ou multi-região; é uma ferramenta de desenvolvimento e testes.

---

## Outros provedores

- **Google Cloud Storage (GCS)**: conceitos parecidos (buckets, objetos); API própria, mas existem adaptadores e SDKs.
- **Azure Blob Storage**: containers e blobs; integração com ecossistema Microsoft.

Todos oferecem durabilidade, escalabilidade e opções de ciclo de vida e versionamento. A escolha costuma depender do provedor de nuvem já adotado pela organização.

---

## Custos e boas práticas

- Na AWS, cobra-se por armazenamento, requisições e transferência de dados para fora da região. Para estudo, o free tier cobre um volume pequeno.
- Use **presigned URLs** para que o frontend baixe (ou envie) diretamente no S3, reduzindo carga no seu backend e aproveitando a rede da AWS.
- Configure **CORS** no bucket se o frontend (outro domínio) for acessar o S3 diretamente (ex.: upload via presigned PUT).

---

## Conclusão

O S3 e serviços equivalentes são a base de object storage em nuvem. Com LocalStack você pode praticar em casa; com credenciais AWS, o mesmo código funciona contra o S3 real. No [tutorial-s3-backend.md](tutorial-s3-backend.md) você implementará upload e download usando **LocalStack** (e opcionalmente AWS S3) com Node.js.

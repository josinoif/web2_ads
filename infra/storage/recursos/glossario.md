# Glossário — Armazenamento de arquivos

| Termo | Definição |
|-------|-----------|
| **Bucket** | Container lógico em object storage (S3, MinIO) que agrupa objetos. O nome do bucket é usado em todas as operações (upload, download, listagem). |
| **Object storage** | Modelo de armazenamento em que dados são tratados como **objetos** identificados por uma **key**, dentro de **buckets**, acessados por API HTTP (PUT, GET, etc.), em vez de sistema de arquivos tradicional. |
| **Key** | Identificador único do objeto dentro de um bucket. É uma string que pode lembrar um caminho (ex.: `pasta/arquivo.pdf`), mas não é obrigatoriamente uma hierarquia real no disco. |
| **Presigned URL** | URL temporária gerada pelo backend (com as credenciais do serviço) que permite a um cliente fazer GET ou PUT diretamente no object storage sem precisar das chaves de API. Expira após um tempo definido. |
| **Multipart upload** | Estratégia de enviar um arquivo em várias partes (chunks); o servidor ou o object storage monta o objeto final. Usado para arquivos grandes e para reduzir risco de timeout. |
| **Endpoint** | URL da API do serviço de storage (ex.: `http://localhost:9000` para MinIO, `https://s3.sa-east-1.amazonaws.com` para AWS S3 em uma região). |
| **Filesystem** | Armazenamento em pastas e arquivos no disco do servidor (sistema de arquivos local). Não usa API de object storage. |
| **LocalStack** | Emulador de serviços AWS (incluindo S3) que roda localmente, permitindo desenvolver e testar sem conta na AWS. |
| **IAM** | Identity and Access Management (AWS). Gerencia usuários, funções e permissões para acessar recursos como S3 (ex.: políticas que permitem PutObject, GetObject em um bucket). |

# Conceitos de armazenamento de arquivos em aplicações web

## Introdução

Aplicações web frequentemente precisam **receber arquivos** enviados pelo usuário (fotos, documentos, vídeos) e **persisti-los** para depois exibir ou permitir download. A escolha de **onde** e **como** armazenar esses arquivos impacta custo, escalabilidade e manutenção. Este módulo apresenta os conceitos centrais: filesystem vs object storage, buckets, objetos e formas de acesso.

---

## Filesystem (disco do servidor)

No **filesystem**, os arquivos são salvos em pastas no disco da máquina onde a aplicação roda. O backend recebe o upload (por exemplo via multipart/form-data), valida e grava em um diretório configurado (ex.: `uploads/`).

- **Vantagens**: simples, sem custo adicional, controle total sobre o caminho e o nome do arquivo.
- **Limitações**: não escala bem com múltiplas instâncias (cada servidor tem seu próprio disco); backup e recuperação ficam a cargo do time; disco pode encher.

É uma opção válida para desenvolvimento, protótipos ou aplicações pequenas com um único servidor.

---

## Object storage (S3, MinIO, etc.)

No **object storage**, os arquivos não são organizados em “pastas” do sistema de arquivos, e sim como **objetos** identificados por uma **chave** (key), dentro de **buckets**. O acesso é feito por API HTTP (ex.: PUT para upload, GET para download), e o provedor (ou o MinIO self-hosted) gerencia redundância, backup e escala.

- **Bucket**: container lógico que agrupa objetos (ex.: um bucket por ambiente ou por tipo de mídia). Em muitos provedores o nome do bucket é globalmente único.
- **Objeto**: o arquivo em si, com metadados (content-type, tamanho). A **key** é o “caminho” do objeto (ex.: `avatares/usuario-123.jpg`).
- **Endpoint**: URL da API do serviço (ex.: `https://s3.amazonaws.com`, ou para MinIO: `http://localhost:9000`).

Vantagens típicas: escala horizontal, durabilidade, possibilidade de CDN e de URLs temporárias (presigned) sem expor credenciais no frontend.

---

## Multipart upload

Para **arquivos grandes**, enviar tudo em uma única requisição pode ser lento e sujeito a timeout. O **multipart upload** divide o arquivo em partes: o cliente envia cada parte e o servidor (ou o object storage) monta o objeto final. A API S3 (e MinIO compatível) oferece multipart nativo; em upload para o próprio backend, pode-se usar bibliotecas que processam o stream em chunks.

---

## URLs públicas vs presigned (assinadas)

- **URL pública**: o objeto fica acessível a quem tiver o link. Útil para conteúdo realmente público (ex.: imagens de catálogo).
- **URL pré-assinada (presigned)**: o backend gera uma URL temporária que inclui uma assinatura; qualquer um com essa URL pode fazer GET (ou PUT) durante o período de validade, sem precisar de credenciais. Assim o frontend pode baixar (ou enviar) arquivos sem receber as chaves da API.

Em aplicações web, presigned URLs são comuns para download seguro e, em alguns fluxos, para upload direto do navegador para o object storage.

---

## Conclusão

Entender a diferença entre filesystem e object storage, e os conceitos de bucket, objeto, key e presigned URL, é a base para escolher a abordagem certa e implementar upload/download com segurança. No próximo arquivo você verá **quando usar cada abordagem** (disco, MinIO, S3) em função do cenário.

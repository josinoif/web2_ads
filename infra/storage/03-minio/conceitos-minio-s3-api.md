# MinIO e a API S3

## Introdução

**MinIO** é um servidor de **object storage** compatível com a **API Amazon S3**. Ou seja, você pode usar os mesmos conceitos (buckets, objetos, keys) e, em muitos casos, o mesmo código ou SDK que usaria com a AWS S3, apontando para um endpoint MinIO. Isso facilita desenvolver e testar localmente sem custo de nuvem e, se quiser, migrar depois para S3 trocando endpoint e credenciais.

---

## MinIO em resumo

- **Open source**: pode ser instalado no seu próprio servidor ou rodar em containers (Docker).
- **S3-compatível**: operações como PutObject, GetObject, ListObjects, DeleteObject e presigned URLs funcionam de forma equivalente.
- **Uso típico**: desenvolvimento local (MinIO em Docker), produção self-hosted (um ou mais nós MinIO) ou como camada privada em datacenter.

O MinIO expõe uma **API** (porta 9000 por padrão) e um **Console web** (porta 9001) para criar buckets, ver objetos e gerenciar políticas.

---

## Conceitos da API S3 (aplicáveis ao MinIO)

- **Bucket**: container lógico. Todo objeto pertence a um bucket. Em MinIO você cria buckets pelo Console ou pela API (ex.: `mc` ou SDK).
- **Objeto**: o arquivo em si. Identificado por uma **key** (string), que pode parecer um caminho (ex.: `avatares/2024/usuario-123.jpg`). Cada objeto tem metadados (content-type, size) e o corpo (bytes).
- **PutObject**: upload — envia o conteúdo e a key; o servidor armazena e responde com sucesso ou erro.
- **GetObject**: download — informa bucket e key; o servidor devolve o stream do objeto.
- **ListObjects**: lista as keys em um bucket (com prefixo opcional), útil para listar arquivos de um “folder” lógico.
- **Presigned URL**: URL temporária gerada pelo backend (com credenciais) que permite que um cliente faça GET ou PUT diretamente no MinIO/S3 sem expor as chaves. O backend chama uma API do SDK para gerar a URL e a devolve ao frontend.

Com MinIO, você usa um **SDK** (por exemplo `minio` para Node.js ou `minio-py` para Python) que já implementa essas operações.

---

## Docker para rodar MinIO localmente

A forma mais prática de usar MinIO em casa é subir um container:

```bash
docker run -d -p 9000:9000 -p 9001:9001 --name minio \
  -e MINIO_ROOT_USER=minioadmin -e MINIO_ROOT_PASSWORD=minioadmin \
  minio/minio server /data --console-address ":9001"
```

- **9000**: API S3 (o seu backend se conecta aqui).
- **9001**: Console web (criar buckets, ver arquivos).
- **MINIO_ROOT_USER / MINIO_ROOT_PASSWORD**: credenciais iniciais (troque em produção).

Depois de subir, acesse `http://localhost:9001`, faça login e crie um bucket (ex.: `uploads`). O backend usará esse nome de bucket e as credenciais para fazer PutObject e GetObject.

---

## Conclusão

MinIO traz o modelo S3 para o seu ambiente (local ou self-hosted), permitindo desenvolver e testar upload/download e presigned URLs sem depender da AWS. No [tutorial-minio-docker-backend.md](tutorial-minio-docker-backend.md) você subirá o MinIO com Docker e implementará um backend Express que envia e baixa arquivos no MinIO.

# 08 — Armazenamento de arquivos distribuídos

**Conceito:** object storage (modelo S3) — arquivos como objetos endereçáveis, separados do disco local da aplicação; vários clientes acessam o mesmo “bucket”.

**Stack:** Python 3 · MinIO via Docker (API S3-compatível)

**Status:** planejado

## Objetivo do mini-projeto

Subir MinIO, criar um bucket, fazer **upload/download** por dois “nós” (dois scripts/clientes) e observar que o arquivo não mora no filesystem da app — mora no serviço de objetos.

## Experimento sugerido

1. Subir MinIO com Docker Compose.
2. Upload de um arquivo pelo cliente A.
3. Listagem/download pelo cliente B (outra máquina/processo).
4. (Opcional) Remover o container da app e ver que o objeto continua no volume do MinIO.
5. Contrastar com salvar em `./uploads` local (o que quebra na escala com N réplicas da app).

## O que observar

- Disco local da app **não** escala com réplicas (cada pod/processo tem seu FS).
- Object storage compartilha o mesmo namespace de objetos entre clientes.
- URLs pré-assinadas, buckets e metadados são o modelo mental (não “pasta no servidor web”).

## Ligação com o repositório

Material paralelo em [`infra/storage/`](../../infra/storage/) (fundamentação, MinIO, S3). Este tutorial enfatiza o ângulo de **sistema distribuído**: por que a app não deve guardar arquivo “em si mesma” quando há vários nós.

## Perguntas-guia

- O que acontece com uploads em `./uploads` se houver 3 réplicas atrás de um load balancer?
- Object storage vs NFS/disco compartilhado: trade-offs?
- Onde entram CDN e cache na frente do object storage?

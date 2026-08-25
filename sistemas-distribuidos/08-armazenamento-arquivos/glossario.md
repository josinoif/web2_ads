# Glossário — Object storage e metadados

**Módulo:** [08](README.md) · **Consulta sob demanda** (abra quando travar num termo; não é leitura linear do caminho mínimo).

| Termo | Definição curta |
|-------|-----------------|
| **Object storage** | Serviço que guarda blobs endereçados por bucket + key (API tipo S3). |
| **DFS (clássico)** | Sistema de arquivos em rede (ex.: NFS) — “parece pasta”; contraste deste módulo, não o lab. |
| **Bucket** | Namespace lógico de objetos (ex.: `trabalhos`). |
| **Key / object_key** | Identificador do objeto dentro do bucket. |
| **Blob / objeto** | Os **bytes** do arquivo (conteúdo). |
| **Metadado** | Dados sobre o arquivo (aluno, disciplina, hash, status, key). |
| **MinIO** | Object storage S3-compatível usado nos labs (Docker). |
| **Disco local / `./uploads`** | Arquivo no filesystem do processo/container da API — não compartilhado entre réplicas. |
| **Sticky session** | Balanceador sempre manda o mesmo cliente ao mesmo pod — falso remédio para disco local. |
| **Desacoplamento** | Bytes fora da API; recreate da API não apaga o objeto no MinIO. |
| **Durabilidade (do blob)** | Objeto sobrevive a falha/perda do storage (réplica, erasure, backup) — distinto de desacoplamento. |
| **Content-addressable (CAS)** | Key derivada do conteúdo (ex.: SHA-256); blob imutável por construção. |
| **Deduplicação (dedup)** | Um blob físico para N entregas lógicas — **neste lab, feita pela app**. |
| **Refcount** | Contagem de referências ao blob; apaga objeto só quando chega a 0. |
| **Blob órfão** | Objeto no storage sem metadado que o referencie. |
| **Metadado órfão / mentiroso** | Registro “entregue” sem bytes correspondentes. |
| **Checksum / SHA-256** | Hash do conteúdo — dedup + verify no download. |
| **Soft verify** | Lab padrão: GET 200 + `X-Integridade: falha` + body (ensina o problema). |
| **Reject on integrity** | `REJECT_ON_INTEGRITY_FAIL=1` → GET **409** (eco de produção). |
| **Read-after-write (key)** | Após PutObject ok, GET da **mesma key** costuma ver o objeto. |
| **Versionamento** | Guardar versões do mesmo objeto/key ao sobrescrever (conceito). |
| **RPO** | Recovery Point Objective — quanto dado se aceita perder após incidente. |
| **RTO** | Recovery Time Objective — quanto tempo até o serviço voltar. |
| **Erasure coding** | Fragmentos com paridade — sobrevive a perda de discos com menos espaço que N cópias cheias. |
| **Cluster MinIO / S3** | Vários nós do object storage; a app ainda usa Put/Get — lab é single-node. |
| **Pre-signed URL** | URL temporária assinada; browser faz upload/download **direto** no storage. |
| **Multipart upload** | Arquivo grande em partes + Complete; retry por parte; Abort/lifecycle limpa incompletos. |
| **CDN** | Cache na borda para leitura — ≠ durabilidade do blob. |
| **KMS / at-rest** | Criptografia do objeto em disco / chave gerenciada (conceito). |
| **GridFS** | Guardar arquivos em chunks no Mongo — alternativa; não é o foco do lab. |
| **Stateless app** | API sem estado local durável — escala horizontal com storage externo. |

Ver também: [glossário CAP](../03-consistencia-cap/glossario.md) · [glossário replicação](../02-replicacao/glossario.md).

# Tecnologias e escolhas — Armazenamento de arquivos

**Módulo:** [08](README.md) · Use no workshop ou quando travar em “onde coloco o PDF?”.

---

## 1. Onde guardar os bytes

| Opção | Quando faz sentido | Quando dói |
|-------|-------------------|------------|
| Disco da API | Protótipo 1 processo | N réplicas, recreate, deploys |
| Sticky + disco local | Quase nunca | Esconde o problema; quebra no recreate |
| Volume compartilhado / NFS | Legado, apps que exigem POSIX | Locks, latência, SPOF |
| Object storage (MinIO/S3) | Multi-nó, uploads, anexos | Precisa metadado + política de falha |
| Dentro do DB (BYTEA / GridFS) | Arquivos minúsculos, tudo num store | DB vira gargalo de I/O; backups incham |

Neste módulo: **MinIO para bytes** + **DB para metadado**.  
Object storage compartilhado é **pré-requisito** de escala horizontal da API de upload ([05](../05-escalabilidade/)).

---

## 2. Postgres vs Mongo neste módulo

| | Postgres (lab A) | Mongo (lab B) |
|--|------------------|---------------|
| Domínio | Entrega com status ACID | Catálogo + dedup/refcount (mesmo portal) |
| Extra | 2 APIs · local vs MinIO · órfãos · desacoplamento | CAS na app · apagar lógico · RPO |
| Portas | 8090–91 / 5442 / 9010–11 | 8092 / 27123 / 9020–21 |

A escolha do DB é do **metadado**, não “quem armazena arquivo”.

---

## 3. Ordem de escrita e falha parcial

| Ordem | Risco se falhar no meio |
|-------|-------------------------|
| Meta primeiro, depois blob | “Entregue” sem arquivo (pior) |
| Blob primeiro, depois meta | Blob órfão (recuperável com reconciliação) |
| Só um dos dois + 201 | Mentira — evitar |

Labs: blob → meta → 201; flag didática força órfão.  
Retry sem idempotência ([06](../06-falhas-timeout/)) + key UUID → mais órfãos.

---

## 4. Dedup: quando sim / quando não

| Dedup por hash (app) | Evitar dedup “cego” |
|----------------------|---------------------|
| Anexos repetidos, templates, espaço caro | Auditoria exige cópia independente |
| Refcount claro no apagar | Compliance “uma cópia por aluno” |

MinIO single-node do lab **não** faz dedup nativa — a app implementa CAS.

---

## 5. Desacoplamento vs durabilidade

| Sintoma | Pergunta |
|---------|----------|
| API recreate e download ok | Desacoplamento — bom |
| Volume MinIO sumiu e download 404 | Durabilidade/RPO — precisa backup/réplica |

CDN / mais nós na frente = **disponibilidade de leitura**, não substitui backup.

---

## 6. Produção além do lab (cola)

| Precisa de… | Conceito | Lab? |
|-------------|----------|------|
| Sobreviver disco/nó do storage | Cluster + **erasure** ou réplicas; multi-AZ | Não — só discussão + Exp. RPO/backup |
| PDF 200 MB sem estourar a API | **Pre-signed** (browser → MinIO) | Não — [teoria §9](teoria.md) / `infra/storage` |
| Retry sem reenviar 2 GB | **Multipart** (partes + complete) | Não |
| Leitura rápida mundial | **CDN** na frente do objeto | Não — [07](../07-cache-distribuido/) |
| “Entregue” verdadeiro | Sempre: blob **e** metadado (mesmo com pre-signed) | Sim (fluxo via API) |

Detalhe: [teoria §9](teoria.md).

---

## 7. Relação com outros módulos

| Se a dor for… | Vá para… |
|---------------|----------|
| Lag / sync do **banco** | [02](../02-replicacao/) |
| Partição / CP vs AP | [03](../03-consistencia-cap/) |
| N APIs sem storage compartilhado | [05](../05-escalabilidade/) + este módulo |
| Timeout/retry no upload | [06](../06-falhas-timeout/) |
| Cache/CDN na frente do objeto | [07](../07-cache-distribuido/) + `infra/storage` |
| Operar MinIO no dia a dia | [`infra/storage`](../../infra/storage/) |

---

## 8. Cola rápida

| Sintoma | Primeira pergunta |
|---------|-------------------|
| Download 404 numa API, 200 noutra | Bytes no disco local? Sticky? |
| “Entregue” mas arquivo some | Metadado sem blob? Ordem de escrita? |
| Bucket cheio de objetos sem dono | Job de órfãos / retry sem idempotência? |
| Dois uploads idênticos dobram espaço | Key aleatória em vez de CAS na app? |
| `down -v` / volume sumiu | RPO: havia backup do storage? (ver Exp. backup/restore) |
| `X-Integridade: falha` | Soft verify — `provar-integridade-falha.sh` (também cobre **409**) |
| “Precisa de cluster MinIO no lab?” | Não — leia [teoria §9](teoria.md); lab prova o modelo, não o cluster |
| Upload grande abandonado no meio | Multipart sem Complete → Abort/lifecycle ([teoria §9.3](teoria.md)) |

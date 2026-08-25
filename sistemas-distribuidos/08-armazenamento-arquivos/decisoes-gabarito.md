# Gabarito enxuto — decisões (módulo 08)

> **Só depois** do workshop em [decisoes.md](decisoes.md). Abrir cedo reduz o aprendizado.

Use para calibrar — são critérios, não redação única.

---

## Cenário 1 — Quatro réplicas

1. Arquivo no disco do pod A; GET no pod B → 404 / “sumiu”.  
2. Sticky **não** resolve: recreate, deploy, uneven load, falha do pod “certo”.  
3. Object storage compartilha bytes; DB guarda key, aluno, status.  
4. Lab: `local` falha na outra API; `minio` funciona nas duas.

## Cenário 2 — Prazo legal

1. 202 só com blob → listagem vazia / professor não vê; aluno acha que entregou.  
2. Lab: só `entregue` após INSERT; falha de meta → não confirma (pode sobrar órfão).  
3. Retry com key UUID → outro PutObject / outro órfão; preferir CAS/hash ou Idempotency-Key ([06](../06-falhas-timeout/)).  
4. Priorizar **não mentir** o status — erro claro + retry controlado.

## Cenário 3 — Mesmo template

1. Dedup por hash **na app** (CAS); MinIO do lab **não** deduplica sozinho.  
2. Apagar lógico decrementa refcount; remove blob só se refcount=0.  
3. Lab Mongo: dois POSTs, um objeto, dois docs.

## Cenário 4 — Auditoria

1. Nova key por versão **ou** versionamento S3; não sobrescrever “no escuro”.  
2. CAS puro pode confundir “cópias idênticas” com histórico — combine hash + registro de versão/timestamp.  
3. Lab não faz versionamento S3 nem WORM — mencionar em produção.

## Cenário 5 — MinIO SPOF no lab vs produção

1. Volume apagado sem backup → RPO = perda dos objetos.  
2. Com Exp. backup/restore: após wipe dá para recuperar — prova positiva leve (não é erasure).  
3. Recreate da API **não** protege o volume — é só desacoplamento.  
4. Produção: cluster com réplicas/**erasure**, multi-AZ, **backup agendado** — lab: mirror pontual + [teoria §9](teoria.md).  
5. Não: metadado sem bytes não recupera o PDF.

## Cenário 6 — Mito Mongo/Postgres

1. Bytes no object storage; DB = metadado/catálogo.  
2. BYTEA/GridFS: arquivos minúsculos, ferramenta interna, tudo-num-store aceitável.  
3. “Mongo ≠ filesystem; Postgres ≠ incapaz de metadado de arquivo.”

## Cenário 7 — Arquivo grande

1. Browser → MinIO: blob pode existir antes do metadado; API só marca `entregue` após complete/ETag/callback — emitir pre-signed **não** é confirmação.  
2. Multipart: retry por parte; Put único de 200 MB falha = recomeçar tudo; sem Complete → Abort/lifecycle (partes órfãs).  
3. Lab **não** implementa; conceito em [teoria §9](teoria.md) + `infra/storage` / Xu Ch.14.  
4. Não: cluster melhora **durabilidade/disponibilidade do storage**; metadado + política de status continuam na app.

---

## Frase-modelo de fechamento

> O arquivo mora no **storage compartilhado**; a entrega é verdade só quando **blob e metadado** concordam — desacoplar da API não substitui **durabilidade/backup** do blob.

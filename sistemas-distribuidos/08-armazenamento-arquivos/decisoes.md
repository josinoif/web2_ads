# Workshop de decisões — Armazenamento de arquivos

**Módulo:** [08](README.md)  
Faça depois da [teoria](teoria.md) e, de preferência, do [lab Postgres](tutorial-entrega-postgres.md).  
Termos sob demanda: [glossario.md](glossario.md).

---

## Como usar

Para cada cenário:

1. Onde ficam os **bytes**? Onde fica o **metadado**?  
2. O que acontece com N réplicas de API?  
3. Se falhar no meio do upload — o que o usuário vê?  
4. Dedup / versionamento / RPO entram?  
5. É desacoplamento da API ou durabilidade do storage?  
6. Ponte [03](../03-consistencia-cap/): prioriza **não mentir** o status ou **seguir respondendo** a listagem?

### Critérios de uma boa resposta

Cite: (a) **onde mora o arquivo**, (b) **política na falha parcial**, (c) **um risco concreto** (órfão, mentira, perda, sticky).

> **Não abra o gabarito agora.** Espelho enxuto só **depois**: [decisoes-gabarito.md](decisoes-gabarito.md).

---

## Cenário 1 — Quatro réplicas de API

Portal de provas com 4 pods atrás do ingress. Time sugere `mkdir uploads` no Dockerfile “como no monólito”. Ops sugere sticky session “para o download achar o arquivo”.

**Perguntas**

1. O que quebra no download entre pods?  
2. Sticky session resolve? Por quê (não)?  
3. MinIO (ou S3) resolve o quê — e o que ainda precisa de metadado?  
4. Depois do lab: compare Exp. local vs MinIO nas duas APIs.

---

## Cenário 2 — Entrega no prazo legal

Aluno envia PDF no último minuto. PutObject no MinIO ok; INSERT no Postgres falha (timeout). Produto discute devolver `202` “recebemos o arquivo”. Cliente ainda pode **retentar** o POST ([06](../06-falhas-timeout/)).

**Perguntas**

1. Aceita 202 só com blob? O que o professor vê na listagem?  
2. Relacione com a política do lab (só `entregue` com meta + blob).  
3. O que o retry com key UUID pode gerar?  
4. Ponte CAP: o que priorizar neste fluxo?

---

## Cenário 3 — Turma manda o mesmo template

40 alunos enviam o PDF modelo da disciplina (bytes idênticos). Disco do storage está caro.

**Perguntas**

1. Deduplicar por SHA-256 **na app**? O MinIO faz isso sozinho neste lab?  
2. O que muda no “apaguei minha entrega”?  
3. Depois do [lab Mongo](tutorial-catalogo-mongodb.md): o que o Exp. de dedup mostrou?

---

## Cenário 4 — Auditoria do professor

Coordenação precisa provar **qual versão** do trabalho existia na data X. Aluno reenvia sobrescrevendo.

**Perguntas**

1. Versionamento de objeto vs só metadado com nova key?  
2. Dedup/CAS ajuda ou atrapalha a auditoria?  
3. O que o lab **não** implementa (e você mencionaria em produção)?

---

## Cenário 5 — MinIO SPOF no lab vs produção

No Compose há **um** MinIO. Ops pergunta: “e se o disco desse container morrer?”

**Perguntas**

1. O que `docker compose down -v` / Exp. perda de volume ensina sobre RPO?  
2. O Exp. backup/restore muda a conclusão?  
3. Recreate da **API** (lab Postgres) protege contra perda do volume?  
4. O que mudaria em produção (réplicas/erasure/backup automatizado) sem montar cluster no lab?  
5. Metadado no Postgres sozinho salva o PDF?

---

## Cenário 6 — Mito “Mongo = arquivos; Postgres = só tabela”

Time junior quer GridFS “porque é Mongo” e BYTEA “porque é Postgres” para PDFs de 20 MB.

**Perguntas**

1. O que o módulo recomenda para bytes vs metadado?  
2. Quando BYTEA/GridFS ainda faria sentido?  
3. Desfaça o mito em uma frase.

---

## Cenário 7 — Arquivo grande / upload direto

Produto quer PDF de 200 MB sem estourar a memória da API. Alguém cita pre-signed URL e multipart. Outro insiste em “montar cluster MinIO no Compose do lab”.

**Perguntas**

1. O que muda na falha parcial se o browser fala **direto** com o MinIO?  
2. Multipart resolve o quê que um PutObject único não resolve?  
3. O lab cobre pre-signed/multipart/cluster? Onde ler o conceito ([teoria §9](teoria.md), `infra/storage`, Xu Ch.14)?  
4. Cluster MinIO substitui a necessidade de metadado + política “entregue”?

---

## Depois do workshop

Confira [tecnologias-e-escolhas.md](tecnologias-e-escolhas.md) e o [gabarito](decisoes-gabarito.md) (só depois).

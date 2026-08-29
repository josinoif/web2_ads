# Tutorial — Entrega de trabalhos (Postgres + MinIO)

**Lab:** [lab-entrega-postgres](lab-entrega-postgres/) · API `http://127.0.0.1:8090` (api1) e `:8091` (api2)  
**Teoria:** [teoria.md](teoria.md) §1–6 · [glossario](glossario.md)  
**SO:** Linux, macOS e Windows — [como rodar os comandos](../ferramentas/linux-e-windows.md).  

> **Caminho mínimo:** C.1 → **Exp. 1–6** (órfãos inclusos).  
> Exp. 4 = desacoplamento (recreate da API). Exp. 6 = órfão + reconciliação.  
> Exp. 7 (integridade soft + 409) = caminho **completo** / opcional.

---

## Parte A — Tecnologia (o essencial)

| Peça | Papel |
|------|--------|
| Postgres | Metadado da entrega (`status=entregue`, `object_key`, `sha256`) |
| MinIO | Bytes (bucket `trabalhos`) — **não** deduplica sozinho |
| api1 / api2 | Duas réplicas — prova que disco local **não** compartilha |
| `STORAGE_BACKEND` | `minio` (padrão) · `local` (contraste didático) |
| `FAIL_AFTER_BLOB` | `1` → PutObject ok, metadado **não** grava (órfão) |
| `sha256` no metadado | **Integridade** (conferida no GET) — neste lab a **key ainda é UUID**, não CAS |
| `X-Integridade` | Soft (padrão): 200 + header; com `REJECT_ON_INTEGRITY_FAIL=1`: **409** |

> CAS com key = `sha256/...` fica no [lab Mongo](tutorial-catalogo-mongodb.md).

Fluxo feliz:

```text
POST /entregas
  1. PutObject (MinIO) ou write local
  2. INSERT entregas status=entregue
  3. 201 + JSON
```

> **Simplificações:** sem multipart; credenciais MinIO didáticas; órfão forçado por flag (não crash real do Postgres); key com UUID (retry pode gerar outro órfão — ponte [06](../06-falhas-timeout/)).

---

## Parte B — Contexto

Prazo de entrega: alunos sobem PDF. O portal roda **várias** APIs ([05](../05-escalabilidade/)). Se o arquivo ficar em `./uploads` do container, metade dos downloads “some”. Object storage + metadado no Postgres resolve o endereço compartilhado — e introduz falha parcial (bytes ok, meta não).

Pergunta: *como confirmar “entregue” sem mentir se o storage ou o DB falhar no meio?*

---

## Parte C — Lab

### C.1 Subir

```bash
cd sistemas-distribuidos/08-armazenamento-arquivos/lab-entrega-postgres
# opcional, lab limpo:
# docker compose down -v
./scripts/up.sh
./scripts/status.sh
```

### C.2 Experimento 1 — Upload + listagem (MinIO)

```bash
./scripts/set-backend.sh minio
./scripts/enviar.sh aluno-01
./scripts/status.sh
```

**Exemplo de resposta (trechos):**

```json
{
  "entrega": {
    "id": 1,
    "aluno_id": "aluno-01",
    "storage": "minio",
    "status": "entregue",
    "sha256": "…"
  },
  "servido_por": "api1"
}
```

**Esperado:** HTTP `201`, `storage: minio`, entrega em `/entregas`.

### C.3 Experimento 2 — Download na outra réplica

```bash
# captura o último id e baixa pela api2
ID=$(curl -s http://127.0.0.1:8090/entregas | python3 -c \
  "import sys,json; print(json.load(sys.stdin)['entregas'][-1]['id'])")
./scripts/baixar.sh "${ID}" 8091
```

**Esperado:** HTTP 200, `X-Servido-Por: api2`, `X-Integridade: ok`, arquivo em `/tmp/entrega-<id>.bin`.

### C.4 Experimento 3 — Local vs MinIO (dor distribuída)

```bash
./scripts/provar-local-vs-minio.sh
```

**Esperado:**

| Backend | Upload api1 → download api2 |
|---------|------------------------------|
| `local` | **404** (disco só na api1) |
| `minio` | **200** (objeto compartilhado) |

### C.5 Experimento 4 — API recreate (**desacoplamento**)

```bash
./scripts/provar-api-recreate.sh
```

**Esperado:** após recreate de api1/api2, download ainda funciona.  
Isso prova que o arquivo **não mora na API** — **não** prova que o blob sobrevive se o volume do MinIO sumir (isso é RPO, no lab Mongo).

### C.6 Experimento 5 — MinIO parado

```bash
./scripts/provar-minio-down.sh
```

**Esperado:** `503` com `code: storage_indisponivel`, **sem** linha `entregue` nova. Depois MinIO volta.

> **MinIO parado ≠ volume apagado.** Aqui o storage está indisponível (não aceita upload), mas os objetos no volume **continuam**. Perda permanente do volume (RPO) é o Exp. 4 do [lab Mongo](tutorial-catalogo-mongodb.md) — no mínimo, fixe isso pela [teoria §4](teoria.md).

### C.7 Experimento 6 — Blob órfão + reconciliação

```bash
./scripts/provar-orfao.sh
./scripts/reconciliar-orfaos.sh
```

**Esperado:** upload com `blob_orfao: true` e `status: falha`; `/admin/orfaos` lista keys; reconciliar remove do bucket.

### C.8 Experimento 7 (completo / opcional) — integridade: soft vs 409

```bash
./scripts/provar-integridade-falha.sh
```

**Esperado:**
1. Download íntegro → `X-Integridade: ok`
2. Após `mc pipe` (cliente MinIO via serviço Compose `minio-init`) corromper a key → soft verify: **200** + `X-Integridade: falha` + body
3. Com `REJECT_ON_INTEGRITY_FAIL=1` → **409** JSON (`code: integridade_falha`) — eco de produção

> Não precisa instalar `mc` no host: os scripts usam a imagem do serviço `minio-init`.

---

## O que anotar

1. Por que `local` quebra com 2 APIs (e sticky session não resolve).  
2. Ordem blob → meta → 201; só então `entregue`.  
3. Órfão = custo recuperável; “entregue” mentiroso = pior.  
4. Recreate da API = desacoplamento ≠ durabilidade do storage.  
5. Soft verify ensina o problema; 409 ensina a reação de produção.  
6. Arquivo enorme / cluster MinIO: [teoria §9](teoria.md) (conceito; não é este lab).

**Próximo (caminho completo):** [tutorial-catalogo-mongodb.md](tutorial-catalogo-mongodb.md) — *mesmo portal; agora o problema é espaço/dedup.*  
Decisões: [decisoes.md](decisoes.md)
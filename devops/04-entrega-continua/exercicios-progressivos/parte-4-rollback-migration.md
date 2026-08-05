# Parte 4 — Rollback e Migration Expand/Contract

> **Duração:** 1 hora.
> **Objetivo:** desenhar o **runbook de rollback** da LogiTrack e aplicar o padrão **Expand/Contract** numa mudança real de schema.

---

## Contexto

Com pipeline (Parte 2) e release controlado (Parte 3), o risco residual está em **como desfazer** quando algo sai errado — e em **como evoluir o banco** sem quebrar versões anteriores. É o tema do [Bloco 4](../bloco-4/04-release-engineering.md).

---

## Parte A — Runbook de Rollback

### 1. Escreva `docs/runbook-rollback.md`

Use como base o **Exercício 5 do Bloco 4** ([runbook mínimo](../bloco-4/04-exercicios-resolvidos.md#exerc%C3%ADcio-5--runbook-de-rollback-curto)). Adapte para seu serviço Tracking com:

- **3 cenários concretos** (A: < 15 min sem migration, B: migração destrutiva aplicada, C: dados novos > 1h).
- **Comandos reais** para o seu `deploy.sh` e/ou `switch.sh`.
- **Ações de feature flag** como **primeira** medida de mitigação (mais rápida que rollback).
- **Critérios de NÃO-rollback** explícitos.
- **Comunicação** (status page, Slack).

### 2. Crie `scripts/rollback.sh`

Um script minimalista que:

- Recebe `VERSION_PREV` e `ENV`.
- Valida que o artefato dessa versão existe no registry/cache.
- Executa o deploy para a versão alvo.
- Roda smoke test pós-rollback (reuso do `tests/smoke/`).

Exemplo:

```bash
#!/usr/bin/env bash
# scripts/rollback.sh — volta o serviço para uma versão conhecida.
set -euo pipefail

VERSION_PREV="${1:?uso: rollback.sh VERSION_PREV ENV}"
ENV="${2:?ENV é obrigatório}"

ARTIFACT_DIR="${ARTIFACT_DIR:-./artifacts}"
ARTIFACT="${ARTIFACT_DIR}/logitrack-tracking-${VERSION_PREV}.whl"

if [[ ! -f "$ARTIFACT" ]]; then
  echo "[rollback] artefato ${ARTIFACT} não encontrado — buscar no registry."
  exit 2
fi

echo "[rollback] voltando ${ENV} para ${VERSION_PREV}"
./scripts/deploy.sh "$ENV" "$ARTIFACT"

echo "[rollback] smoke test..."
TARGET_URL="${TARGET_URL:-http://localhost:8000}" \
  pytest tests/smoke -q

echo "[rollback] concluído."
```

Torne executável.

### 3. Simule um rollback

Escreva em `docs/simulacao-rollback.md` um **log de execução** (real ou narrado):

- Estado: prod rodando `v1.2.3`.
- Deploy de `v1.2.4` → 5xx sobem para 3%.
- Alerta disparado.
- Ação 1: flag `ESTIMATIVA_ML_PERCENT=0` (instantâneo).
- Ação 2 (se flag não resolveu): `./scripts/rollback.sh v1.2.3 production`.
- Smoke test verde.
- Postmortem agendado.

---

## Parte B — Migration Expand/Contract

### 4. Cenário de migração

A LogiTrack quer **dividir** o campo `status` (VARCHAR) em uma tabela normalizada `status(id, codigo, descricao)` com `status_id` (FK) em `pacote`.

Use como base o **Exercício 2 do Bloco 4** ([Refazer schema com Expand/Contract](../bloco-4/04-exercicios-resolvidos.md#exerc%C3%ADcio-2--refazer-schema-com-expandcontract)). Adapte para a sua aplicação:

### 5. Escreva as migrations

Crie os 3 arquivos em `migrations/`:

- `migrations/001_expand_status.sql`
- `migrations/002_contract_status.sql`

E um `README.md` em `migrations/` descrevendo a ordem, pré-requisitos e o que **cada versão do código** faz.

### 6. Documente a compatibilidade entre versões

Crie `docs/migrations-compatibilidade.md` com a matriz:

| Deploy | Schema esperado | Código v1.0 funciona? | Código v1.1 funciona? | Código v2.0 funciona? |
|--------|------------------|------------------------|------------------------|------------------------|
| Antes de qualquer migration | Só `endereco` | ✅ | ❌ (quer `rua/numero/cidade`) | ❌ |
| Após 001 (expand) | Ambos | ✅ | ✅ | ❌ |
| Após 002 (contract) | Só novas | ❌ | ✅ | ✅ |

Indique **em quais deploys** é seguro rodar cada migration.

### 7. Integrar migrations ao pipeline

Adicione no `cd.yml` (Parte 2) passos para **expand** e **contract**:

```yaml
- name: Apply migrations (expand phase)
  env:
    DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
  run: ./scripts/migrate.sh --phase=expand

# ... deploy ...

- name: Apply migrations (contract phase)
  if: success()
  env:
    DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
  run: ./scripts/migrate.sh --phase=contract
```

E um `scripts/migrate.sh` simples que aceita `--phase=expand|contract` e roda os `.sql` apropriados. Exemplo:

```bash
#!/usr/bin/env bash
set -euo pipefail

PHASE=""
for arg in "$@"; do
  case "$arg" in
    --phase=*) PHASE="${arg#*=}" ;;
  esac
done

MIGRATIONS_DIR="${MIGRATIONS_DIR:-./migrations}"

case "$PHASE" in
  expand)
    for f in "$MIGRATIONS_DIR"/*_expand_*.sql; do
      [[ -f "$f" ]] || continue
      echo "[migrate-expand] $f"
      psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"
    done
    ;;
  contract)
    for f in "$MIGRATIONS_DIR"/*_contract_*.sql; do
      [[ -f "$f" ]] || continue
      echo "[migrate-contract] $f"
      psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"
    done
    ;;
  *)
    echo "uso: migrate.sh --phase=expand|contract" >&2
    exit 1
    ;;
esac
```

**Nota:** se não tiver Postgres real rodando no pipeline, crie um job com `services: postgres:` (exemplo no [Bloco 2, seção 5.2](../bloco-2/02-deployment-pipeline.md#52-githubworkflowscdyml--deployment-pipeline)) ou **documente** que o passo foi testado manualmente com Docker local.

---

## Entregáveis

```
logitrack-tracking/
├── scripts/
│   ├── rollback.sh
│   └── migrate.sh
├── migrations/
│   ├── README.md
│   ├── 001_expand_status.sql
│   └── 002_contract_status.sql
├── docs/
│   ├── runbook-rollback.md
│   ├── simulacao-rollback.md
│   └── migrations-compatibilidade.md
└── .github/workflows/
    └── cd.yml                # atualizado com passos de migration
```

---

## Critérios de sucesso

- [ ] `runbook-rollback.md` cobre **3 cenários** distintos, com comandos e critérios de NÃO-rollback.
- [ ] `rollback.sh` executável, com validação de pré-condições.
- [ ] `simulacao-rollback.md` narra um cenário completo, incluindo flag como primeira linha.
- [ ] **2 migrations** (expand, contract) em SQL válido.
- [ ] `migrations-compatibilidade.md` com matriz mostrando compatibilidade entre versões.
- [ ] `cd.yml` com passos de expand e contract em fases distintas.
- [ ] **Admite limite**: se Postgres real não está no pipeline, declara explicitamente.

---

## Dicas

- **Migration idempotente é crítico.** Use `IF NOT EXISTS`, `ON CONFLICT DO NOTHING`, `WHERE col IS NULL`.
- **Contract nunca rode no mesmo deploy do expand.** Ponto.
- **Backup antes de contract** — recomende (e documente) mesmo se o padrão já é seguro.
- O runbook é escrito **para quem está de plantão de madrugada**. Clareza > elegância.

---

## Próximo passo

Última parada: **[Parte 5 — Plano de Transformação](parte-5-plano-transformacao.md)**, onde você amarra tudo num plano de 6 meses para a LogiTrack.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Feature Flags e Estratégia de Release](parte-3-feature-flags.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](../README.md) | **Próximo →**<br>[Parte 5 — Plano de Transformação e Projeção DORA](parte-5-plano-transformacao.md) |

<!-- nav:end -->

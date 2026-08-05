# Exercícios Resolvidos — Bloco 4

Exercícios do Bloco 4 ([Release Engineering, Versionamento e Rollback](04-release-engineering.md)).

---

## Exercício 1 — Decidir o bump SemVer

Para cada sequência de commits, informe a próxima versão a partir de `v2.3.4`.

### Caso A

```
feat(tracking): adiciona ETA precisa por transportadora
fix(billing): corrige arredondamento de centavos
docs(readme): atualiza exemplos
```

### Caso B

```
feat(api)!: remove endpoint /v1/pacotes

BREAKING CHANGE: clientes devem migrar para /v2/pacotes.
```

### Caso C

```
chore(deps): atualiza pydantic
test(billing): adiciona teste de borda
```

### Caso D

```
fix(tracking): trata null no callback da transportadora
fix(consulta): cache de 60s para listagem
perf(notif): reduz consumo de memória em 30%
```

### Solução

| Caso | Commits relevantes | Bump | Próxima versão |
|------|---------------------|------|----------------|
| A | `feat:` (MINOR) + `fix:` (PATCH) + `docs:` (none). **Maior vence.** | MINOR | **v2.4.0** |
| B | `feat!:` OU `BREAKING CHANGE:` ⇒ MAJOR | MAJOR | **v3.0.0** |
| C | `chore:` + `test:` — nenhum dos dois altera versão | NENHUM | **v2.3.4** |
| D | Três `fix/perf` — todos PATCH | PATCH | **v2.3.5** |

**Insight:** o **maior** bump entre os commits do intervalo define a bump final. Um único `feat!:` sobe MAJOR mesmo em meio a 200 `fix:`.

---

## Exercício 2 — Refazer schema com Expand/Contract

A LogiTrack quer **separar** o campo `endereco` (VARCHAR(255)) da tabela `pacote` em 3 colunas: `rua`, `numero`, `cidade`. Escreva os 3 deploys (Expand, Migrate, Contract), indicando **SQL** e **mudança de código**.

### Solução

**Estado atual (v1.0):**

```sql
-- tabela já existente
CREATE TABLE pacote (
    id SERIAL PRIMARY KEY,
    endereco VARCHAR(255) NOT NULL
);
```

Código v1.0: lê/escreve `endereco`.

---

**Deploy 1 — Expand (v1.1)**

SQL (`migrations/010_expand_endereco.sql`):

```sql
ALTER TABLE pacote
    ADD COLUMN IF NOT EXISTS rua VARCHAR(200),
    ADD COLUMN IF NOT EXISTS numero VARCHAR(20),
    ADD COLUMN IF NOT EXISTS cidade VARCHAR(100);

-- Backfill: faz melhor esforço parseando o campo antigo.
-- Idempotente: só popula onde as novas estão NULL.
UPDATE pacote
   SET rua    = split_part(endereco, ',', 1),
       numero = split_part(endereco, ',', 2),
       cidade = split_part(endereco, ',', 3)
 WHERE rua IS NULL AND numero IS NULL AND cidade IS NULL;
```

Código v1.1:

- **Lê** `endereco` (antigo).
- **Escreve** em `endereco` E nas 3 novas.
- Nunca lê `rua/numero/cidade` — ainda.

---

**Deploy 2 — Migrate (v1.2)**

Sem SQL (ou SQL opcional para adicionar NOT NULL / índice, se seguro).

Código v1.2:

- **Lê** das novas colunas (`rua/numero/cidade`). Fallback para `endereco` quando nulos (dados legados pendentes).
- **Escreve** nas novas E em `endereco` (ainda compatível com v1.0 e v1.1 rodando em paralelo durante rollout).

---

**Deploy 3 — Contract (v2.0 — breaking change interno; coluna removida)**

Pré-condição: **nenhuma versão v1.0 ou v1.1 ativa** em produção — confirmado monitorando o cluster por pelo menos 1 a 2 semanas após v1.2.

SQL (`migrations/020_contract_endereco.sql`):

```sql
-- ponto de não retorno: rollback para v1.x só via restore de backup.
ALTER TABLE pacote
    ALTER COLUMN rua SET NOT NULL,
    ALTER COLUMN numero SET NOT NULL,
    ALTER COLUMN cidade SET NOT NULL,
    DROP COLUMN endereco;
```

Código v2.0:

- **Só** lê/escreve `rua/numero/cidade`.

**Principais garantias:**

| Deploy | Estado do sistema | Compatível com versões anteriores? |
|--------|-------------------|-------------------------------------|
| v1.1 | 2 representações convivem | Sim (v1.0 segue funcionando) |
| v1.2 | 2 representações convivem | Sim (v1.1 segue funcionando) |
| v2.0 | Só nova representação | **Não** — rollback para v1.x quebra |

**Observação:** se a restrição de NOT NULL é arriscada (pode haver dados legados que escaparam do backfill), fazer um **deploy 2.5** que **verifica** antes de o deploy 3 aplicar NOT NULL.

---

## Exercício 3 — Decidir rollback vs forward fix

Para cada cenário, decida **rollback** ou **forward fix** e justifique em 2 a 3 linhas.

| # | Cenário |
|---|---------|
| 1 | Deploy há 5 min, 50x mais 5xx que baseline. Sem migration. |
| 2 | Deploy há 2h, bug retornando preço de frete com 2 casas decimais a mais. 30k pedidos processados. |
| 3 | Deploy há 40 min, canary em 15%, smoke detectou 503 na rota `/rastrear`. Nenhuma migration destrutiva. |
| 4 | Deploy há 1h15min, migration dropou coluna `status_legacy`. Bug no novo código. |
| 5 | Deploy há 10 min, mas é a versão com **expand** do Exercício 2. Bug na escrita dupla. |

### Solução

| # | Decisão | Justificativa |
|---|---------|---------------|
| 1 | **ROLLBACK** | Tempo curto, sem migration, impacto alto. Voltar para v-1 é seguro e restaura serviço. |
| 2 | **FORWARD FIX** | 2h já geraram dados inconsistentes no banco. Rollback não corrige os 30k pedidos; pode piorar (v-1 talvez cobre valor incorreto novamente). Melhor: v+1 corrigindo cálculo + script de reconciliação. |
| 3 | **ROLLBACK** (do canary, para 0%) | Canary existe exatamente para esse caso. Não é rollback de fleet inteiro — é "desligar canary". Depois, investigar e lançar v+1. |
| 4 | **FORWARD FIX** | Migration é **irreversível** sem restore de backup. v-1 espera coluna que não existe. Corrigir e lançar v+1 é o único caminho viável em tempo razoável. |
| 5 | **ROLLBACK** | Expand foi compatível — a v-1 ainda funciona com schema novo (ignora colunas novas). O bug está no código da v1.1 fazendo escrita dupla errada; voltar é seguro. |

**Padrão recorrente:** **migrations destrutivas** e **tempo decorrido** são os dois fatores que empurram para forward fix. Deploy recente, dados íntegros e schema compatível → rollback é a decisão certa.

---

## Exercício 4 — Classificar freezes

Para cada deploy freeze proposto, diga se é **legítimo** ou **muleta** e justifique.

| # | Freeze |
|---|--------|
| a | "Não deployar entre 23-11 e 01-12 por Black Friday" |
| b | "Deploy só terça e quinta, 10h às 16h" |
| c | "Congelar deploys durante auditoria ISO 27001 entre 15-06 e 30-06" |
| d | "Não deployar nunca em ano eleitoral" |
| e | "Freeze de 12h antes e depois do jogo da final do campeonato" (fintech que patrocina) |

### Solução

| # | Classificação | Justificativa |
|---|----------------|----------------|
| a | **Legítimo** | Datado, específico, justificável (pico de volume). Acabou, voltou ao normal. |
| b | **Muleta** | Norma permanente, sem justificativa específica; esconde falta de confiança no pipeline. |
| c | **Legítimo** | Datado (15 dias), motivo específico (auditoria), trilha de mudança congelada evita ruído. |
| d | **Muleta extrema** | "Ano inteiro" é permanente; motivo vago; força acúmulo de risco. |
| e | **Legítimo** | 24h janela específica, pico previsível de tráfego, proteção de receita. |

**Princípio sumarizado:** freeze deve ter **data**, **motivo** e **exceção** (o que prevalece sobre o freeze — hotfix de segurança, por exemplo).

---

## Exercício 5 — Runbook de rollback curto

Escreva um runbook de rollback para o serviço **Consulta** da LogiTrack. Deve ter no máximo 1 página, com comandos concretos (pode usar placeholders). Cubra 3 cenários.

### Solução

```markdown
# Runbook — Rollback do serviço Consulta

Responsável: on-call Tracking — Slack #ops-tracking

## Pré-condições

- Serviço usa **Blue-Green** via Nginx em `lb-01`.
- Variáveis: `$VERSION_PREV`, `$VERSION_CURR`.
- Ambos ambientes (blue, green) rodando o artefato desejado.

## Cenário A — Deploy acabou (< 15 min) e canary está degradado

1. **Desligue o canary** (flag):
   ```bash
   ssh lb-01 'export LOGITRACK_FLAG_CANARY_CONSULTA_PERCENT=0'
   ssh consulta-all 'systemctl reload consulta'
   ```
2. Monitore `dashboard-consulta` por 5 min.
3. Se métricas normalizaram → escreva incidente e agende v+1 com correção.

## Cenário B — Deploy há < 1h, sem migration destrutiva, erros amplos

1. **Chaveie o load balancer** para ambiente anterior:
   ```bash
   ssh lb-01 '/opt/lb/switch.sh blue'   # ou green, o que está ocioso
   ```
   Tempo esperado: **< 30 segundos**.
2. Abra incidente, notifique status page.
3. **NÃO** faça novo deploy até postmortem definir fix.

## Cenário C — Deploy há > 1h OU migration destrutiva aplicada

**NÃO faça rollback automático.** Rollback perderia dados ou quebraria schema.

1. Abra incidente crítico.
2. Acione líder técnico + DBA.
3. Trilhe **forward fix**:
   - Cria branch `hotfix/<descricao>` a partir da tag atual em prod.
   - Corrige.
   - Pipeline acelerado: merge → CI → bypass staging (**com aprovação dupla**) → prod.
4. Durante o fix, avalie se flags operacionais podem **mitigar** o impacto.

## Quando NUNCA dar rollback

- Migration com DROP de coluna/tabela já aplicada.
- Dados novos criados com nova schema > 2h.
- Cliente externo (transportadora) já consumiu v+1 da API pública.

## Comunicação

- Canal Slack `#status-logitrack`: aviso antes e depois.
- Status page público: atualizar a cada 15 min enquanto incidente aberto.
```

**Características que deve ter um bom runbook:**

- **Curto**, para ser útil sob pressão.
- **Comandos exatos**.
- **Critério para NÃO rodar rollback** (cenário C) — mais importante que o comando.
- **Comunicação** incluída.

---

## Exercício 6 — Instrumentar o pipeline para automatizar versionamento

O pipeline atual do Módulo 2 (`ci.yml` + `cd.yml`) computa versão manualmente. Você quer que, ao final do job `deploy-production`, uma **nova tag** `v{MAJOR}.{MINOR}.{PATCH}` seja criada **automaticamente** a partir dos Conventional Commits desde a última tag.

a) Liste os 5 passos no YAML que realizam isso.
b) Que cuidado tomar para **não** criar tags duplicadas?

### Solução

**a) Passos no YAML:**

```yaml
- name: Fetch all tags
  run: git fetch --tags --force

- name: Resolve last tag
  id: last_tag
  run: |
    LAST=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
    echo "last=${LAST}" >> "$GITHUB_OUTPUT"

- name: Decide next version
  id: next
  run: |
    NEXT=$(
      git log "${{ steps.last_tag.outputs.last }}..HEAD" \
        --format='%s%n%b%n--END--' \
      | python scripts/bump_semver.py "${{ steps.last_tag.outputs.last }}"
    )
    echo "next=${NEXT}" >> "$GITHUB_OUTPUT"

- name: Abort if no bump needed
  if: steps.next.outputs.next == steps.last_tag.outputs.last
  run: |
    echo "Nenhum commit relevante desde ${{ steps.last_tag.outputs.last }}. Pulando tag."
    exit 0   # encerra o step sem falhar

- name: Create and push tag
  if: steps.next.outputs.next != steps.last_tag.outputs.last
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    git config user.email "bot@logitrack.com"
    git config user.name  "logitrack-bot"
    git tag -a "${{ steps.next.outputs.next }}" -m "Release ${{ steps.next.outputs.next }}"
    git push origin "${{ steps.next.outputs.next }}"
```

**b) Cuidados contra tags duplicadas:**

1. **Verificar se a tag já existe antes de criar:**
   ```bash
   git rev-parse "refs/tags/${NEXT}" >/dev/null 2>&1 && exit 0
   ```
2. **Concurrency** no workflow, impedindo 2 rodadas simultâneas disputando a mesma tag:
   ```yaml
   concurrency:
     group: release-${{ github.ref }}
     cancel-in-progress: false
   ```
3. **Permissão** `contents: write` no workflow.
4. **Policy de proteção** em `main` para não permitir `push --tags` manual fora do pipeline.
5. **Idempotência**: se a tag já existe, o job termina sem erro — evita falhar quando há retry manual.

---

## Próximo passo

- Revise o **[Bloco 4](04-release-engineering.md)** se necessário.
- Mergulhe nos **[exercícios progressivos](../exercicios-progressivos/README.md)** — é hora de **construir**.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 4 — Release Engineering: Versionamento, Migrations e Rollback](04-release-engineering.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](../README.md) | **Próximo →**<br>[Exercícios Progressivos — Módulo 4](../exercicios-progressivos/README.md) |

<!-- nav:end -->

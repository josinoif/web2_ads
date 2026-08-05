# Bloco 3 — Exercícios resolvidos

> Leia [03-contratos-plataforma.md](./03-contratos-plataforma.md) antes.

---

## Exercício 1 — Capability catalog mínimo

**Enunciado.** Proponha um capability catalog com 4 capabilities para o Platform Team da OrbitaTech. Para cada, declare: interface, SLO interno, owner, preço relativo (1x/3x/10x).

**Resposta.**

```markdown
| Capability          | Interface                          | SLO interno               | Owner              | Preco (indice) |
|---------------------|------------------------------------|---------------------------|--------------------|----------------|
| postgres-db         | Scaffolder + CRD (DatabaseClaim)   | provisionamento <=10min p95 | platform-db        | 1x (bronze) / 3x (silver) / 10x (gold) |
| kafka-topic         | Scaffolder + CRD (TopicClaim)      | topic criado <=2min p95    | platform-stream    | 0.5x por topico (flat) |
| service-workload    | Score.dev spec + Helm standard     | deploy <=8min p95          | platform-runtime   | incluso no tier do app |
| observability-stack | auto-descoberta via labels         | 99.9% scrape; logs 7 dias bronze / 30 dias gold | platform-obs | incluso |
```

Observações:
- **Interface declarativa** (CRD, `score.yaml`, label auto-descoberta) > tickets.
- **Preço** como índice relativo, mesmo sem chargeback real.
- **Owner** subgrupo dentro do Platform Team (plausível em grupo de 8 pessoas: pares de 2).

---

## Exercício 2 — Escolher tier

**Enunciado.** Um novo serviço `notificacoes-push` da OrbitaTech envia notificações não-críticas (promoções), picos 500 req/s, falha aceitável de 0.5%. Qual tier? Justifique.

**Resposta.**

**Tier: Silver.**

- **Não é cliente crítico** (promoção); atraso ou perda ocasional é aceitável.
- **500 req/s com p95 razoável** não exige SLO 99,95% (gold); 99,9% já serve.
- **Bronze** (99%) significaria 7h fora/mês — inaceitável para um canal de comunicação mesmo promocional.
- Custo: 3x vs 10x (gold). Poupar 7x de infraestrutura é material quando falamos de um serviço de pico 500 rps.

Reavaliar em 6 meses se uso mudar (ex.: virou notificação transacional → gold).

---

## Exercício 3 — Rascunho de RFC

**Enunciado.** Escreva um RFC curto (1 página) para a proposta *"Adotar Score.dev como spec padrão de workload para golden path `python-fastapi`"*.

**Resposta.**

```markdown
# RFC-007: Adotar Score.dev como spec de workload no golden path python-fastapi

- Status: review
- Proponente: @platform-runtime
- Data: 2026-04-15
- Janela de revisao: ate 2026-04-29

## Contexto e problema
Os golden paths atuais geram Helm chart direto. Em 6 meses a plataforma
devera suportar tambem Nomad para workloads batch. Sem abstracao, teriamos
templates duplicados.

## Motivacao
- Desacoplar intencao (workload do squad) de implementacao (K8s hoje).
- Reduzir manutencao de templates.
- Alinhar com tendencia CNCF (Score esta em sandbox; Humanitec backed).

## Proposta
- Templates python-fastapi passam a gerar `score.yaml` + CI que aplica via `score-compose` localmente e `humanitec`/ custom operator em staging/prod.
- Helm chart gerado sera interno (platform-side), oculto do squad.

## Alternativas consideradas
- Manter Helm como superficie visivel: mais simples hoje, porem acoplado.
- Usar OAM (Open Application Model): perdeu tracao.
- Criar nosso proprio CRD: N.I.H. (reinvencao).

## Impacto
- Squads ja existentes: nenhum, enquanto nao migrarem.
- Novos servicos via golden path: mudanca transparente (score.yaml no repo, nada mais).
- Platform Team: ~3 pessoas-semana para implementar conversor score->helm.

## Rollout
- Sprint 1: POC (1 squad piloto).
- Sprint 2: GA em golden path python-fastapi.
- Sprint 3: avaliar migracao para go-http.

## Revisao
Comentarios no PR #PR-NNN; decisao em reuniao 2026-04-29.
```

**Características**:
- Problema sem solução antes da proposta.
- Alternativas explícitas — mostra pensamento.
- Rollout faseado.
- Data de decisão clara.

---

## Exercício 4 — Validar catálogo

**Enunciado.** Crie um catálogo mínimo (3 arquivos) com erros propositais e rode `catalog_validator.py`.

**Arquivo `catalog/groups.yaml`:**

```yaml
apiVersion: backstage.io/v1alpha1
kind: Group
metadata:
  name: squad-pagamentos
spec:
  type: team
```

**Arquivo `catalog/services/pix-core.yaml`:**

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: pix-core
  tags: [python]
spec:
  type: service
  lifecycle: production
  owner: group:default/squad-pagamentos
  dependsOn:
    - resource:default/ledger-db-INEXISTENTE
```

**Arquivo `catalog/services/relatorios.yaml`:**

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: relatorios
spec:
  type: service
  lifecycle: stable               # invalido
  owner: squad-sem-grupo          # formato incorreto
```

Rodar:

```bash
python catalog_validator.py catalog/
```

**Saída esperada:**

```
Validacao de catalogo
severidade  entidade             regra        mensagem
high        Component/pix-core   TIER-PROD    production exige exatamente uma tag tier-{bronze,silver,gold}
high        Component/relatorios OWNER-FMT    owner deve comecar com 'group:'
high        Component/relatorios LIFECYCLE    lifecycle invalido: stable
medium      Component/pix-core   DEP-UNK      dependsOn 'resource:default/ledger-db-INEXISTENTE' nao encontrado no catalogo
```

Exit 1 (HIGH).

**Correções:**

- `pix-core`: adicionar tag `tier-gold` (é crítico).
- `relatorios`: `owner: group:default/squad-relatorios` (e criar esse grupo).
- `relatorios`: `lifecycle: production` (ou `experimental`).
- `pix-core`: criar o Resource `ledger-db` no catálogo ou corrigir referência.

---

## Exercício 5 — Deprecation plan

**Enunciado.** A plataforma quer remover o template antigo `flask-service` (só 2 squads usam; 1 já migrou). Escreva o plano de deprecation em 1 página.

**Resposta.**

```markdown
# RFC-009: Deprecation do template flask-service

- Status: accepted
- Data de anuncio: 2026-04-20
- Sunset date: 2026-10-20 (6 meses)
- Proponente: @platform-runtime

## Motivacao
- Flask nao e mais golden path; python-fastapi o substitui desde 2025.
- Manutencao dupla custa ~0.5 FTE do Platform Team.
- Apenas 1 squad ativamente usa (condominios).
- CVEs e correcoes agora mais demoradas no stack legado.

## Quem e afetado
Catalog query: `tags:flask` e `template:flask-service`.
- squad-condominios: 2 servicos.
- squad-tools: 1 servico (ja migrando).

## Alternativa
Migrar para template python-fastapi. Guia em docs/migracao-flask-fastapi.md.

## Cronograma
- 2026-04-20: anuncio; template marcado como [deprecated] no portal.
- 2026-06-01: novos servicos em flask-service *bloqueados* (Scaffolder esconde).
- 2026-08-01: alertas semanais para squads que ainda usam.
- 2026-10-20: remocao do template. Servicos ainda em flask continuam rodando, mas sem suporte, sem CVE scan automatico, sem image base atualizada.

## Suporte a migracao
- Office hours (ter/qui 10h) por Platform Runtime.
- Script de migracao automatica para 80% dos casos.
- Pair programming para casos complexos.

## Consequencia se nao migrar
- Sem atualizacao de base image -> CVEs acumulam.
- Sem template -> fixes dependem do squad.
- Custo operacional migra para o squad.
```

---

## Exercício 6 — Matriz de responsabilidade

**Enunciado.** Um dev reclama: *"A aplicacao caiu porque o Kubernetes reciclou o Pod. Isso e problema da plataforma, nao meu."* Como você (líder Platform) responde, com base em matriz de responsabilidades?

**Resposta.**

```markdown
Entendo a frustracao. Vamos olhar o que aconteceu com a matriz na mao.

**O que e responsabilidade da plataforma (meu time):**
- O cluster K8s estar operacional. Esta - nenhum outro servico foi afetado.
- A imagem base hardened. Esta atualizada.
- O Helm standard dar suporte a PodDisruptionBudget, HPA, probes. Esta.

**O que e responsabilidade do squad (seu time):**
- Configurar probes (liveness/readiness) corretamente.
- Definir PDB adequado ao tier (para gold, PDB e default).
- Implementar graceful shutdown no app.
- Escolher tier (voce escolheu bronze).

O Pod foi reciclado durante roll node update (rotina documentada). Em
**bronze** nao temos PDB nem multi-replica; qualquer reciclagem causa
downtime. Isso esta no contrato do tier bronze (documentado).

**Opcoes:**
1. Aceitar o downtime ocasional (bronze continua).
2. Migrar para silver (3x custo). PDB + 2 replicas eliminam o problema.
3. Corrigir probes e graceful shutdown (inclui voce; plataforma ajuda com template).

Vamos ter uma call para decidir? Tenho horario amanha as 14h.
```

**Chave**: resposta **baseada em contrato** (tier bronze sem PDB). Sem culpar. Oferece caminhos claros. Platform Team **ajuda** — mas responsabilidade fica clara.

---

## Autoavaliação

- [ ] Defino capability com interface, SLO, owner, custo.
- [ ] Escolho tier com justificativa.
- [ ] Escrevo RFC curto e objetivo.
- [ ] Valido catálogo com `catalog_validator.py`.
- [ ] Planejo deprecation com prazo, suporte, consequência.
- [ ] Respondo a squad com base em matriz de responsabilidade, sem culpar.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Service Catalog e Contratos de Plataforma](03-contratos-plataforma.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Bloco 4 — Métricas de Plataforma: DORA, SPACE, DevEx e NPS interno](../bloco-4/04-metricas-plataforma.md) |

<!-- nav:end -->

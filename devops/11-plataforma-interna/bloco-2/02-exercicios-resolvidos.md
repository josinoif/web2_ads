# Bloco 2 — Exercícios resolvidos

> Leia [02-backstage-golden-paths.md](./02-backstage-golden-paths.md) antes.

---

## Exercício 1 — Modelar `catalog-info.yaml`

**Enunciado.** Escreva um `catalog-info.yaml` completo para o serviço `aluguel-marketplace` da OrbitaTech, que:
- Provê API HTTP `aluguel-marketplace-http-v2`.
- Depende de banco `marketplace-db` e serviço `score-inquilino`.
- Pertence ao System `aluguel` dentro do Domain `locacao`.
- É mantido pelo grupo `squad-aluguel`.
- É production.

**Resposta.**

```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: aluguel-marketplace
  title: "Aluguel Marketplace"
  description: "Core do marketplace de alugueis (listagem, busca, matching)."
  tags: [python, django, production, tier-gold]
  annotations:
    github.com/project-slug: orbita/aluguel-marketplace
    backstage.io/techdocs-ref: dir:.
    grafana/dashboard-selector: "service=aluguel-marketplace"
  links:
    - url: https://grafana.orbita.example/d/aluguel
      title: Dashboard
      icon: dashboard
spec:
  type: service
  lifecycle: production
  owner: group:default/squad-aluguel
  system: aluguel
  providesApis:
    - aluguel-marketplace-http-v2
  dependsOn:
    - resource:default/marketplace-db
    - component:default/score-inquilino
---
apiVersion: backstage.io/v1alpha1
kind: API
metadata:
  name: aluguel-marketplace-http-v2
  description: "API HTTP publica do marketplace (autenticada)."
spec:
  type: openapi
  lifecycle: production
  owner: group:default/squad-aluguel
  system: aluguel
  definition:
    $text: https://github.com/orbita/aluguel-marketplace/blob/main/openapi.yaml
---
apiVersion: backstage.io/v1alpha1
kind: Resource
metadata:
  name: marketplace-db
spec:
  type: postgres-db
  owner: group:default/platform-team
  system: aluguel
---
apiVersion: backstage.io/v1alpha1
kind: System
metadata:
  name: aluguel
spec:
  owner: group:default/squad-aluguel
  domain: locacao
---
apiVersion: backstage.io/v1alpha1
kind: Domain
metadata:
  name: locacao
spec:
  owner: group:default/locacao-chapter
---
apiVersion: backstage.io/v1alpha1
kind: Group
metadata:
  name: squad-aluguel
spec:
  type: team
  profile:
    displayName: Squad Aluguel
  parent: locacao-chapter
  children: []
```

Múltiplas entidades num arquivo separadas por `---`. Esse formato importa **tudo de uma vez** quando registrado.

---

## Exercício 2 — Listar perguntas de um Scaffolder

**Enunciado.** Projete o conjunto de **parameters** para o template `novo-topico-kafka` (golden path "novo tópico Kafka"). Limite: **máximo 6 perguntas**.

**Resposta.**

```yaml
parameters:
  - title: Identificacao
    required: [name, owner, team_email]
    properties:
      name:
        title: Nome do topico
        type: string
        pattern: "^[a-z][a-z0-9-]{3,60}$"
        description: "Ex.: aluguel.pagamentos.confirmados (use dot notation)."
      owner:
        title: Squad owner
        type: string
        ui:field: OwnerPicker
        ui:options:
          catalogFilter:
            kind: Group
      team_email:
        title: Email do time (on-call)
        type: string
        format: email

  - title: Configuracao
    required: [tier, partitions]
    properties:
      tier:
        title: Tier de servico
        type: string
        enum: [bronze, silver, gold]
        description: "gold = SLO >= 99,95%, replicas 3; silver = 99,9%; bronze = 99%."
      partitions:
        title: Particoes
        type: integer
        minimum: 1
        maximum: 32
        default: 3
      retention_days:
        title: Retencao (dias)
        type: integer
        minimum: 1
        maximum: 365
        default: 7
```

**6 perguntas**, com defaults razoáveis para evitar paralisia:

1. `name` (obrigatório, validado).
2. `owner` (do catálogo).
3. `team_email` (para auditoria e on-call).
4. `tier` (enumerado; evita roda livre).
5. `partitions` (com default 3).
6. `retention_days` (com default 7).

**Princípios**:
- Nada de "Comentário adicional (opcional)" — se ninguém preenche, removemos.
- Defaults sensatos cobrem 80% dos casos.
- Enum > texto livre sempre que possível.
- Pattern em nomes previne caos.

---

## Exercício 3 — Auditar template

**Enunciado.** Crie um template propositalmente incompleto em `/tmp/bad-template/template.yaml` e rode `template_audit.py`:

**Template ruim:**

```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: bad-template
spec:
  type: service
  parameters:
    - properties:
        name:
          type: string
  steps:
    - id: tpl
      action: fetch:template
      input:
        url: ./skeleton
```

Sem `skeleton/`.

**Saída esperada:**

```
Auditoria de template em /tmp/bad-template
severidade  regra           mensagem
high        META-DESC       metadata.description obrigatoria para exibicao no portal
high        SPEC-OWNER      spec.owner obrigatorio para accountability
high        PARAM-OWNER     parametros devem ter 'owner'
high        STEP-PUBLISH    falta step publish:* (github, gitlab...)
high        STEP-CATALOG    falta step catalog:register para aparecer no Software Catalog
high        SKEL-CATALOG    skeleton/catalog-info.yaml ausente; repositorio gerado nao entra no catalogo
medium      OUTPUT-ENTITYREF output sem entityRef; usuario nao volta para o catalogo
medium      SKEL-README     skeleton/README.md ausente; repositorio nasce sem docs
low         META-TAGS       metadata.tags vazio; dificulta descoberta
```

Exit 1 (high). Correções: preencher description, owner, parameter owner, adicionar `publish:github`, `catalog:register`, criar `skeleton/catalog-info.yaml` e `skeleton/README.md`, adicionar output entityRef.

---

## Exercício 4 — Golden path ou módulo opcional?

**Enunciado.** Diga se cada item deve (a) entrar no golden path `python-fastapi`, (b) ser opção no scaffolder, ou (c) ficar fora. Justifique.

1. `pytest` instalado e 1 teste de exemplo.
2. Cliente de Redis configurado (30% dos serviços usam Redis).
3. Integração com PagerDuty (5 squads têm; 90% não).
4. Plugin ArgoCD no CI (100% usam ArgoCD).
5. Dockerfile alpine + Python 2.7 (legado).

**Respostas.**

1. **Golden path (default).** Test-first é princípio não-negociável.
2. **Opção no Scaffolder** (`include_redis: true`). Nem todos precisam; forçar cria clutter.
3. **Fora.** Minoria; se precisar, squad adiciona depois. Podem ser biblioteca/capability separada.
4. **Golden path.** Uso universal = default razoável.
5. **Fora, com orientação para **deprecar**.** Python 2.7 end-of-life; plataforma não perpetua.

---

## Exercício 5 — TechDocs estrutura

**Enunciado.** Proponha a estrutura `docs/` (com `mkdocs.yml`) para um serviço `pix-core`, cobrindo: introdução, arquitetura, API, SLOs, runbook, onboarding do dev novo.

**Resposta.**

`mkdocs.yml`:

```yaml
site_name: pix-core
docs_dir: docs
nav:
  - Introducao: index.md
  - Arquitetura: arquitetura.md
  - API: api.md
  - SLOs: slos.md
  - Runbook: runbook.md
  - Onboarding: onboarding.md
plugins:
  - techdocs-core
```

`docs/index.md`:

```markdown
# pix-core

Servico responsavel pelo envio e recebimento de PIX na OrbitaTech.

## Links rapidos
- [Dashboard](https://grafana.orbita/d/pix)
- [On-call](./runbook.md)
- [API](./api.md)
```

`docs/onboarding.md`:

```markdown
# Onboarding ao servico (dev novo)

## Em 30 minutos voce consegue
1. Clonar `pix-core` e rodar `make up` (`docker compose up`).
2. Ver `/healthz` em `http://localhost:8080/healthz`.
3. Rodar a suite: `make test`.

## Em 2 dias voce consegue
- Fazer um PR que altere um comportamento com teste.
- Acompanhar o deploy automatico em staging.

## Em 2 semanas voce consegue
- Ficar em on-call secundario.
- Ler dashboards e runbook sem ajuda.
```

---

## Exercício 6 — Migração incremental

**Enunciado.** A OrbitaTech tem 47 serviços legados, cada um com pipeline própria. Você publicou o golden path. Como migrar os 47 sem forçar, mantendo adoção voluntária?

**Resposta — plano de 4 sprints:**

1. **Sprint 1 — Oferta clara.** Publicar template; rodar 3 casos-piloto com squads que já pediam melhoria. Documentar economia de tempo (se antes demoravam 5 dias para criar serviço, agora 2h).
2. **Sprint 2 — Shadow run.** Oferecer *migration script* que converte um serviço legado em formato golden path; rodar em dois serviços que squads aceitem (low-risk). Publicar antes/depois.
3. **Sprint 3 — Consumption-based.** Oferecer **vantagens** para quem migrar: dashboards prontos, CVE auto-scan, relatórios FinOps, alertas de SLO — coisas que o "legado" não ganha. Dor de não migrar cresce naturalmente.
4. **Sprint 4 em diante — Deprecation.** Declarar em RFC: suporte a modelos antigos termina em **6 meses**; ferramentas centrais (bot de CVE, scanner LGPD) só rodam sobre golden path. Quem quiser ficar, pode — mas carrega o custo.

**Princípios:**
- Nunca forçar no início.
- **Benefícios** derretem resistência; **proibição** sem benefício vira ressentimento.
- Deprecation é legítima, mas **longa** e comunicada.

---

## Autoavaliação

- [ ] Escrevo `catalog-info.yaml` completo com relations e owner.
- [ ] Defino parameters de Scaffolder com no máx. 6 perguntas significativas.
- [ ] Estruturo `skeleton/` funcional (CI, Dockerfile, catalog-info, docs).
- [ ] Publico TechDocs relevante com seções-chave.
- [ ] Audito template com `template_audit.py`.
- [ ] Distingo *golden path default*, *opção*, *fora*.
- [ ] Desenho migração incremental sem forçar, com deprecation planejada.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 2 — Backstage e Golden Paths](02-backstage-golden-paths.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Bloco 3 — Service Catalog e Contratos de Plataforma](../bloco-3/03-contratos-plataforma.md) |

<!-- nav:end -->

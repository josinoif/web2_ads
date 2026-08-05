# Parte 2 — Backstage e Software Catalog

**Objetivo.** Subir o portal Backstage localmente e popular o Software Catalog com ≥ 8 entidades representando a OrbitaTech.

**Pré-requisitos.** Parte 1 concluída. Node 20+, yarn.

**Entregáveis em `orbita-idp/`:**

1. `idp/` — app Backstage gerado com `create-app`.
2. `catalog/` — arquivos YAML do catálogo (≥ 8 entidades).
3. `docs/catalog-guia.md` — guia para squads registrarem serviços.
4. `Makefile` com `portal-up`, `catalog-validate`.
5. Screenshot do portal com pelo menos 1 System Graph populado.

---

## 2.1 Criar o app Backstage

```bash
cd orbita-idp
npx @backstage/create-app@latest --path idp
# Nome: orbita-idp
cd idp
yarn install
```

Edite `app-config.yaml` para apontar catálogo local:

```yaml
catalog:
  rules:
    - allow: [Component, API, Resource, System, Domain, Group, User, Location]
  locations:
    - type: file
      target: ../catalog/all.yaml
```

Rode:

```bash
yarn dev
# abrir http://localhost:3000
```

## 2.2 Popular o catálogo

Crie `catalog/all.yaml` com `Location` kinds apontando para subdirs:

```yaml
apiVersion: backstage.io/v1alpha1
kind: Location
metadata:
  name: orbita-groups
spec:
  type: file
  targets:
    - ./groups.yaml
---
apiVersion: backstage.io/v1alpha1
kind: Location
metadata:
  name: orbita-services
spec:
  type: file
  targets:
    - ./services/aluguel-marketplace.yaml
    - ./services/score-inquilino.yaml
    - ./services/condominios-core.yaml
    - ./services/notificacoes.yaml
    - ./services/ledger.yaml
    - ./services/pix-core.yaml
---
apiVersion: backstage.io/v1alpha1
kind: Location
metadata:
  name: orbita-resources
spec:
  type: file
  targets:
    - ./resources/marketplace-db.yaml
    - ./resources/ledger-db.yaml
    - ./resources/kafka-eventos.yaml
```

Para cada serviço, arquivo completo (modelo no Exercício 1 do Bloco 2).

Entidades **mínimas** exigidas (≥ 8):
- 5 Components (serviços).
- 2 Resources (DB, Kafka).
- 1 System (p.ex. "aluguel").
- Pelo menos 1 Domain.
- Pelo menos 3 Groups (squad-aluguel, squad-pagamentos, platform-team).
- 1 API (opcional mas recomendado).

## 2.3 Adicionar TechDocs

- Pelo menos **1 serviço** com `mkdocs.yml` e `docs/` completos.
- Annotation `backstage.io/techdocs-ref: dir:.` em seu `catalog-info.yaml`.
- Verificar aba "Docs" no portal.

## 2.4 Guia para squads

`docs/catalog-guia.md` mostra como um squad adiciona seu serviço:

1. Copiar template de `catalog-info.yaml`.
2. Editar metadados.
3. Abrir PR em `orbita-idp`.
4. Após merge, catálogo atualiza em <= 5 min.

Inclui seção "campos obrigatórios" e "erros comuns".

## 2.5 Makefile

```makefile
.PHONY: portal-up portal-build catalog-validate

portal-up:
	cd idp && yarn dev

portal-build:
	cd idp && yarn build

catalog-validate:
	python ../bloco-3/catalog_validator.py catalog/
```

---

## Critérios de aceitação da Parte 2

- [ ] `yarn dev` sobe o portal em http://localhost:3000 sem erro.
- [ ] Catálogo exibe ≥ 8 entidades.
- [ ] Ao menos 1 componente com TechDocs renderizando.
- [ ] Owner e relations corretos (testado no System Graph).
- [ ] `make catalog-validate` retorna exit 0 (catálogo válido).
- [ ] `docs/catalog-guia.md` claro para um dev externo seguir.
- [ ] Screenshot incluído em `docs/screenshots/portal.png`.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 1 — Estratégia, personas e Team Topologies](parte-1-estrategia.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Parte 3 — Golden paths: dois templates funcionais](parte-3-golden-paths.md) |

<!-- nav:end -->

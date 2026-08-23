# Mapa canônico — Linhas P e A (`loja-api`)

Documento de referência da jornada NestJS com **e-commerce em duas velocidades**.

**Narrativa da jornada:** [README — Sinopse e episódios](README.md). Este arquivo é o **contrato** HTTP / linhas P e A — em conflito com o tutorial, **o mapa prevalece**. **Travou na implementação?** Compare com o [gabarito de verificação — linha P](SOLUCAO-P.md).

| Linha | Nome | Obrigatória? | Regra |
|-------|------|--------------|--------|
| **P** | Principal | Sim | Ao fim de cada capítulo a API sobe e os curls de P passam. O capítulo seguinte **só depende de P**. |
| **A** | Alternativa (desafio) | Não | Amplia o domínio. Pode usar tudo de P. **Nunca** é importada por código da linha P. |

**Projeto:** `loja-api` (NestJS 10 + TypeScript).  
**Banco:** **PostgreSQL 16** (Docker). Driver: `pg`.  
**Base URL:** `http://localhost:3000`  
**Auth (a partir do cap. 6):** `Authorization: Bearer <access_token>`

---

## Entidades

### Núcleo P (sempre)

| Entidade | Campos mínimos | Surgem no |
|----------|----------------|-----------|
| `Product` | `id`, `name`, `price`, `stock` (+ `imageFilename` no Cap. 9) | Cap. 2 (memória) → 5 (DB) |
| `User` | `id`, `username`, `email`, `password`, `role` | Cap. 6 (`role` efetivo no 7) |
| `Order` | `id`, `userId`, `status`, `createdAt` | Cap. 5.1 |
| `OrderItem` | `id`, `orderId`, `productId`, `quantity`, `unitPrice` | Cap. 5.1 |

`status` do pedido em P: `OPEN` \| `PAID` \| `CANCELLED` (em P, criação sempre `OPEN`; transição `PAID`/`CANCELLED` pode ser simplificada até o cap. A de pagamento).

### Linha A (opcional, por capítulo)

| Entidade / recurso | Capítulo A |
|--------------------|------------|
| Busca / `PATCH` em produto | 2 |
| DTOs extras / aninhados | 2.1 |
| `CatalogService` (agregação) | 3 |
| `Category` | 5 |
| Regras de estoque no pedido | 5.1 |
| `GET /auth/me` ou refresh | 6 |
| Role `MANAGER` | 7 |
| Docs das rotas A | 8 |
| Galeria de imagens | 9 |
| Specs das features A | 10 |
| `Address`, `Payment`, cupom… | Capstone |

---

## Módulos sugeridos

```text
src/
  products/          # P (+ rotas A de busca/categoria se existirem)
  orders/            # P (a partir de 5.1)
  auth/              # P (a partir de 6)
  categories/        # só A (cap. 5)
  payments/          # só A (capstone / desafio)
  addresses/         # só A (capstone / desafio)
```

`AppModule` da trilha oficial importa só módulos P. Módulos A o aluno adiciona ao fazer o desafio.

---

## Legenda das tabelas de rotas

| Coluna | Significado |
|--------|-------------|
| Auth | `-` público · `JWT` autenticado · `ADMIN` / `CLIENT` papel exigido |
| Body / Query | Contrato mínimo |
| Resposta | Status HTTP esperado no caminho feliz |

---

## Cap. 0 — TypeScript para Nest

Sem rotas. Checkpoint: checklist de leitura do material.

---

## Cap. 1 — Nest + primeira app

### P

| Método | Rota | Auth | Resposta |
|--------|------|------|----------|
| `GET` | `/health` | - | `200` `{ "status": "ok" }` |

**Arquivos:** `main.ts`, `app.module.ts`, controller de health (ou `AppController`).

### A (opcional)

| Método | Rota | Auth | Notas |
|--------|------|------|-------|
| `GET` | `/health/version` | - | `{ "name": "loja-api", "version": "0.1.0" }` lido de `package.json` ou constante |

**Se pular A:** cap. 2 só precisa de `/health` e do projeto criado.

---

## Cap. 2 — Controllers (produtos em memória)

Persistência: **array em memória** no controller ou stub; service completo fica no cap. 3.

### P

| Método | Rota | Auth | Body / params | Resposta |
|--------|------|------|---------------|----------|
| `GET` | `/products` | - | - | `200` `Product[]` |
| `GET` | `/products/:id` | - | `id` | `200` produto ou `404` |
| `POST` | `/products` | - | `{ "name", "price", "stock" }` | `201` produto |
| `PUT` | `/products/:id` | - | body completo | `200` produto |
| `DELETE` | `/products/:id` | - | - | `204` |

### A (opcional)

| Método | Rota | Auth | Body / query | Resposta |
|--------|------|------|--------------|----------|
| `GET` | `/products?q=` | - | `q` substring do nome | `200` filtrado |
| `PATCH` | `/products/:id` | - | body parcial | `200` produto |

**Se pular A:** cap. 2.1 valida só o CRUD P (`POST`/`PUT` completos).

---

## Cap. 2.1 — DTOs e validação

Mesmas rotas P do cap. 2; o contrato passa a ser **DTO + `ValidationPipe`**.

### P

| DTO | Usado em |
|-----|----------|
| `CreateProductDto` | `POST /products` — `name` string min 2; `price` number > 0; `stock` int ≥ 0 |
| `UpdateProductDto` | `PUT /products/:id` — mesmo contrato (substituição total) |
| `PatchProductDto` (A) | `PATCH /products/:id` — `PartialType(CreateProductDto)` |

`main.ts`: `ValidationPipe` com `whitelist`, `forbidNonWhitelisted`, `transform`.

| Caso de teste | Esperado |
|---------------|----------|
| Body válido | `201` / `200` |
| Campo extra | `400` |
| `price` ≤ 0 ou tipo errado | `400` |

### A (opcional)

| Recurso | Detalhe |
|---------|---------|
| `PatchProductDto` via `PartialType` no `PATCH` (se fez A do cap. 2) | |
| `ListProductsQueryDto` | `q?`, `minPrice?`, `maxPrice?` em `GET /products` |
| Mensagens `message` customizadas nos decorators | |

**Se pular A:** cap. 3/5 usam só `CreateProductDto` / update completo.

---

## Cap. 3 — Services, DI e Modules

### P

Rotas **idênticas** ao cap. 2 (P). Mudança interna:

- `ProductsController` → `ProductsService`
- `ProductsModule` com `controllers` + `providers`
- `AppModule` importa `ProductsModule`

### A (opcional)

| Método | Rota | Auth | Resposta |
|--------|------|------|----------|
| `GET` | `/catalog/summary` | - | `200` `{ "totalProducts", "totalStockUnits" }` |

Implementação: `CatalogService` injeta `ProductsService` (demonstra DI entre services).

**Se pular A:** persistência (cap. 5) só refatora `ProductsService`.

---

## Cap. 4 — Persistência (conceitos)

Sem novas rotas obrigatórias. Checkpoint conceitual (entidade × DTO, `forRoot` / `forFeature`, `synchronize`).

### A (opcional)

Diagrama / texto: `Category` 1:N `Product` — **sem** implementar ainda (implementação no A do cap. 5).

---

## Cap. 5 — CRUD produtos + PostgreSQL

Mesmas rotas P do cap. 2, agora com **TypeORM** + entidade `Product` + **PostgreSQL**.

### P

| Método | Rota | Auth | Resposta |
|--------|------|------|----------|
| `GET` | `/products` | - | `200` |
| `GET` | `/products/:id` | - | `200` / `404` (`NotFoundException`) |
| `POST` | `/products` | - | `201` + DTO do 2.1 |
| `PUT` | `/products/:id` | - | `200` / `404` |
| `DELETE` | `/products/:id` | - | `204` / `404` |

Docker PostgreSQL + `TypeOrmModule` conforme tutorial (`docker-compose.postgres.yml` nesta pasta).

### A (opcional) — categorias

| Método | Rota | Auth | Body | Resposta |
|--------|------|------|------|----------|
| `POST` | `/categories` | -* | `{ "name" }` | `201` |
| `GET` | `/categories` | - | - | `200` |
| `GET` | `/categories/:id` | - | - | `200` / `404` |
| `PUT` | `/categories/:id` | - | `{ "name" }` | `200` |
| `DELETE` | `/categories/:id` | - | - | `204` |
| `GET` | `/categories/:id/products` | - | - | `200` produtos da categoria |
| `PATCH` | `/products/:id/category` | - | `{ "categoryId" }` | `200` associa FK |

\* Até o cap. 6/7 essas rotas A podem ficar públicas; depois o aluno restringe a `ADMIN` se quiser.

**Se pular A:** `Product` sem `categoryId`; pedidos (5.1) não dependem de categoria.

---

## Cap. 5.1 — Pedidos (núcleo P do checkout)

Pode ser seção final do cap. 5 ou arquivo `5.1.pedidos.md`. **Obrigatório na linha P** para o e-commerce fazer sentido antes de auth (criação “anônima” **não** — pedidos entram de fato protegidos no cap. 6; neste capítulo a API de pedidos pode existir e ser aberta temporariamente **ou** já documentar que no 6 exige JWT).

**Decisão canônica:** no 5.1 as rotas de pedido existem e funcionam **sem** JWT (usuário ainda não existe). No cap. 6, `userId` passa a vir do token e as mutações/listagens exigem JWT. Assim o 5.1 não bloqueia quem ainda não viu auth, e o 6 só **endurece** o mesmo contrato.

### P

| Método | Rota | Auth (5.1) | Auth (após 6) | Body | Resposta |
|--------|------|------------|---------------|------|----------|
| `POST` | `/orders` | - | `JWT` | `{ "items": [ { "productId", "quantity" } ] }` | `201` pedido + itens; debita `stock` |
| `GET` | `/orders` | - | `JWT` | - | `200` lista (**após 7:** próprios; **ADMIN** vê todos) |
| `GET` | `/orders/:id` | - | `JWT` | - | `200` / `404` (**após 7:** só se for dono ou ADMIN) |
| `POST` | `/orders/:id/cancel` | - | `JWT` | - | `200` status `CANCELLED`; devolve estoque se `OPEN` |

Regras P ao criar:

1. Todo `productId` existe.
2. `quantity` ≥ 1 e ≤ `stock`.
3. Snapshot `unitPrice` = preço atual do produto.
4. `stock` decrementado atomicamente o suficiente para a aula (transação simples ou checks no service).

### A (opcional)

| Método | Rota | Notas |
|--------|------|-------|
| `PATCH` | `/orders/:id/status` | Body `{ "status" }` com máquina de estados (`OPEN`→`PAID`\|`CANCELLED`) |
| — | — | Rejeitar pedido se estoque insuficiente com mensagem de domínio clara |
| — | — | Impedir cancelar se já `PAID` |

**Se pular A:** só `OPEN` + `cancel`; sem transição `PAID` até pagamento (capstone).

---

## Cap. 6 — Autenticação JWT

Ordem de estudo após 5/5.1 (upload/Swagger ficam depois na jornada).

### P

| Método | Rota | Auth | Body | Resposta |
|--------|------|------|------|----------|
| `POST` | `/auth/register` | - | `{ "username", "email", "password" }` | `201` usuário **sem** `password` (`role` default `CLIENT`) |
| `POST` | `/auth/login` | - | `{ "username", "password" }` | `200` `{ "access_token" }` |

**Endurecimento das rotas P existentes:**

| Método | Rota | Auth |
|--------|------|------|
| `POST` | `/products` | `JWT` |
| `PUT` | `/products/:id` | `JWT` |
| `DELETE` | `/products/:id` | `JWT` |
| `GET` | `/products`, `/products/:id` | - (público) |
| `POST` | `/orders` | `JWT` |
| `GET` | `/orders`, `/orders/:id` | `JWT` |
| `POST` | `/orders/:id/cancel` | `JWT` |

Pedido: `userId` = `sub` do JWT (ignorar `userId` no body).

### A (opcional)

| Método | Rota | Auth | Resposta |
|--------|------|------|----------|
| `GET` | `/auth/me` | `JWT` | `200` `{ "userId", "username", "email", "role" }` |
| `POST` | `/auth/refresh` | refresh token | `200` novo `access_token` (se implementar par de tokens) |

**Se pular A:** cap. 7 usa só login + payload com `role`.

**Não fazer em P:** aceitar `role` no body de `register` (privilege escalation). Admin via seed/SQL.

---

## Cap. 7 — Autorização (roles)

Roles P: `ADMIN` \| `CLIENT`.

### P — matriz de acesso

| Rota | `CLIENT` | `ADMIN` |
|------|----------|---------|
| `GET /products`, `GET /products/:id` | sim | sim |
| `POST/PUT/DELETE /products` | não `403` | sim |
| `POST /orders`, `GET /orders` (próprios), `GET /orders/:id` (próprio), cancel próprio | sim | sim |
| `GET /orders` (todos) | não | sim (opcional na mesma rota com branch no service) |

Rotas didáticas extras (como no material atual de roles), opcionais para demo:

| Método | Rota | Auth |
|--------|------|------|
| `GET` | `/demo/admin` | `JWT` + `ADMIN` |
| `GET` | `/demo/client` | `JWT` + `CLIENT` |

### A (opcional)

| Recurso | Detalhe |
|---------|---------|
| Role `MANAGER` | Pode `PUT` produto e ver todos os pedidos; não pode `DELETE` produto |
| `@Roles('ADMIN')` em rotas A de `/categories` | |

**Se pular A:** só `ADMIN` / `CLIENT`.

---

## Cap. 8 — Swagger

### P

- UI em `GET /api` (ou `/docs` — **fixar:** `/api`).
- Documentar as rotas P **já existentes** (produtos, pedidos, auth/roles dos caps. 5–7).
- `addBearerAuth()` + `@ApiBearerAuth()` nas rotas JWT.
- `@ApiProperty` em `CreateProductDto` e DTOs de auth/order.
- Rotas de **upload** (`/products/:id/image`) entram no Swagger no **cap. 9**, quando forem criadas.

### A (opcional)

- Tags e schemas das rotas A que o aluno implementou (`categories`, `auth/me`, etc.).
- Exemplos de resposta 400/401/403.

**Se pular A:** Swagger cobre só o núcleo P.

---

## Cap. 9 — Upload (após docs; mesmo projeto)

### P

| Método | Rota | Auth | Body | Resposta |
|--------|------|------|------|----------|
| `POST` | `/products/:id/image` | `ADMIN` | `multipart/form-data` campo `file` | `200` `{ "imageUrl": "/products/:id/image" }` |
| `GET` | `/products/:id/image` | - | - | arquivo ou redirect/static |

Coluna no banco: `Product.imageFilename` (nullable) — nome do arquivo em `./uploads`.  
`imageUrl` aparece **só na resposta HTTP** (path público), não como coluna. Validar existência do produto (`404`).

### A (opcional)

| Método | Rota | Notas |
|--------|------|-------|
| `POST` | `/products/:id/images` | várias imagens; limite MIME (`image/jpeg`, `image/png`) e tamanho |
| `DELETE` | `/products/:id/images/:imageId` | |

**Se pular A:** uma imagem por produto basta para o cap. 10.

---

## Cap. 10 — Testes

### P (obrigatório na aula)

| Tipo | O que cobrir |
|------|----------------|
| Unitário | `ProductsService` (create, not found, stock) com mock de repository |
| E2E | `POST /products` válido → 201; inválido → 400; `GET /products/:id` inexistente → 404 |
| E2E auth | login → create product com Bearer; sem token → 401 |

### A (opcional)

Specs apenas das features A implementadas (`categories`, `auth/me`, upload múltiplo…).  
Arquivos sugeridos: `*.a.spec.ts` ou pasta `test/desafios/`.

**Se pular A:** pipeline/aula roda só a suíte P.

---

## Capstone — Exercício e-commerce completo

Quem só fez **P** já tem loja utilizável. O capstone **não reinicia** o projeto: amplia A (e o UML do `exercicio-1.md`).

### Sugestão de pacotes A (aluno escolhe ≥ 1 “pacote completo” + opcionais)

**Pacote Endereço**

| Método | Rota | Auth |
|--------|------|------|
| `POST` | `/addresses` | `JWT` |
| `GET` | `/addresses` | `JWT` (próprios) |
| `PUT` | `/addresses/:id` | `JWT` |
| `DELETE` | `/addresses/:id` | `JWT` |
| `PATCH` | `/orders/:id/address` | `JWT` + body `{ "addressId" }` |

**Pacote Pagamento** (desafio clássico)

| Método | Rota | Auth | Regras |
|--------|------|------|--------|
| `POST` | `/orders/:id/payments` | `JWT` | 1 pagamento ativo/pedido; só `OPEN` |
| `GET` | `/payments` | `JWT` / `ADMIN` | filtros `status`, `orderId` |
| `PATCH` | `/payments/:id/status` | `ADMIN` ou dono conforme regra | |
| `DELETE` | `/payments/:id` | `ADMIN` | |

Métodos: `CARD` \| `BOLETO` \| `PIX`. Status: `PENDING` \| `PAID` \| `CANCELLED`.  
Ao marcar pagamento `PAID` → pedido `PAID`. Não alterar método após criar.

**Pacote catálogo rico** (se ainda não fez A do cap. 5)

- Fechar CRUD `Category` + associação produto.

### Critério de nota (sugestão)

| Nível | Entrega |
|-------|---------|
| Mínimo | Linha P caps. 1–10 rodando + README |
| Médio | P + 1 pacote A do capstone |
| Completo | P + categorias + endereço + pagamento + Swagger atualizado |

---

## Ordem canônica de estudo (README)

| Ordem | Arquivo | Foco P |
|-------|---------|--------|
| 0 | `0.typescript-para-nestjs.md` | Leitura TS |
| 1 | `1.introducao_nestjs.md` | `/health` |
| 2 | `2.controllers.md` | CRUD `/products` memória |
| 2.1 | `2.1.dtos-e-validacao.md` | DTOs produto |
| 3 | `3.services.md` | `ProductsService` + module |
| 4 | `4.introducao_nestjs_persistencia.md` | Conceitos |
| 5 | `5.crud_nest_bd.md` | Produtos + PostgreSQL |
| 5.1 | `5.1.pedidos.md` | `/orders` |
| 6 | `6.autenticacao.md` | JWT + endurecer mutações |
| 7 | `7.autorizacao.md` | Roles |
| 8 | `8.documentacao_api.md` | Swagger `/api` |
| 9 | `9.upload_arquivos.md` | Imagem do produto |
| 10 | `10.testes_software.md` | Suíte P |
| — | `exercicio-1.md` | Capstone A |

A **numeração dos arquivos** segue a ordem de estudo.

---

## Seed oficial

Ver [`seed/`](seed/): usuários **ana** (ADMIN) e **cli** (CLIENT), senha `secret123`, ≥ 2 produtos.  
Folha de curls: [`CURLS-P.md`](CURLS-P.md).

---

## Checklist rápido “P completo”

Ao final da trilha obrigatória, estes curls (ajuste token) devem funcionar:

```bash
# ver também CURLS-P.md e seed/ (ana=ADMIN, cli=CLIENT, senha secret123)
curl -s localhost:3000/health
curl -s localhost:3000/products
curl -s -X POST localhost:3000/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"ana","password":"secret123"}'
curl -s localhost:3000/api
```

---

## Contrato anti-quebra (resumo)

1. Código P não importa módulos/entidades só de A.  
2. Cada capítulo termina com seção **Desafio (Linha A)** explícita: “dispensável para o cap. N+1”.  
3. Seed oficial: 1 `ADMIN`, 1 `CLIENT`, ≥ 2 produtos.  
4. Testes da disciplina cobrem só P.  
5. Capstone evolui `loja-api`; não pede `nest new` do zero (salvo aluno que não acompanhou a trilha).

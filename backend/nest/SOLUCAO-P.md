# Gabarito de verificação — linha P (`loja-api`)

Não substitui implementar capítulo a capítulo. Use quando estiver travado: compare **comportamento HTTP** e **arquivos tocados** com o esperado abaixo.

Contrato canônico: [MAPA-LINHAS-P-A.md](MAPA-LINHAS-P-A.md). Curls: [CURLS-P.md](CURLS-P.md).

```mermaid
flowchart LR
    Travou[Travou?] --> Mapa[MAPA contrato]
    Mapa --> Curls[CURLS-P]
    Curls --> Sol[SOLUCAO-P este arquivo]
    Sol --> Cap[voltar ao capítulo]
```

---

## Por capítulo — o que deve funcionar

| Cap. | Verificação rápida |
|------|-------------------|
| **1** | `GET /health` → `200` `{ "status": "ok" }` |
| **2** | CRUD `/products` em memória; `POST` → `201`; `DELETE` → `204`; id inexistente → `404` |
| **2.1** | `POST /products` com `price: "barato"` → **400**; `ValidationPipe` em `main.ts` |
| **3** | Mesmos curls do cap. 2; lógica no `ProductsService` |
| **4** | Só leitura conceitual — **nenhum curl novo**; entenda entidade × DTO e Postgres antes do cap. 5 |
| **5** | Produto sobrevive restart; Postgres via Docker |
| **5.1** | `POST /orders` debita `stock`; cancel devolve estoque; estoque insuficiente → **400** |
| **6** | `seed.sql` + login Ana/Cli; `POST /products` sem token → **401**; **qualquer** Bearer (Ana **ou** Cli) → **201** (ADMIN-only = cap. 7) |
| **7** | Cli em `POST /products` → **403**; Ana → **201**; Cli em `POST /orders` → **201** |
| **8** | `GET /api` abre Swagger; Authorize com JWT |
| **9** | Ana upload imagem → **200**; Cli upload → **403**; MIME inválido → **400** |
| **10** | `npm test` + `npm run test:e2e` (após `bash scripts/e2e-prepare.sh`) |

---

## Árvore mínima esperada (caps. 6–7)

```text
loja-api/src/
  main.ts
  app.module.ts
  products/
    product.entity.ts
    products.module.ts
    products.service.ts
    products.controller.ts
    dto/create-product.dto.ts
    dto/update-product.dto.ts
  orders/
    order.entity.ts
    order-item.entity.ts
    orders.module.ts
    orders.service.ts
    orders.controller.ts
    dto/create-order.dto.ts
  auth/
    user.entity.ts
    auth.module.ts
    auth.service.ts
    auth.controller.ts
    jwt.strategy.ts
    jwt-auth.guard.ts
    roles.decorator.ts
    roles.guard.ts
    dto/register.dto.ts
    dto/login.dto.ts
```

---

## Seeds

```bash
# backend/nest/
bash seed/verify-seed.sh          # sempre após seed.sql
docker exec -i loja-postgres psql -U loja -d loja < seed/seed.sql
```

Login de lab: `ana` / `cli` → senha `secret123`.

---

## O que esta trilha **não** inclui

- Repositório com código-fonte completo da solução (você constrói no `loja-api`).
- Pacotes da linha A (capstone em [exercicio-1.md](exercicio-1.md)).

Professores podem publicar um branch `solucao-p` no repositório da turma espelhando esta árvore.

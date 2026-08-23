# Seed oficial — `loja-api`

Dados mínimos da **linha P** para lab e testes.

| Usuário | Senha | Role |
|---------|-------|------|
| `ana` | `secret123` | `ADMIN` (dona da loja) |
| `cli` | `secret123` | `CLIENT` |

Produtos: **Caneca Nest** (stock 10), **Camiseta ADS** (stock 25).

## Qual arquivo usar

| Arquivo | Quando |
|---------|--------|
| [`seed-catalog.sql`](seed-catalog.sql) | Após cap. **5** (só tabela `products`) |
| [`seed.sql`](seed.sql) | Após caps. **5.1 + 6** (tabelas `orders` / `order_items` / `users`) |

## Como aplicar

```bash
# a partir de backend/nest/
docker compose -f docker-compose.postgres.yml up -d

# só catálogo (cap. 5):
docker exec -i loja-postgres psql -U loja -d loja < seed/seed-catalog.sql

# seed completo (auth + pedidos):
docker exec -i loja-postgres psql -U loja -d loja < seed/seed.sql
bash seed/verify-seed.sh
```

> **`seed.sql` apaga** produtos, usuários e pedidos existentes (inclui pedidos de teste do cap. 5.1). Use de propósito no cap. 6+.

A API precisa ter subido ao menos uma vez com `synchronize: true` para criar as tabelas.

## Verificação

```bash
bash seed/verify-seed.sh
# OK: seed.sql verificado (ana/cli → secret123)
```

## Personagens

- **Ana** — administra catálogo (criar/editar produto, upload).  
- **Cli** — compra (pedidos).

Usados nos curls de [`CURLS-P.md`](../CURLS-P.md) e nos caps. de auth/roles/testes.

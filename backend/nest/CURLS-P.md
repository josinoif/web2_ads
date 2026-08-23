# Folha de curls — linha P (`loja-api`)

Base: `http://localhost:3000`  
Seed: [`seed/README.md`](seed/README.md) — **Ana** (ADMIN) e **Cli** (CLIENT), senha `secret123`.

Ordem alinhada à [trilha](README.md). Em conflito de contrato, o [mapa](MAPA-LINHAS-P-A.md) prevalece.

**Cwd dos comandos `docker exec` / `seed/`:** assuma shell em **`backend/nest/`**. Se estiver em `loja-api/`, use `../seed/...` e `docker compose -f ../docker-compose.postgres.yml`.

| Passos desta folha | Implemente antes de rodar |
|--------------------|---------------------------|
| 0–1 | Cap. 1 (`/health`) |
| 2–4 | Caps. 2–3 (produtos em memória + service) |
| 5 | Cap. 5 (Postgres + produtos) |
| 5.1 | Cap. 5.1 (`/orders`) |
| bloco seed + 6 | Cap. 6 (`auth`, JWT — **401** sem token; **qualquer** Bearer → **201** em `POST /products`) |
| 7 | Cap. 7 (roles — Cli leva **403** em `POST /products`) |
| 8 | Cap. 8 (Swagger `/api`) |
| 9 | Cap. 9 (upload) |

Travou? Compare com o [gabarito de verificação P](SOLUCAO-P.md).

```bash
# 0) Postgres + API — rode o compose a partir de backend/nest/
docker compose -f docker-compose.postgres.yml up -d
cd loja-api && npm run start:dev
# seed (paths relativos a backend/nest/):
#   cap. 5:   docker exec -i loja-postgres psql -U loja -d loja < seed/seed-catalog.sql
#   cap. 6+:  docker exec -i loja-postgres psql -U loja -d loja < seed/seed.sql
# se o shell estiver em loja-api/, use ../seed/...

# 1) Health (cap. 1)
curl -s http://localhost:3000/health

# 2–4) Catálogo em memória / service (sem seed ainda — use POST)
curl -s -X POST http://localhost:3000/products \
  -H 'Content-Type: application/json' \
  -d '{"name":"Caneca Nest","price":39.9,"stock":10}'
curl -s http://localhost:3000/products
curl -s http://localhost:3000/products/1

# 5) Catálogo no Postgres — seed só de products (a partir de backend/nest/)
# docker exec -i loja-postgres psql -U loja -d loja < seed/seed-catalog.sql
curl -s http://localhost:3000/products

# 5.1) Pedido (público neste capítulo; depois exige JWT do Cli)
curl -s -X POST http://localhost:3000/orders \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"productId":1,"quantity":2}]}'
curl -s http://localhost:3000/orders/1
curl -s -X POST http://localhost:3000/orders/1/cancel

# === OBRIGATÓRIO antes dos passos 6–9 (cap. 6+) ===
# Shell em backend/nest/ (se estiver em loja-api/, volte: cd ..)
# Apaga pedidos de teste do 5.1 e recria Ana (ADMIN) + Cli (CLIENT)
docker exec -i loja-postgres psql -U loja -d loja < seed/seed.sql
bash seed/verify-seed.sh
# em loja-api/:  docker exec ... < ../seed/seed.sql  &&  bash ../seed/verify-seed.sh

# 6) Auth — login
curl -s -X POST http://localhost:3000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"ana","password":"secret123"}'
curl -s -X POST http://localhost:3000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"cli","password":"secret123"}'

# 6) Auth — extrair token (escolha uma opção)
# Opção A — python3:
TOKEN_ANA=$(curl -s -X POST http://localhost:3000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"ana","password":"secret123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

TOKEN_CLI=$(curl -s -X POST http://localhost:3000/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"cli","password":"secret123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Opção B — jq (se tiver instalado):
# TOKEN_ANA=$(curl -s ... | jq -r .access_token)

# Opção C — manual: rode o login, copie access_token e export TOKEN_ANA='eyJ...' / TOKEN_CLI='eyJ...'

# 6b) JWT nas mutações (cap. 6 — ainda SEM roles: Ana e Cli criam produto)
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:3000/products \
  -H 'Content-Type: application/json' \
  -d '{"name":"X","price":1,"stock":1}'
# esperado: 401

curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:3000/products \
  -H "Authorization: Bearer $TOKEN_ANA" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Caneca Nest","price":39.9,"stock":5}'
# esperado: 201

curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:3000/products \
  -H "Authorization: Bearer $TOKEN_CLI" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Caneca Cli","price":19.9,"stock":3}'
# esperado: 201 (no cap. 7 isto vira 403)

# 7) Roles — Ana cria produto; Cli toma 403 (só depois do cap. 7)
curl -s -X POST http://localhost:3000/products \
  -H "Authorization: Bearer $TOKEN_ANA" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Adesivo IFPE","price":5.5,"stock":100}'

curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:3000/products \
  -H "Authorization: Bearer $TOKEN_CLI" \
  -H 'Content-Type: application/json' \
  -d '{"name":"X","price":1,"stock":1}'
# esperado: 403

# Cli cria pedido autenticado
curl -s -X POST http://localhost:3000/orders \
  -H "Authorization: Bearer $TOKEN_CLI" \
  -H 'Content-Type: application/json' \
  -d '{"items":[{"productId":1,"quantity":1}]}'

# 8) Swagger
# abra http://localhost:3000/api — Authorize com o token da Ana
# (rotas de imagem entram no Swagger no cap. 9)

# 9) Upload (Ana) — fixture do material: backend/nest/fixtures/caneca.jpg
test -f ./fixtures/caneca.jpg || cp ../fixtures/caneca.jpg ./fixtures/
curl -s -X POST http://localhost:3000/products/1/image \
  -H "Authorization: Bearer $TOKEN_ANA" \
  -F 'file=@./fixtures/caneca.jpg'
# MIME inválido → 400:
# echo x > /tmp/fake.txt && curl ... -F "file=@/tmp/fake.txt"
curl -s -o /tmp/p.jpg -w '%{http_code}\n' http://localhost:3000/products/1/image
```

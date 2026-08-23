# Tutorial NestJS — Backend (`loja-api`)

Material de estudo para construir uma API de **e-commerce** com **NestJS 10** e **PostgreSQL**.

## Linhas P e A

| Linha | Nome | Regra |
|-------|------|--------|
| **P** | Principal (obrigatória) | Ao fim do capítulo a API sobe e os curls de P passam. O capítulo seguinte **só depende de P**. |
| **A** | Alternativa (desafio) | Amplia o domínio. **Nunca** é importada pelo código da linha P. |

Detalhe canônico das rotas: [`MAPA-LINHAS-P-A.md`](MAPA-LINHAS-P-A.md).  
**Em conflito entre tutorial e mapa, o mapa prevalece.**

**Projeto único:** `loja-api` — crie com `npx -y @nestjs/cli@10 new loja-api` **dentro de** [`backend/nest/`](.) (ao lado do Compose e do `seed/`).  
**Banco:** PostgreSQL 16 — [`docker-compose.postgres.yml`](docker-compose.postgres.yml).  
**Seed oficial:** [`seed/`](seed/) — **Ana** (ADMIN) e **Cli** (CLIENT), senha `secret123`.  
**Folha de curls P:** [`CURLS-P.md`](CURLS-P.md).  
**Gabarito de verificação P:** [`SOLUCAO-P.md`](SOLUCAO-P.md) — checklist HTTP e árvore de arquivos (sem código pronto).

| Shell em… | Compose | Seed |
|-----------|---------|------|
| `backend/nest/` | `docker compose -f docker-compose.postgres.yml up -d` | `seed/seed-catalog.sql` ou `seed/seed.sql` |
| `backend/nest/loja-api/` | `docker compose -f ../docker-compose.postgres.yml up -d` | `../seed/...` |

---

## Sinopse da loja

**Ana** sobe a `loja-api` → cadastra a **Caneca Nest** no catálogo → valida a entrada com DTOs → organiza a regra no service → grava no **PostgreSQL** → **Cli** compra (pedido + estoque) → ambos se autenticam com JWT → Ana ganha poder de **ADMIN** → documenta no Swagger → sobe a foto do produto → testa a linha P → amplia com pacotes A no capstone.

---

## Como cada capítulo está organizado

1. **Objetivo** — o que você deve conseguir ao terminar  
2. **Pré-requisito / próximo passo**  
3. **Contexto** — problema da `loja-api` (Ana / Cli)  
4. **Conceito** em pontos estratégicos  
5. **Linha P** — implementação + curls  
6. **Desafio (Linha A)** — opcional  
7. **Checkpoint** + frase *o que a loja ganhou hoje*  
8. Rodapé: contrato do mapa

---

## Pré-requisitos

- Node.js 18+ (LTS 20 recomendado; trilha testada com Nest 10), npm, Docker  
- HTTP/REST básico; JS básico → cap. 0 para TypeScript/Nest  
- Comandos `nest g` → rode **`npx nest g …` dentro de `loja-api/`** (usa o CLI local do projeto)  
- Variáveis de ambiente: copie [`.env.example`](.env.example) para `loja-api/.env`  

---

## Docker — troubleshooting

| Sintoma | O que fazer |
|---------|-------------|
| `Cannot connect to the Docker daemon` | Inicie o Docker Desktop / serviço (`sudo systemctl start docker` no Linux). |
| `port is already allocated` (5432) | Pare o Postgres local ou altere a porta no `docker-compose.postgres.yml`. |
| API sobe, queries falham | `docker compose -f docker-compose.postgres.yml ps` — espere `healthy` no `loja-postgres`. |
| `relation "users" does not exist` ao aplicar seed | Suba a API uma vez (`synchronize: true`) **antes** do `seed.sql`. |

Teste rápido:

```bash
docker compose -f docker-compose.postgres.yml up -d
docker exec -it loja-postgres psql -U loja -d loja -c '\conninfo'
```

---

## Ordem de estudo (= numeração dos arquivos)

| Ordem | Arquivo | Episódio | Foco P | Duração sugerida |
|-------|---------|----------|--------|------------------|
| 0 | [`0.typescript-para-nestjs.md`](0.typescript-para-nestjs.md) | Óculos para ler o `loja-api` | Ler código Nest | Pré-aula ou 2 encontros |
| 1 | [`1.introducao_nestjs.md`](1.introducao_nestjs.md) | A loja sobe (`/health`) | `loja-api` + health | 1 encontro |
| 2 | [`2.controllers.md`](2.controllers.md) | A vitrine abre (RAM) | CRUD `/products` | 1 encontro |
| 2.1 | [`2.1.dtos-e-validacao.md`](2.1.dtos-e-validacao.md) | Porta da frente | DTOs + pipe | 1 encontro + consulta em casa (§5–7) |
| 3 | [`3.services.md`](3.services.md) | Estoque lógico | `ProductsService` + DI | 1 encontro |
| 4 | [`4.introducao_nestjs_persistencia.md`](4.introducao_nestjs_persistencia.md) | Por que o Postgres | Conceitos TypeORM | ½–1 encontro |
| 5 | [`5.crud_nest_bd.md`](5.crud_nest_bd.md) | Caneca sobrevive ao restart | Produtos no PG | 1 encontro |
| 5.1 | [`5.1.pedidos.md`](5.1.pedidos.md) | Cli compra | `/orders` | 1 encontro |
| 6 | [`6.autenticacao.md`](6.autenticacao.md) | Identidade Ana/Cli | JWT (Partes A+B) | 1 lab longo ou 2 |
| 7 | [`7.autorizacao.md`](7.autorizacao.md) | Mesmo token ≠ todas as portas | Roles | 1 encontro |
| 8 | [`8.documentacao_api.md`](8.documentacao_api.md) | Cardápio vivo `/api` | Swagger | ½–1 encontro |
| 9 | [`9.upload_arquivos.md`](9.upload_arquivos.md) | Foto na Caneca Nest | Upload | 1 encontro |
| 10 | [`10.testes_software.md`](10.testes_software.md) | Rede de segurança | Suíte P | 1 encontro |
| — | [`exercicio-1.md`](exercicio-1.md) | Pacotes A | Capstone | Projeto / prazo do professor |

**Cap. 2.1:** na aula foque §1–4 + §4.1; §5–7 é consulta de decorators.

---

## PostgreSQL e seed

```bash
docker compose -f docker-compose.postgres.yml up -d
# após cap. 5 (só products):
docker exec -i loja-postgres psql -U loja -d loja < seed/seed-catalog.sql
# após auth + pedidos (seed completo):
docker exec -i loja-postgres psql -U loja -d loja < seed/seed.sql
bash seed/verify-seed.sh   # confirma ana/cli → secret123
```

**Testes e2e (cap. 10):** com Docker no ar, `bash scripts/e2e-prepare.sh` sobe Postgres, sincroniza schema se necessário e aplica o seed. **Pare** `npm run start:dev` antes — o prepare usa a porta `3000`.

```bash
# cap. 10 — a partir de backend/nest/
bash scripts/e2e-prepare.sh
cd loja-api && npm run test:e2e
```

| Variável | Valor |
|----------|--------|
| host / port | `localhost` / `5432` |
| user / password / db | `loja` / `loja` / `loja` |

Driver: `pg`.

---

## Domínio mínimo (P)

| Entidade | Capítulo |
|----------|----------|
| `Product` | 2 → 5 |
| `Order` + `OrderItem` | 5.1 |
| `User` (+ `role`) | 6–7 |

Personagens: **Ana** administra; **Cli** compra.

---

## Compatibilidade

NestJS 10 + PostgreSQL 16.

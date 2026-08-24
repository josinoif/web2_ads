# Lab — Concorrência Postgres (3 APIs)

**Tutorial:** [tutorial-concorrencia-postgres.md](../tutorial-concorrencia-postgres.md)  
**Porta:** `8087` (nginx) · Postgres `5438`

## Subir

```bash
docker compose up -d --build
./scripts/status.sh
```

## Endpoints

- `POST /matricular?mode=broken|transaction|advisory|optimistic`  
- `GET /disciplinas/{id}`  
- `GET /coordenacao/status`  

## Scripts

| Script | Uso |
|--------|-----|
| `disputa-vaga.sh --paralelo --mode broken` | Exp. 1 overbooking |
| `disputa-vaga.sh --paralelo --mode transaction` | Exp. 2 correto |
| `comparar-modos.sh` | Demo completa (lento) |

## Encerrar

```bash
docker compose down -v
```

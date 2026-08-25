# Lab — Escala na camada de dados

**Tutorial:** [tutorial-escala-dados.md](../tutorial-escala-dados.md)  
**Porta:** `8090` · Mongo A `27119` · Mongo B `27120`

## Subir

```bash
docker compose up -d --build
./scripts/status.sh
```

## Endpoints

- `POST /avisos` `{"campus_id":"A","titulo":"..."}`
- `GET /avisos?campus_id=A` (um shard)
- `GET /avisos` (fan-out nos dois shards)
- `GET /escala/status`

## Scripts

| Script | Uso |
|--------|-----|
| `publicar-lote.sh hot\|spread` | Carga concentrada vs espalhada |
| `medir-writes.sh` | Contagens hot/spread + fan-out |

**Evidência principal:** distribuição nos shards. `WRITE_MS` / `READ_SHARD_MS` só tornam tempo e fan-out mais legíveis.

## Encerrar

```bash
docker compose down -v
```

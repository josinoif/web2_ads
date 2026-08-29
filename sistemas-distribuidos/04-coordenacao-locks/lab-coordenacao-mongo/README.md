# Lab — Coordenação Mongo + Redis

> **Linux e Windows:** `docker compose` é o mesmo nos dois SOs. No PowerShell, `./scripts/foo.sh` vira `.\lab.ps1 foo` (nesta pasta) e `curl` vira `curl.exe`. Guia: [linux-e-windows.md](../../ferramentas/linux-e-windows.md).


**Tutorial:** [tutorial-coordenacao-mongo-redis.md](../tutorial-coordenacao-mongo-redis.md)  
**Porta:** `8088` · Mongo `27118` · Redis `6380`

## Subir

```bash
docker compose up -d --build
./scripts/status.sh
```

## Endpoints

- `POST /reservar?mode=rmw|atomic|redis-lock&hold_seconds=0`  
- `GET /filas/{disciplina_id}`  
- `GET /coordenacao/status`  

## Scripts

| Script | Uso |
|--------|-----|
| `disputa-fila.sh --paralelo --mode rmw` | Overbooking |
| `disputa-fila.sh --paralelo --mode atomic` | Atomic doc |
| `provocar-lock-orfao.sh` | TTL / lock órfão |
| `comparar-atomico-vs-rmw.sh` | Demo completa |

## Encerrar

```bash
docker compose down -v
```

# Lab — timeout / retry / dedup (MongoDB)

**Tutorial:** [tutorial-timeout-mongodb.md](../tutorial-timeout-mongodb.md)  
**Portas:** API `8093` · Mongo `27121`

## Subir

```bash
cd sistemas-distribuidos/06-falhas-timeout/lab-timeout-mongodb
./scripts/up.sh
```

## Comandos rápidos

| Ação | Comando |
|------|---------|
| Status | `./scripts/status.sh` |
| Store lento | `./scripts/provocar-lento.sh 3000` |
| Unique on/off | `./scripts/ativar-unique.sh 1` (limpa avisos) / `0` |
| Publicar | `./scripts/publicar.sh "Titulo"` |
| Retry sem unique | `UNIQUE=0 ./scripts/publicar-com-retry.sh` |
| Retry com unique | `UNIQUE=1 ./scripts/publicar-com-retry.sh` |

Timeout do cliente → JSON `erro: cliente`. Retry só em timeout/503 (para em 409).  
`writeConcern` = revisão opcional do módulo 03 (1 nó ≈ sem diferença visível).

## Encerrar

```bash
docker compose down -v
```

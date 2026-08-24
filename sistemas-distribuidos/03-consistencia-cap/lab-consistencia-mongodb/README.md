# Lab — MongoDB readConcern / writeConcern + feed de avisos

**Tutorial:** [tutorial-consistencia-mongodb.md](../tutorial-consistencia-mongodb.md)  
**Porta API:** `8086` · Mongo host (mongo1): `27117`

## Subir

```bash
docker compose up -d --build
curl -s http://localhost:8086/health | python3 -m json.tool
```

## Comandos rápidos

| Ação | Comando |
|------|---------|
| Publicar (majority) | `./scripts/publicar-aviso.sh "Prova adiada"` |
| Publicar (w1) | `WC=w1 ./scripts/publicar-aviso.sh "Aviso rápido"` |
| Comparar leituras | `./scripts/comparar-concerns.sh` |
| Divergência sob partição | `./scripts/provocar-divergencia.sh` |
| Partição parcial | `./scripts/particionar-mongo.sh` |
| Curar | `./scripts/curar-particao-mongo.sh` |
| Status cluster | `curl -s localhost:8086/consistencia/status \| python3 -m json.tool` |

## Encerrar

```bash
docker compose down -v
```

**Antes de subir:** encerre labs do módulo 02 se usarem `27017`/`8083` — este lab usa `27117`/`8086`.

## Redes

- `app_net` — API ↔ mongo1 (primary)  
- `rs_net` — mongo1 ↔ mongo2 ↔ mongo3; API também está aqui para `dest=secondary`  
- `particionar-mongo.sh` desconecta mongo2/3 de `rs_net` (primary isolado do quórum de replicação)

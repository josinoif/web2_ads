# Lab — partição Postgres + matrícula CP

**Tutorial:** [tutorial-particao-postgres.md](../tutorial-particao-postgres.md)  
**Porta API:** `8085` · Postgres host: `5436` (primary) / `5437` (réplica)

## Subir

```bash
docker compose up -d --build
./scripts/verificar-modo-cp.sh   # sync_state deve ser sync
curl -s http://localhost:8085/health | python3 -m json.tool
```

## Comandos rápidos

| Ação | Comando |
|------|---------|
| Matricular | `./scripts/matricular.sh SD-101 aluno-1` |
| Disputa última vaga | `./scripts/provocar-disputa-vaga.sh` |
| Simular partição | `./scripts/particionar.sh` |
| Curar partição | `./scripts/curar-particao.sh` |
| Status sync | `curl -s localhost:8085/consistencia/status \| python3 -m json.tool` |
| Disciplina (primary/réplica) | `curl -s 'localhost:8085/disciplinas/SD-101?dest=replica'` |

## Encerrar

```bash
docker compose down -v
```

## Redes

- `app_net` — API ↔ primary  
- `repl_net` — primary ↔ réplica; API também está aqui para `GET ?dest=replica`  
- `particionar.sh` desconecta **só** a réplica de `repl_net` (API continua alcançando primary e réplica isolada para leitura)
